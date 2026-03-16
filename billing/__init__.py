"""
Glaze Lab Billing Module
Multiple payment provider adapters for maximum flexibility.
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class PaymentProvider(ABC):
    """Abstract base class for payment providers."""

    @abstractmethod
    def create_checkout_session(
        self,
        user_id: str,
        tier: str,
        success_url: str,
        cancel_url: str
    ) -> Optional[Dict[str, Any]]:
        """Create a checkout session for subscription.

        Args:
            user_id: User's unique identifier
            tier: Subscription tier (pro, studio, education)
            success_url: URL to redirect after successful payment
            cancel_url: URL to redirect if user cancels

        Returns:
            Dict with 'url' and 'provider' keys, or None on failure
        """
        pass

    @abstractmethod
    def handle_webhook(
        self,
        payload: bytes,
        signature: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """Handle webhook from payment provider.

        Args:
            payload: Raw webhook payload bytes
            signature: Webhook signature header for verification

        Returns:
            Dict with action details, or None if not relevant
        """
        pass

    @abstractmethod
    def cancel_subscription(self, subscription_id: str) -> bool:
        """Cancel an active subscription.

        Args:
            subscription_id: Provider's subscription ID

        Returns:
            True if cancelled successfully, False otherwise
        """
        pass

    @abstractmethod
    def get_subscription(self, subscription_id: str) -> Optional[Dict[str, Any]]:
        """Get subscription details.

        Args:
            subscription_id: Provider's subscription ID

        Returns:
            Dict with subscription details, or None if not found
        """
        pass


# Pricing configuration
PRICING = {
    'pro': {
        'monthly': 9.00,
        'yearly': 90.00,  # ~2 months free
        'currency': 'USD',
        'features': [
            'Unlimited glazes',
            'Recipe calculator',
            'Basic analytics',
            'Export to PDF'
        ]
    },
    'studio': {
        'monthly': 29.00,
        'yearly': 290.00,
        'currency': 'USD',
        'features': [
            'Everything in Pro',
            'Team collaboration (5 users)',
            'Advanced analytics',
            'API access',
            'Priority support'
        ]
    },
    'education': {
        'yearly': 199.00,
        'currency': 'USD',
        'features': [
            'Everything in Studio',
            'Unlimited users',
            'LMS integration',
            'Curriculum templates',
            'Dedicated support'
        ]
    }
}
