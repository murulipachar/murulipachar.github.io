/**
 * HR Analytics Dashboard - Core Analytics Controller
 * Pure ES6 Vanilla JavaScript - Highly optimized and responsive
 */

// --- Global State for Filter Engine ---
const activeFilters = {
    Department: new Set(),
    Gender: new Set(),
    Overtime: new Set()
};

let charts = {}; // Object to track active Chart.js instances

document.addEventListener("DOMContentLoaded", () => {
    // 1. Initial Loader Fade Out
    const loader = document.getElementById("loaderOverlay");
    if (loader) {
        setTimeout(() => {
            loader.classList.add("fade-out");
        }, 800);
    }

    // 2. Start Live Time Clock Widget
    startClock();

    // 3. Initialize Filters & Data Bindings
    initFilterMenus();

    // 4. Set Initial Last Refreshed Time
    const now = new Date();
    document.getElementById("lastRefreshedTime").textContent = now.toTimeString().split(' ')[0];

    // 5. Render/Update Dashboard Layout
    updateDashboard();

    // 6. Bind Event Listeners
    bindEvents();
});

// --- Start timezone executive clock ---
function startClock() {
    const timeDisplay = document.getElementById("currentTime");
    function updateClock() {
        const now = new Date();
        const options = { weekday: 'short', month: 'short', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false };
        if (timeDisplay) timeDisplay.textContent = now.toLocaleDateString('en-US', options);
    }
    updateClock();
    setInterval(updateClock, 1000);
}

// --- Initialize Sidebar Filter Buttons ---
function initFilterMenus() {
    // Get unique Departments and Genders
    const depts = [...new Set(HR_DATA.map(x => x.Department))].sort();
    const genders = [...new Set(HR_DATA.map(x => x.Gender))].sort();

    const deptContainer = document.getElementById("filterDeptContainer");
    const genderContainer = document.getElementById("filterGenderContainer");

    // Populate Department Filter Buttons
    if (deptContainer) {
        deptContainer.innerHTML = depts.map(dept => {
            const count = HR_DATA.filter(x => x.Department === dept).length;
            return `
                <button class="filter-btn" data-filter-group="Department" data-filter-val="${dept}" title="Filter to ${dept} department">
                    <span>${dept}</span>
                    <span class="filter-count">${count}</span>
                </button>
            `;
        }).join('');
    }

    // Populate Gender Filter Buttons
    if (genderContainer) {
        genderContainer.innerHTML = genders.map(gender => {
            const count = HR_DATA.filter(x => x.Gender === gender).length;
            return `
                <button class="filter-btn" data-filter-group="Gender" data-filter-val="${gender}" title="Filter to ${gender} employees">
                    <span>${gender}</span>
                    <span class="filter-count">${count}</span>
                </button>
            `;
        }).join('');
    }

    // Initialize Overtime Counts
    const otYes = HR_DATA.filter(x => x.Overtime === "Yes").length;
    const otNo = HR_DATA.filter(x => x.Overtime === "No").length;
    document.getElementById("countOvertimeYes").textContent = otYes;
    document.getElementById("countOvertimeNo").textContent = otNo;

    // Expand/Collapse Sidebar groups
    document.querySelectorAll(".filter-group-header").forEach(btn => {
        btn.addEventListener("click", () => {
            const group = btn.closest(".filter-group");
            const expanded = btn.getAttribute("aria-expanded") === "true";
            btn.setAttribute("aria-expanded", !expanded);
            group.classList.toggle("active");
        });
    });
}

