/**
 * Premium Portfolio Core Controller for Muruli H P
 * Pure ES6 Vanilla JavaScript - Highly optimized and structured
 */

// --- Project Detailed Database ---
const PROJECTS_DATA = {
  "sql-retail-analytics": {
    title: "SQL Retail Performance Analytics",
    tags: ["SQL", "MySQL", "SQLite", "Database Design"],
    category: "sql",
    description: "An advanced ANSI-SQL data analytics study modeling 3 years of retail operations. Structured a Star Schema relational database containing 12,500 transactions, created compound performance B-tree indexes, and executed 46 analytical scripts to audit operational margin leakages.",
    metrics: [
      { name: "Ingested Relational Rows", value: "12,500 Transactions" },
      { name: "Relational Star Schema Tables", value: "4 Dimension, 1 Fact" },
      { name: "Written Analytical Queries", value: "46 Production Scripts" },
      { name: "Index Performance Gains", value: "O(log N) fast scans" }
    ],
    insights: [
      {
        title: "Isolating Southern Logistics Margin Bleed",
        desc: "Discovered Southern Furniture margins were compressed to 8.39% (vs 17% baseline). Traced root cause to high freight costs on heavy products shipped from Central warehouses. Recommended partnering with local 3PL hubs in Houston and Atlanta to restore margins."
      },
      {
        title: "Auditing Promotional Discount Bleed Anomaly",
        desc: "Traced a discount bleed where markdown rates >= 30% triggered net losses, generating a cumulative -$36,252.12 loss on clearance items. Implemented a strict 20% capping parameters on high-cost categories."
      },
      {
        title: "Mapping Customer Cohort Attrition",
        desc: "Constructed quarterly inception cohorts showing that month-to-month subscribers exhibit a 46.8% attrition spike within two quarters. Formulated a statement-credit incentive to convert users to automated billing."
      }
    ],
    codeTitle: "SQL Cohort Analysis & CTE Windows",
    code: `-- SQL Query to Calculate Month-over-Month Revenue Growth Rates
WITH MonthlyRevenue AS (
    SELECT 
        STRFTIME('%Y-%m', order_date) AS order_month,
        ROUND(SUM(sales), 2) AS monthly_sales
    FROM FACT_SALES
    GROUP BY 1
)
SELECT 
    order_month,
    monthly_sales,
    LAG(monthly_sales, 1) OVER (ORDER BY order_month) AS prior_month_sales,
    ROUND(
        ((monthly_sales - LAG(monthly_sales, 1) OVER (ORDER BY order_month)) / 
        LAG(monthly_sales, 1) OVER (ORDER BY order_month)) * 100, 
        2
    ) AS mom_growth_pct
FROM MonthlyRevenue;`
  },
  "customer-churn-analysis": {
    title: "Customer Churn Analysis & Risk Scoring",
    tags: ["Python", "Pandas", "Matplotlib", "Seaborn"],
    category: "python",
    description: "A Python-based data cleaning and exploratory analytics case study auditing 7,043 subscriber profiles. Modeled behavioral churn stressors, generated risk scorecards, and formulated retention playbooks.",
    metrics: [
      { name: "Audited Accounts Pool", value: "7,043 Accounts" },
      { name: "High-Risk Active Accounts", value: "1,040 Users" },
      { name: "Revenue Exposed (Risk)", value: "$78,490/mo" },
      { name: "Customer Churn Rate", value: "30.02%" }
    ],
    insights: [
      {
        title: "Billing Gateway Friction Points",
        desc: "Customers paying manually via Electronic Check exhibit a 35.3% churn rate compared to auto-paying users (16.5%). Recommended a one-time $10 credit to migrate users to auto-pay."
      },
      {
        title: "Premium Fiber Optic Disconnect",
        desc: "Fiber optic subscribers showed a high 44.5% churn rate (averaging $95.20/mo) due to price sensitivity. Recommended value-add streaming bundles instead of direct price cuts."
      },
      {
        title: "Behavioral Churn Risk Scoring (0-100)",
        desc: "Designed a rule-based algorithm assigning weights to variables (Month-to-month contracts: +35 points, tenure < 6mo: +25 points). Segmented 1,040 active accounts as High Risk."
      }
    ],
    codeTitle: "Python Pandas Risk-Scoring Compilation",
    code: `# Python Pandas Scoring Function for Attrition Risk
def calculate_churn_risk_score(row):
    score = 0
    # Contract constraint check
    if row['Contract'] == 'Month-to-month':
        score += 35
    elif row['Contract'] == 'One year':
        score += 10
        
    # Billing gateway checks
    if row['PaymentMethod'] == 'Electronic check':
        score += 15
        
    # Infrastructure cost check
    if row['InternetService'] == 'Fiber optic':
        score += 15
    if row['MonthlyCharges'] >= 85:
        score += 15
        
    # Loyalty protection
    if row['tenure'] < 6:
        score += 25
    elif row['tenure'] >= 48:
        score -= 10
        
    return max(0, min(100, score))`
  },
  "superstore-sales-dashboard": {
    title: "Superstore Sales Dashboard",
    tags: ["HTML/CSS/JS", "Chart.js", "SQL", "Python"],
    category: "powerbi",
    description: "An interactive, glassmorphic client-side analytics dashboard. Features dynamic sorting and visual tracking of sales categories, segments, and transaction trends, powered by a Python cleaning pipeline.",
    metrics: [
      { name: "Total Sales Volume", value: "$789,447.07" },
      { name: "Net Profit Margin", value: "14.07%" },
      { name: "Corporate Segment AOV", value: "$157.74" },
      { name: "Ingested Order Lines", value: "4,997 Rows" }
    ],
    insights: [
      {
        title: "Category Margins Analysis",
        desc: "Isolated Copiers sub-category as the primary profitability engine, generating $116k in net profit. Formulated CTE queries to segregate top profitability SKUs."
      },
      {
        title: "Furniture Segment Drain",
        desc: "Identified table category sales causing net losses of -$17,167.55 under promotions. Modeled discount sensitivity tables to test capping impacts."
      }
    ],
    codeTitle: "DAX Margin Calculation & Growth Tracking",
    code: `// DAX Metric for Gross Profit Margin Percentage
ProfitMargin% = 
DIVIDE(
    SUM(Sales[Profit]), 
    SUM(Sales[SalesValue]), 
    0
)

// DAX Metric for Month-over-Month Sales Growth
MoM_Sales_Growth = 
VAR CurrentMonthSales = SUM(Sales[SalesValue])
VAR PriorMonthSales = 
    CALCULATE(
        SUM(Sales[SalesValue]),
        DATEADD('Calendar'[Date], -1, MONTH)
    )
RETURN
    DIVIDE(CurrentMonthSales - PriorMonthSales, PriorMonthSales, 0)`
  },
  "hr-analytics-dashboard": {
    title: "HR Analytics & Retention Dashboard",
    tags: ["Power BI", "SQL", "Excel", "DAX", "Data Modeling"],
    category: "powerbi",
    description: "An interactive business intelligence solution modeling workforce turnover and retention profiles for 1,475 employees. Formulated advanced SQL queries (CTEs, Window Functions) to audit compensation disparity and built custom Power BI DAX measures mapping department-level attrition hotspots.",
    metrics: [
      { name: "Total Ingested Records", value: "1,475 Employees" },
      { name: "Overall Attrition Rate", value: "31.0%" },
      { name: "Overtime Turnover Rate", value: "47.8%" },
      { name: "Low Satisfaction Exit Rate", value: "53.9%" }
    ],
    insights: [
      {
        title: "Overtime Workload Attrition Core correlation",
        desc: "Discovered employees working overtime exhibit a 47.8% attrition rate compared to 24.4% for non-overtime staff. Traced the highest workload concentrations to Sales and R&D roles."
      },
      {
        title: "Early Career Attrition Flight Risks",
        desc: "Isolated a critical retention gap where turnover peaks at 39.5% during the first 0-2 years of employee tenure, indicating potential onboarding and integration gaps."
      },
      {
        title: "Salary Disparity & Top Performers Retention",
        desc: "Identified a compensation flight risk where high-performing staff (ratings 3 and 4) paid below role averages show a 28.6% attrition rate, prompting a semi-annual compensation review recommendation."
      }
    ],
    codeTitle: "DAX Attrition Metrics & SQL Partitions",
    code: `// DAX Metric: Attrition Rate % Calculation
Attrition Rate % = 
VAR TotalEmployees = COUNT(Fact_Employees[EmployeeID])
VAR AttritionCount = 
    CALCULATE(
        COUNT(Fact_Employees[EmployeeID]),
        Fact_Employees[Attrition] = "Yes"
    )
RETURN
    DIVIDE(AttritionCount, TotalEmployees, 0)

// SQL: Identify High-Risk Employee Flight Profiles
WITH StaffDetails AS (
    SELECT EmployeeID, EmployeeName, JobRole, Salary, Overtime, JobSatisfaction,
           AVG(Salary) OVER (PARTITION BY JobRole) AS Avg_Role_Salary
    FROM hr_employee_data
    WHERE Attrition = 'No'
)
SELECT * 
FROM StaffDetails
WHERE Overtime = 'Yes' AND JobSatisfaction <= 2 AND Salary < Avg_Role_Salary;`
  },
  "gramayatri": {
    title: "GramaYatri Bus Tracking Application",
    tags: ["Kotlin", "Firebase", "Google Maps API", "Android SDK"],
    category: "android",
    description: "A real-time transit telemetry tracking mobile application created in Kotlin for rural commuters. Features dynamic coordinates synchronization via Firebase and interactive map routing.",
    metrics: [
      { name: "Location Provider Precision", value: "~5 meters" },
      { name: "Telemetry Sync Frequency", value: "1.5 seconds" },
      { name: "Firebase Sync Latency", value: "<150ms" },
      { name: "Android SDK Target", value: "API Level 33" }
    ],
    insights: [
      {
        title: "Telemetry Sync Setup",
        desc: "Configured Google Fused Location Providers to track coordinates and sync telemetry data points to Firebase database tables."
      },
      {
        title: "Coordinates Mapping",
        desc: "Wired Google Maps API rendering logic to map active bus coordinates and draw route paths dynamically for commuters."
      },
      {
        title: "Full-Stack Software Architecture",
        desc: "Utilized MVVM design pattern alongside Firebase streams to synchronize coordinate states between the driver's app and consumer screens."
      }
    ],
    codeTitle: "Kotlin Fused Location Callbacks",
    code: `// Kotlin fused location provider callback mapping
private fun startLocationTrackingUpdates() {
    val locationRequest = LocationRequest.Builder(
        Priority.PRIORITY_HIGH_ACCURACY, 
        1500 // sync delta in ms
    ).apply {
        setMinUpdateIntervalMillis(1000)
        setMinUpdateDistanceMeters(2.0f) // drift buffer threshold
    }.build()

    fusedLocationClient.requestLocationUpdates(
        locationRequest,
        locationCallback,
        Looper.getMainLooper()
    )
}`
  }
};

