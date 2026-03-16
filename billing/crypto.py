"""
BTCPay Server Payment Provider
Self-hosted cryptocurrency payment processing.
"""
import requests
from typing import Optional, Dict, Any

from . import PaymentProvider, PRICING


class BTCPayProvider(PaymentProvider):
    """BTCPay Server payment provider implementation.

    BTCPay is a self-hosted, open-source cryptocurrency payment processor.
    Supports Bitcoin, Lightning Network, and other cryptocurrencies.
    """

    def __init__(self, btcpay_url: str, store_id: str, api_key: str):
        """Initialize BTCPay provider.

        Args:
            btcpay_url: URL of your BTCPay Server instance
            store_id: BTCPay store ID
            api_key: BTCPay API key
        """
        self.btcpay_url = btcpay_url.rstrip('/')
        self.store_id = store_id
        self.api_key = api_key
        self.headers = {
            'Authorization': f'token {api_key}',
            'Content-Type': 'application/json'
        }

    def create_checkout_session(
        self,
        user_id: str,
        tier: str,
        success_url: str,
        cancel_url: str,
        interval: str = 'monthly'
    ) -> Optional[Dict[str, Any]]:
        """Create a BTCPay invoice.

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

        pricing = PRICING.get(tier, {})
        amount = pricing.get(interval, 9.00)

        try:
            response = requests.post(
                f"{self.btcpay_url}/api/v1/stores/{self.store_id}/invoices",
                headers=self.headers,
                json={
                    'amount': str(amount),
                    'currency': 'USD',
                    'metadata': {
                        'user_id': user_id,
                        'tier': tier,
                        'interval': interval
                    },
                    'checkout': {
                        'redirectURL': success_url,
                        'redirectAutomatically': True
                    }
                },
                timeout=10
            )

            if response.status_code == 200:
                invoice = response.json()
                return {
                    'url': invoice.get('checkoutLink'),
                    'provider': 'btcpay',
                    'invoice_id': invoice.get('id')
                }

            print(f"BTCPay error: {response.status_code} - {response.text}")
            return None

        except requests.RequestException as e:
            print(f"BTCPay request error: {e}")
            return None

    def handle_webhook(
        self,
        payload: bytes,
        signature: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """Handle BTCPay webhook.

        Args:
            payload: Raw webhook payload
            signature: BTCPay-Sig header (HMAC signature)

        Returns:
            Dict with action details if relevant
        """
        import json
        import hmac
        import hashlib

        if not signature:
            return None

        try:
            # Verify signature
            # BTCPay sends: "sha256=<hex>"
            expected_sig = signature.replace('sha256=', '')
            computed_sig = hmac.new(
                self.api_key.encode(),
                payload,
                hashlib.sha256
            ).hexdigest()

            if not hmac.compare_digest(expected_sig, computed_sig):
                print("Invalid BTCPay webhook signature")
                return None

            data = json.loads(payload.decode('utf-8'))
            event_type = data.get('type')

            if event_type == 'InvoiceProcessing':
                # Payment received, waiting for confirmations
                invoice = data.get('data', {})
                metadata = invoice.get('metadata', {})

                return {
                    'action': 'payment_pending',
                    'user_id': metadata.get('user_id'),
                    'tier': metadata.get('tier'),
                    'invoice_id': invoice.get('id'),
                    'provider': 'btcpay'
                }

            elif event_type == 'InvoiceSettled':
                # Payment confirmed
                invoice = data.get('data', {})
                metadata = invoice.get('metadata', {})

                return {
                    'action': 'subscribe',
                    'user_id': metadata.get('user_id'),
                    'tier': metadata.get('tier'),
                    'invoice_id': invoice.get('id'),
                    'provider': 'btcpay'
                }

            elif event_type == 'InvoiceExpired':
                # Payment not received in time
                return {
                    'action': 'payment_expired',
                    'invoice_id': data.get('data', {}).get('id'),
                    'provider': 'btcpay'
                }

            return None

        except Exception as e:
            print(f"BTCPay webhook error: {e}")
            return None

    def cancel_subscription(self, subscription_id: str) -> bool:
        """Cancel a BTCPay 'subscription'.

        Note: BTCPay doesn't have native subscriptions.
        This marks the invoice as invalid for tracking purposes.

        Args:
            subscription_id: BTCPay invoice ID

        Returns:
            True if cancelled successfully
        """
        try:
            # BTCPay doesn't have traditional subscriptions
            # We can only archive/mark the invoice
            response = requests.delete(
                f"{self.btcpay_url}/api/v1/stores/{self.store_id}/invoices/{subscription_id}",
                headers=self.headers,
                timeout=10
            )

            return response.status_code == 200

        except requests.RequestException:
            return False

    def get_subscription(self, subscription_id: str) -> Optional[Dict[str, Any]]:
        """Get BTCPay invoice details.

        Args:
            subscription_id: BTCPay invoice ID

        Returns:
            Dict with invoice details
        """
        try:
            response = requests.get(
                f"{self.btcpay_url}/api/v1/stores/{self.store_id}/invoices/{subscription_id}",
                headers=self.headers,
                timeout=10
            )

            if response.status_code == 200:
                invoice = response.json()
                metadata = invoice.get('metadata', {})

                return {
                    'id': invoice.get('id'),
                    'status': invoice.get('status'),
                    'amount': invoice.get('amount'),
                    'user_id': metadata.get('user_id'),
                    'tier': metadata.get('tier'),
                    'provider': 'btcpay'
                }

            return None

        except requests.RequestException:
            return None

    def get_invoice(self, invoice_id: str) -> Optional[Dict[str, Any]]:
        """Get invoice details (alias for get_subscription).

        Args:
            invoice_id: BTCPay invoice ID

        Returns:
            Dict with invoice details
        """
        return self.get_subscription(invoice_id)