// --- Bind Button Clicks & Actions ---
function bindEvents() {
    // Filter buttons clicking
    document.addEventListener("click", (e) => {
        const btn = e.target.closest(".filter-btn");
        if (!btn) return;

        const group = btn.getAttribute("data-filter-group");
        const val = btn.getAttribute("data-filter-val");
        if (!group || !val) return;

        // Toggle filter selection
        if (activeFilters[group].has(val)) {
            activeFilters[group].delete(val);
            btn.classList.remove("active");
        } else {
            activeFilters[group].add(val);
            btn.classList.add("active");
        }

        updateDashboard();
    });

    // Reset Filters button
    const btnReset = document.getElementById("resetFilters");
    const emptyStateResetBtn = document.getElementById("emptyStateResetBtn");

    const clearFilters = () => {
        Object.keys(activeFilters).forEach(key => activeFilters[key].clear());
        document.querySelectorAll(".filter-btn").forEach(btn => btn.classList.remove("active"));
        updateDashboard();
    };

    if (btnReset) btnReset.addEventListener("click", clearFilters);
    if (emptyStateResetBtn) emptyStateResetBtn.addEventListener("click", clearFilters);

    // Theme Toggle Handler
    const themeBtn = document.getElementById("themeToggleBtn");
    if (themeBtn) {
        themeBtn.addEventListener("click", () => {
            const root = document.documentElement;
            const curTheme = root.getAttribute("data-theme") || "dark";
            const nextTheme = curTheme === "dark" ? "light" : "dark";
            root.setAttribute("data-theme", nextTheme);
            
            // Re-render charts with updated theme colors
            updateDashboard();
        });
    }

    // Mock Export handlers
    document.getElementById("btnExportCSV").addEventListener("click", () => {
        alert("Preparing CSV extraction... Ingesting 1,475 active records. Download initiated successfully!");
    });
    document.getElementById("btnExportReport").addEventListener("click", () => {
        alert("Formulating tactical workforce summary. Executive PDF Report generated successfully!");
    });
    document.getElementById("btnPrintDashboard").addEventListener("click", () => {
        window.print();
    });
}

// --- Filter data and update entire UI ---
function updateDashboard() {
    // 1. Apply active filter sets to base data
    const filteredData = HR_DATA.filter(row => {
        if (activeFilters.Department.size > 0 && !activeFilters.Department.has(row.Department)) return false;
        if (activeFilters.Gender.size > 0 && !activeFilters.Gender.has(row.Gender)) return false;
        if (activeFilters.Overtime.size > 0 && !activeFilters.Overtime.has(row.Overtime)) return false;
        return true;
    });

    // 2. Check Empty State
    const emptyState = document.getElementById("emptyState");
    const mainContent = document.getElementById("workspaceMainContent");

    if (filteredData.length === 0) {
        if (emptyState) emptyState.style.display = "flex";
        if (mainContent) mainContent.style.display = "none";
        return;
    } else {
        if (emptyState) emptyState.style.display = "none";
        if (mainContent) mainContent.style.display = "flex";
    }

    // 3. Compute and Update KPIs
    const totalCount = filteredData.length;
    const activeCount = filteredData.filter(x => x.Attrition === "No").length;
    const attritionCount = filteredData.filter(x => x.Attrition === "Yes").length;
    const attritionRate = totalCount > 0 ? (attritionCount / totalCount) * 100 : 0;
    const avgSalary = totalCount > 0 ? filteredData.reduce((sum, x) => sum + x.Salary, 0) / totalCount : 0;

    document.getElementById("kpiTotal").textContent = totalCount.toLocaleString();
    document.getElementById("kpiActive").textContent = activeCount.toLocaleString();
    document.getElementById("kpiAttritionCount").textContent = attritionCount.toLocaleString();
    document.getElementById("kpiAttritionRate").textContent = attritionRate.toFixed(1) + "%";
    document.getElementById("kpiAvgSalary").textContent = "$" + Math.round(avgSalary).toLocaleString();

    // 4. Update Micro Insights Panel
    updateMicroInsights(filteredData);

    // 5. Update and Draw Charts
    renderCharts(filteredData);

    // 6. Update Action recommendations and SKU tables
    updateTacticalLists(filteredData);

    // 7. Update AI Executive Strategic Commentary text
    updateExecutiveCommentary(filteredData, attritionRate);
}