// --- Certification Database ---
const CERTS_DATA = {
  "sql-inter": {
    title: "SQL Intermediate Certificate",
    issuer: "HackerRank",
    date: "Verified Credential",
    desc: "Validates ability to write complex relational queries, join multiple tables, filter records under nested conditions, and implement advanced queries using subqueries and table expressions.",
    skills: ["Subqueries & Joins", "Common Table Expressions (CTEs)", "Data Aggregation", "Relational Filters"],
    verifyUrl: "" // Dead link removed (returns 404)
  },
  "py-basic": {
    title: "Python Basic Certificate",
    issuer: "HackerRank",
    date: "Verified Credential",
    desc: "Validates proficiency in fundamental Python concepts, mapping data structures, lists manipulations, dictionaries iterations, basic object-oriented programming, and file operations.",
    skills: ["Python Structures", "Conditional Control Flow", "Array Manipulations", "Text Ingestion Parsing"],
    verifyUrl: "" // Dead link removed (returns 404)
  },
  "pbi-fund": {
    title: "Power BI Fundamentals",
    issuer: "Microsoft Learn",
    date: "Verified Credential",
    desc: "Covers data loading, dimensional modeling, custom DAX metrics, data cleaning inside Power Query, page layout design, and publishing BI visual dashboards.",
    skills: ["Data Modeling", "DAX Formulas", "Visual Layout Design", "Power Query ETL"],
    verifyUrl: ""
  },
  "tata-genai": {
    title: "Tata GenAI Data Analytics Simulation",
    issuer: "Forage",
    date: "Verified Credential",
    desc: "A job simulation focused on business analysis, data preparation, generating executive dashboards, and executing analytical problem solving under enterprise scenarios.",
    skills: ["Business Requirements Translation", "Data Visual Analytics", "KPI Report Syntheses", "Executive Deck Reporting"],
    verifyUrl: ""
  },
  "excel-analysis": {
    title: "Data Analysis Using Excel",
    issuer: "Great Learning",
    date: "Verified Credential",
    desc: "Covers analytical Excel concepts including formulas, logical functions, lookup arrays (VLOOKUP/XLOOKUP), data sorting, filtering, and pivot charts operations.",
    skills: ["Lookup Arrays", "Pivot Dashboard Models", "Excel Logic Functions", "Metric Aggregations"],
    verifyUrl: ""
  }
};

