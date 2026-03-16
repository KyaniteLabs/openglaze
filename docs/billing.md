# Billing Setup

Configure payment providers for OpenGlaze.

## Overview

OpenGlaze supports multiple payment providers:

| Provider | Type | Self-Hostable | Best For |
|----------|------|---------------|----------|
| Stripe | Credit Card | No | General use |
| PayPal | PayPal | No | International |
| BTCPay | Cryptocurrency | Yes | Privacy-focused |
| Manual | Invoice/PO | N/A | Education, Enterprise |

## Stripe Setup

### 1. Create Stripe Account

1. Sign up at [stripe.com](https://stripe.com)
2. Complete account verification
3. Get API keys from Dashboard > Developers > API keys

### 2. Create Products

In Stripe Dashboard:

1. Go to Products
2. Create three products:
   - **Pro** ($9/month, $90/year)
   - **Studio** ($29/month, $290/year)
   - **Education** ($199/year)

3. Copy the Price IDs (format: `price_xxxxx`)

### 3. Configure Webhooks

1. Add endpoint: `https://your-domain.com/api/billing/webhook/stripe`
2. Select events: checkout.session.completed, subscription events
3. Copy the Webhook signing secret

### 4. Environment Variables

```bash
STRIPE_API_KEY=sk_live_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx
STRIPE_PRICE_PRO_MONTHLY=price_xxxxx
STRIPE_PRICE_STUDIO_MONTHLY=price_xxxxx
STRIPE_PRICE_EDUCATION_YEARLY=price_xxxxx
```

## Manual Billing

For educational institutions and enterprises.

```bash
# Approve via API (admin only)
curl -X POST http://localhost:8768/api/admin/approve \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -d '{"approval_token": "xxx"}'
```

## Testing Webhooks

```bash
stripe listen --forward-to localhost:8768/api/billing/webhook/stripe
```

## Next Steps

- [Configuration Guide](configuration.md)