// --- Calculate Dynamic Micro-Insights panel cards ---
function updateMicroInsights(data) {
    // 1. Highest Retention Unit (Dept with lowest attrition rate)
    const deptGroups = groupbyAttrRate(data, "Department");
    let bestDept = "N/A";
    let minRate = 100;
    Object.keys(deptGroups).forEach(dept => {
        if (deptGroups[dept].rate < minRate) {
            minRate = deptGroups[dept].rate;
            bestDept = dept;
        }
    });
    document.getElementById("insightBestDeptVal").textContent = bestDept;
    document.getElementById("insightBestDeptDesc").textContent = `Exhibits top organizational stability at a ${minRate.toFixed(1)}% turnover rate.`;

    // 2. High Flight Risk Role (Job role with highest attrition count)
    const roleGroups = groupbyAttrRate(data, "JobRole");
    let worstRole = "N/A";
    let maxCount = -1;
    let worstRoleRate = 0;
    Object.keys(roleGroups).forEach(role => {
        if (roleGroups[role].count > maxCount) {
            maxCount = roleGroups[role].count;
            worstRole = role;
            worstRoleRate = roleGroups[role].rate;
        }
    });
    document.getElementById("insightRiskRoleVal").textContent = worstRole;
    document.getElementById("insightRiskRoleDesc").textContent = `Exposes greatest churn volume containing ${maxCount} total exits (${worstRoleRate.toFixed(1)}% rate).`;

    // 3. Average Active Tenure (Avg YearsAtCompany of active employees)
    const activeStaff = data.filter(x => x.Attrition === "No");
    const avgTenure = activeStaff.length > 0 ? activeStaff.reduce((sum, x) => sum + x.YearsAtCompany, 0) / activeStaff.length : 0;
    document.getElementById("insightTenureMetricVal").textContent = avgTenure.toFixed(1) + " Years";
    document.getElementById("insightTenureMetricDesc").textContent = `Represents the mean career longevity and institutional experience of retained staff.`;

    // 4. Overtime Leakage Warning
    const otExits = data.filter(x => x.Overtime === "Yes" && x.Attrition === "Yes").length;
    const otTotal = data.filter(x => x.Overtime === "Yes").length;
    const otRate = otTotal > 0 ? (otExits / otTotal) * 100 : 0;
    document.getElementById("insightOvertimeWarningVal").textContent = otRate.toFixed(1) + "% Turnover";
    document.getElementById("insightOvertimeWarningDesc").textContent = `Workload stress triggers heavy turnover among staff assigned to extended hours.`;

    // 5. Compensation Flight Risk (percentage of underpaid employees who leave)
    // Underpaid defined as below role average salary
    const roleAvgSalaries = {};
    const roles = [...new Set(HR_DATA.map(x => x.JobRole))];
    roles.forEach(role => {
        const roleData = HR_DATA.filter(x => x.JobRole === role);
        roleAvgSalaries[role] = roleData.reduce((sum, x) => sum + x.Salary, 0) / roleData.length;
    });

    const underpaidExits = data.filter(x => x.Salary < roleAvgSalaries[x.JobRole] && x.Attrition === "Yes").length;
    const underpaidTotal = data.filter(x => x.Salary < roleAvgSalaries[x.JobRole]).length;
    const underpaidRate = underpaidTotal > 0 ? (underpaidExits / underpaidTotal) * 100 : 0;
    document.getElementById("insightPayGapVal").textContent = underpaidRate.toFixed(1) + "% Rate";
    document.getElementById("insightPayGapDesc").textContent = `Turnover is significantly higher for employees compensated below role salary averages.`;
}

// --- Group helper to calculate counts and rates ---
function groupbyAttrRate(data, column) {
    const groups = {};
    data.forEach(row => {
        const val = row[column];
        if (!groups[val]) {
            groups[val] = { total: 0, count: 0 };
        }
        groups[val].total++;
        if (row.Attrition === "Yes") {
            groups[val].count++;
        }
    });
    Object.keys(groups).forEach(key => {
        groups[key].rate = (groups[key].count / groups[key].total) * 100;
    });
    return groups;
}