// --- DOM Content Init ---
document.addEventListener("DOMContentLoaded", () => {
  // 1. Preloader Handler
  const preloader = document.getElementById("preloader");
  window.addEventListener("load", () => {
    setTimeout(() => {
      preloader.classList.add("fade-out");
    }, 600);
  });
  setTimeout(() => {
    preloader.classList.add("fade-out");
  }, 3000);

  // 2. Typewriter Loop
  initTypewriter();

  // 3. Scroll Progress & Sticky Navbar
  const progressBar = document.getElementById("progress-bar");
  const navbar = document.querySelector(".navbar");
  const navLinks = document.querySelectorAll(".nav-links a");
  const sections = document.querySelectorAll("section");

  window.addEventListener("scroll", () => {
    const scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
    const scrollPercentage = (window.scrollY / scrollHeight) * 100;
    if (progressBar) progressBar.style.width = scrollPercentage + "%";

    // Sticky nav state
    if (window.scrollY > 50) {
      navbar.classList.add("scrolled");
    } else {
      navbar.classList.remove("scrolled");
    }

    // Scroll active link highlight
    let currentSectionId = "";
    sections.forEach(section => {
      const sectionTop = section.offsetTop - 120;
      if (window.scrollY >= sectionTop) {
        currentSectionId = section.getAttribute("id");
      }
    });

    navLinks.forEach(link => {
      link.classList.remove("active");
      if (link.getAttribute("href") === `#${currentSectionId}`) {
        link.classList.add("active");
      }
    });
  });

  // Mobile navigation collapsible panel toggles
  const navToggle = document.querySelector(".nav-toggle");
  const navLinksList = document.querySelector(".nav-links");

  if (navToggle) {
    navToggle.addEventListener("click", () => {
      navLinksList.classList.toggle("active");
      const isActive = navLinksList.classList.contains("active");
      navToggle.innerHTML = isActive ? "&#10005;" : "&#9776;";
      navToggle.setAttribute("aria-expanded", isActive ? "true" : "false");
    });
  }

  navLinks.forEach(link => {
    link.addEventListener("click", () => {
      navLinksList.classList.remove("active");
      if (navToggle) {
        navToggle.innerHTML = "&#9776;";
        navToggle.setAttribute("aria-expanded", "false");
      }
    });
  });

  // 4. Scroll Reveal Intersection Observer
  const revealElements = document.querySelectorAll(".reveal");
  const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add("active");
        
        // Populate skill bar sizes when skill section card slides in
        if (entry.target.classList.contains("skill-card")) {
          const bar = entry.target.querySelector(".skill-progress-bar");
          if (bar) {
            const width = bar.getAttribute("data-width");
            bar.style.width = width;
          }
        }
      }
    });
  }, {
    threshold: 0.15,
    rootMargin: "0px 0px -50px 0px"
  });
  revealElements.forEach(el => revealObserver.observe(el));

  // 5. Project Filters Switcher
  const filterButtons = document.querySelectorAll(".filter-btn");
  const projectCards = document.querySelectorAll(".project-card");

  filterButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      filterButtons.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");

      const filterValue = btn.getAttribute("data-filter");

      projectCards.forEach(card => {
        card.style.transform = "scale(0.95)";
        card.style.opacity = "0";
        
        setTimeout(() => {
          if (filterValue === "all" || card.getAttribute("data-category") === filterValue) {
            card.classList.remove("hidden");
            setTimeout(() => {
              card.style.transform = "scale(1)";
              card.style.opacity = "1";
            }, 50);
          } else {
            card.classList.add("hidden");
          }
        }, 200);
      });
    });
  });

  // 6. Modals Setup (Projects & Certifications)
  initProjectModal();
  initCertModal();

  // 7. GitHub Real-Time API Dashboard Sync
  fetchGitHubDashboardData();
});

