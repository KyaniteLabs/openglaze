"""
Payment Provider Router
Selects and configures the appropriate payment provider.
"""
import os
from typing import Optional

from . import PaymentProvider
from .stripe import StripeProvider
from .paypal import PayPalProvider
from .crypto import BTCPayProvider
from .manual import ManualProvider


def get_provider(provider_name: str) -> Optional[PaymentProvider]:
    """Get a configured payment provider by name.

    Args:
        provider_name: Name of the provider (stripe, paypal, btcpay, manual)

    Returns:
        Configured PaymentProvider instance or None if not available
    """
    providers = {
        'stripe': _get_stripe_provider,
        'paypal': _get_paypal_provider,
        'btcpay': _get_btcpay_provider,
        'manual': _get_manual_provider
    }

    factory = providers.get(provider_name)
    if not factory:
        return None

    return factory()


def get_available_providers() -> list:
    """Get list of available payment providers based on configuration.

    Returns:
        List of provider names that are properly configured
    """
    available = []

    if os.environ.get('STRIPE_API_KEY') and os.environ.get('STRIPE_WEBHOOK_SECRET'):
        available.append('stripe')

    if os.environ.get('PAYPAL_CLIENT_ID') and os.environ.get('PAYPAL_CLIENT_SECRET'):
        available.append('paypal')

    if os.environ.get('BTCPAY_URL') and os.environ.get('BTCPAY_API_KEY'):
        available.append('btcpay')

    # Manual provider is always available
    available.append('manual')

    return available


def _get_stripe_provider() -> Optional[PaymentProvider]:
    """Get Stripe provider if configured."""
    api_key = os.environ.get('STRIPE_API_KEY')
    webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')

    if not api_key or not webhook_secret:
        return None

    return StripeProvider(api_key=api_key, webhook_secret=webhook_secret)


def _get_paypal_provider() -> Optional[PaymentProvider]:
    """Get PayPal provider if configured."""
    client_id = os.environ.get('PAYPAL_CLIENT_ID')
    client_secret = os.environ.get('PAYPAL_CLIENT_SECRET')
    mode = os.environ.get('PAYPAL_MODE', 'sandbox')

    if not client_id or not client_secret:
        return None

    return PayPalProvider(
        client_id=client_id,
        client_secret=client_secret,
        mode=mode
    )


def _get_btcpay_provider() -> Optional[PaymentProvider]:
    """Get BTCPay provider if configured."""
    url = os.environ.get('BTCPAY_URL')
    store_id = os.environ.get('BTCPAY_STORE_ID')
    api_key = os.environ.get('BTCPAY_API_KEY')

    if not url or not store_id or not api_key:
        return None

    return BTCPayProvider(
        btcpay_url=url,
        store_id=store_id,
        api_key=api_key
    )


def _get_manual_provider() -> PaymentProvider:
    """Get manual provider (always available)."""
    return ManualProvider(
        admin_email=os.environ.get('MANUAL_BILLING_EMAIL', 'billing@example.com')
    )