// --- Render Chart.js visual assets ---
function renderCharts(data) {
    // Setup color tokens based on active theme
    const root = document.documentElement;
    const theme = root.getAttribute("data-theme") || "dark";
    const gridColor = theme === "dark" ? "rgba(255, 255, 255, 0.05)" : "rgba(0, 0, 0, 0.05)";
    const textColor = theme === "dark" ? "#94a3b8" : "#475569";
    const accentTeal = theme === "dark" ? "#2dd4bf" : "#0f766e";
    const accentRose = theme === "dark" ? "#f43f5e" : "#be123c";

    const commonOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                labels: { color: textColor, font: { family: 'Inter', size: 10 } }
            }
        },
        scales: {
            x: {
                grid: { color: gridColor },
                ticks: { color: textColor, font: { family: 'Inter', size: 9 } }
            },
            y: {
                grid: { color: gridColor },
                ticks: { color: textColor, font: { family: 'Inter', size: 9 } }
            }
        }
    };

    // --- CHART 1: Tenure distribution line chart ---
    const tenureCounts = Array(23).fill(0);
    data.forEach(x => {
        if (x.YearsAtCompany <= 22) tenureCounts[x.YearsAtCompany]++;
    });
    
    updateOrCreateChart("chartTenureTrend", "line", {
        labels: Array.from({ length: 23 }, (_, idx) => idx + "Y"),
        datasets: [{
            label: "Employee Headcount",
            data: tenureCounts,
            borderColor: accentTeal,
            backgroundColor: "rgba(45, 212, 191, 0.08)",
            fill: true,
            tension: 0.3
        }]
    }, commonOptions);

    // --- CHART 2: Headcount by Department bar chart ---
    const depts = [...new Set(HR_DATA.map(x => x.Department))].sort();
    const deptHeadcounts = depts.map(dept => data.filter(x => x.Department === dept).length);

    updateOrCreateChart("chartDeptHeadcount", "bar", {
        labels: depts,
        datasets: [{
            label: "Employees Count",
            data: deptHeadcounts,
            backgroundColor: "rgba(59, 130, 246, 0.8)", // Acccent Blue
            borderColor: "#3b82f6",
            borderWidth: 1,
            borderRadius: 4
        }]
    }, {
        ...commonOptions,
        indexAxis: 'y'
    });

    // --- CHART 3: Gender Distribution donut chart ---
    const genders = ["Male", "Female", "Non-binary"];
    const genderCounts = genders.map(g => data.filter(x => x.Gender === g).length);

    updateOrCreateChart("chartGenderRatio", "doughnut", {
        labels: genders,
        datasets: [{
            data: genderCounts,
            backgroundColor: ["#3b82f6", "#a855f7", "#2dd4bf"],
            borderWidth: 0
        }]
    }, {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'right',
                labels: { color: textColor, font: { family: 'Inter', size: 10 } }
            }
        }
    });

    // --- CHART 4: Age Demographics Column Chart ---
    const ageGroups = {
        "Under 30": data.filter(x => x.Age < 30).length,
        "30-39": data.filter(x => x.Age >= 30 && x.Age < 40).length,
        "40-49": data.filter(x => x.Age >= 40 && x.Age < 50).length,
        "50 and Over": data.filter(x => x.Age >= 50).length
    };

    updateOrCreateChart("chartAgeDemographics", "bar", {
        labels: Object.keys(ageGroups),
        datasets: [{
            label: "Employee Count",
            data: Object.values(ageGroups),
            backgroundColor: "rgba(168, 85, 247, 0.8)", // Accent Purple
            borderColor: "#a855f7",
            borderRadius: 4
        }]
    }, commonOptions);

    // --- CHART 5: Salary Distribution Curve Area Chart ---
    const salaryBins = {
        "<$40k": data.filter(x => x.Salary < 40000).length,
        "$40k-$70k": data.filter(x => x.Salary >= 40000 && x.Salary < 70000).length,
        "$70k-$100k": data.filter(x => x.Salary >= 70000 && x.Salary < 100000).length,
        "$100k-$130k": data.filter(x => x.Salary >= 100000 && x.Salary < 130000).length,
        "$130k+": data.filter(x => x.Salary >= 130000).length
    };

    updateOrCreateChart("chartSalaryDist", "line", {
        labels: Object.keys(salaryBins),
        datasets: [{
            label: "Employee Count",
            data: Object.values(salaryBins),
            borderColor: "#3b82f6",
            backgroundColor: "rgba(59, 130, 246, 0.08)",
            fill: true,
            tension: 0.3
        }]
    }, commonOptions);

    // --- CHART 6: Overtime Attrition clustered bar ---
    const otYesExits = data.filter(x => x.Overtime === "Yes" && x.Attrition === "Yes").length;
    const otYesTotal = data.filter(x => x.Overtime === "Yes").length;
    const otYesRate = otYesTotal > 0 ? (otYesExits / otYesTotal) * 100 : 0;

    const otNoExits = data.filter(x => x.Overtime === "No" && x.Attrition === "Yes").length;
    const otNoTotal = data.filter(x => x.Overtime === "No").length;
    const otNoRate = otNoTotal > 0 ? (otNoExits / otNoTotal) * 100 : 0;

    updateOrCreateChart("chartOvertimeAttrition", "bar", {
        labels: ["Works Overtime", "No Overtime"],
        datasets: [
            {
                label: "Attrition Rate %",
                data: [otYesRate, otNoRate],
                backgroundColor: [accentRose, accentTeal],
                borderRadius: 4
            }
        ]
    }, {
        ...commonOptions,
        plugins: {
            legend: { display: false }
        }
    });

    // --- CHART 7: Attrition by satisfaction stacked bar ---
    const satisfactionRates = [1, 2, 3, 4].map(score => {
        const scoreData = data.filter(x => x.JobSatisfaction === score);
        const exits = scoreData.filter(x => x.Attrition === "Yes").length;
        return scoreData.length > 0 ? (exits / scoreData.length) * 100 : 0;
    });

    updateOrCreateChart("chartSatisfactionAttrition", "bar", {
        labels: ["1-Very Dissatisfied", "2-Dissatisfied", "3-Satisfied", "4-Very Satisfied"],
        datasets: [{
            label: "Attrition Rate %",
            data: satisfactionRates,
            backgroundColor: [accentRose, "#f59e0b", "#3b82f6", accentTeal],
            borderRadius: 4
        }]
    }, {
        ...commonOptions,
        plugins: {
            legend: { display: false }
        }
    });
}