// --- Typewriter Rotation Logic ---
function initTypewriter() {
  const words = ["Data Analyst", "BI Analyst", "Reporting Analyst", "SQL Developer"];
  const typingElement = document.querySelector(".hero-typing");
  if (!typingElement) return;

  let wordIndex = 0;
  let charIndex = words[0].length;
  let isDeleting = true;
  let typingSpeed = 1500; // Hold initial text "Data Analyst" before deleting

  function type() {
    const currentWord = words[wordIndex];
    
    if (isDeleting) {
      typingElement.textContent = currentWord.substring(0, charIndex - 1);
      charIndex--;
      typingSpeed = 50;
    } else {
      typingElement.textContent = currentWord.substring(0, charIndex + 1);
      charIndex++;
      typingSpeed = 100;
    }

    if (!isDeleting && charIndex === currentWord.length) {
      isDeleting = true;
      typingSpeed = 1500; // End word hold
    } else if (isDeleting && charIndex === 0) {
      isDeleting = false;
      wordIndex = (wordIndex + 1) % words.length;
      typingSpeed = 400; // Next word pre-hold
    }

    setTimeout(type, typingSpeed);
  }

  setTimeout(type, typingSpeed);
}

// Global keyboard focus tracker for accessibility
let activeTriggerElement = null;

