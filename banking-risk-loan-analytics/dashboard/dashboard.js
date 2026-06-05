/* ==============================================================================
   BANKING RISK & LOAN ANALYTICS PLATFORM - DASHBOARD LOGIC
   Handles interactive cross-filtering, real-time banking KPIs recalculation,
   and Chart.js instance updating.
   ============================================================================== */

document.addEventListener("DOMContentLoaded", () => {
    // 1. Column Indexes Mapping
    const COL = {
        CUST_ID: 0,
        CUST_NAME: 1,
        AGE: 2,
        GENDER: 3,
        OCCUPATION: 4,
        INCOME: 5,
        CREDIT_SCORE: 6,
        LOAN_ID: 7,
        LOAN_TYPE: 8,
        LOAN_AMOUNT: 9,
        INTEREST_RATE: 10,
        TERM_MONTHS: 11,
        EMI: 12,
        BRANCH_NAME: 13,
        REGION: 14,
        APP_DATE: 15,
        APPROVAL_STATUS: 16,
        RISK_SCORE: 17,
        RISK_CATEGORY: 18,
        DEFAULT_STATUS: 19,
        DEFAULT_AMOUNT: 20,
        RECOVERED_AMOUNT: 21,
        PMTS_DUE: 22,
        PMTS_LATE: 23,
        PMTS_MISSED: 24,
        INTEREST_COLLECTED: 25
    };

    // 2. Chart Instances Storage (for lifecycle destruction)
    let charts = {
        timelines: null,
        riskCategories: null,
        creditDistribution: null,
        branchPerformance: null
    };

    // 3. Filter Elements Selection
    const filterBranch = document.getElementById("filter-branch");
    const filterLoanType = document.getElementById("filter-loan-type");
    const filterAgeGroup = document.getElementById("filter-age-group");
    const filterCreditBand = document.getElementById("filter-credit-band");
    const filterApproval = document.getElementById("filter-approval");
    const btnResetFilters = document.getElementById("btn-reset-filters");

    // 4. Bind Listeners
    filterBranch.addEventListener("change", updateDashboard);
    filterLoanType.addEventListener("change", updateDashboard);
    filterAgeGroup.addEventListener("change", updateDashboard);
    filterCreditBand.addEventListener("change", updateDashboard);
    filterApproval.addEventListener("change", updateDashboard);
    
    btnResetFilters.addEventListener("click", () => {
        filterBranch.value = "ALL";
        filterLoanType.value = "ALL";
        filterAgeGroup.value = "ALL";
        filterCreditBand.value = "ALL";
        filterApproval.value = "ALL";
        updateDashboard();
    });

    // Render dashboard initially
    updateDashboard();

    // ==============================================================================
    // CORE DASHBOARD UPDATE PIPELINE
    // ==============================================================================
    function updateDashboard() {
        const branchVal = filterBranch.value;
        const typeVal = filterLoanType.value;
        const ageVal = filterAgeGroup.value;
        const creditVal = filterCreditBand.value;
        const approvalVal = filterApproval.value;

        // Filter Dataset in Memory
        const filteredData = window.BANKING_DATA.filter(row => {
            // Branch filter
            if (branchVal !== "ALL" && row[COL.BRANCH_NAME] !== branchVal) {
                return false;
            }
            // Loan Type filter
            if (typeVal !== "ALL" && row[COL.LOAN_TYPE] !== typeVal) {
                return false;
            }
            // Age Group filter
            if (ageVal !== "ALL") {
                const age = row[COL.AGE];
                if (ageVal === "18-25" && (age < 18 || age > 25)) return false;
                if (ageVal === "26-35" && (age < 26 || age > 35)) return false;
                if (ageVal === "36-50" && (age < 36 || age > 50)) return false;
                if (ageVal === "50+" && age <= 50) return false;
            }
            // Credit Score Band filter
            if (creditVal !== "ALL") {
                const score = row[COL.CREDIT_SCORE];
                if (creditVal === "Super Prime" && score < 750) return false;
                if (creditVal === "Prime" && (score < 680 || score >= 750)) return false;
                if (creditVal === "Near Prime" && (score < 620 || score >= 680)) return false;
                if (creditVal === "Subprime" && (score < 580 || score >= 620)) return false;
                if (creditVal === "Deep Subprime" && score >= 580) return false;
            }
            // Approval Status filter
            if (approvalVal !== "ALL" && row[COL.APPROVAL_STATUS] !== approvalVal) {
                return false;
            }
            return true;
        });

        // Recalculate KPIs
        calculateKPIs(filteredData);

        // Render Visual Charts
        renderTimelinesChart(filteredData);
        renderRiskCategoriesChart(filteredData);
        renderCreditDistributionChart(filteredData);
        renderBranchPerformanceChart(filteredData);

        // Populate High-Risk Borrowers Table
        populateHighRiskTable(filteredData);
    }

    // ==============================================================================
    // KPI CALCULATION ENGINE
    // ==============================================================================
    function calculateKPIs(data) {
        let totalCustomers = new Set();
        let approvedCount = 0;
        let rejectedCount = 0;
        let defaultCount = 0;
        
        let totalDuePmts = 0;
        let totalMissedPmts = 0;
        
        let sumCreditScore = 0;
        let totalInterestRevenue = 0;
        let totalRiskExposure = 0;

        data.forEach(row => {
            totalCustomers.add(row[COL.CUST_ID]);
            
            if (row[COL.APPROVAL_STATUS] === "Approved") {
                approvedCount++;
                sumCreditScore += row[COL.CREDIT_SCORE];
                totalDuePmts += row[COL.PMTS_DUE];
                totalMissedPmts += row[COL.PMTS_MISSED];
                totalInterestRevenue += row[COL.INTEREST_COLLECTED];
                
                if (row[COL.DEFAULT_STATUS] !== "Active/Paid") {
                    defaultCount++;
                    totalRiskExposure += row[COL.DEFAULT_AMOUNT];
                }
            } else {
                rejectedCount++;
            }
        });

        const totalApplications = approvedCount + rejectedCount;
        const approvalRate = totalApplications > 0 ? (approvedCount / totalApplications) * 100 : 0;
        const defaultRate = approvedCount > 0 ? (defaultCount / approvedCount) * 100 : 0;
        const repaymentRate = totalDuePmts > 0 ? ((totalDuePmts - totalMissedPmts) / totalDuePmts) * 100 : 100;
        const avgCredit = approvedCount > 0 ? Math.round(sumCreditScore / approvedCount) : 0;

        // Render to UI
        document.getElementById("kpi-customers").textContent = formatNumber(totalCustomers.size);
        document.getElementById("kpi-approval").textContent = approvalRate.toFixed(1) + "%";
        document.getElementById("kpi-default").textContent = defaultRate.toFixed(1) + "%";
        document.getElementById("kpi-repayment").textContent = repaymentRate.toFixed(1) + "%";
        document.getElementById("kpi-credit").textContent = formatNumber(avgCredit);
        document.getElementById("kpi-revenue").textContent = formatCurrency(totalInterestRevenue);
        document.getElementById("kpi-exposure").textContent = formatCurrency(totalRiskExposure);
    }

    // ==============================================================================
    // CHART 1: MONTHLY APPROVALS & DEFAULT TIMELINES
    // ==============================================================================
    function renderTimelinesChart(data) {
        const monthlyData = {};
        
        data.forEach(row => {
            const monthStr = row[COL.APP_DATE].substring(0, 7); // "YYYY-MM"
            if (!monthlyData[monthStr]) {
                monthlyData[monthStr] = { approved: 0, defaulted: 0 };
            }
            if (row[COL.APPROVAL_STATUS] === "Approved") {
                monthlyData[monthStr].approved++;
                if (row[COL.DEFAULT_STATUS] !== "Active/Paid") {
                    monthlyData[monthStr].defaulted++;
                }
            }
        });

        const sortedMonths = Object.keys(monthlyData).sort();
        const approvedSeries = sortedMonths.map(m => monthlyData[m].approved);
        const defaultedSeries = sortedMonths.map(m => monthlyData[m].defaulted);

        if (charts.timelines) charts.timelines.destroy();

        const ctx = document.getElementById("chart-timelines").getContext("2d");
        charts.timelines = new Chart(ctx, {
            type: "line",
            data: {
                labels: sortedMonths,
                datasets: [
                    {
                        label: "Approved Loans",
                        data: approvedSeries,
                        borderColor: "#00E5FF",
                        backgroundColor: "rgba(0, 229, 255, 0.04)",
                        borderWidth: 2.5,
                        tension: 0.3,
                        fill: true,
                        yAxisID: "y"
                    },
                    {
                        label: "Defaulted Loans",
                        data: defaultedSeries,
                        borderColor: "#FF1744",
                        backgroundColor: "rgba(255, 23, 68, 0.04)",
                        borderWidth: 2,
                        borderDash: [3, 3],
                        tension: 0.3,
                        fill: false,
                        yAxisID: "y1"
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: { mode: "index", intersect: false },
                plugins: {
                    legend: { labels: { color: "#94A3B8" } },
                    tooltip: { backgroundColor: "#101420" }
                },
                scales: {
                    x: {
                        grid: { color: "rgba(255,255,255,0.03)" },
                        ticks: { color: "#94A3B8", font: { size: 9 } }
                    },
                    y: {
                        type: "linear",
                        display: true,
                        position: "left",
                        grid: { color: "rgba(255,255,255,0.03)" },
                        ticks: { color: "#94A3B8" }
                    },
                    y1: {
                        type: "linear",
                        display: true,
                        position: "right",
                        grid: { drawOnChartArea: false },
                        ticks: { color: "#94A3B8" }
                    }
                }
            }
        });
    }

    // ==============================================================================
    // CHART 2: RISK CATEGORY CAPITAL SHARE DOUGHNUT
    // ==============================================================================
    function renderRiskCategoriesChart(data) {
        const riskVolume = {
            "Low Risk": 0,
            "Medium Risk": 0,
            "High Risk": 0,
            "Critical Risk": 0
        };

        data.forEach(row => {
            if (row[COL.APPROVAL_STATUS] === "Approved") {
                const cat = row[COL.RISK_CATEGORY];
                if (riskVolume.hasOwnProperty(cat)) {
                    riskVolume[cat] += row[COL.LOAN_AMOUNT];
                }
            }
        });

        const labels = Object.keys(riskVolume);
        const values = Object.values(riskVolume);

        const colors = {
            "Low Risk": "#00E676",
            "Medium Risk": "#FF9100",
            "High Risk": "#FF1744",
            "Critical Risk": "#B71C1C"
        };
        const bgColors = labels.map(l => colors[l]);

        if (charts.riskCategories) charts.riskCategories.destroy();

        const ctx = document.getElementById("chart-risk-categories").getContext("2d");
        charts.riskCategories = new Chart(ctx, {
            type: "doughnut",
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: bgColors,
                    borderColor: "#101420",
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: "bottom",
                        labels: { color: "#94A3B8", boxWidth: 12 }
                    },
                    tooltip: {
                        backgroundColor: "#101420",
                        callbacks: {
                            label: function(context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const pct = ((context.raw / total) * 100).toFixed(1);
                                return `${context.label}: ${formatCurrencyShort(context.raw)} (${pct}%)`;
                            }
                        }
                    }
                },
                cutout: "60%"
            }
        });
    }

    // ==============================================================================
    // CHART 3: CREDIT SCORE DISTRIBUTION & DEFAULTS
    // ==============================================================================
    function renderCreditDistributionChart(data) {
        // Group by Credit Bands
        const bands = {
            "Deep Subprime (<580)": { approved: 0, defaulted: 0 },
            "Subprime (580-619)": { approved: 0, defaulted: 0 },
            "Near Prime (620-679)": { approved: 0, defaulted: 0 },
            "Prime (680-749)": { approved: 0, defaulted: 0 },
            "Super Prime (>=750)": { approved: 0, defaulted: 0 }
        };

        data.forEach(row => {
            if (row[COL.APPROVAL_STATUS] === "Approved") {
                const score = row[COL.CREDIT_SCORE];
                let band = "Super Prime (>=750)";
                if (score < 580) band = "Deep Subprime (<580)";
                else if (score < 620) band = "Subprime (580-619)";
                else if (score < 680) band = "Near Prime (620-679)";
                else if (score < 750) band = "Prime (680-749)";

                bands[band].approved++;
                if (row[COL.DEFAULT_STATUS] !== "Active/Paid") {
                    bands[band].defaulted++;
                }
            }
        });

        const labels = Object.keys(bands);
        const approvedVol = labels.map(l => bands[l].approved);
        const defaultedVol = labels.map(l => bands[l].defaulted);

        if (charts.creditDistribution) charts.creditDistribution.destroy();

        const ctx = document.getElementById("chart-credit-distribution").getContext("2d");
        charts.creditDistribution = new Chart(ctx, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [
                    {
                        label: "Approved Count",
                        data: approvedVol,
                        backgroundColor: "rgba(0, 229, 255, 0.75)",
                        borderColor: "#00E5FF",
                        borderWidth: 1,
                        borderRadius: 4
                    },
                    {
                        label: "Defaults Count",
                        data: defaultedVol,
                        backgroundColor: "rgba(255, 23, 68, 0.75)",
                        borderColor: "#FF1744",
                        borderWidth: 1,
                        borderRadius: 4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { labels: { color: "#94A3B8" } },
                    tooltip: { backgroundColor: "#101420" }
                },
                scales: {
                    x: {
                        grid: { color: "rgba(255,255,255,0.03)" },
                        ticks: { color: "#94A3B8", font: { size: 9 } }
                    },
                    y: {
                        grid: { color: "rgba(255,255,255,0.03)" },
                        ticks: { color: "#94A3B8" }
                    }
                }
            }
        });
    }

    // ==============================================================================
    // CHART 4: BRANCH LENDING & DEFAULT EXPOSURE
    // ==============================================================================
    function renderBranchPerformanceChart(data) {
        const branches = {};
        
        data.forEach(row => {
            const branch = row[COL.BRANCH_NAME];
            if (!branches[branch]) {
                branches[branch] = { disbursed: 0, defaultLoss: 0 };
            }
            if (row[COL.APPROVAL_STATUS] === "Approved") {
                branches[branch].disbursed += row[COL.LOAN_AMOUNT];
                if (row[COL.DEFAULT_STATUS] !== "Active/Paid") {
                    branches[branch].defaultLoss += row[COL.DEFAULT_AMOUNT];
                }
            }
        });

        const labels = Object.keys(branches).sort();
        const disbursedAmt = labels.map(b => branches[b].disbursed);
        const defaultedAmt = labels.map(b => branches[b].defaultLoss);

        if (charts.branchPerformance) charts.branchPerformance.destroy();

        const ctx = document.getElementById("chart-branch-performance").getContext("2d");
        charts.branchPerformance = new Chart(ctx, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [
                    {
                        label: "Total Disbursed Capital",
                        data: disbursedAmt,
                        backgroundColor: "rgba(157, 78, 221, 0.75)",
                        borderColor: "#9D4EDD",
                        borderWidth: 1,
                        borderRadius: 4
                    },
                    {
                        label: "Net Default Exposure",
                        data: defaultedAmt,
                        backgroundColor: "rgba(255, 23, 68, 0.65)",
                        borderColor: "#FF1744",
                        borderWidth: 1,
                        borderRadius: 4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { labels: { color: "#94A3B8" } },
                    tooltip: { backgroundColor: "#101420" }
                },
                scales: {
                    x: {
                        grid: { color: "rgba(255,255,255,0.03)" },
                        ticks: { color: "#94A3B8", font: { size: 9 } }
                    },
                    y: {
                        grid: { color: "rgba(255,255,255,0.03)" },
                        ticks: {
                            color: "#94A3B8",
                            callback: value => formatCurrencyShort(value)
                        }
                    }
                }
            }
        });
    }

    // ==============================================================================
    // TOP 10 HIGH-RISK BORROWERS TABLE
    // ==============================================================================
    function populateHighRiskTable(data) {
        // Filter approved loans that fall into High Risk or Critical Risk category
        const highRiskLoans = data.filter(row => {
            return row[COL.APPROVAL_STATUS] === "Approved" && 
                   (row[COL.RISK_CATEGORY] === "High Risk" || row[COL.RISK_CATEGORY] === "Critical Risk");
        });

        // Sort descending by Loan_Amount
        const sortedLoans = highRiskLoans
            .sort((a, b) => b[COL.LOAN_AMOUNT] - a[COL.LOAN_AMOUNT])
            .slice(0, 10);

        const tbody = document.querySelector("#table-high-risk-borrowers tbody");
        tbody.innerHTML = "";

        sortedLoans.forEach((row, idx) => {
            const tr = document.createElement("tr");
            
            const riskBadgeClass = row[COL.RISK_CATEGORY].replace(/\s+/g, ""); // strip space for class binding
            
            tr.innerHTML = `
                <td class="td-highlight">#${idx + 1}</td>
                <td>${row[COL.CUST_ID]}</td>
                <td class="td-highlight">${row[COL.CUST_NAME]}</td>
                <td>${formatCurrency(row[COL.INCOME])}</td>
                <td class="td-highlight">${row[COL.CREDIT_SCORE]}</td>
                <td>${row[COL.LOAN_TYPE]}</td>
                <td class="td-accent">${formatCurrency(row[COL.LOAN_AMOUNT])}</td>
                <td>${row[COL.RISK_SCORE]}</td>
                <td><span class="badge-risk ${riskBadgeClass}">${row[COL.RISK_CATEGORY]}</span></td>
                <td class="td-loss">${row[COL.PMTS_MISSED] + row[COL.PMTS_LATE]}</td>
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