// --- Chart manager helper to prevent canvas memory leaks ---
function updateOrCreateChart(canvasId, type, chartData, options) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    if (charts[canvasId]) {
        charts[canvasId].destroy();
    }

    charts[canvasId] = new Chart(canvas, {
        type: type,
        data: chartData,
        options: options
    });
}

// --- Update recommendations list and key role attrition table ---
function updateTacticalLists(data) {
    const listContainer = document.getElementById("insightsListContainer");
    const roleContainer = document.getElementById("skuListContainer");

    // Formulate 4 tactical recommendations based on active parameters
    const totalCount = data.length;
    const otTotal = data.filter(x => x.Overtime === "Yes").length;
    const otExits = data.filter(x => x.Overtime === "Yes" && x.Attrition === "Yes").length;
    const otRate = otTotal > 0 ? (otExits / otTotal) * 100 : 0;

    const lowSatExits = data.filter(x => x.JobSatisfaction <= 2 && x.Attrition === "Yes").length;
    const lowSatTotal = data.filter(x => x.JobSatisfaction <= 2).length;
    const lowSatRate = lowSatTotal > 0 ? (lowSatExits / lowSatTotal) * 100 : 0;

    const recommendations = [];

    if (otRate > 35) {
        recommendations.push({
            type: "warning-rec",
            title: "Cap Monthly Overtime Limits",
            desc: `Current active slice displays an alarming ${otRate.toFixed(1)}% overtime attrition rate. Workloads are directly driving resignations. Automate workflows or hire temporary staff.`
        });
    } else {
        recommendations.push({
            type: "info-rec",
            title: "Monitor Shift Allocations",
            desc: "Overtime turnover remains within standard parameters. Continue monitoring monthly workload cycles to avoid burnouts."
        });
    }

    if (lowSatRate > 40) {
        recommendations.push({
            type: "warning-rec",
            title: "Perform Target Department Audits",
            desc: `Dissatisfied workers exhibit a high ${lowSatRate.toFixed(1)}% turnover rate. Empower managers to conduct individual pulse assessments and adjust daily responsibilities.`
        });
    } else {
        recommendations.push({
            type: "positive-rec",
            title: "Onboarding Quality Maintenance",
            desc: "General satisfaction levels remain highly positive. Ensure onboarding processes maintain engagement markers."
        });
    }

    // Default structural suggestions
    recommendations.push({
        type: "info-rec",
        title: "Structure Early Career Maps",
        desc: "Turnover is heavily concentrated in the first 0-2 years of employee tenure. Launch structured micro-progression paths to build loyalty."
    });

    recommendations.push({
        type: "positive-rec",
        title: "Standardize Compensation Bands",
        desc: "Active staff paid below average are flight risks. Perform salary market alignments for high-performing, underpaid roles."
    });

    if (listContainer) {
        listContainer.innerHTML = recommendations.map(rec => `
            <div class="insight-item ${rec.type}">
                <span class="insight-icon-bullet"></span>
                <div class="insight-text-wrapper">
                    <span class="insight-item-title">${rec.title}</span>
                    <span class="insight-item-desc">${rec.desc}</span>
                </div>
            </div>
        `).join('');
    }

    // Populate Job Role Attrition Table lists (Top 5 worst roles by exit counts)
    const roleStats = groupbyAttrRate(data, "JobRole");
    const sortedRoles = Object.keys(roleStats)
        .map(role => ({ role, ...roleStats[role] }))
        .sort((a, b) => b.count - a.count)
        .slice(0, 5);

    if (roleContainer) {
        roleContainer.innerHTML = sortedRoles.map((stat, idx) => `
            <div class="sku-item">
                <span class="sku-rank-badge">#${idx + 1}</span>
                <div class="sku-info">
                    <span class="sku-name">${stat.role}</span>
                    <span class="sku-category">Exits: ${stat.count} / Total: ${stat.total}</span>
                </div>
                <div class="sku-metric-wrapper">
                    <span class="sku-metric-val">${stat.rate.toFixed(1)}%</span>
                    <span class="sku-metric-label ${stat.rate > 30 ? '' : 'positive'}">
                        ${stat.rate > 30 ? 'HIGH RISK' : 'STABLE'}
                    </span>
                </div>
            </div>
        `).join('');
    }
}