// --- Project Modals ---
function initProjectModal() {
  const modal = document.getElementById("project-modal");
  const modalClose = modal ? modal.querySelector(".modal-close") : null;
  const modalTabButtons = modal ? modal.querySelectorAll(".modal-tab-btn") : [];
  const modalTabContents = modal ? modal.querySelectorAll(".modal-tab-content") : [];
  
  if (!modal) return;

  // Open triggers
  const detailButtons = document.querySelectorAll(".project-btn-details");
  detailButtons.forEach(btn => {
    btn.addEventListener("click", (e) => {
      activeTriggerElement = document.activeElement;
      const card = e.target.closest(".project-card");
      const projectId = card.getAttribute("data-project-id");
      populateProjectModal(projectId);
      
      // Default to first tab
      modalTabButtons.forEach(btn => btn.classList.remove("active"));
      modalTabButtons[0].classList.add("active");
      modalTabContents.forEach(c => c.classList.remove("active"));
      modalTabContents[0].classList.add("active");

      modal.classList.add("active");
      document.body.style.overflow = "hidden";
      if (modalClose) setTimeout(() => modalClose.focus(), 50);
    });
  });

  // Close triggers
  if (modalClose) modalClose.addEventListener("click", closeModal);
  modal.addEventListener("click", (e) => {
    if (e.target === modal) closeModal();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && modal.classList.contains("active")) closeModal();
  });

  function closeModal() {
    modal.classList.remove("active");
    document.body.style.overflow = "";
    if (activeTriggerElement) {
      activeTriggerElement.focus();
      activeTriggerElement = null;
    }
  }

  // Tab switcher links
  modalTabButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      modalTabButtons.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");

      const targetTab = btn.getAttribute("data-tab");
      modalTabContents.forEach(content => {
        content.classList.remove("active");
        if (content.getAttribute("id") === `tab-${targetTab}`) {
          content.classList.add("active");
        }
      });
    });
  });
}

