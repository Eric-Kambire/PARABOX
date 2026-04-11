/** @odoo-module **/
/**
 * PARABOX Dashboard Direction v2 — Odoo 17 Community
 * OWL + Chart.js + RPC auto-refresh 60s
 * Architecture : composant OWL autonome enregistré comme action client
 */

import { Component, onWillStart, onMounted, onWillUnmount, useState, useRef } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

// ─── Helpers ─────────────────────────────────────────────────────────────────

/**
 * Formate un nombre : >= 1M → "1.2M", >= 1000 → "850k", sinon nombre entier.
 */
function fmtNum(val) {
    if (val === null || val === undefined || isNaN(val)) return '—';
    if (val >= 1_000_000) return (val / 1_000_000).toFixed(1) + 'M';
    if (val >= 1_000)     return (val / 1_000).toFixed(0) + 'k';
    return val.toFixed ? val.toFixed(0) : String(val);
}

/**
 * Retourne la classe d'état selon les flags alert/danger.
 */
function stateClass(alert, danger) {
    if (danger || alert === 'danger') return 'state-danger';
    if (alert === true || alert === 'warning') return 'state-warning';
    return 'state-success';
}

/**
 * Charge Chart.js depuis CDN une seule fois.
 * Retourne une Promise qui se résout quand Chart est disponible.
 */
let _chartLoadPromise = null;
function loadChartJs() {
    if (typeof Chart !== 'undefined') return Promise.resolve();
    if (_chartLoadPromise) return _chartLoadPromise;
    _chartLoadPromise = new Promise((resolve, reject) => {
        const s = document.createElement('script');
        s.src = 'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js';
        s.onload = resolve;
        s.onerror = reject;
        document.head.appendChild(s);
    });
    return _chartLoadPromise;
}

// Couleurs Chart.js
const CHART_COLORS = ['#0078d7','#10b981','#f59e0b','#ef4444','#8b5cf6','#00b4d8','#f97316'];

// ─── Composant Principal ──────────────────────────────────────────────────────

class ParaboxDashboard extends Component {
    static template = "parabox_dashboard.Dashboard";

    setup() {
        this.rpc    = useService("rpc");
        this.action = useService("action");

        // Refs pour accéder aux canvas Chart.js
        this.canvasCA      = useRef("canvasCA");
        this.canvasLitiges = useRef("canvasLitiges");
        this.canvasEncours = useRef("canvasEncours");
        this.canvasBLs     = useRef("canvasBLs");
        this.clockRef      = useRef("clock");

        this.state = useState({
            loading:     true,
            error:       null,
            kpis:        null,
            last_update: '—',
            alertes:     [],
        });

        this._refreshTimer = null;
        this._clockTimer   = null;
        this._charts       = {};
        this._isDestroyed  = false;

        onWillStart(async () => {
            await this._loadData();
        });

        onMounted(() => {
            // Force scroll dans le conteneur Odoo action
            this._forceScroll();
            this._startClock();
            this._startRefresh();
        });

        onWillUnmount(() => {
            this._isDestroyed = true;
            clearInterval(this._refreshTimer);
            clearInterval(this._clockTimer);
            Object.values(this._charts).forEach(c => { try { c.destroy(); } catch (_) {} });
        });
    }

    // ── Data loading ─────────────────────────────────────────────────────────

    async _loadData() {
        if (this._isDestroyed) return;
        try {
            const result = await this.rpc('/web/dataset/call_kw', {
                model:  'parabox.dashboard.data',
                method: 'get_kpis',
                args:   [],
                kwargs: {},
            });
            if (this._isDestroyed) return;
            this.state.kpis        = result;
            this.state.last_update = result.timestamp;
            this.state.alertes     = result.alertes || [];
            this.state.loading     = false;
            this.state.error       = null;
            // Dessine les graphiques après un rendu OWL
            setTimeout(() => this._drawAllCharts(), 80);
        } catch (e) {
            console.error('[PARABOX Dashboard] Erreur RPC:', e);
            this.state.error   = "Erreur de chargement. Vérifiez la connexion ou réactualisez.";
            this.state.loading = false;
        }
    }

