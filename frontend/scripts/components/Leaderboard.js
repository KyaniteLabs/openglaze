/**
 * Leaderboard - Human vs AI accuracy chart/table (standalone widget)
 */
class Leaderboard {
    constructor(container) {
        this.container = container;
        this.element = null;
        this.render();
        this.fetch();
    }

    render() {
        this.element = document.createElement('div');
        this.element.className = 'leaderboard-widget';

        this.element.innerHTML = `
            <div class="lb-header">
                <h3 class="lb-title">Prediction Accuracy</h3>
                <p class="lb-subtitle">You vs AI — who predicts better?</p>
            </div>
            <div id="lb-content">
                <div class="gam-loading">Loading leaderboard...</div>
            </div>
        `;
        this.container.appendChild(this.element);
    }

    async fetch() {
        const contentEl = this.element.querySelector('#lb-content');
        try {
            const res = await fetch('/api/predictions/leaderboard');
            if (!res.ok) {
                contentEl.innerHTML = '<div class="gam-empty">Not available</div>';
                return;
            }
            const data = await res.json();
            this.renderChart(data);
        } catch (e) {
            contentEl.innerHTML = '<div class="gam-empty">Failed to load</div>';
        }
    }

    renderChart(data) {
        const contentEl = this.element.querySelector('#lb-content');
        const user = data.user || { correct: 0, total: 0, accuracy: 0, points: 0 };
        const ai = data.ai || { correct: 0, total: 0, accuracy: 0, points: 0 };

        const maxAccuracy = Math.max(user.accuracy, ai.accuracy, 100);

        contentEl.innerHTML = `
            <div class="lb-bars">
                <div class="lb-bar-row">
                    <span class="lb-bar-label">You</span>
                    <div class="lb-bar-track">
                        <div class="lb-bar-fill lb-bar-user" style="width: ${user.accuracy}%"></div>
                    </div>
                    <span class="lb-bar-value">${user.accuracy}%</span>
                </div>
                <div class="lb-bar-row">
                    <span class="lb-bar-label">AI</span>
                    <div class="lb-bar-track">
                        <div class="lb-bar-fill lb-bar-ai" style="width: ${ai.accuracy}%"></div>
                    </div>
                    <span class="lb-bar-value">${ai.accuracy}%</span>
                </div>
            </div>
            <table class="pred-lb-table lb-table">
                <thead>
                    <tr><th></th><th>Correct</th><th>Total</th><th>Points</th></tr>
                </thead>
                <tbody>
                    <tr class="pred-lb-you">
                        <td><strong>You</strong></td><td>${user.correct}</td><td>${user.total}</td><td>${user.points}</td>
                    </tr>
                    <tr class="pred-lb-ai">
                        <td><strong>AI (Kama)</strong></td><td>${ai.correct}</td><td>${ai.total}</td><td>${ai.points}</td>
                    </tr>
                </tbody>
            </table>
        `;
    }
}