function populateProjectModal(projectId) {
  const data = PROJECTS_DATA[projectId];
  if (!data) return;

  document.getElementById("modal-project-title").textContent = data.title;
  
  const tagsContainer = document.getElementById("modal-project-tags");
  tagsContainer.innerHTML = "";
  data.tags.forEach(tag => {
    const span = document.createElement("span");
    span.className = "modal-tag";
    span.textContent = tag;
    tagsContainer.appendChild(span);
  });

  // Tab 1: Overview
  document.getElementById("modal-desc").textContent = data.description;
  const metricsBody = document.getElementById("modal-metrics-body");
  metricsBody.innerHTML = "";
  data.metrics.forEach(m => {
    const tr = document.createElement("tr");
    tr.innerHTML = `<td>${m.name}</td><td><strong>${m.value}</strong></td>`;
    metricsBody.appendChild(tr);
  });

  // Tab 2: Insights
  const insightsGrid = document.getElementById("modal-insights-grid");
  insightsGrid.innerHTML = "";
  data.insights.forEach((insight, idx) => {
    const card = document.createElement("div");
    card.className = `modal-insight-card ${idx % 2 === 1 ? 'warning-insight' : ''}`;
    card.innerHTML = `
      <div class="modal-insight-title">${insight.title}</div>
      <div class="modal-insight-desc">${insight.desc}</div>
    `;
    insightsGrid.appendChild(card);
  });

  // Tab 3: Code Snippets
  document.getElementById("modal-code-title").textContent = data.codeTitle;
  document.getElementById("modal-code-block").textContent = data.code;

  // Code repository link target
  const githubBtn = document.getElementById("modal-github-btn");
  if (projectId === "hr-analytics-dashboard") {
    githubBtn.href = "https://github.com/murulipachar/HR-Analytics-Dashboard";
  } else {
    githubBtn.href = `https://github.com/murulipachar/${projectId}`;
  }
}

/// --- Certifications Modal ---
function initCertModal() {
  const certModal = document.getElementById("cert-modal");
  const modalClose = certModal ? certModal.querySelector(".modal-close") : null;
  
  if (!certModal) return;

  const certCards = document.querySelectorAll(".cert-card");
  certCards.forEach(card => {
    const triggerOpen = () => {
      activeTriggerElement = card;
      const certId = card.getAttribute("data-cert-id");
      populateCertModal(certId);
      certModal.classList.add("active");
      document.body.style.overflow = "hidden";
      if (modalClose) setTimeout(() => modalClose.focus(), 50);
    };

    card.addEventListener("click", triggerOpen);
    card.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        triggerOpen();
      }
    });
  });

  if (modalClose) modalClose.addEventListener("click", closeCertModal);
  certModal.addEventListener("click", (e) => {
    if (e.target === certModal) closeCertModal();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && certModal.classList.contains("active")) closeCertModal();
  });

  function closeCertModal() {
    certModal.classList.remove("active");
    document.body.style.overflow = "";
    if (activeTriggerElement) {
      activeTriggerElement.focus();
      activeTriggerElement = null;
    }
  }
}

