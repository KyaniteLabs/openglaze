"""
Manual Payment Provider
For education, enterprise, and custom billing arrangements.
"""
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

from . import PaymentProvider, PRICING


class ManualProvider(PaymentProvider):
    """Manual payment provider for non-automated billing.

    Use cases:
    - Educational institutions (purchase orders)
    - Enterprise accounts (invoicing)
    - Bank transfers
    - Check payments
    - Sponsored accounts
    """

    def __init__(self, admin_email: str = 'billing@example.com'):
        """Initialize manual provider.

        Args:
            admin_email: Email for billing inquiries
        """
        self.admin_email = admin_email
        self.pending_approvals = {}  # In production, use database

    def create_checkout_session(
        self,
        user_id: str,
        tier: str,
        success_url: str,
        cancel_url: str,
        interval: str = 'monthly'
    ) -> Optional[Dict[str, Any]]:
        """Create a manual approval request.

        Args:
            user_id: User's unique identifier
            tier: Subscription tier
            success_url: Redirect URL after approval
            cancel_url: Redirect URL if cancelled

        Returns:
            Dict with pending approval URL and provider name
        """
        # Education is yearly only
        if tier == 'education':
            interval = 'yearly'

        # Generate approval token
        approval_token = str(uuid.uuid4())

        # Store pending approval (in production, use database)
        self.pending_approvals[approval_token] = {
            'user_id': user_id,
            'tier': tier,
            'interval': interval,
            'created_at': datetime.utcnow().isoformat(),
            'status': 'pending'
        }

        pricing = PRICING.get(tier, {})
        amount = pricing.get(interval, 0)

        return {
            'url': f'/billing/manual-approval?token={approval_token}&tier={tier}',
            'provider': 'manual',
            'approval_token': approval_token,
            'amount': amount,
            'currency': 'USD',
            'admin_email': self.admin_email,
            'instructions': self._get_instructions(tier, amount)
        }

    def _get_instructions(self, tier: str, amount: float) -> str:
        """Get payment instructions for manual processing.

        Args:
            tier: Subscription tier
            amount: Amount due

        Returns:
            Formatted payment instructions
        """
        return f"""
To complete your {tier.title()} subscription (${amount:.2f}/year for education, monthly for others):

1. INVOICE REQUEST
   Email: {self.admin_email}
   Subject: Glaze Lab {tier.title()} Subscription
   Include: Your email, studio/school name, billing address

2. PURCHASE ORDER (Educational Institutions)
   - Generate PO for ${amount:.2f}
   - Email to {self.admin_email}
   - Include user account email(s) to activate

3. BANK TRANSFER
   Contact {self.admin_email} for wire transfer details

4. CHECK PAYMENT
   Mail to: [Your Business Address]
   Include: Account email and desired tier

Processing time: 1-3 business days after receipt.

Questions? Contact {self.admin_email}
        """.strip()

    def handle_webhook(
        self,
        payload: bytes,
        signature: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """Manual provider has no webhooks.

        Args:
            payload: Raw webhook payload
            signature: Webhook signature

        Returns:
            Always None (no automated webhooks)
        """
        # Manual billing has no automated webhooks
        # Approvals are processed via admin panel
        return None

    def cancel_subscription(self, subscription_id: str) -> bool:
        """Cancel a manual subscription.

        Args:
            subscription_id: Manual subscription ID

        Returns:
            True if cancelled successfully
        """
        # In production, update database record
        # For now, just return True
        return True

    def get_subscription(self, subscription_id: str) -> Optional[Dict[str, Any]]:
        """Get manual subscription details.

        Args:
            subscription_id: Manual subscription ID

        Returns:
            Dict with subscription details
        """
        # Check pending approvals
        if subscription_id in self.pending_approvals:
            return self.pending_approvals[subscription_id]

        # In production, query database
        return None

    def approve_subscription(
        self,
        approval_token: str,
        admin_user: str,
        notes: str = ''
    ) -> Optional[Dict[str, Any]]:
        """Approve a pending subscription (admin action).

        Args:
            approval_token: Token from checkout session
            admin_user: Admin user who approved
            notes: Optional notes

        Returns:
            Dict with approval details
        """
        if approval_token not in self.pending_approvals:
            return None

        approval = self.pending_approvals[approval_token]

        if approval['status'] != 'pending':
            return None

        # Mark as approved
        approval['status'] = 'approved'
        approval['approved_at'] = datetime.utcnow().isoformat()
        approval['approved_by'] = admin_user
        approval['notes'] = notes

        return {
            'action': 'subscribe',
            'user_id': approval['user_id'],
            'tier': approval['tier'],
            'interval': approval['interval'],
            'provider': 'manual',
            'approval_token': approval_token
        }

    def reject_subscription(
        self,
        approval_token: str,
        admin_user: str,
        reason: str = ''
    ) -> bool:
        """Reject a pending subscription (admin action).

        Args:
            approval_token: Token from checkout session
            admin_user: Admin user who rejected
            reason: Rejection reason

        Returns:
            True if rejected successfully
        """
        if approval_token not in self.pending_approvals:
            return False

        approval = self.pending_approvals[approval_token]

        if approval['status'] != 'pending':
            return False

        # Mark as rejected
        approval['status'] = 'rejected'
        approval['rejected_at'] = datetime.utcnow().isoformat()
        approval['rejected_by'] = admin_user
        approval['rejection_reason'] = reason

        return True

    def list_pending(self) -> list:
        """List all pending approvals.

        Returns:
            List of pending approval records
        """
        return [
            {'token': token, **data}
            for token, data in self.pending_approvals.items()
            if data['status'] == 'pending'
        ]
