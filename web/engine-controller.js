/**
 * EngineController - Lexicon analysis engine wrapper
 */

class EngineController {
    constructor() {
        this.output = document.getElementById('engine-output');
        this.apiBase = '/api';

        // Listen to bridge events
        studioBridge.on('chat:analyze', (data) => this.analyzeText(data.text));
        studioBridge.on('chat:show-seeds', () => this.showSeeds());
    }

    async analyzeText(text) {
        try {
            const response = await fetch(`${this.apiBase}/analyze`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();
            this.displayAnalysis(data);

            // Notify other controllers
            studioBridge.emit('engine:analyzed', data);

        } catch (error) {
            this.displayError(error.message);
        }
    }

    displayAnalysis(data) {
        const score = data.sentiment_score || 0;
        let sentimentClass = 'sentiment-neutral';
        if (score > 0.1) sentimentClass = 'sentiment-positive';
        if (score < -0.1) sentimentClass = 'sentiment-negative';

        const html = `
            <div class="analysis-section">
                <h3>Text</h3>
                <p>${this.escapeHtml(data.text)}</p>
            </div>
            
            <div class="sentiment-score ${sentimentClass}">
                ${score > 0 ? '+' : ''}${score.toFixed(3)}
            </div>
            
            <div class="analysis-section">
                <h3>Keywords</h3>
                ${data.keywords.map(k => `<span class="token">${k}</span>`).join('')}
            </div>
            
            <div class="analysis-section">
                <h3>Entities</h3>
                ${data.entities.length ? data.entities.map(e =>
            `<span class="token">${e.text} (${e.label})</span>`
        ).join('') : '<p>No entities found</p>'}
            </div>
            
            <div class="analysis-section">
                <h3>Tokens (${data.tokens.length})</h3>
                ${data.tokens.slice(0, 20).map(t =>
            `<span class="token" title="${t.pos} / ${t.dep}">${t.text}</span>`
        ).join('')}
                ${data.tokens.length > 20 ? `<p>... and ${data.tokens.length - 20} more</p>` : ''}
            </div>
        `;

        this.output.innerHTML = html;
    }

    async showSeeds() {
        try {
            const response = await fetch(`${this.apiBase}/seeds`);
            const data = await response.json();

            const sortedSeeds = Object.entries(data.seeds)
                .sort((a, b) => a[1] - b[1]);

            const html = `
                <div class="analysis-section">
                    <h3>Semantic Seeds (${sortedSeeds.length})</h3>
                    <div style="display:flex; gap:8px; margin-bottom:10px;">
                        <input id="new-seed-word" placeholder="word" style="padding:6px; border-radius:4px; border:1px solid #3e3e42; background:#1e1e1e; color:#d4d4d4;" />
                        <input id="new-seed-value" placeholder="value" type="number" step="0.01" min="-1" max="1" style="padding:6px; width:120px; border-radius:4px; border:1px solid #3e3e42; background:#1e1e1e; color:#d4d4d4;" />
                        <button onclick="engineController.addSeed()">Add</button>
                        <button onclick="engineController.showConstraints()">Constraints</button>
                    </div>
                    ${sortedSeeds.map(([word, value]) =>
                `
                    <div style="display:flex; gap:8px; align-items:center; margin:4px 0;">
                        <div class="token" style="min-width:160px">${word}: ${value > 0 ? '+' : ''}${value.toFixed(2)}</div>
                        <input id="edit-${word}" type="number" step="0.01" min="-1" max="1" value="${value}" style="padding:6px; width:120px; border-radius:4px; border:1px solid #3e3e42; background:#1e1e1e; color:#d4d4d4;" />
                        <button onclick="engineController.updateSeed('${word}', document.getElementById('edit-${word}').value)">Save</button>
                        <button onclick="engineController.deleteSeed('${word}')" style="background:#a33;">Delete</button>
                    </div>
                `
            ).join('')}
                </div>
            `;

            this.output.innerHTML = html;

        } catch (error) {
            this.displayError(error.message);
        }
    }

    async addSeed() {
        const word = document.getElementById('new-seed-word').value.trim();
        const value = parseFloat(document.getElementById('new-seed-value').value);
        if (!word || isNaN(value)) return alert('Provide word and numeric value');

        try {
            const r = await fetch(`${this.apiBase}/seeds`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ word, value }) });
            if (!r.ok) throw new Error('Failed to add seed');
            this.showSeeds();
        } catch (e) {
            this.displayError(e.message);
        }
    }

    async updateSeed(word, value) {
        const parsed = parseFloat(value);
        if (isNaN(parsed)) return alert('Invalid value (must be numeric)');

        try {
            const r = await fetch(`${this.apiBase}/seeds/${word}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ word, value: parsed }) });
            if (!r.ok) throw new Error('Failed to update seed');
            this.showSeeds();
        } catch (e) {
            this.displayError(e.message);
        }
    }

    async deleteSeed(word) {
        if (!confirm(`Delete seed "${word}"?`)) return;
        try {
            const r = await fetch(`${this.apiBase}/seeds/${word}`, { method: 'DELETE' });
            if (!r.ok) throw new Error('Failed to delete');
            this.showSeeds();
        } catch (e) {
            this.displayError(e.message);
        }
    }

    async showConstraints() {
        try {
            const response = await fetch(`${this.apiBase}/constraints`);
            const data = await response.json();

            const html = `
                <div class="analysis-section">
                    <h3>Constraints (${data.constraints.length})</h3>
                    ${data.constraints.length ? data.constraints.map(c => `
                        <div style="display:flex; gap:8px; align-items:center; margin:4px 0;">
                            <div class="token">${c[0]} ${c[1]} ${c[2]}</div>
                            <button onclick="engineController.removeConstraint('${c[0]}','${c[1]}','${c[2]}')" style="background:#a33;">Delete</button>
                        </div>
                    `).join('') : '<p>No constraints yet</p>'}
                    <div style="margin-top:12px; display:flex; gap:8px; align-items:center;">
                        <input id="c-word1" placeholder="word1" style="padding:6px; border-radius:4px; border:1px solid #3e3e42; background:#1e1e1e; color:#d4d4d4;" />
                        <select id="c-op" style="padding:6px; border-radius:4px; border:1px solid #3e3e42; background:#1e1e1e; color:#d4d4d4;">
                            <option value="<"><</option>
                            <option value=">">></option>
                            <option value="=">=</option>
                        </select>
                        <input id="c-word2" placeholder="word2" style="padding:6px; border-radius:4px; border:1px solid #3e3e42; background:#1e1e1e; color:#d4d4d4;" />
                        <button onclick="engineController.addConstraint()">Add Constraint</button>
                    </div>
                </div>
            `;

            this.output.innerHTML = html;
        } catch (e) {
            this.displayError(e.message);
        }
    }

    async addConstraint() {
        const w1 = document.getElementById('c-word1').value.trim();
        const op = document.getElementById('c-op').value;
        const w2 = document.getElementById('c-word2').value.trim();
        if (!w1 || !w2) return alert('word1 and word2 required');

        try {
            const r = await fetch(`${this.apiBase}/constraints`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ word1: w1, operator: op, word2: w2 }) });
            if (!r.ok) throw new Error('Failed to add constraint');
            this.showConstraints();
        } catch (e) {
            this.displayError(e.message);
        }
    }

    async removeConstraint(w1, op, w2) {
        if (!confirm(`Delete constraint ${w1} ${op} ${w2}?`)) return;
        try {
            const r = await fetch(`${this.apiBase}/constraints`, { method: 'DELETE', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ word1: w1, operator: op, word2: w2 }) });
            if (!r.ok) throw new Error('Failed');
            this.showConstraints();
        } catch (e) {
            this.displayError(e.message);
        }
    }

    displayError(message) {
        this.output.innerHTML = `
            <div class="analysis-section">
                <h3 style="color: #f48771;">Error</h3>
                <p>${this.escapeHtml(message)}</p>
            </div>
        `;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize controller
const engineController = new EngineController();