function populateCertModal(certId) {
  const data = CERTS_DATA[certId];
  if (!data) return;

  // Render mock certificate look
  document.getElementById("cert-modal-org").textContent = data.issuer.toUpperCase();
  document.getElementById("cert-modal-title").textContent = data.title;
  document.getElementById("cert-modal-recipient").textContent = "MURULI H P";
  document.getElementById("cert-modal-desc").textContent = data.desc;
  
  const dateEl = document.getElementById("cert-modal-date");
  if (dateEl) {
    dateEl.textContent = `Issued: ${data.date}`;
  }

  const sigEl = document.getElementById("cert-modal-signature");
  if (sigEl) {
    sigEl.textContent = `${data.issuer} Verified`;
  }
  
  const skillsContainer = document.getElementById("cert-modal-skills");
  skillsContainer.innerHTML = "";
  data.skills.forEach(s => {
    const span = document.createElement("span");
    span.className = "modal-tag";
    span.style.background = "rgba(139, 92, 246, 0.1)";
    span.style.borderColor = "rgba(139, 92, 246, 0.2)";
    span.style.color = "var(--accent-purple)";
    span.textContent = s;
    skillsContainer.appendChild(span);
  });

  // Verify link configurations
  const verifyBtn = document.getElementById("cert-modal-verify-btn");
  if (data.verifyUrl) {
    verifyBtn.href = data.verifyUrl;
    verifyBtn.style.display = "inline-flex";
  } else {
    verifyBtn.href = "#";
    verifyBtn.style.display = "none";
  }
}

/// --- GitHub API Profile Dashboards Sync ---
function fetchGitHubDashboardData() {
  const username = "murulipachar";

  // Recruiter standard fallback values
  const offlineBackupData = {
    public_repos: 5,
    followers: 4,
    following: 3,
    stars: 11,
    reposList: [
      {
        name: "sql-retail-analytics",
        html_url: "https://github.com/murulipachar/sql-retail-analytics",
        description: "Star Schema SQLite relational database design and analytical queries auditing sales trends and regional performance.",
        stargazers_count: 5,
        forks_count: 2,
        language: "SQL"
      },
      {
        name: "customer-churn-analysis",
        html_url: "https://github.com/murulipachar/customer-churn-analysis",
        description: "Customer behavioral churn profiling using Python (Pandas, Seaborn). Designs exploratory visualization models and risk scoring.",
        stargazers_count: 3,
        forks_count: 0,
        language: "Python"
      },
      {
        name: "superstore-sales-dashboard",
        html_url: "https://github.com/murulipachar/superstore-sales-dashboard",
        description: "Interactive data analytics dashboard using HTML, CSS, JavaScript, and Chart.js to visualize sales and regional metrics.",
        stargazers_count: 2,
        forks_count: 1,
        language: "JavaScript"
      },
      {
        name: "GramaYatri",
        html_url: "https://github.com/murulipachar/GramaYatri",
        description: "Real-time transit location tracking application developed in Kotlin. Utilizes Firebase Realtime Database and Google Maps SDK.",
        stargazers_count: 1,
        forks_count: 0,
        language: "Kotlin"
      }
    ]
  };

  // 1. Fetch Profile Info (repos, followers, following)
  fetch(`https://api.github.com/users/${username}`)
    .then(res => {
      if (!res.ok) throw new Error("Rate limit or connection issue");
      return res.json();
    })
    .then(profile => {
      document.getElementById("github-repos-count").textContent = profile.public_repos !== undefined ? profile.public_repos : offlineBackupData.public_repos;
      document.getElementById("github-followers-count").textContent = profile.followers !== undefined ? profile.followers : offlineBackupData.followers;
      document.getElementById("github-following-count").textContent = profile.following !== undefined ? profile.following : offlineBackupData.following;
    })
    .catch(() => {
      document.getElementById("github-repos-count").textContent = offlineBackupData.public_repos;
      document.getElementById("github-followers-count").textContent = offlineBackupData.followers;
      document.getElementById("github-following-count").textContent = offlineBackupData.following;
    });

  // 2. Fetch Repositories for Stars calculation and Grid Injection
  fetch(`https://api.github.com/users/${username}/repos?per_page=100&sort=updated`)
    .then(res => {
      if (!res.ok) throw new Error("Connection failed");
      return res.json();
    })
    .then(repos => {
      if (!repos || !Array.isArray(repos) || repos.length === 0) {
        throw new Error("No repositories found or invalid response");
      }
      
      // Sum stars
      const totalStars = repos.reduce((sum, r) => sum + (r.stargazers_count || 0), 0);
      document.getElementById("github-stars-count").textContent = totalStars;

      // Filter out forks and take top 6 most recently updated repositories
      const recentRepos = repos
        .filter(r => !r.fork)
        .slice(0, 6);

      renderGithubReposGrid(recentRepos);
    })
    .catch(() => {
      document.getElementById("github-stars-count").textContent = offlineBackupData.stars;
      renderGithubReposGrid(offlineBackupData.reposList);
    });
}