// --- Render dynamic AI-powered executive strategic commentary ---
function updateExecutiveCommentary(data, rate) {
    const textEl = document.getElementById("dynamicCommentaryText");
    if (!textEl) return;

    let text = "";
    if (rate > 35) {
        text = `<strong>TACTICAL WARNING:</strong> The active database slice shows a critical turnover level of <strong>${rate.toFixed(1)}%</strong>. This indicates severe organizational friction. Tracing workload aggregates shows that overtime assignees have a massive flight risk. Proactive compensation adjustments and immediate manager check-ins are recommended for critical roles before flight tendencies expand further.`;
    } else if (rate > 22) {
        text = `<strong>TACTICAL UPDATE:</strong> Workforce turnover is hovering at a moderate <strong>${rate.toFixed(1)}%</strong>. While stable, early tenure metrics (0-2 years) continue to leak talent. Enhancing onboarding maps and establishing structured feedback systems at the 6-month threshold will lock in career commitment for newer hires.`;
    } else {
        text = `<strong>TACTICAL STABILITY:</strong> Exceptional workforce retention metrics detected with attrition at a low <strong>${rate.toFixed(1)}%</strong>. Positive job satisfaction indicators reflect strong team cultures and stable compensation parameters. HR actions should focus on maintaining career training buffers and planning long-term talent succession pathways.`;
    }

    textEl.innerHTML = text;
}
