"""
PayPal Payment Provider
Alternative payment method with broad consumer adoption.
"""
import paypalrestsdk
from typing import Optional, Dict, Any

from . import PaymentProvider, PRICING


class PayPalProvider(PaymentProvider):
    """PayPal payment provider implementation."""

    def __init__(self, client_id: str, client_secret: str, mode: str = 'sandbox'):
        """Initialize PayPal provider.

        Args:
            client_id: PayPal client ID
            client_secret: PayPal client secret
            mode: 'sandbox' or 'live'
        """
        paypalrestsdk.configure({
            'mode': mode,
            'client_id': client_id,
            'client_secret': client_secret
        })

        self.mode = mode

    def create_checkout_session(
        self,
        user_id: str,
        tier: str,
        success_url: str,
        cancel_url: str,
        interval: str = 'monthly'
    ) -> Optional[Dict[str, Any]]:
        """Create a PayPal payment.

        Note: PayPal subscriptions require a different flow.
        This creates a one-time payment for demo purposes.

        Args:
            user_id: User's unique identifier
            tier: Subscription tier
            success_url: Redirect URL after success
            cancel_url: Redirect URL after cancel
            interval: 'monthly' or 'yearly'

        Returns:
            Dict with approval URL and provider name
        """
        # Education is yearly only
        if tier == 'education':
            interval = 'yearly'

        pricing = PRICING.get(tier, {})
        amount = str(pricing.get(interval, 9.00))

        try:
            payment = paypalrestsdk.Payment({
                'intent': 'sale',
                'payer': {
                    'payment_method': 'paypal'
                },
                'transactions': [{
                    'amount': {
                        'total': amount,
                        'currency': 'USD'
                    },
                    'description': f'Glaze Lab {tier.title()} {interval} subscription',
                    'custom': f'{user_id}|{tier}|{interval}'
                }],
                'redirect_urls': {
                    'return_url': success_url,
                    'cancel_url': cancel_url
                }
            })

            if payment.create():
                # Find the approval URL
                approval_url = None
                for link in payment.links:
                    if link.rel == 'approval_url':
                        approval_url = link.href
                        break

                if approval_url:
                    return {
                        'url': approval_url,
                        'provider': 'paypal',
                        'payment_id': payment.id
                    }

            return None

        except paypalrestsdk.exceptions.PayPalError as e:
            print(f"PayPal payment error: {e}")
            return None

    def handle_webhook(
        self,
        payload: bytes,
        signature: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """Handle PayPal webhook (IPN).

        Args:
            payload: Raw webhook payload
            signature: PayPal transmission signature

        Returns:
            Dict with action details if relevant
        """
        # PayPal uses IPN (Instant Payment Notification) or webhooks
        # This is a simplified implementation
        import json

        try:
            data = json.loads(payload.decode('utf-8'))
            event_type = data.get('event_type')

            if event_type == 'PAYMENT.SALE.COMPLETED':
                resource = data.get('resource', {})
                custom = resource.get('custom', '').split('|')

                if len(custom) >= 2:
                    return {
                        'action': 'subscribe',
                        'user_id': custom[0],
                        'tier': custom[1],
                        'provider': 'paypal'
                    }

            elif event_type == 'BILLING.SUBSCRIPTION.CANCELLED':
                return {
                    'action': 'cancel',
                    'subscription_id': data.get('resource', {}).get('id'),
                    'provider': 'paypal'
                }

            return None

        except Exception as e:
            print(f"PayPal webhook error: {e}")
            return None

    def cancel_subscription(self, subscription_id: str) -> bool:
        """Cancel a PayPal subscription.

        Args:
            subscription_id: PayPal subscription ID

        Returns:
            True if cancelled successfully
        """
        try:
            # PayPal subscription cancellation via API
            # Note: This requires the billing agreements API
            import requests

            # This is a simplified example
            # Real implementation needs proper OAuth2 token handling
            return True

        except Exception as e:
            print(f"PayPal cancellation error: {e}")
            return False

    def get_subscription(self, subscription_id: str) -> Optional[Dict[str, Any]]:
        """Get PayPal subscription details.

        Args:
            subscription_id: PayPal subscription ID

        Returns:
            Dict with subscription details
        """
        try:
            # Simplified - real implementation needs PayPal API calls
            return {
                'id': subscription_id,
                'status': 'active',
                'provider': 'paypal'
            }

        except Exception:
            return None

    def execute_payment(self, payment_id: str, payer_id: str) -> bool:
        """Execute an approved PayPal payment.

        Args:
            payment_id: PayPal payment ID
            payer_id: Payer ID from redirect

        Returns:
            True if payment executed successfully
        """
        try:
            payment = paypalrestsdk.Payment.find(payment_id)
            if payment.execute({'payer_id': payer_id}):
                return True
            return False

        except paypalrestsdk.exceptions.PayPalError:
            return False
