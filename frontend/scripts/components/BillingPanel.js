/**
 * BillingPanel - Tier cards, provider selection, checkout button
 */
class BillingPanel {
    constructor(container) {
        this.container = container;
        this.element = null;
        this.providers = [];
        this.render();
        this.fetchProviders();
    }

    render() {
        this.element = document.createElement('div');
        this.element.className = 'billing-panel';

        this.element.innerHTML = `
            <div class="bill-header">
                <h3 class="bill-title">Plans & Billing</h3>
                <p class="bill-subtitle">Choose the plan that fits your studio</p>
            </div>
            <div class="bill-tiers" id="bill-tiers">
                <div class="bill-tier bill-tier-free">
                    <div class="bill-tier-name">Free</div>
                    <div class="bill-tier-price">$0<span>/mo</span></div>
                    <ul class="bill-tier-features">
                        <li>Up to 20 combinations</li>
                        <li>Basic compatibility checks</li>
                        <li>Community templates</li>
                    </ul>
                    <div class="bill-tier-current">Current Plan</div>
                </div>
                <div class="bill-tier bill-tier-pro bill-tier-featured">
                    <div class="bill-tier-badge">Popular</div>
                    <div class="bill-tier-name">Pro</div>
                    <div class="bill-tier-price">$12<span>/mo</span></div>
                    <ul class="bill-tier-features">
                        <li>Unlimited combinations</li>
                        <li>Full AI predictions</li>
                        <li>Advanced chemistry tools</li>
                        <li>Studio collaboration</li>
                    </ul>
                    <button class="btn btn-primary bill-upgrade-btn" onclick="this.closest('.billing-panel').__billing.startCheckout('pro')">
                        Upgrade to Pro
                    </button>
                </div>
                <div class="bill-tier bill-tier-studio">
                    <div class="bill-tier-name">Studio</div>
                    <div class="bill-tier-price">$39<span>/mo</span></div>
                    <ul class="bill-tier-features">
                        <li>Everything in Pro</li>
                        <li>Team management</li>
                        <li>Priority AI access</li>
                        <li>API access</li>
                    </ul>
                    <button class="btn btn-secondary bill-upgrade-btn" onclick="this.closest('.billing-panel').__billing.startCheckout('studio')">
                        Upgrade to Studio
                    </button>
                </div>
            </div>
            <div class="bill-providers" id="bill-providers" style="display:none;">
                <h4 class="gam-section-title">Payment Methods</h4>
                <div id="bill-provider-list"></div>
            </div>
        `;
        this.element.__billing = this;
        this.container.appendChild(this.element);
    }

    async fetchProviders() {
        try {
            const res = await fetch('/api/billing/providers');
            if (!res.ok) return;
            this.providers = await res.json();
            if (this.providers.length) {
                const section = this.element.querySelector('#bill-providers');
                section.style.display = 'block';
                const list = this.element.querySelector('#bill-provider-list');
                list.innerHTML = this.providers.map(p =>
                    `<span class="bill-provider-tag">${p}</span>`
                ).join('');
            }
        } catch (e) {
            console.error('Billing providers error:', e);
        }
    }

    async startCheckout(tier) {
        const provider = this.providers[0] || 'manual';
        try {
            const res = await fetch('/api/billing/checkout', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ provider, tier })
            });
            const data = await res.json();
            if (res.ok && data.url) {
                window.open(data.url, '_blank');
            } else if (res.ok) {
                alert(`Checkout initiated via ${provider}. You'll receive further instructions.`);
            } else {
                alert(data.error || 'Checkout failed');
            }
        } catch (e) {
            alert('Network error — please try again');
        }
    }
}
