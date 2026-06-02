/* ==========================================================================
   Obsidian Glassmorphic BI Executive Dashboard - JavaScript Logic
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    const app = new DashboardApp();
    app.init();
});

class DashboardApp {
    constructor() {
        this.rawData = [];
        this.filteredData = [];
        
        // Active Filter States
        this.filters = {
            region: 'ALL',
            segment: 'ALL',
            category: 'ALL'
        };
        
        // Chart.js Instances
        this.charts = {};
        
        // Animated Counter Tracker
        this.counterIntervals = [];
    }

    /**
     * Entry Point Initialization
     */
    async init() {
        this.initTheme();
        this.startLiveClock();
        this.initCharts();
        await this.loadData();
        this.registerFilterListeners();
        this.registerCollapsibleListeners();
        this.registerActionListeners();
    }

    /**
     * Set up default or cached theme on load
     */
    initTheme() {
        const cachedTheme = localStorage.getItem('retail-bi-theme') || 'dark';
        document.documentElement.setAttribute('data-theme', cachedTheme);
        setTimeout(() => {
            this.updateChartTheme(cachedTheme);
        }, 100);
    }

    /**
     * Start live UTC/Local executive clock in header
     */
    startLiveClock() {
        const timeEl = document.getElementById('currentTime');
        const updateClock = () => {
            const now = new Date();
            const formatStr = now.toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
                year: 'numeric'
            }) + ' | ' + now.toLocaleTimeString('en-US', {
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit',
                hour12: true
            });
            if (timeEl) timeEl.textContent = formatStr;
        };
        updateClock();
        setInterval(updateClock, 1000);
    }

    /**
     * Record dynamic refreshed indicator time
     */
    setRefreshedIndicator() {
        const now = new Date();
        const formatStr = now.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: false
        });
        const refreshEl = document.getElementById('lastRefreshedTime');
        if (refreshEl) refreshEl.textContent = formatStr;
    }

    /**
     * Fetch JSON dataset and transition dashboard state
     */
    async loadData() {
        try {
            console.log("Loading dashboard dataset from data.js...");
            if (typeof superstoreData === 'undefined') {
                throw new Error("superstoreData is not defined. Ensure data.js is loaded correctly.");
            }
            this.rawData = superstoreData;
            console.log(`Loaded ${this.rawData.length} retail lines successfully.`);
            
            // Populate filter buttons with counts of the raw data
            this.updateFilterButtonsCounts();
            
            // Initial render
            this.renderDashboard();
            this.setRefreshedIndicator();
            
            // Hide Loader
            const loader = document.getElementById('loaderOverlay');
            if (loader) {
                loader.style.opacity = '0';
                setTimeout(() => loader.remove(), 500);
            }
        } catch (error) {
            console.error("Critical Error loading dashboard dataset:", error);
            const loaderText = document.querySelector('.loader-text');
            if (loaderText) {
                loaderText.innerHTML = `<span style="color: #f43f5e;">CRITICAL ERROR: Failed to load data. Ensure data.js has been compiled by data_pipeline.py first.</span>`;
            }
        }
    }

    /**
     * Populate filter counts dynamically based on loaded data
     */
    updateFilterButtonsCounts() {
        const counts = {
            region: { 'West': 0, 'East': 0, 'Central': 0, 'South': 0 },
            segment: { 'Consumer': 0, 'Corporate': 0, 'Home Office': 0 },
            category: { 'Furniture': 0, 'Office Supplies': 0, 'Technology': 0 }
        };
        
        // Count totals
        this.rawData.forEach(row => {
            if (counts.region[row.reg] !== undefined) counts.region[row.reg]++;
            if (counts.segment[row.seg] !== undefined) counts.segment[row.seg]++;
            if (counts.category[row.cat] !== undefined) counts.category[row.cat]++;
        });
        
        // Write counts into the DOM elements
        for (const [group, groupCounts] of Object.entries(counts)) {
            for (const [name, val] of Object.entries(groupCounts)) {
                const countBadge = document.querySelector(`[data-filter-group="${group}"][data-filter-val="${name}"] .filter-count`);
                if (countBadge) {
                    countBadge.textContent = val.toLocaleString();
                }
            }
        }
    }

    /**
     * Add click listeners to side filters
     */
    registerFilterListeners() {
        const filterBtns = document.querySelectorAll('.filter-btn');
        filterBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const button = e.currentTarget;
                const group = button.getAttribute('data-filter-group');
                const val = button.getAttribute('data-filter-val');
                
                // Toggle active state in group
                const groupBtns = document.querySelectorAll(`[data-filter-group="${group}"]`);
                
                if (this.filters[group] === val) {
                    // Clicking already active filter resets it to ALL
                    this.filters[group] = 'ALL';
                    button.classList.remove('active');
                } else {
                    this.filters[group] = val;
                    groupBtns.forEach(b => b.classList.remove('active'));
                    button.classList.add('active');
                }
                
                console.log("Filters Updated:", this.filters);
                this.renderDashboard();
            });
        });
        
        // Reset button
        const resetBtn = document.getElementById('resetFilters');
        if (resetBtn) {
            resetBtn.addEventListener('click', () => {
                this.filters.region = 'ALL';
                this.filters.segment = 'ALL';
                this.filters.category = 'ALL';
                
                filterBtns.forEach(b => b.classList.remove('active'));
                console.log("Filters Reset to default.");
                this.renderDashboard();
            });
        }

        // Empty state reset button
        const emptyResetBtn = document.getElementById('emptyStateResetBtn');
        if (emptyResetBtn) {
            emptyResetBtn.addEventListener('click', () => {
                this.filters.region = 'ALL';
                this.filters.segment = 'ALL';
                this.filters.category = 'ALL';
                
                filterBtns.forEach(b => b.classList.remove('active'));
                console.log("Empty state filters reset.");
                this.renderDashboard();
            });
        }
    }

    /**
     * Handle collapsible section clicks
     */
    registerCollapsibleListeners() {
        const collapsibleHeaders = document.querySelectorAll('.filter-group-header');
        collapsibleHeaders.forEach(header => {
            header.addEventListener('click', (e) => {
                const section = e.currentTarget.closest('.collapsible-section');
                if (section) {
                    const isActive = section.classList.contains('active');
                    section.classList.toggle('active');
                    e.currentTarget.setAttribute('aria-expanded', !isActive);
                }
            });
        });
    }

    /**
     * Hook up export features and theme selector
     */
    registerActionListeners() {
        // Theme Toggling
        const themeBtn = document.getElementById('themeToggleBtn');
        if (themeBtn) {
            themeBtn.addEventListener('click', () => {
                const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
                const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
                document.documentElement.setAttribute('data-theme', newTheme);
                localStorage.setItem('retail-bi-theme', newTheme);
                this.updateChartTheme(newTheme);
            });
        }

        // Action Exports
        const btnCSV = document.getElementById('btnExportCSV');
        if (btnCSV) {
            btnCSV.addEventListener('click', () => this.exportToCSV());
        }

        const btnReport = document.getElementById('btnExportReport');
        if (btnReport) {
            btnReport.addEventListener('click', () => this.exportReport());
        }

        const btnPrint = document.getElementById('btnPrintDashboard');
        if (btnPrint) {
            btnPrint.addEventListener('click', () => window.print());
        }
    }

    /**
     * Update Chart default colors and reload based on light/dark mode
     */
    updateChartTheme(theme) {
        const textColor = theme === 'dark' ? '#94a3b8' : '#475569';
        const gridColor = theme === 'dark' ? 'rgba(255, 255, 255, 0.04)' : 'rgba(15, 23, 42, 0.05)';
        
        Chart.defaults.color = textColor;
        
        Object.values(this.charts).forEach(chart => {
            if (!chart || !chart.options) return;
            
            if (chart.options.scales) {
                if (chart.options.scales.x) {
                    chart.options.scales.x.grid.color = gridColor;
                    chart.options.scales.x.ticks.color = textColor;
                }
                if (chart.options.scales.y) {
                    chart.options.scales.y.grid.color = gridColor;
                    chart.options.scales.y.ticks.color = textColor;
                }
            }
            if (chart.options.plugins && chart.options.plugins.legend) {
                chart.options.plugins.legend.labels.color = theme === 'dark' ? '#f8fafc' : '#0f172a';
            }
            chart.update();
        });
    }

    /**
     * Filter data, calculate aggregates, update KPIs, update Charts
     */
    renderDashboard() {
        // 1. Apply active filter rules
        this.filteredData = this.rawData.filter(row => {
            const matchesRegion = this.filters.region === 'ALL' || row.reg === this.filters.region;
            const matchesSegment = this.filters.segment === 'ALL' || row.seg === this.filters.segment;
            const matchesCategory = this.filters.category === 'ALL' || row.cat === this.filters.category;
            return matchesRegion && matchesSegment && matchesCategory;
        });
        
        console.log(`Filtered Data size: ${this.filteredData.length} records.`);
        
        // Check for empty state
        const emptyState = document.getElementById('emptyState');
        const workspaceContent = document.getElementById('workspaceMainContent');
        
        if (this.filteredData.length === 0) {
            if (emptyState) emptyState.style.display = 'flex';
            if (workspaceContent) workspaceContent.style.display = 'none';
            return; // Skip rendering elements to prevent Chart.js exceptions
        } else {
            if (emptyState) emptyState.style.display = 'none';
            if (workspaceContent) workspaceContent.style.display = 'block';
        }
        
        // 2. Calculate KPI numbers
        let totalSales = 0;
        let totalProfit = 0;
        const uniqueOrders = new Set();
        const uniqueCustomers = new Set();
        
        this.filteredData.forEach(row => {
            totalSales += row.sales;
            totalProfit += row.profit;
            uniqueOrders.add(row.ord);
            uniqueCustomers.add(row.cust);
        });
        
        const totalOrders = uniqueOrders.size;
        const totalCustomers = uniqueCustomers.size;
        const profitMargin = totalSales > 0 ? (totalProfit / totalSales) * 100 : 0;
        
        // Adjust Profit Trend UI indicator
        const kpiProfitTrend = document.getElementById('kpiProfitTrend');
        if (kpiProfitTrend) {
            if (totalProfit >= 0) {
                kpiProfitTrend.className = 'kpi-trend trend-up';
                kpiProfitTrend.innerHTML = `<span class="trend-badge">▲ Healthy</span> <span style="color: var(--text-muted);">positive yield</span>`;
            } else {
                kpiProfitTrend.className = 'kpi-trend trend-down';
                kpiProfitTrend.innerHTML = `<span class="trend-badge" style="background: rgba(244,63,94,0.1); color: var(--color-loss);">▼ Squeezed</span> <span style="color: var(--text-muted);">active losses</span>`;
            }
        }

        // Adjust Margin Trend UI indicator
        const kpiMarginTrend = document.getElementById('kpiMarginTrend');
        if (kpiMarginTrend) {
            if (profitMargin >= 10) {
                kpiMarginTrend.className = 'kpi-trend trend-up';
                kpiMarginTrend.innerHTML = `<span class="trend-badge">▲ Strong</span> <span style="color: var(--text-muted);">industry standard</span>`;
            } else if (profitMargin >= 0) {
                kpiMarginTrend.className = 'kpi-trend trend-neutral';
                kpiMarginTrend.innerHTML = `<span class="trend-badge" style="background: rgba(245,158,11,0.1); color: var(--color-customers);">■ Moderate</span> <span style="color: var(--text-muted);">low pricing margin</span>`;
            } else {
                kpiMarginTrend.className = 'kpi-trend trend-down';
                kpiMarginTrend.innerHTML = `<span class="trend-badge" style="background: rgba(244,63,94,0.1); color: var(--color-loss);">▼ Squeezed</span> <span style="color: var(--text-muted);">unprofitable</span>`;
            }
        }
        
        // 3. Trigger animated counter updates for KPIs
        this.updateKpiCounters(totalSales, totalProfit, totalOrders, profitMargin, totalCustomers);
        
        // 4. Update and animate the 7 Chart.js graphs
        this.updateChartsData();
        
        // 5. Update SKU lists and dynamic narrative insights
        this.updateDynamicSKUs();
        this.updateExecutiveInsights(totalSales, totalProfit, profitMargin, totalOrders);
        this.updateMicroInsights(totalSales, totalProfit, profitMargin);
        this.updateBusinessCommentary(totalSales, totalProfit, profitMargin);
    }

    /**
     * Trigger animation of counts on the 5 KPI cards
     */
    updateKpiCounters(sales, profit, orders, margin, customers) {
        // Clear active animations
        this.counterIntervals.forEach(ci => clearInterval(ci));
        this.counterIntervals = [];
        
        this.animateCounter('kpiSales', sales, true);
        this.animateCounter('kpiProfit', profit, true);
        this.animateCounter('kpiOrders', orders, false);
        this.animateCounter('kpiMargin', margin, false, '%');
        this.animateCounter('kpiCustomers', customers, false);
    }

    /**
     * Count Incrementor using requestAnimationFrame style interval
     */
    animateCounter(elementId, targetValue, isCurrency = false, suffix = '') {
        const el = document.getElementById(elementId);
        if (!el) return;
        
        let start = 0;
        const duration = 800; // 0.8s animation
        const stepTime = 16;   // ~60 FPS
        const steps = duration / stepTime;
        const increment = targetValue / steps;
        
        const timer = setInterval(() => {
            start += increment;
            if ((increment >= 0 && start >= targetValue) || (increment < 0 && start <= targetValue)) {
                clearInterval(timer);
                start = targetValue;
            }
            
            // Format number
            let formatted = '';
            if (isCurrency) {
                formatted = (start >= 0 ? '' : '-') + '$' + Math.round(Math.abs(start)).toLocaleString();
            } else {
                if (suffix === '%') {
                    formatted = start.toFixed(2) + '%';
                } else {
                    formatted = Math.round(start).toLocaleString();
                }
            }
            el.textContent = formatted;
        }, stepTime);
        
        this.counterIntervals.push(timer);
    }

    /**
     * Initialize empty Chart.js instances with responsive styling
     */
    initCharts() {
        Chart.defaults.color = '#94a3b8';
        Chart.defaults.font.family = "'Outfit', sans-serif";
        Chart.defaults.font.size = 11;
        
        const gridConfig = {
            color: 'rgba(255, 255, 255, 0.04)',
            drawTicks: false
        };
        
        // Helper to generate empty options
        const getCommonOptions = (title, displayLegend = false) => ({
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 1200,
                easing: 'easeOutQuart'
            },
            plugins: {
                legend: {
                    display: displayLegend,
                    position: 'bottom',
                    labels: { boxWidth: 12, padding: 15, color: '#f8fafc' }
                },
                tooltip: {
                    backgroundColor: '#0d1222',
                    titleColor: '#f8fafc',
                    bodyColor: '#e2e8f0',
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderWidth: 1,
                    padding: 10,
                    cornerRadius: 8,
                    usePointStyle: true
                }
            },
            scales: {
                x: { grid: gridConfig, ticks: { color: '#94a3b8' } },
                y: { grid: gridConfig, ticks: { color: '#94a3b8' } }
            }
        });

        // 1. Monthly Sales Trend (Line Chart)
        this.charts.monthlyTrend = new Chart(document.getElementById('chartMonthlyTrend'), {
            type: 'line',
            data: { labels: [], datasets: [] },
            options: {
                ...getCommonOptions('Monthly Trend', true),
                interaction: { mode: 'index', intersect: false }
            }
        });

        // 2. Region-wise Sales (Bar Chart)
        this.charts.regionSales = new Chart(document.getElementById('chartRegionSales'), {
            type: 'bar',
            data: { labels: [], datasets: [] },
            options: {
                ...getCommonOptions('Region Sales', false),
                scales: {
                    x: { grid: gridConfig },
                    y: { grid: gridConfig, ticks: { callback: val => '$' + val.toLocaleString() } }
                }
            }
        });

        // 3. Profit by Category (Pie Chart)
        this.charts.categoryProfit = new Chart(document.getElementById('chartCategoryProfit'), {
            type: 'pie',
            data: { labels: [], datasets: [] },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    duration: 1200,
                    easing: 'easeOutQuart'
                },
                plugins: {
                    legend: { display: true, position: 'bottom', labels: { boxWidth: 12, color: '#f8fafc' } },
                    tooltip: {
                        backgroundColor: '#0d1222',
                        borderColor: 'rgba(255, 255, 255, 0.1)',
                        borderWidth: 1,
                        callbacks: {
                            label: context => ` Profit: $${Math.round(context.raw).toLocaleString()}`
                        }
                    }
                }
            }
        });

        // 4. Sales by Segment (Donut Chart)
        this.charts.segmentSales = new Chart(document.getElementById('chartSegmentSales'), {
            type: 'doughnut',
            data: { labels: [], datasets: [] },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '70%',
                animation: {
                    duration: 1200,
                    easing: 'easeOutQuart'
                },
                plugins: {
                    legend: { display: true, position: 'bottom', labels: { boxWidth: 12, color: '#f8fafc' } },
                    tooltip: {
                        backgroundColor: '#0d1222',
                        borderColor: 'rgba(255, 255, 255, 0.1)',
                        borderWidth: 1,
                        callbacks: {
                            label: context => ` Sales: $${Math.round(context.raw).toLocaleString()}`
                        }
                    }
                }
            }
        });

        // 5. Top Products Analysis (Horizontal Bar Chart)
        this.charts.topProducts = new Chart(document.getElementById('chartTopProducts'), {
            type: 'bar',
            data: { labels: [], datasets: [] },
            options: {
                indexAxis: 'y',
                ...getCommonOptions('Top Products', false),
                scales: {
                    x: { grid: gridConfig, ticks: { callback: val => '$' + val.toLocaleString() } },
                    y: { grid: { display: false } }
                }
            }
        });

        // 6. Profit vs Discount (Scatter Chart)
        this.charts.profitDiscount = new Chart(document.getElementById('chartProfitDiscount'), {
            type: 'scatter',
            data: { datasets: [] },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    duration: 1200,
                    easing: 'easeOutQuart'
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: '#0d1222',
                        borderColor: 'rgba(255, 255, 255, 0.1)',
                        borderWidth: 1,
                        callbacks: {
                            label: context => `Discount: ${Math.round(context.raw.x * 100)}% | Profit: $${Math.round(context.raw.y).toLocaleString()} | SKU: ${context.raw.label}`
                        }
                    }
                },
                scales: {
                    x: { 
                        title: { display: true, text: 'Discount Level (%)', color: '#94a3b8' },
                        grid: gridConfig,
                        ticks: { callback: val => (val * 100) + '%' }
                    },
                    y: { 
                        title: { display: true, text: 'Net Profit ($)', color: '#94a3b8' },
                        grid: gridConfig 
                    }
                }
            }
        });

        // 7. Regional Profitability (Stacked Bar Chart)
        this.charts.regionalCategoryProfit = new Chart(document.getElementById('chartRegionalCategoryProfit'), {
            type: 'bar',
            data: { labels: [], datasets: [] },
            options: {
                ...getCommonOptions('Regional Product Mix', true),
                scales: {
                    x: { stacked: true, grid: gridConfig },
                    y: { stacked: true, grid: gridConfig, ticks: { callback: val => '$' + val.toLocaleString() } }
                }
            }
        });
    }

    /**
     * Compute aggregations and refresh Chart.js visuals
     */
    updateChartsData() {
        const data = this.filteredData;
        
        // --------------------------------------------------
        // CHART 1: Monthly Sales Trend (Line Chart)
        // --------------------------------------------------
        const monthlyAgg = {};
        data.forEach(row => {
            const m = row.date.substring(0, 7); // YYYY-MM
            if (!monthlyAgg[m]) monthlyAgg[m] = { sales: 0, profit: 0 };
            monthlyAgg[m].sales += row.sales;
            monthlyAgg[m].profit += row.profit;
        });
        
        const sortedMonths = Object.keys(monthlyAgg).sort();
        const salesTrendData = sortedMonths.map(m => monthlyAgg[m].sales);
        const profitTrendData = sortedMonths.map(m => monthlyAgg[m].profit);
        
        // Create canvas gradients
        const ctxMonthly = document.getElementById('chartMonthlyTrend').getContext('2d');
        const salesGrad = ctxMonthly.createLinearGradient(0, 0, 0, 300);
        salesGrad.addColorStop(0, 'rgba(14, 165, 233, 0.35)');
        salesGrad.addColorStop(1, 'rgba(14, 165, 233, 0.00)');
        
        this.charts.monthlyTrend.data = {
            labels: sortedMonths.map(m => {
                const [y, mm] = m.split('-');
                const dateObj = new Date(parseInt(y), parseInt(mm) - 1, 1);
                return dateObj.toLocaleDateString('en-US', { month: 'short', year: '2-digit' });
            }),
            datasets: [
                {
                    label: 'Gross Sales',
                    data: salesTrendData.map(v => Math.round(v)),
                    borderColor: '#0ea5e9',
                    backgroundColor: salesGrad,
                    fill: true,
                    tension: 0.35,
                    borderWidth: 2,
                    pointBackgroundColor: '#0ea5e9',
                    pointHoverRadius: 6
                },
                {
                    label: 'Net Profit',
                    data: profitTrendData.map(v => Math.round(v)),
                    borderColor: '#10b981',
                    borderDash: [5, 5],
                    fill: false,
                    tension: 0.3,
                    borderWidth: 2,
                    pointBackgroundColor: '#10b981',
                    pointHoverRadius: 6
                }
            ]
        };
        this.charts.monthlyTrend.update();

        // --------------------------------------------------
        // CHART 2: Region-wise Sales (Bar Chart)
        // --------------------------------------------------
        const regionAgg = { 'West': 0, 'East': 0, 'Central': 0, 'South': 0 };
        data.forEach(row => {
            if (regionAgg[row.reg] !== undefined) regionAgg[row.reg] += row.sales;
        });
        
        const ctxRegion = document.getElementById('chartRegionSales').getContext('2d');
        const barGrad = ctxRegion.createLinearGradient(0, 0, 0, 300);
        barGrad.addColorStop(0, '#6366f1');
        barGrad.addColorStop(1, '#0ea5e9');
        
        this.charts.regionSales.data = {
            labels: Object.keys(regionAgg),
            datasets: [{
                label: 'Gross Sales',
                data: Object.values(regionAgg).map(v => Math.round(v)),
                backgroundColor: barGrad,
                borderRadius: 8,
                maxBarThickness: 45
            }]
        };
        this.charts.regionSales.update();

        // --------------------------------------------------
        // CHART 3: Profit by Category (Pie Chart)
        // --------------------------------------------------
        const catProfitAgg = { 'Furniture': 0, 'Office Supplies': 0, 'Technology': 0 };
        data.forEach(row => {
            if (catProfitAgg[row.cat] !== undefined) catProfitAgg[row.cat] += row.profit;
        });
        
        const pieColors = [
            '#a855f7', // Furniture (Purple)
            '#6366f1', // Office Supplies (Indigo)
            '#10b981'  // Technology (Emerald)
        ];
        
        this.charts.categoryProfit.data = {
            labels: Object.keys(catProfitAgg),
            datasets: [{
                data: Object.values(catProfitAgg).map(v => Math.round(v)),
                backgroundColor: pieColors,
                borderColor: '#0d1222',
                borderWidth: 2
            }]
        };
        this.charts.categoryProfit.update();

        // --------------------------------------------------
        // CHART 4: Sales by Segment (Donut Chart)
        // --------------------------------------------------
        const segSalesAgg = { 'Consumer': 0, 'Corporate': 0, 'Home Office': 0 };
        data.forEach(row => {
            if (segSalesAgg[row.seg] !== undefined) segSalesAgg[row.seg] += row.sales;
        });
        
        const donutColors = [
            '#0ea5e9', // Consumer (Cyan)
            '#f59e0b', // Corporate (Amber)
            '#ec4899'  // Home Office (Pink)
        ];
        
        this.charts.segmentSales.data = {
            labels: Object.keys(segSalesAgg),
            datasets: [{
                data: Object.values(segSalesAgg).map(v => Math.round(v)),
                backgroundColor: donutColors,
                borderColor: '#0d1222',
                borderWidth: 2
            }]
        };
        this.charts.segmentSales.update();

        // --------------------------------------------------
        // CHART 5: Top Products Analysis (Horizontal Bar)
        // --------------------------------------------------
        const prodAgg = {};
        data.forEach(row => {
            if (!prodAgg[row.prod]) prodAgg[row.prod] = 0;
            prodAgg[row.prod] += row.sales;
        });
        
        const sortedProducts = Object.entries(prodAgg)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 7); // Top 7 products
            
        this.charts.topProducts.data = {
            labels: sortedProducts.map(p => p[0].split(' SKU-')[0]),
            datasets: [{
                label: 'Gross Sales',
                data: sortedProducts.map(p => Math.round(p[1])),
                backgroundColor: 'rgba(14, 165, 233, 0.75)',
                borderColor: '#0ea5e9',
                borderWidth: 1,
                borderRadius: 4,
                maxBarThickness: 25
            }]
        };
        this.charts.topProducts.update();

        // --------------------------------------------------
        // CHART 6: Profit vs Discount (Scatter Chart)
        // --------------------------------------------------
        let scatterSample = [...data];
        if (scatterSample.length > 300) {
            // Fisher-Yates Shuffle and slice to prevent DOM lag
            for (let i = scatterSample.length - 1; i > 0; i--) {
                const j = Math.floor(Math.random() * (i + 1));
                [scatterSample[i], scatterSample[j]] = [scatterSample[j], scatterSample[i]];
            }
            scatterSample = scatterSample.slice(0, 300);
        }
        
        const scatterData = scatterSample.map(row => {
            let pColor = '#10b981'; // Green for profit
            if (row.profit < 0) pColor = '#f43f5e'; // Red for losses
            
            return {
                x: row.disc,
                y: row.profit,
                label: row.prod.split(' SKU-')[0] + ` (Qty: ${row.qty})`,
                color: pColor
            };
        });
        
        this.charts.profitDiscount.data = {
            datasets: [{
                data: scatterData,
                backgroundColor: scatterData.map(d => d.color),
                pointRadius: 5,
                pointHoverRadius: 8
            }]
        };
        this.charts.profitDiscount.update();

        // --------------------------------------------------
        // CHART 7: Regional Profitability (Stacked Bar)
        // --------------------------------------------------
        const regionalCatMix = {
            'West': { Furniture: 0, 'Office Supplies': 0, Technology: 0 },
            'East': { Furniture: 0, 'Office Supplies': 0, Technology: 0 },
            'Central': { Furniture: 0, 'Office Supplies': 0, Technology: 0 },
            'South': { Furniture: 0, 'Office Supplies': 0, Technology: 0 }
        };
        
        data.forEach(row => {
            if (regionalCatMix[row.reg] && regionalCatMix[row.reg][row.cat] !== undefined) {
                regionalCatMix[row.reg][row.cat] += row.profit;
            }
        });
        
        const regionsList = ['West', 'East', 'Central', 'South'];
        
        this.charts.regionalCategoryProfit.data = {
            labels: regionsList,
            datasets: [
                {
                    label: 'Furniture Profit',
                    data: regionsList.map(r => Math.round(regionalCatMix[r]['Furniture'])),
                    backgroundColor: '#a855f7',
                    borderRadius: 4
                },
                {
                    label: 'Office Supplies Profit',
                    data: regionsList.map(r => Math.round(regionalCatMix[r]['Office Supplies'])),
                    backgroundColor: '#6366f1',
                    borderRadius: 4
                },
                {
                    label: 'Technology Profit',
                    data: regionsList.map(r => Math.round(regionalCatMix[r]['Technology'])),
                    backgroundColor: '#10b981',
                    borderRadius: 4
                }
            ]
        };
        this.charts.regionalCategoryProfit.update();
    }

    /**
     * Update SKU List in right sidebar / details pane
     */
    updateDynamicSKUs() {
        const container = document.getElementById('skuListContainer');
        if (!container) return;
        
        // Group by product name
        const skus = {};
        this.filteredData.forEach(row => {
            if (!skus[row.prod]) {
                skus[row.prod] = { name: row.prod, cat: row.cat, sales: 0, profit: 0 };
            }
            skus[row.prod].sales += row.sales;
            skus[row.prod].profit += row.profit;
        });
        
        // Sort and select top 4 profitable SKUs
        const topSKUs = Object.values(skus)
            .sort((a, b) => b.profit - a.profit)
            .slice(0, 4);
            
        container.innerHTML = '';
        
        if (topSKUs.length === 0) {
            container.innerHTML = `<div class="sku-row"><span class="sku-name">No products in filter</span></div>`;
            return;
        }
        
        topSKUs.forEach(sku => {
            const shortName = sku.name.split(' (')[0];
            const profitFormatted = (sku.profit >= 0 ? '+' : '') + '$' + Math.round(sku.profit).toLocaleString();
            const profitClass = sku.profit >= 0 ? '' : 'negative';
            
            const html = `
                <div class="sku-row">
                    <div class="sku-info">
                        <span class="sku-name" title="${sku.name}">${shortName}</span>
                        <span class="sku-category">${sku.cat}</span>
                    </div>
                    <div class="sku-metrics">
                        <span class="sku-profit ${profitClass}">${profitFormatted}</span>
                        <span class="sku-sales">Sales: $${Math.round(sku.sales).toLocaleString()}</span>
                    </div>
                </div>
            `;
            container.insertAdjacentHTML('beforeend', html);
        });
    }

    /**
     * Calculate and display the 5 dedicated premium executive insights cards in real-time
     */
    updateMicroInsights(sales, profit, margin) {
        const data = this.filteredData;
        if (data.length === 0) return;

        // 1. Highest Profit Region
        const regMetrics = {};
        data.forEach(row => {
            if (!regMetrics[row.reg]) regMetrics[row.reg] = { profit: 0, sales: 0 };
            regMetrics[row.reg].profit += row.profit;
            regMetrics[row.reg].sales += row.sales;
        });
        
        let bestRegion = 'West';
        let maxRegionProfit = -Infinity;
        let bestRegionSales = 0;
        
        Object.entries(regMetrics).forEach(([r, m]) => {
            if (m.profit > maxRegionProfit) {
                maxRegionProfit = m.profit;
                bestRegion = r;
                bestRegionSales = m.sales;
            }
        });
        
        const bestRegionMargin = bestRegionSales > 0 ? (maxRegionProfit / bestRegionSales) * 100 : 0;
        const regionValEl = document.getElementById('insightBestRegionVal');
        const regionDescEl = document.getElementById('insightBestRegionDesc');
        if (regionValEl) regionValEl.textContent = `${bestRegion} Region`;
        if (regionDescEl) regionDescEl.textContent = `$${Math.round(maxRegionProfit).toLocaleString()} profit (${bestRegionMargin.toFixed(1)}% margin)`;

        // 2. Top Profit Category
        const catMetrics = {};
        data.forEach(row => {
            if (!catMetrics[row.cat]) catMetrics[row.cat] = { profit: 0, sales: 0 };
            catMetrics[row.cat].profit += row.profit;
            catMetrics[row.cat].sales += row.sales;
        });
        
        let bestCategory = 'Technology';
        let maxCategoryProfit = -Infinity;
        let bestCategorySales = 0;
        
        Object.entries(catMetrics).forEach(([c, m]) => {
            if (m.profit > maxCategoryProfit) {
                maxCategoryProfit = m.profit;
                bestCategory = c;
                bestCategorySales = m.sales;
            }
        });
        
        const bestCategoryMargin = bestCategorySales > 0 ? (maxCategoryProfit / bestCategorySales) * 100 : 0;
        const catValEl = document.getElementById('insightBestCategoryVal');
        const catDescEl = document.getElementById('insightBestCategoryDesc');
        if (catValEl) catValEl.textContent = bestCategory;
        if (catDescEl) catDescEl.textContent = `$${Math.round(maxCategoryProfit).toLocaleString()} profit (${bestCategoryMargin.toFixed(1)}% margin)`;

        // 3. Weakest Performing Segment
        const segMetrics = {};
        data.forEach(row => {
            if (!segMetrics[row.seg]) segMetrics[row.seg] = { profit: 0, sales: 0 };
            segMetrics[row.seg].profit += row.profit;
            segMetrics[row.seg].sales += row.sales;
        });
        
        let weakestSegment = 'Consumer';
        let minSegmentMargin = Infinity;
        
        Object.entries(segMetrics).forEach(([s, m]) => {
            const segMargin = m.sales > 0 ? (m.profit / m.sales) * 100 : 0;
            if (segMargin < minSegmentMargin) {
                minSegmentMargin = segMargin;
                weakestSegment = s;
            }
        });
        
        const segValEl = document.getElementById('insightWeakestSegmentVal');
        const segDescEl = document.getElementById('insightWeakestSegmentDesc');
        if (segValEl) segValEl.textContent = weakestSegment;
        if (segDescEl) segDescEl.textContent = `${minSegmentMargin.toFixed(1)}% margin (Avg benchmark 14.0%)`;

        // 4. Discount Leakage Warning (subcategory average discount > 15% and net profit negative)
        const subMetrics = {};
        data.forEach(row => {
            if (!subMetrics[row.sub]) subMetrics[row.sub] = { profit: 0, discSum: 0, count: 0 };
            subMetrics[row.sub].profit += row.profit;
            subMetrics[row.sub].discSum += row.disc;
            subMetrics[row.sub].count++;
        });
        
        let highestRiskSub = null;
        let maxSubLoss = 0;
        let riskAvgDisc = 0;
        
        Object.entries(subMetrics).forEach(([sub, m]) => {
            const avgDisc = m.count > 0 ? (m.discSum / m.count) * 100 : 0;
            if (avgDisc > 15 && m.profit < 0) {
                const loss = Math.abs(m.profit);
                if (loss > maxSubLoss) {
                    maxSubLoss = loss;
                    highestRiskSub = sub;
                    riskAvgDisc = avgDisc;
                }
            }
        });
        
        const warningCard = document.getElementById('insightDiscountWarning');
        const warningValEl = document.getElementById('insightDiscountWarningVal');
        const warningDescEl = document.getElementById('insightDiscountWarningDesc');
        
        if (highestRiskSub) {
            if (warningCard) {
                warningCard.className = 'insight-micro-card warning active-leak';
            }
            if (warningValEl) {
                warningValEl.textContent = highestRiskSub;
                warningValEl.style.color = 'var(--color-loss)';
            }
            if (warningDescEl) {
                warningDescEl.textContent = `${riskAvgDisc.toFixed(1)}% avg promo discount causing -$${Math.round(maxSubLoss).toLocaleString()} net loss`;
            }
        } else {
            if (warningCard) {
                warningCard.className = 'insight-micro-card positive';
            }
            if (warningValEl) {
                warningValEl.textContent = 'Stable Promos';
                warningValEl.style.color = 'var(--color-profit)';
            }
            if (warningDescEl) {
                warningDescEl.textContent = 'Discount leakage is highly optimized & contained.';
            }
        }

        // 5. Growth Opportunity (subcategory margin > 20% but sales < 15% of total sales)
        let bestGrowthSub = 'N/A';
        let maxGrowthMargin = 0;
        
        Object.entries(subMetrics).forEach(([sub, m]) => {
            let subSales = 0;
            data.forEach(row => {
                if (row.sub === sub) subSales += row.sales;
            });
            const subMargin = subSales > 0 ? (m.profit / subSales) * 100 : 0;
            
            if (subMargin > maxGrowthMargin && subSales < (sales * 0.15) && subSales > 0) {
                maxGrowthMargin = subMargin;
                bestGrowthSub = sub;
            }
        });
        
        const growthValEl = document.getElementById('insightGrowthOpportunityVal');
        const growthDescEl = document.getElementById('insightGrowthOpportunityDesc');
        
        if (bestGrowthSub !== 'N/A') {
            if (growthValEl) growthValEl.textContent = bestGrowthSub;
            if (growthDescEl) growthDescEl.textContent = `Outstanding ${maxGrowthMargin.toFixed(1)}% profit margin. Expand distribution channels!`;
        } else {
            if (growthValEl) growthValEl.textContent = 'N/A';
            if (growthDescEl) growthDescEl.textContent = 'All high-margin channels are currently operating at scale.';
        }
    }

    /**
     * Compile AI-inspired business narrative commentary below visualizations
     */
    updateBusinessCommentary(sales, profit, margin) {
        const textEl = document.getElementById('dynamicCommentaryText');
        if (!textEl) return;
        
        if (this.filteredData.length === 0) {
            textEl.textContent = "Filters yielded zero sales lines. No strategic commentary could be compiled.";
            return;
        }
        
        // Find highest volume subcategory and lowest profit subcategory
        const subMetrics = {};
        this.filteredData.forEach(row => {
            if (!subMetrics[row.sub]) subMetrics[row.sub] = { profit: 0, sales: 0 };
            subMetrics[row.sub].profit += row.profit;
            subMetrics[row.sub].sales += row.sales;
        });
        
        let topSubSales = 'N/A';
        let maxSales = 0;
        let bottomSubProfit = 'N/A';
        let minProfit = Infinity;
        
        Object.entries(subMetrics).forEach(([sub, m]) => {
            if (m.sales > maxSales) {
                maxSales = m.sales;
                topSubSales = sub;
            }
            if (m.profit < minProfit) {
                minProfit = m.profit;
                bottomSubProfit = sub;
            }
        });
        
        const regionStr = this.filters.region === 'ALL' ? 'national retail workspace' : `highly localized ${this.filters.region} market`;
        const segmentStr = this.filters.segment === 'ALL' ? 'omni-channel client base' : `dedicated ${this.filters.segment} segment`;
        
        let sentence1 = `Performance analytics across the ${regionStr} for the ${segmentStr} indicate healthy overall operations, delivering $${Math.round(sales).toLocaleString()} in revenue with a net profit yield of $${Math.round(profit).toLocaleString()} at a solid ${margin.toFixed(2)}% margin.`;
        
        let sentence2 = '';
        if (topSubSales !== 'N/A') {
            const topSubMargin = maxSales > 0 ? (subMetrics[topSubSales].profit / maxSales) * 100 : 0;
            sentence2 = ` The primary volume engine under these parameters is the ${topSubSales} subcategory, which contributed $${Math.round(maxSales).toLocaleString()} in sales with a ${topSubMargin.toFixed(1)}% operating margin.`;
        }
        
        let sentence3 = '';
        if (bottomSubProfit !== 'N/A' && minProfit < 0) {
            sentence3 = ` However, bottom-line performance is being pressured by substantial promotional leakage in ${bottomSubProfit}, eroding regional profitability by -$${Math.round(Math.abs(minProfit)).toLocaleString()}. We recommend a targeted reduction in discount thresholds to restore product-level profit yields.`;
        } else {
            sentence3 = ` In addition, all active product lines are demonstrating balanced pricing control, with promotion leakage strictly managed under typical enterprise safety limits. Operating yield continues to trend upward.`;
        }
        
        textEl.textContent = sentence1 + sentence2 + sentence3;
    }

    /**
     * Recalculate dynamic business narrative insights for recommendations card
     */
    updateExecutiveInsights(sales, profit, margin, orders) {
        const container = document.getElementById('insightsListContainer');
        if (!container) return;
        
        const insights = [];
        const data = this.filteredData;
        
        // 1. Profit Margin Health
        if (margin > 20) {
            insights.push({
                type: 'positive',
                title: 'Exceptional Margin Health',
                desc: `Operating margin stands strong at ${margin.toFixed(1)}%. Highly effective baseline price modeling in selected segments.`,
                icon: `<svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/></svg>`
            });
        } else if (margin > 10) {
            insights.push({
                type: 'neutral',
                title: 'Stable Operational Margins',
                desc: `Current margin is ${margin.toFixed(1)}%. Performance aligns with healthy commercial retail baselines.`,
                icon: `<svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 17h-2v-2h2v2zm0-4h-2V7h2v8z"/></svg>`
            });
        } else {
            insights.push({
                type: 'negative',
                title: 'Margin Pressure Warning',
                desc: `Net margin squeezed to ${margin.toFixed(1)}%. Review promotional discounts on Furniture and low-margin subcategories.`,
                icon: `<svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>`
            });
        }
        
        // 2. High Value Customer Segments
        const segProfit = { Furniture: 0, 'Office Supplies': 0, Technology: 0 };
        data.forEach(row => {
            if (segProfit[row.cat] !== undefined) segProfit[row.cat] += row.profit;
        });
        
        let bestCat = 'Technology';
        let bestProfit = segProfit.Technology;
        if (segProfit.Furniture > bestProfit) { bestCat = 'Furniture'; bestProfit = segProfit.Furniture; }
        if (segProfit['Office Supplies'] > bestProfit) { bestCat = 'Office Supplies'; bestProfit = segProfit['Office Supplies']; }
        
        insights.push({
            type: 'positive',
            title: `Product Mix Driver: ${bestCat}`,
            desc: `${bestCat} is leading net profitability within this dataset filter, generating $${Math.round(bestProfit).toLocaleString()} in net profits.`,
            icon: `<svg viewBox="0 0 24 24"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>`
        });
        
        // 3. Discount Impact (Bleed)
        let totalDiscountCount = 0;
        let highDiscountLoss = 0;
        data.forEach(row => {
            if (row.disc > 0.2) {
                totalDiscountCount++;
                if (row.profit < 0) {
                    highDiscountLoss += Math.abs(row.profit);
                }
            }
        });
        
        if (highDiscountLoss > 0) {
            insights.push({
                type: 'negative',
                title: 'Promotional Revenue Bleed',
                desc: `Heavy promotions (>20% discount) have triggered active losses of $${Math.round(highDiscountLoss).toLocaleString()} in select products.`,
                icon: `<svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>`
            });
        } else {
            insights.push({
                type: 'neutral',
                title: 'Healthy Discount Controls',
                desc: `Promotion leakage is strictly contained. Zero transactions with deep pricing loss detected.`,
                icon: `<svg viewBox="0 0 24 24"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>`
            });
        }
        
        // 4. Regional Performance Focus
        const regSales = { 'West': 0, 'East': 0, 'Central': 0, 'South': 0 };
        data.forEach(row => {
            if (regSales[row.reg] !== undefined) regSales[row.reg] += row.sales;
        });
        const sortedReg = Object.entries(regSales).sort((a,b) => b[1]-a[1]);
        const topReg = sortedReg[0][0];
        const topRegSales = sortedReg[0][1];
        
        insights.push({
            type: 'neutral',
            title: `Dominant Region: ${topReg}`,
            desc: `The ${topReg} region is the primary revenue market, accounting for $${Math.round(topRegSales).toLocaleString()} of active gross sales.`,
            icon: `<svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/></svg>`
        });
        
        // Output inside dashboard
        container.innerHTML = '';
        insights.forEach(ins => {
            const html = `
                <div class="insight-item ${ins.type}">
                    <div class="insight-icon-container">
                        ${ins.icon}
                    </div>
                    <div class="insight-content">
                        <h4>${ins.title}</h4>
                        <p>${ins.desc}</p>
                    </div>
                </div>
            `;
            container.insertAdjacentHTML('beforeend', html);
        });
    }

    /**
     * Trigger browser file download of current filtered rows in CSV format
     */
    exportToCSV() {
        if (this.filteredData.length === 0) {
            alert("No data available to export.");
            return;
        }
        
        const headers = ['Order Date', 'Region', 'Segment', 'Category', 'Sub-Category', 'Product Name', 'Sales', 'Profit', 'Quantity', 'Discount'];
        const csvRows = [headers.join(",")];
        
        this.filteredData.forEach(row => {
            const values = [
                row.date,
                `"${row.reg.replace(/"/g, '""')}"`,
                `"${row.seg.replace(/"/g, '""')}"`,
                `"${row.cat.replace(/"/g, '""')}"`,
                `"${row.sub.replace(/"/g, '""')}"`,
                `"${row.prod.replace(/"/g, '""')}"`,
                row.sales.toFixed(2),
                row.profit.toFixed(2),
                row.qty,
                (row.disc * 100).toFixed(1) + '%'
            ];
            csvRows.push(values.join(","));
        });
        
        const blob = new Blob([csvRows.join("\n")], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement("a");
        const url = URL.createObjectURL(blob);
        link.setAttribute("href", url);
        link.setAttribute("download", `RetailBI_Filtered_Sales_${new Date().toISOString().substring(0,10)}.csv`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    /**
     * Generate and download a beautifully formatted Markdown Executive report
     */
    exportReport() {
        if (this.filteredData.length === 0) {
            alert("No data available to generate report.");
            return;
        }
        
        let totalSales = 0;
        let totalProfit = 0;
        const uniqueOrders = new Set();
        const uniqueCustomers = new Set();
        
        this.filteredData.forEach(row => {
            totalSales += row.sales;
            totalProfit += row.profit;
            uniqueOrders.add(row.ord);
            uniqueCustomers.add(row.cust);
        });
        const margin = totalSales > 0 ? (totalProfit / totalSales) * 100 : 0;
        
        const report = `# RetailBI Executive Performance Analysis Report
**Generated on:** ${new Date().toLocaleDateString('en-US')} at ${new Date().toLocaleTimeString('en-US')}
**Database Source:** Sample Superstore Dataset (5,000 active records)

## Filter Parameters
- **Region Markets:** ${this.filters.region}
- **Customer Segment:** ${this.filters.segment}
- **Product Category:** ${this.filters.category}

---

## 1. Executive Summary & KPIs
- **Gross Revenue:** $${totalSales.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
- **Net Profit:** $${totalProfit.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
- **Profit Margin:** ${margin.toFixed(2)}%
- **Total Order Volume:** ${uniqueOrders.size.toLocaleString()} unique orders
- **Active Accounts:** ${uniqueCustomers.size.toLocaleString()} accounts

---

## 2. Dynamic Strategic Commentary
${document.getElementById('dynamicCommentaryText')?.textContent || "No analysis available."}

---

## 3. Product Subcategory Profit Pool Breakdown
| Subcategory | Category | Sales ($) | Profit ($) | Margin (%) |
| :--- | :--- | :--- | :--- | :--- |
${this.getSubcategoryMarkdownData()}

---

## 4. Operational Risk Audit & Strategy Recommendations
- **Discount Control Strategy:** Keep promotion rates in Furniture under 15% to stop capital bleeding. High table discount rates continue to impact regional margins.
- **Technology Copiers Expansion:** Continue to capitalize on the high-margin Technology sector.copiers have exceptional pricing durability.
- **Regional Target Distribution:** Scale operational investments in highest-volume West and East markets.

---

*Powered by RetailBI Business Intelligence & Sales Analytics Platform.*
`;
        
        const blob = new Blob([report], { type: 'text/markdown;charset=utf-8;' });
        const link = document.createElement("a");
        const url = URL.createObjectURL(blob);
        link.setAttribute("href", url);
        link.setAttribute("download", `RetailBI_Executive_Performance_Report_${new Date().toISOString().substring(0,10)}.md`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    /**
     * Compute markdown rows for subcategory report tables
     */
    getSubcategoryMarkdownData() {
        const subMetrics = {};
        this.filteredData.forEach(row => {
            if (!subMetrics[row.sub]) {
                subMetrics[row.sub] = { cat: row.cat, sales: 0, profit: 0 };
            }
            subMetrics[row.sub].sales += row.sales;
            subMetrics[row.sub].profit += row.profit;
        });
        
        return Object.entries(subMetrics)
            .sort((a, b) => b[1].profit - a[1].profit)
            .map(([sub, m]) => {
                const mrg = m.sales > 0 ? (m.profit / m.sales) * 100 : 0;
                return `| ${sub} | ${m.cat} | $${m.sales.toFixed(2)} | $${m.profit.toFixed(2)} | ${mrg.toFixed(2)}% |`;
            })
            .join("\n");
    }
}