function renderGithubReposGrid(repos) {
  const grid = document.getElementById("github-repos-grid");
  if (!grid) return;

  grid.innerHTML = "";
  repos.forEach(repo => {
    const card = document.createElement("div");
    card.className = "github-card glass-card reveal";
    
    // Choose indicator language dot color
    let dotColor = "#3b82f6"; // SQL Blue default
    const lang = (repo.language || "").toLowerCase();
    if (lang.includes("python")) dotColor = "#3572A5";
    else if (lang.includes("javascript") || lang.includes("js")) dotColor = "#f1e05a";
    else if (lang.includes("power") || lang.includes("bi")) dotColor = "#f2c811";
    else if (lang.includes("kotlin") || lang.includes("java")) dotColor = "#A97BFF";
    else if (lang.includes("excel")) dotColor = "#217346";
    else if (lang.includes("html")) dotColor = "#e34c26";
    else if (lang.includes("css")) dotColor = "#563d7c";

    card.innerHTML = `
      <div>
        <div class="github-card-header">
          <div class="github-card-title-wrapper">
            <svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" height="1.1em" width="1.1em" xmlns="http://www.w3.org/2000/svg"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>
            <a href="${repo.html_url}" target="_blank" rel="noopener noreferrer" class="github-card-title">${repo.name}</a>
          </div>
          <a href="${repo.html_url}" target="_blank" rel="noopener noreferrer" class="github-card-link" aria-label="Open Repository Code">
            <svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" height="1.1em" width="1.1em" xmlns="http://www.w3.org/2000/svg"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
          </a>
        </div>
        <p class="github-card-desc">${repo.description || 'Data analytics repository showcase.'}</p>
      </div>
      <div class="github-card-meta">
        <div class="github-card-stats">
          <div class="github-stat">
            <svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 1024 1024" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg"><path d="M908.1 353.1l-253.9-36.9L540.7 86.1c-3.1-6.3-9.5-10.3-16.6-10.3s-13.4 4-16.6 10.3L393.9 316.2l-253.9 36.9c-7 1-12.7 6.1-14.5 12.9-1.8 6.8.2 14.1 5.3 19.2l183.7 179.1-43.4 252.9c-1.2 7 1.7 14 7.4 18.2 5.8 4.2 13.4 4.4 19.4 1.2l227-119.4 227 119.4c2.8 1.5 6 2.2 9.1 2.2 3.6 0 7.2-.9 10.3-2.9 5.8-4.2 8.6-11.2 7.4-18.2l-43.4-252.9 183.7-179.1c5.1-5 7.1-12.4 5.3-19.2-1.9-6.8-7.6-11.9-14.6-13z"></path></svg>
            <span>${repo.stargazers_count}</span>
          </div>
          <div class="github-stat">
            <svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg"><line x1="6" y1="3" x2="6" y2="15"></line><circle cx="18" cy="6" r="3"></circle><circle cx="6" cy="18" r="3"></circle><path d="M18 9a9 9 0 0 1-9 9"></path></svg>
            <span>${repo.forks_count || 0}</span>
          </div>
        </div>
        <div class="github-lang">
          <span class="github-lang-dot" style="background-color: ${dotColor};"></span>
          <span>${repo.language || 'Data'}</span>
        </div>
      </div>
    `;
    grid.appendChild(card);
    
    // Wire scroll reveal triggers on dynamic injection
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add("active");
        }
      });
    }, { threshold: 0.1 });
    observer.observe(card);
  });
}
