/* ==============================================================================
   E-COMMERCE BUSINESS INTELLIGENCE PLATFORM - DASHBOARD LOGIC
   Handles interactive cross-filtering, real-time metrics recalculation,
   and Chart.js instance updating.
   ============================================================================== */

document.addEventListener("DOMContentLoaded", () => {
    // 1. Column Indexes Mapping
    const COL = {
        CUST_ID: 0,
        CUST_NAME: 1,
        SEGMENT: 2,
        ORDER_ID: 3,
        ORDER_DATE: 4,
        SHIP_DATE: 5,
        SHIP_MODE: 6,
        PROD_ID: 7,
        PROD_NAME: 8,
        CATEGORY: 9,
        SUBCATEGORY: 10,
        REGION: 11,
        STATE: 12,
        CITY: 13,
        QTY: 14,
        PRICE: 15,
        DISCOUNT: 16,
        SALES: 17,
        COST: 18,
        PROFIT: 19,
        RETURN_STATUS: 20,
        RETURN_REASON: 21
    };

    // Subcategory map per Category to handle dynamic filter binding
    const SUBCATEGORIES_BY_CATEGORY = {
        "Technology": ["Phones", "Copiers", "Accessories", "Machines"],
        "Furniture": ["Chairs", "Tables", "Bookcases", "Furnishings"],
        "Office Supplies": ["Paper", "Art", "Binders", "Storage", "Envelopes"]
    };

    // 2. Chart Instances Storage (for lifecycle destruction)
    let charts = {
        trends: null,
        categories: null,
        regions: null,
        latency: null,
        elasticity: null
    };

    // 3. Filter Elements Selection
    const filterYear = document.getElementById("filter-year");
    const filterRegion = document.getElementById("filter-region");
    const filterCategory = document.getElementById("filter-category");
    const filterSubcategory = document.getElementById("filter-subcategory");
    const btnResetFilters = document.getElementById("btn-reset-filters");

    // 4. Bind Listeners
    filterYear.addEventListener("change", updateDashboard);
    filterRegion.addEventListener("change", updateDashboard);
    
    // Dynamic subcategory listing on category select
    filterCategory.addEventListener("change", () => {
        populateSubcategories();
        updateDashboard();
    });
    filterSubcategory.addEventListener("change", updateDashboard);
    
    btnResetFilters.addEventListener("click", () => {
        filterYear.value = "ALL";
        filterRegion.value = "ALL";
        filterCategory.value = "ALL";
        populateSubcategories();
        updateDashboard();
    });

    // Populate subcategories initially
    populateSubcategories();

    // Render dashboard initially
    updateDashboard();

    // ==============================================================================
    // FILTER MANAGEMENT
    // ==============================================================================
    function populateSubcategories() {
        const cat = filterCategory.value;
        filterSubcategory.innerHTML = '<option value="ALL">All Subcategories</option>';
        
        if (cat === "ALL") {
            // Add all subcategories from the map
            Object.values(SUBCATEGORIES_BY_CATEGORY).flat().forEach(subcat => {
                const opt = document.createElement("option");
                opt.value = subcat;
                opt.textContent = subcat;
                filterSubcategory.appendChild(opt);
            });
        } else {
            // Add specific subcategories
            SUBCATEGORIES_BY_CATEGORY[cat].forEach(subcat => {
                const opt = document.createElement("option");
                opt.value = subcat;
                opt.textContent = subcat;
                filterSubcategory.appendChild(opt);
            });
        }
    }

    // ==============================================================================
    // CORE DASHBOARD UPDATE PIPELINE
    // ==============================================================================
    function updateDashboard() {
        const yearVal = filterYear.value;
        const regionVal = filterRegion.value;
        const catVal = filterCategory.value;
        const subcatVal = filterSubcategory.value;

        // A. Filter Dataset in Memory
        const filteredData = window.ECOMMERCE_DATA.filter(row => {
            // Year filter
            if (yearVal !== "ALL") {
                const orderYear = row[COL.ORDER_DATE].substring(0, 4);
                if (orderYear !== yearVal) return false;
            }
            // Region filter
            if (regionVal !== "ALL" && row[COL.REGION] !== regionVal) {
                return false;
            }
            // Category filter
            if (catVal !== "ALL" && row[COL.CATEGORY] !== catVal) {
                return false;
            }
            // Subcategory filter
            if (subcatVal !== "ALL" && row[COL.SUBCATEGORY] !== subcatVal) {
                return false;
            }
            return true;
        });

        // B. Recalculate KPIs
        calculateKPIs(filteredData);

        // C. Render Visual Charts
        renderTrendsChart(filteredData);
        renderCategoriesChart(filteredData);
        renderRegionsChart(filteredData);
        renderLatencyChart(filteredData);
        renderElasticityChart(filteredData);

        // D. Populate Top Customers Table
        populateTopCustomersTable(filteredData);
    }

    // ==============================================================================
    // KPI CALCULATION ENGINE
    // ==============================================================================
    function calculateKPIs(data) {
        let totalSales = 0;
        let totalCost = 0;
        let totalProfit = 0;
        
        const uniqueOrders = new Set();
        const uniqueCustomers = new Set();
        const returnedOrders = new Set();
        const totalOrdersInDataSet = new Set();

        data.forEach(row => {
            totalSales += row[COL.SALES];
            totalCost += row[COL.COST];
            totalProfit += row[COL.PROFIT];
            
            const orderId = row[COL.ORDER_ID];
            totalOrdersInDataSet.add(orderId);
            uniqueCustomers.add(row[COL.CUST_ID]);
            
            if (row[COL.RETURN_STATUS] === "Returned") {
                returnedOrders.add(orderId);
            }
        });

        const profitMargin = totalSales > 0 ? (totalProfit / totalSales) * 100 : 0;
        const returnRate = totalOrdersInDataSet.size > 0 ? (returnedOrders.size / totalOrdersInDataSet.size) * 100 : 0;

        // Render to UI
        document.getElementById("kpi-sales").textContent = formatCurrency(totalSales);
        document.getElementById("kpi-profit").textContent = formatCurrency(totalProfit);
        document.getElementById("kpi-margin").textContent = profitMargin.toFixed(1) + "%";
        document.getElementById("kpi-orders").textContent = formatNumber(totalOrdersInDataSet.size);
        document.getElementById("kpi-returns").textContent = returnRate.toFixed(1) + "%";

        // Net profit styling adjustments for negative profitability
        const profitCard = document.getElementById("kpi-profit");
        if (totalProfit < 0) {
            profitCard.style.color = "var(--red)";
        } else {
            profitCard.style.color = "var(--green)";
        }
    }

    // ==============================================================================
    // CHART 1: MONTH-OVER-MONTH SALES & PROFIT TRENDS
    // ==============================================================================
    function renderTrendsChart(data) {
        // Group by month
        const monthlyData = {};
        data.forEach(row => {
            const monthStr = row[COL.ORDER_DATE].substring(0, 7); // "YYYY-MM"
            if (!monthlyData[monthStr]) {
                monthlyData[monthStr] = { sales: 0, profit: 0 };
            }
            monthlyData[monthStr].sales += row[COL.SALES];
            monthlyData[monthStr].profit += row[COL.PROFIT];
        });

        // Sort months chronologically
        const sortedMonths = Object.keys(monthlyData).sort();
        const salesPoints = sortedMonths.map(m => monthlyData[m].sales);
        const profitPoints = sortedMonths.map(m => monthlyData[m].profit);

        if (charts.trends) charts.trends.destroy();

        const ctx = document.getElementById("chart-trends").getContext("2d");
        charts.trends = new Chart(ctx, {
            type: "line",
            data: {
                labels: sortedMonths,
                datasets: [
                    {
                        label: "Gross Revenue",
                        data: salesPoints,
                        borderColor: "#00F2FE",
                        backgroundColor: "rgba(0, 242, 254, 0.04)",
                        borderWidth: 2.5,
                        tension: 0.35,
                        fill: true,
                        yAxisID: "y"
                    },
                    {
                        label: "Net Profit",
                        data: profitPoints,
                        borderColor: "#00E676",
                        backgroundColor: "rgba(0, 230, 118, 0.04)",
                        borderWidth: 2,
                        borderDash: [4, 4],
                        tension: 0.35,
                        fill: false,
                        yAxisID: "y1"
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: "index",
                    intersect: false
                },
                plugins: {
                    legend: {
                        labels: { color: "#90A0B3", font: { family: "Plus Jakarta Sans" } }
                    },
                    tooltip: {
                        backgroundColor: "#0C101A",
                        titleColor: "#FFF",
                        bodyColor: "#90A0B3",
                        borderColor: "rgba(255,255,255,0.08)",
                        borderWidth: 1
                    }
                },
                scales: {
                    x: {
                        grid: { color: "rgba(255,255,255,0.03)" },
                        ticks: { color: "#90A0B3", font: { size: 10 } }
                    },
                    y: {
                        type: "linear",
                        display: true,
                        position: "left",
                        grid: { color: "rgba(255,255,255,0.03)" },
                        ticks: {
                            color: "#90A0B3",
                            callback: value => formatCurrencyShort(value)
                        }
                    },
                    y1: {
                        type: "linear",
                        display: true,
                        position: "right",
                        grid: { drawOnChartArea: false },
                        ticks: {
                            color: "#90A0B3",
                            callback: value => formatCurrencyShort(value)
                        }
                    }
                }
            }
        });
    }

    // ==============================================================================
    // CHART 2: CATEGORY CONTRIBUTION DOUGHNUT
    // ==============================================================================
    function renderCategoriesChart(data) {
        const categories = {};
        data.forEach(row => {
            const cat = row[COL.CATEGORY];
            categories[cat] = (categories[cat] || 0) + row[COL.SALES];
        });

        const labels = Object.keys(categories);
        const values = Object.values(categories);

        // Chart.js Color Map for Obsidian Theme
        const colors = {
            "Technology": "#00F2FE",
            "Furniture": "#8A2BE2",
            "Office Supplies": "#FFD600"
        };
        const bgColors = labels.map(l => colors[l] || "#90A0B3");

        if (charts.categories) charts.categories.destroy();

        const ctx = document.getElementById("chart-categories").getContext("2d");
        charts.categories = new Chart(ctx, {
            type: "doughnut",
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: bgColors,
                    borderColor: "#0C101A",
                    borderWidth: 2,
                    hoverOffset: 12
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: "bottom",
                        labels: { color: "#90A0B3", font: { family: "Plus Jakarta Sans" } }
                    },
                    tooltip: {
                        backgroundColor: "#0C101A",
                        callbacks: {
                            label: function(context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const pct = ((context.raw / total) * 100).toFixed(1);
                                return `${context.label}: ${formatCurrency(context.raw)} (${pct}%)`;
                            }
                        }
                    }
                },
                cutout: "65%"
            }
        });
    }

    // ==============================================================================
    // CHART 3: REGIONAL PERFORMANCE BAR
    // ==============================================================================
    function renderRegionsChart(data) {
        const regions = {};
        data.forEach(row => {
            const reg = row[COL.REGION];
            if (!regions[reg]) {
                regions[reg] = { sales: 0, profit: 0 };
            }
            regions[reg].sales += row[COL.SALES];
            regions[reg].profit += row[COL.PROFIT];
        });

        const labels = Object.keys(regions);
        const sales = labels.map(r => regions[r].sales);
        const profitMargin = labels.map(r => regions[r].sales > 0 ? (regions[r].profit / regions[r].sales) * 100 : 0);

        if (charts.regions) charts.regions.destroy();

        const ctx = document.getElementById("chart-regions").getContext("2d");
        charts.regions = new Chart(ctx, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [
                    {
                        label: "Gross Sales",
                        data: sales,
                        backgroundColor: "rgba(138, 43, 226, 0.75)",
                        borderColor: "#8A2BE2",
                        borderWidth: 1.5,
                        yAxisID: "y"
                    },
                    {
                        label: "Profit Margin %",
                        data: profitMargin,
                        backgroundColor: "rgba(0, 242, 254, 0.15)",
                        borderColor: "#00F2FE",
                        borderWidth: 2,
                        type: "line",
                        tension: 0.2,
                        yAxisID: "y1"
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: "#90A0B3" }
                    },
                    tooltip: {
                        backgroundColor: "#0C101A"
                    }
                },
                scales: {
                    x: {
                        grid: { color: "rgba(255,255,255,0.03)" },
                        ticks: { color: "#90A0B3" }
                    },
                    y: {
                        type: "linear",
                        display: true,
                        position: "left",
                        grid: { color: "rgba(255,255,255,0.03)" },
                        ticks: {
                            color: "#90A0B3",
                            callback: value => formatCurrencyShort(value)
                        }
                    },
                    y1: {
                        type: "linear",
                        display: true,
                        position: "right",
                        grid: { drawOnChartArea: false },
                        ticks: {
                            color: "#90A0B3",
                            callback: value => value.toFixed(0) + "%"
                        }
                    }
                }
            }
        });
    }

    // ==============================================================================
    // CHART 4: SHIPPING LATENCY RETURN RATE MULTIPLIER
    // ==============================================================================
    function renderLatencyChart(data) {
        // Collect order shipping latency and check returns status
        // Group latency by order ID first to avoid double counting orders
        const orders = {};
        data.forEach(row => {
            const orderId = row[COL.ORDER_ID];
            if (!orders[orderId]) {
                const ordDt = new Date(row[COL.ORDER_DATE]);
                const shpDt = new Date(row[COL.SHIP_DATE]);
                const days = Math.round((shpDt - ordDt) / (1000 * 60 * 60 * 24));
                orders[orderId] = {
                    days: days,
                    returned: row[COL.RETURN_STATUS] === "Returned"
                };
            } else if (row[COL.RETURN_STATUS] === "Returned") {
                orders[orderId].returned = true;
            }
        });

        // Group into latency buckets: 0-2 days, 3-4 days, 5-6 days, 7+ days
        const buckets = {
            "0-2 Days (Express)": { total: 0, returned: 0 },
            "3-4 Days (Priority)": { total: 0, returned: 0 },
            "5-6 Days (Standard)": { total: 0, returned: 0 },
            "7+ Days (Delayed)": { total: 0, returned: 0 }
        };

        Object.values(orders).forEach(o => {
            let bName = "7+ Days (Delayed)";
            if (o.days <= 2) bName = "0-2 Days (Express)";
            else if (o.days <= 4) bName = "3-4 Days (Priority)";
            else if (o.days <= 6) bName = "5-6 Days (Standard)";

            buckets[bName].total++;
            if (o.returned) buckets[bName].returned++;
        });

        const labels = Object.keys(buckets);
        const rates = labels.map(l => buckets[l].total > 0 ? (buckets[l].returned / buckets[l].total) * 100 : 0);

        if (charts.latency) charts.latency.destroy();

        const ctx = document.getElementById("chart-returns-latency").getContext("2d");
        charts.latency = new Chart(ctx, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [{
                    label: "Order Return Rate %",
                    data: rates,
                    backgroundColor: rates.map(r => r > 10 ? "rgba(255, 23, 68, 0.7)" : "rgba(0, 242, 254, 0.6)"),
                    borderColor: rates.map(r => r > 10 ? "#FF1744" : "#00F2FE"),
                    borderWidth: 1.5,
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: "#0C101A",
                        callbacks: {
                            label: function(context) {
                                const bName = context.label;
                                return `Return Rate: ${context.raw.toFixed(1)}% (Total Orders: ${buckets[bName].total})`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: { color: "rgba(255,255,255,0.03)" },
                        ticks: { color: "#90A0B3", font: { size: 10 } }
                    },
                    y: {
                        grid: { color: "rgba(255,255,255,0.03)" },
                        ticks: {
                            color: "#90A0B3",
                            callback: value => value + "%"
                        }
                    }
                }
            }
        });
    }

    // ==============================================================================
    // CHART 5: DISCOUNT MARGIN ELASTICITY
    // ==============================================================================
    function renderElasticityChart(data) {
        // Group by discount buckets
        const discountGroups = {
            "0% (None)": { sales: 0, profit: 0 },
            "5-10% (Low)": { sales: 0, profit: 0 },
            "11-20% (Medium)": { sales: 0, profit: 0 },
            "21-30% (High)": { sales: 0, profit: 0 },
            "31%+ (Deep)": { sales: 0, profit: 0 }
        };

        data.forEach(row => {
            const disc = row[COL.DISCOUNT];
            let key = "31%+ (Deep)";
            if (disc === 0) key = "0% (None)";
            else if (disc <= 0.10) key = "5-10% (Low)";
            else if (disc <= 0.20) key = "11-20% (Medium)";
            else if (disc <= 0.30) key = "21-30% (High)";

            discountGroups[key].sales += row[COL.SALES];
            discountGroups[key].profit += row[COL.PROFIT];
        });

        const labels = Object.keys(discountGroups);
        const margins = labels.map(l => {
            const g = discountGroups[l];
            return g.sales > 0 ? (g.profit / g.sales) * 100 : 0;
        });

        if (charts.elasticity) charts.elasticity.destroy();

        const ctx = document.getElementById("chart-discount-elasticity").getContext("2d");
        charts.elasticity = new Chart(ctx, {
            type: "line",
            data: {
                labels: labels,
                datasets: [{
                    label: "Net Margin %",
                    data: margins,
                    borderColor: "#FFD600",
                    backgroundColor: "rgba(255, 214, 0, 0.05)",
                    borderWidth: 2.5,
                    tension: 0.15,
                    fill: true,
                    pointBackgroundColor: margins.map(m => m < 0 ? "#FF1744" : "#00E676"),
                    pointRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: "#0C101A",
                        callbacks: {
                            label: function(context) {
                                return `Avg Margin: ${context.raw.toFixed(1)}%`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: { color: "rgba(255,255,255,0.03)" },
                        ticks: { color: "#90A0B3" }
                    },
                    y: {
                        grid: { color: "rgba(255,255,255,0.03)" },
                        ticks: {
                            color: "#90A0B3",
                            callback: value => value.toFixed(0) + "%"
                        }
                    }
                }
            }
        });
    }

    // ==============================================================================
    // TOP CUSTOMERS TABLE INGESTION
    // ==============================================================================
    function populateTopCustomersTable(data) {
        // Group by Customer ID
        const customers = {};
        data.forEach(row => {
            const custId = row[COL.CUST_ID];
            if (!customers[custId]) {
                customers[custId] = {
                    id: custId,
                    name: row[COL.CUST_NAME],
                    segment: row[COL.SEGMENT],
                    region: row[COL.REGION],
                    spend: 0,
                    profit: 0,
                    returns: new Set()
                };
            }
            customers[custId].spend += row[COL.SALES];
            customers[custId].profit += row[COL.PROFIT];
            
            if (row[COL.RETURN_STATUS] === "Returned") {
                customers[custId].returns.add(row[COL.ORDER_ID]);
            }
        });

        // Convert to array and sort by spend descending
        const sortedCustomers = Object.values(customers)
            .sort((a, b) => b.spend - a.spend)
            .slice(0, 10);

        const tbody = document.querySelector("#table-top-customers tbody");
        tbody.innerHTML = "";

        sortedCustomers.forEach((c, idx) => {
            const tr = document.createElement("tr");
            
            const profitClass = c.profit < 0 ? "td-loss" : "td-profit";
            const segmentClass = c.segment.replace(/\s+/g, ""); // strip space for class binding

            tr.innerHTML = `
                <td class="td-highlight">#${idx + 1}</td>
                <td>${c.id}</td>
                <td class="td-highlight">${c.name}</td>
                <td><span class="badge-segment ${segmentClass}">${c.segment}</span></td>
                <td>${c.region}</td>
                <td class="td-accent">${formatCurrency(c.spend)}</td>
                <td class="${profitClass}">${formatCurrency(c.profit)}</td>
                <td>${c.returns.size}</td>
            `;
            tbody.appendChild(tr);
        });
    }

    // ==============================================================================
    // FORMATTING HELPERS
    // ==============================================================================
    function formatCurrency(val) {
        return new Intl.NumberFormat("en-US", {
            style: "currency",
            currency: "USD",
            minimumFractionDigits: 2
        }).format(val);
    }

    function formatCurrencyShort(val) {
        if (Math.abs(val) >= 1e6) {
            return "$" + (val / 1e6).toFixed(1) + "M";
        } else if (Math.abs(val) >= 1e3) {
            return "$" + (val / 1e3).toFixed(0) + "K";
        }
        return "$" + val;
    }

    function formatNumber(val) {
        return new Intl.NumberFormat("en-US").format(val);
    }
});