    _startRefresh() {
        this._refreshTimer = setInterval(() => this._loadData(), 60_000);
    }

    // ── Horloge ──────────────────────────────────────────────────────────────

    _startClock() {
        const tick = () => {
            const el = this.clockRef.el;
            if (el) {
                el.textContent = new Date().toLocaleTimeString('fr-MA', {
                    hour: '2-digit', minute: '2-digit', second: '2-digit',
                });
            }
        };
        tick();
        this._clockTimer = setInterval(tick, 1000);
    }

    // ── Charts ───────────────────────────────────────────────────────────────

    async _drawAllCharts() {
        if (!this.state.kpis) return;
        try {
            await loadChartJs();
        } catch (_) {
            console.warn('[PARABOX] Chart.js CDN indisponible — graphiques désactivés.');
            return;
        }
        const ch = this.state.kpis.charts;
        this._drawBarCA(ch.ca_mensuel);
        this._drawDoughnutLitiges(ch.litiges_par_type);
        this._drawBarEncours(ch.top5_encours);
        this._drawDoughnutBLs(ch.statuts_bl);
    }

    _destroyChart(key) {
        if (this._charts[key]) {
            try { this._charts[key].destroy(); } catch (_) {}
            delete this._charts[key];
        }
    }

    _drawBarCA(data) {
        const canvas = this.canvasCA.el;
        if (!canvas) return;
        this._destroyChart('ca');
        this._charts.ca = new Chart(canvas, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'CA (DH)',
                    data: data.data,
                    backgroundColor: data.data.map((_, i) =>
                        i === data.data.length - 1 ? '#0078d7' : 'rgba(0,120,215,0.35)'
                    ),
                    borderColor:  '#0078d7',
                    borderWidth:  1.5,
                    borderRadius: 6,
                    borderSkipped: false,
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: ctx => ' ' + fmtNum(ctx.raw) + ' DH'
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: '#f1f5f9' },
                        ticks: {
                            font: { size: 10 },
                            callback: v => fmtNum(v),
                        }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { font: { size: 10 } }
                    }
                }
            }
        });
    }

    _drawDoughnutLitiges(data) {
        const canvas = this.canvasLitiges.el;
        if (!canvas) return;
        this._destroyChart('litiges');
        if (!data.data || data.data.length === 0) return;
        this._charts.litiges = new Chart(canvas, {
            type: 'doughnut',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.data,
                    backgroundColor: CHART_COLORS,
                    borderWidth: 2,
                    borderColor: '#fff',
                    hoverOffset: 6,
                }]
            },
            options: {
                responsive: true,
                cutout: '62%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            font: { size: 10 },
                            boxWidth: 10,
                            padding: 8,
                        }
                    }
                }
            }
        });
    }

    _drawBarEncours(data) {
        const canvas = this.canvasEncours.el;
        if (!canvas) return;
        this._destroyChart('encours');
        if (!data.data || data.data.length === 0) return;
        this._charts.encours = new Chart(canvas, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Encours (DH)',
                    data: data.data,
                    backgroundColor: 'rgba(239,68,68,0.65)',
                    borderColor: '#ef4444',
                    borderWidth: 1.5,
                    borderRadius: 4,
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: { label: ctx => ' ' + fmtNum(ctx.raw) + ' DH' }
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        grid: { color: '#f1f5f9' },
                        ticks: { font: { size: 10 }, callback: v => fmtNum(v) }
                    },
                    y: { grid: { display: false }, ticks: { font: { size: 10 } } }
                }
            }
        });
    }

    _drawDoughnutBLs(data) {
        const canvas = this.canvasBLs.el;
        if (!canvas) return;
        this._destroyChart('bls');
        if (!data.data || data.data.length === 0) return;
        const COLORS_BL = {
            'Livré':     '#10b981',
            'En attente': '#f59e0b',
            'Prêt':      '#0078d7',
            'Annulé':    '#ef4444',
        };
        this._charts.bls = new Chart(canvas, {
            type: 'doughnut',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.data,
                    backgroundColor: data.labels.map(l => COLORS_BL[l] || '#8b5cf6'),
                    borderWidth: 2,
                    borderColor: '#fff',
                    hoverOffset: 5,
                }]
            },
            options: {
                responsive: true,
                cutout: '58%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            font: { size: 10 },
                            boxWidth: 10,
                            padding: 8,
                        }
                    }
                }
            }
        });
    }

    // ── Scroll fix ───────────────────────────────────────────────────────────

    /**
     * Odoo 17 enveloppe les actions client dans un flex container avec overflow:hidden.
     * On force le scroll sur l'élément racine du composant ET sur son parent direct.
     */
    _forceScroll() {
        try {
            const root = this.__owl__.bdom?.el || document.querySelector('.o_parabox_dashboard');
            if (!root) return;
            root.style.overflowY = 'auto';
            root.style.flex      = '1 1 auto';
            root.style.minHeight = '0';
            // Remonter dans le DOM jusqu'a .o_action pour autoriser le scroll
            let parent = root.parentElement;
            let depth  = 0;
            while (parent && depth < 10) {
                const cls = parent.className || '';
                if (cls.includes('o_action') || cls.includes('o_action_manager')) {
                    parent.style.overflow = 'hidden';
                    break;
                }
                parent = parent.parentElement;
                depth++;
            }
        } catch (e) {
            console.warn('[PARABOX] _forceScroll error:', e);
        }
    }

    // ── Getters pratiques pour le template ───────────────────────────────────

    get finance()    { return this.state.kpis?.finance    || {}; }
    get logistique() { return this.state.kpis?.logistique || {}; }
    get charts()     { return this.state.kpis?.charts     || {}; }
    get hasAlertes() { return this.state.alertes.length > 0; }

    get caColor() {
        const f = this.finance;
        if (!f.ca_mois) return 'c-blue';
        return f.ca_mois.evolution >= 0 ? 'c-green' : 'c-yellow';
    }

    get otifPct()     { return Math.min(100, this.logistique.otif?.value || 0); }
    get fillRatePct() { return Math.min(100, this.logistique.fill_rate?.value || 0); }

    /** Formate un nombre. */
    fmt(val) { return fmtNum(val); }

    /** Classe de couleur carte selon alerte. */
    dotState(alert) {
        if (alert === 'danger' || alert === true) return 'c-red';
        if (alert === 'warning') return 'c-yellow';
        return 'c-green';
    }

    /** Classe du dot de statut. */
    alertDot(alert) {
        if (alert === 'danger' || alert === true) return 'danger';
        if (alert === 'warning') return 'warn';
        return 'ok';
    }

    /** Navigue vers la vue liste des BL en cours dans Odoo. */
    openBLsEnCours() {
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: 'BL en cours',
            res_model: 'stock.picking',
            view_mode: 'list,form',
            domain: [['picking_type_code','=','outgoing'],['state','in',['confirmed','assigned']]],
            views: [[false,'list'],[false,'form']],
        });
    }

    openFacturesRetard() {
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: 'Factures en retard',
            res_model: 'account.move',
            view_mode: 'list,form',
            domain: [
                ['move_type','=','out_invoice'],
                ['state','=','posted'],
                ['payment_state','not in',['paid','reversed']],
            ],
            views: [[false,'list'],[false,'form']],
        });
    }
}

// ─── Enregistrement de l'action client ────────────────────────────────────────

registry.category("actions").add("parabox_dashboard", ParaboxDashboard);
