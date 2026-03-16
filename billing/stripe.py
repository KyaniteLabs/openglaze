"""
Stripe Payment Provider
Industry-standard payment processing.
"""
import stripe
from typing import Optional, Dict, Any

from . import PaymentProvider


class StripeProvider(PaymentProvider):
    """Stripe payment provider implementation."""

    def __init__(self, api_key: str, webhook_secret: str):
        """Initialize Stripe provider.

        Args:
            api_key: Stripe API key (sk_live_... or sk_test_...)
            webhook_secret: Stripe webhook signing secret
        """
        stripe.api_key = api_key
        self.webhook_secret = webhook_secret

        # Price IDs (configure in Stripe Dashboard)
        self.prices = {
            'pro_monthly': os.environ.get('STRIPE_PRICE_PRO_MONTHLY', 'price_pro_monthly'),
            'pro_yearly': os.environ.get('STRIPE_PRICE_PRO_YEARLY', 'price_pro_yearly'),
            'studio_monthly': os.environ.get('STRIPE_PRICE_STUDIO_MONTHLY', 'price_studio_monthly'),
            'studio_yearly': os.environ.get('STRIPE_PRICE_STUDIO_YEARLY', 'price_studio_yearly'),
            'education_yearly': os.environ.get('STRIPE_PRICE_EDUCATION_YEARLY', 'price_education_yearly'),
        }

    def create_checkout_session(
        self,
        user_id: str,
        tier: str,
        success_url: str,
        cancel_url: str,
        interval: str = 'monthly'
    ) -> Optional[Dict[str, Any]]:
        """Create a Stripe checkout session.

        Args:
            user_id: User's unique identifier
            tier: Subscription tier
            success_url: Redirect URL after success
            cancel_url: Redirect URL after cancel
            interval: 'monthly' or 'yearly'

        Returns:
            Dict with checkout URL and provider name
        """
        # Education is yearly only
        if tier == 'education':
            interval = 'yearly'

        price_key = f"{tier}_{interval}"
        price_id = self.prices.get(price_key)

        if not price_id:
            return None

        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=success_url,
                cancel_url=cancel_url,
                client_reference_id=user_id,
                metadata={
                    'user_id': user_id,
                    'tier': tier
                }
            )

            return {
                'url': session.url,
                'provider': 'stripe',
                'session_id': session.id
            }

        except stripe.error.StripeError as e:
            print(f"Stripe checkout error: {e}")
            return None

    def handle_webhook(
        self,
        payload: bytes,
        signature: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """Handle Stripe webhook.

        Args:
            payload: Raw webhook payload
            signature: Stripe-Signature header

        Returns:
            Dict with action details if relevant
        """
        if not signature:
            return None

        try:
            event = stripe.Webhook.construct_event(
                payload, signature, self.webhook_secret
            )

            event_type = event['type']

            if event_type == 'checkout.session.completed':
                session = event['data']['object']
                return {
                    'action': 'subscribe',
                    'user_id': session.get('client_reference_id'),
                    'tier': session.get('metadata', {}).get('tier'),
                    'subscription_id': session.get('subscription'),
                    'provider': 'stripe'
                }

            elif event_type == 'customer.subscription.deleted':
                subscription = event['data']['object']
                return {
                    'action': 'cancel',
                    'subscription_id': subscription['id'],
                    'provider': 'stripe'
                }

            elif event_type == 'invoice.payment_failed':
                invoice = event['data']['object']
                return {
                    'action': 'payment_failed',
                    'subscription_id': invoice.get('subscription'),
                    'provider': 'stripe'
                }

            return None

        except stripe.error.SignatureVerificationError:
            print("Invalid Stripe webhook signature")
            return None
        except Exception as e:
            print(f"Stripe webhook error: {e}")
            return None

    def cancel_subscription(self, subscription_id: str) -> bool:
        """Cancel a Stripe subscription.

        Args:
            subscription_id: Stripe subscription ID

        Returns:
            True if cancelled successfully
        """
        try:
            stripe.Subscription.delete(subscription_id)
            return True
        except stripe.error.StripeError:
            return False

    def get_subscription(self, subscription_id: str) -> Optional[Dict[str, Any]]:
        """Get Stripe subscription details.

        Args:
            subscription_id: Stripe subscription ID

        Returns:
            Dict with subscription details
        """
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)

            return {
                'id': subscription.id,
                'status': subscription.status,
                'current_period_start': subscription.current_period_start,
                'current_period_end': subscription.current_period_end,
                'cancel_at_period_end': subscription.cancel_at_period_end,
                'provider': 'stripe'
            }

        except stripe.error.StripeError:
            return None
