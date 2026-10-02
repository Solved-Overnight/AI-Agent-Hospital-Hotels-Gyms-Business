import { useEffect, useMemo, useState } from "react";
import "./styles.css";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
const THEME_KEY = "brightsmile_admin_theme";
const PAGE_SIZE = 10;

const THEMES = [
  { id: "oled", label: "OLED" },
  { id: "midnight", label: "Midnight" },
  { id: "pearl", label: "Pearl" },
  { id: "clinical", label: "Clinical" },
];

const NAV_ITEMS = [
  { id: "overview", label: "Overview", icon: "home" },
  { id: "appointments", label: "Appointments", icon: "calendar" },
  { id: "doctors", label: "Doctors", icon: "user" },
  { id: "reports", label: "Reports", icon: "chart" },
  { id: "settings", label: "Settings", icon: "sliders" },
];

/* ---------- Icons (inline SVG, stroke-based) ---------- */

const ICONS = {
  home: <path d="M3 10.5 12 3l9 7.5V20a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z" />,
  calendar: (
    <>
      <rect x="3" y="4.5" width="18" height="16.5" rx="3" />
      <path d="M8 2.5v4M16 2.5v4M3 10h18" />
    </>
  ),
  user: (
    <>
      <circle cx="12" cy="8" r="4" />
      <path d="M4 21c0-4.4 3.6-7 8-7s8 2.6 8 7" />
    </>
  ),
  chart: <path d="M5 20V11M12 20V4M19 20v-6" />,
  sliders: (
    <>
      <path d="M4 7h9M17 7h3M4 17h3M11 17h9" />
      <circle cx="15" cy="7" r="2" />
      <circle cx="9" cy="17" r="2" />
    </>
  ),
  search: (
    <>
      <circle cx="11" cy="11" r="7" />
      <path d="m20 20-3.5-3.5" />
    </>
  ),
  check: (
    <>
      <circle cx="12" cy="12" r="9" />
      <path d="m8 12.5 2.8 2.8L16 9.5" />
    </>
  ),
  close: <path d="M6 6l12 12M18 6 6 18" />,
  chevron: <path d="m9 6 6 6-6 6" />,
  refresh: <path d="M20 12a8 8 0 1 1-2.34-5.66M20 4v5h-5" />,
  smile: (
    <>
      <circle cx="12" cy="12" r="9" />
      <path d="M6.5 13.5c1.4 3 9.6 3 11 0M9 9.5h.01M15 9.5h.01" />
    </>
  ),
  inbox: <path d="M3 13h5l1.5 3h5L16 13h5M5.5 5h13L21 13v6a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1v-6z" />,
  spark: (
    <>
      <path d="m12 3 1.5 5.5L19 10l-5.5 1.5L12 17l-1.5-5.5L5 10l5.5-1.5L12 3Z" />
      <path d="m19 15 .7 2.3L22 18l-2.3.7L19 21l-.7-2.3L16 18l2.3-.7L19 15Z" />
    </>
  ),
  clock: (
    <>
      <circle cx="12" cy="12" r="9" />
      <path d="M12 7v5l3.5 2" />
    </>
  ),
  arrowUp: <path d="M6 15 12 9l6 6M12 9v10" />,
};

function Icon({ name, className = "" }) {
  return (
    <svg className={`icon ${className}`} viewBox="0 0 24 24" aria-hidden="true">
      {ICONS[name]}
    </svg>
  );
}

/* ---------- Helpers ---------- */

function toLocalISODate(date = new Date()) {
  const pad = (n) => String(n).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`;
}

function getGreeting() {
  const hour = new Date().getHours();
  if (hour < 12) return "Good morning";
  if (hour < 18) return "Good afternoon";
  return "Good evening";
}

/* A local, dependency-free Ndot-style 5x7 dot-matrix renderer.
   This deliberately mirrors the rounded-dot lettering in the supplied reference
   instead of relying on a remote font that can fail to load in local builds. */
const NDOT_GLYPHS = {
  A: ["01110","10001","10001","11111","10001","10001","10001"],
  D: ["11110","10001","10001","10001","10001","10001","11110"],
  E: ["11111","10000","10000","11110","10000","10000","11111"],
  F: ["11111","10000","10000","11110","10000","10000","10000"],
  G: ["01111","10000","10000","10111","10001","10001","01111"],
  I: ["11111","00100","00100","00100","00100","00100","11111"],
  M: ["10001","11011","10101","10101","10001","10001","10001"],
  N: ["10001","11001","10101","10011","10001","10001","10001"],
  O: ["01110","10001","10001","10001","10001","10001","01110"],
  R: ["11110","10001","10001","11110","10100","10010","10001"],
  T: ["11111","00100","00100","00100","00100","00100","00100"],
  V: ["10001","10001","10001","10001","10001","01010","00100"],
  Y: ["10001","10001","01010","00100","00100","00100","00100"],
};

function NdotGreeting({ text }) {
  const normalized = String(text).toUpperCase();
  const dot = 5;
  const step = 8;
  const glyphGap = 5;
  const spaceGap = 14;
  const width = normalized.split("").reduce((total, char, index) => {
    const advance = char === " " ? spaceGap : (5 * step + glyphGap);
    return total + advance + (index < normalized.length - 1 ? 0 : 0);
  }, 0);

  let x = 0;
  const dots = [];
  [...normalized].forEach((char, charIndex) => {
    if (char === " ") {
      x += spaceGap;
      return;
    }
    const glyph = NDOT_GLYPHS[char] || NDOT_GLYPHS.O;
    glyph.forEach((row, r) => {
      [...row].forEach((value, c) => {
        if (value === "1") {
          dots.push(
            <circle
              key={`${charIndex}-${r}-${c}`}
              className="ndot-dot"
              cx={x + c * step + dot / 2}
              cy={r * step + dot / 2}
              r={dot / 2}
            />
          );
        }
      });
    });
    x += 5 * step + glyphGap;
  });

  return (
    <svg
      className="ndot-greeting"
      viewBox={`0 0 ${Math.max(width, x)} 61`}
      role="img"
      aria-label={text}
      preserveAspectRatio="xMinYMid meet"
    >
      {dots}
    </svg>
  );
}

function formatDate(dateString) {
  if (!dateString) return "—";
  return new Date(`${dateString}T00:00:00`).toLocaleDateString(undefined, {
    weekday: "short",
    month: "short",
    day: "numeric",
  });
}

function formatDateShort(dateString) {
  if (!dateString) return "—";
  return new Date(`${dateString}T00:00:00`).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
  });
}

function formatDateTime(dateString) {
  if (!dateString) return "—";
  return new Date(dateString).toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function statusLabel(status) {
  if (!status) return "Unknown";
  return status.charAt(0).toUpperCase() + status.slice(1);
}

function getInitials(name = "") {
  return name
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0])
    .join("")
    .toUpperCase();
}

function getPatientColor(name = "") {
  const colors = ["violet", "blue", "green", "orange", "pink"];
  let value = 0;
  for (let i = 0; i < name.length; i++) value += name.charCodeAt(i);
  return colors[value % colors.length];
}

/* ---------- App ---------- */

function App() {
  const [stats, setStats] = useState(null);
  const [appointments, setAppointments] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [doctors, setDoctors] = useState([]);
  const [doctorsLoading, setDoctorsLoading] = useState(false);
  const [doctorsError, setDoctorsError] = useState("");

  const [showDoctorForm, setShowDoctorForm] = useState(false);
  const [editingDoctorId, setEditingDoctorId] = useState(null);

  const [doctorForm, setDoctorForm] = useState({
    name: "",
    specialization: "",
    daily_capacity: 10,
  });

  const [activeView, setActiveView] = useState("overview");

  const [reportFilters, setReportFilters] = useState({
    start_date: "",
    end_date: "",
    doctor_id: "",
    status: "",
    search: "",
  });

  const [reportData, setReportData] = useState([]);
  const [reportLoading, setReportLoading] = useState(false);
  const [reportError, setReportError] = useState("");

  const [settings, setSettings] = useState(null);
  const [settingsLoading, setSettingsLoading] = useState(false);
  const [settingsError, setSettingsError] = useState("");

  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");
  const [dateFilter, setDateFilter] = useState("");
  const [showAll, setShowAll] = useState(false);

  const [selectedAppointment, setSelectedAppointment] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);

  const [theme, setTheme] = useState(() => {
    const saved = localStorage.getItem(THEME_KEY);
    return THEMES.some((item) => item.id === saved) ? saved : "oled";
  });

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem(THEME_KEY, theme);
  }, [theme]);

  useEffect(() => {
    loadSettings();
  }, []);

  useEffect(() => {
    if (!selectedAppointment) return undefined;
    const onKey = (event) => {
      if (event.key === "Escape") setSelectedAppointment(null);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [selectedAppointment]);

  async function loadSettings() {
    try {
      setSettingsLoading(true);
      setSettingsError("");

      const response = await fetch(`${API_URL}/api/admin/settings`);
      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.detail || "Unable to load clinic settings.");
      }

      setSettings(await response.json());
    } catch (err) {
      console.error(err);
      setSettingsError(err.message || "Unable to load clinic settings.");
    } finally {
      setSettingsLoading(false);
    }
  }

  async function loadDashboard() {
    try {
      setLoading(true);
      setError("");

      const [statsResponse, appointmentsResponse] = await Promise.all([
        fetch(`${API_URL}/api/admin/dashboard`),
        fetch(`${API_URL}/api/admin/appointments`),
      ]);

      if (!statsResponse.ok) throw new Error("Unable to load dashboard statistics.");
      if (!appointmentsResponse.ok) throw new Error("Unable to load appointments.");

      setStats(await statsResponse.json());
      setAppointments(await appointmentsResponse.json());
    } catch (err) {
      console.error(err);
      setError(err.message || "Something went wrong while loading the dashboard.");
    } finally {
      setLoading(false);
    }
  }

  async function loadDoctors() {
    try {
      setDoctorsLoading(true);
      setDoctorsError("");

      const response = await fetch(
        `${API_URL}/api/admin/doctors`
      );

      if (!response.ok) {
        const data = await response.json().catch(() => ({}));

        throw new Error(
          data.detail || "Unable to load doctors."
        );
      }

      const data = await response.json();

      setDoctors(data);
    } catch (err) {
      console.error(err);

      setDoctorsError(
        err.message || "Unable to load doctors."
      );
    } finally {
      setDoctorsLoading(false);
    }
  }

  async function createDoctor() {
    const payload = {
      name: doctorForm.name.trim(),
      specialization: doctorForm.specialization.trim(),
      daily_capacity: Number(doctorForm.daily_capacity),
    };

    if (!payload.name) {
      throw new Error("Doctor name is required.");
    }

    if (!payload.specialization) {
      throw new Error("Specialization is required.");
    }

    if (payload.daily_capacity <= 0) {
      throw new Error(
        "Daily capacity must be greater than zero."
      );
    }

    const response = await fetch(
      `${API_URL}/api/admin/doctors`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      }
    );

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      throw new Error(
        data.detail || "Unable to create doctor."
      );
    }

    return data;
  }

  async function updateDoctor() {
    if (!editingDoctorId) {
      throw new Error("No doctor selected.");
    }

    const payload = {
      name: doctorForm.name.trim(),
      specialization: doctorForm.specialization.trim(),
      daily_capacity: Number(doctorForm.daily_capacity),
    };

    if (!payload.name) {
      throw new Error("Doctor name is required.");
    }

    if (!payload.specialization) {
      throw new Error("Specialization is required.");
    }

    if (payload.daily_capacity <= 0) {
      throw new Error(
        "Daily capacity must be greater than zero."
      );
    }

    const response = await fetch(
      `${API_URL}/api/admin/doctors/${editingDoctorId}`,
      {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      }
    );

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      throw new Error(
        data.detail || "Unable to update doctor."
      );
    }

    return data;
  }

  async function changeDoctorStatus(doctor) {
    const action = doctor.active
      ? "deactivate"
      : "activate";

    const response = await fetch(
      `${API_URL}/api/admin/doctors/${doctor.id}/${action}`,
      {
        method: "POST",
      }
    );

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      throw new Error(
        data.detail ||
          `Unable to ${action} doctor.`
      );
    }

    return data;
  }

  function resetDoctorForm() {
    setDoctorForm({
      name: "",
      specialization: "",
      daily_capacity: 10,
    });

    setEditingDoctorId(null);
    setShowDoctorForm(false);
  }

  function startCreateDoctor() {
    setDoctorForm({
      name: "",
      specialization: "",
      daily_capacity: 10,
    });

    setEditingDoctorId(null);
    setShowDoctorForm(true);
  }

  function startEditDoctor(doctor) {
    setDoctorForm({
      name: doctor.name,
      specialization: doctor.specialization,
      daily_capacity: doctor.daily_capacity,
    });

    setEditingDoctorId(doctor.id);
    setShowDoctorForm(true);
  }

  async function handleDoctorSubmit(event) {
    event.preventDefault();

    try {
      setDoctorsError("");

      if (editingDoctorId) {
        await updateDoctor();
      } else {
        await createDoctor();
      }

      resetDoctorForm();

      await loadDoctors();
      await loadDashboard();
    } catch (err) {
      console.error(err);

      setDoctorsError(
        err.message || "Unable to save doctor."
      );
    }
  }

  async function handleDoctorStatus(doctor) {
    try {
      setDoctorsError("");

      await changeDoctorStatus(doctor);

      await loadDoctors();
      await loadDashboard();
    } catch (err) {
      console.error(err);

      setDoctorsError(
        err.message ||
          "Unable to change doctor status."
      );
    }
  }

  useEffect(() => {
    loadDashboard();
    loadDoctors();
  }, []);

  const filteredAppointments = useMemo(() => {
    const searchValue = search.trim().toLowerCase();

    return appointments.filter((appointment) => {
      const matchesSearch =
        !searchValue ||
        appointment.patient_name?.toLowerCase().includes(searchValue) ||
        appointment.patient_phone?.toLowerCase().includes(searchValue) ||
        appointment.doctor_name?.toLowerCase().includes(searchValue);

      const matchesStatus = !status || appointment.status === status;
      const matchesDate = !dateFilter || appointment.appointment_date === dateFilter;

      return matchesSearch && matchesStatus && matchesDate;
    });
  }, [appointments, search, status, dateFilter]);

  const visibleAppointments = showAll
    ? filteredAppointments
    : filteredAppointments.slice(0, PAGE_SIZE);

  const todayAppointments = useMemo(() => {
    const today = stats?.today || toLocalISODate();

    return appointments
      .filter((appointment) => appointment.appointment_date === today)
      .sort((a, b) => a.patient_number - b.patient_number);
  }, [appointments, stats]);

  const doctorSummary = useMemo(() => {
    const doctors = {};

    appointments.forEach((appointment) => {
      if (!doctors[appointment.doctor_id]) {
        doctors[appointment.doctor_id] = {
          id: appointment.doctor_id,
          name: appointment.doctor_name,
          specialization: appointment.doctor_specialization,
          count: 0,
          scheduled: 0,
          completed: 0,
        };
      }

      const doctor = doctors[appointment.doctor_id];
      doctor.count += 1;
      if (appointment.status === "scheduled") doctor.scheduled += 1;
      if (appointment.status === "completed") doctor.completed += 1;
    });

    return Object.values(doctors);
  }, [appointments]);


  async function loadReports() {
    try {
      setReportLoading(true);
      setReportError("");

      const params = new URLSearchParams();
      if (reportFilters.start_date) params.set("start_date", reportFilters.start_date);
      if (reportFilters.end_date) params.set("end_date", reportFilters.end_date);
      if (reportFilters.doctor_id) params.set("doctor_id", reportFilters.doctor_id);
      if (reportFilters.status) params.set("status", reportFilters.status);
      if (reportFilters.search) params.set("search", reportFilters.search);

      const query = params.toString();
      const response = await fetch(
        `${API_URL}/api/admin/reports/appointments${query ? `?${query}` : ""}`
      );
      const data = await response.json().catch(() => []);

      if (!response.ok) {
        throw new Error(data.detail || "Unable to load appointment report.");
      }

      setReportData(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error(err);
      setReportError(err.message || "Unable to load appointment report.");
      setReportData([]);
    } finally {
      setReportLoading(false);
    }
  }

  function buildReportQuery() {
    const params = new URLSearchParams();
    if (reportFilters.start_date) params.set("start_date", reportFilters.start_date);
    if (reportFilters.end_date) params.set("end_date", reportFilters.end_date);
    if (reportFilters.doctor_id) params.set("doctor_id", reportFilters.doctor_id);
    if (reportFilters.status) params.set("status", reportFilters.status);
    return params.toString();
  }

  function exportExcel() {
    const query = buildReportQuery();
    window.open(
      `${API_URL}/api/admin/reports/appointments/excel${query ? `?${query}` : ""}`,
      "_blank",
      "noopener,noreferrer"
    );
  }

  function exportPDF() {
    const query = buildReportQuery();
    window.open(
      `${API_URL}/api/admin/reports/appointments/pdf${query ? `?${query}` : ""}`,
      "_blank",
      "noopener,noreferrer"
    );
  }

  function clearReportFilters() {
    setReportFilters({
      start_date: "",
      end_date: "",
      doctor_id: "",
      status: "",
      search: "",
    });
    setReportData([]);
    setReportError("");
  }

  async function updateAppointment(id, action) {
    try {
      setActionLoading(true);

      const response = await fetch(`${API_URL}/api/admin/appointments/${id}/${action}`, {
        method: "POST",
      });
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || `Unable to ${action} appointment.`);
      }

      setSelectedAppointment(null);
      await loadDashboard();
    } catch (err) {
      console.error(err);
      setError(err.message);
    } finally {
      setActionLoading(false);
    }
  }

function handleNavigation(view) {
  setActiveView(view);

  const sectionMap = {
    appointments: "appointments-section",
    doctors: "doctors-section",
    reports: "reports-section",
    settings: "settings-section",
  };

  const sectionId = sectionMap[view];

  if (sectionId) {
    setTimeout(() => {
      document
        .getElementById(sectionId)
        ?.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
    }, 50);
  }
}

  const todayLabel = new Date().toLocaleDateString(undefined, {
    weekday: "long",
    month: "long",
    day: "numeric",
  });

  const todayCounts = {
    scheduled: stats?.today_scheduled ?? 0,
    completed: stats?.today_completed ?? 0,
    cancelled: stats?.today_cancelled ?? 0,
  };
  const todayTotal = todayCounts.scheduled + todayCounts.completed + todayCounts.cancelled;

  const utilization = stats?.today_capacity
    ? Math.min(100, Math.round((todayCounts.scheduled / stats.today_capacity) * 100))
    : 0;

  return (
    <div className={`app-shell view-${activeView}`} data-theme={theme}>
      {/* SIDEBAR */}
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">
            <Icon name="smile" />
          </div>
          <div>
            <div className="brand-name">BrightSmile</div>
            <div className="brand-subtitle">AI Reception</div>
          </div>
        </div>

        <div className="clinic-status">
          <span className="status-pulse" />
          <div>
            <strong>Clinic online</strong>
            <small>All systems operational</small>
          </div>
        </div>

        <nav className="navigation" aria-label="Main">
          <div className="nav-label">Workspace</div>

          {NAV_ITEMS.map((item) => (
            <button
              key={item.id}
              className={`nav-item ${activeView === item.id ? "active" : ""}`}
              aria-current={activeView === item.id ? "page" : undefined}
              onClick={() => handleNavigation(item.id)}
            >
              <Icon name={item.icon} />
              <span>{item.label}</span>

              {item.id === "appointments" && appointments.length > 0 && (
                <span className="nav-count">{appointments.length}</span>
              )}
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="admin-profile">
            <div className="admin-avatar">AD</div>
            <div>
              <strong>Administrator</strong>
              <small>Clinic management</small>
            </div>
          </div>
        </div>
      </aside>

      {/* MAIN */}
      <main className="main">
        <header className="topbar">
          <div className="breadcrumb">
            <span>BrightSmile</span>
            <i>/</i>
            <strong>{statusLabel(activeView)}</strong>
          </div>

          <div className="topbar-actions">
            <div className="live-indicator">
              <span />
              Live
            </div>

            <div className="topbar-date">{todayLabel}</div>

            <div className="theme-switch" role="group" aria-label="Theme">
              {THEMES.map((item) => (
                <button
                  key={item.id}
                  className={`sw-${item.id} ${theme === item.id ? "selected" : ""}`}
                  title={item.label}
                  aria-label={`${item.label} theme`}
                  aria-pressed={theme === item.id}
                  onClick={() => setTheme(item.id)}
                />
              ))}
            </div>

            <button className="top-avatar" title="Administrator" aria-label="Administrator">
              AD
            </button>
          </div>
        </header>

        <div className="content">
          {/* PAGE HEADER */}
          <section className="page-header premium-header">
            <div className="page-header-copy">
              <div className="eyebrow"><span className="eyebrow-dot" /> Clinic overview</div>
              <h1><NdotGreeting text={getGreeting()} /></h1>
              <p>Here's what's happening at the clinic today.</p>
            </div>

            <div className="page-header-actions">
              <div className="header-context">
                <span className="header-context-icon"><Icon name="calendar" /></span>
                <span>Today</span>
                <strong>{formatDateShort(stats?.today || toLocalISODate())}</strong>
              </div>
              <button
                className={`btn btn-primary ${loading ? "spinning" : ""}`}
                onClick={loadDashboard}
                disabled={loading}
              >
                <Icon name="refresh" />
                {loading ? "Refreshing" : "Refresh data"}
              </button>
            </div>
          </section>

          {/* METRICS */}
          <section className="metrics-grid" aria-label="Today's key numbers">
            <MetricCard
              label="Today's patients"
              value={stats?.today_total ?? 0}
              detail={`${todayCounts.scheduled} scheduled`}
              icon="user"
              accent="violet"
            />
            <MetricCard
              label="Completed"
              value={todayCounts.completed}
              detail={`${todayCounts.cancelled} cancelled`}
              icon="check"
              accent="green"
            />
            <MetricCard
              label="Remaining capacity"
              value={stats?.today_remaining_capacity ?? 0}
              detail={`of ${stats?.today_capacity ?? 0} available`}
              icon="chart"
              accent="blue"
            />
            <MetricCard
              label="Upcoming"
              value={stats?.upcoming_scheduled ?? 0}
              detail="Scheduled appointments"
              icon="calendar"
              accent="orange"
            />
          </section>

          {/* PRIMARY WORKSPACE */}
          <section className="dashboard-grid">
            {/* APPOINTMENTS — full width primary workspace */}
            <div className="card appointments-card" id="appointments-section">
              <div className="card-head appointments-head">
                <div className="section-heading">
                  <div className="section-icon"><Icon name="calendar" /></div>
                  <div className="section-heading-copy">
                    <div className="section-kicker">Schedule</div>
                    <div className="section-title-line">
                      <h2>Appointments</h2>
                      <span className="live-chip"><span /> Live</span>
                    </div>
                    <p className="card-sub">
                      {loading
                        ? "Loading…"
                        : `Showing ${visibleAppointments.length} of ${filteredAppointments.length}`}
                    </p>
                  </div>
                </div>

                {filteredAppointments.length > PAGE_SIZE && (
                  <button className="btn" onClick={() => setShowAll((value) => !value)}>
                    {showAll ? "Show less" : `View all (${filteredAppointments.length})`}
                  </button>
                )}
              </div>

              <div className="filters">
                <label className="search-box">
                  <Icon name="search" />
                  <input
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    placeholder="Search patient, phone or doctor"
                    aria-label="Search appointments"
                  />
                </label>

                <input
                  type="date"
                  value={dateFilter}
                  onChange={(e) => setDateFilter(e.target.value)}
                  className="date-input"
                  aria-label="Filter by date"
                />

                <select
                  value={status}
                  onChange={(e) => setStatus(e.target.value)}
                  className="status-select"
                  aria-label="Filter by status"
                >
                  <option value="">All statuses</option>
                  <option value="scheduled">Scheduled</option>
                  <option value="completed">Completed</option>
                  <option value="cancelled">Cancelled</option>
                </select>
              </div>

              {loading ? (
                <LoadingState />
              ) : error ? (
                <ErrorState message={error} retry={loadDashboard} />
              ) : filteredAppointments.length === 0 ? (
                <EmptyState />
              ) : (
                <>
                  <div className="table-head" aria-hidden="true">
                    <span>Patient</span>
                    <span>Doctor</span>
                    <span>Date</span>
                    <span>Status</span>
                    <span />
                  </div>

                  <div className="appointment-list">
                    {visibleAppointments.map((appointment) => (
                      <AppointmentRow
                        key={appointment.id}
                        appointment={appointment}
                        onClick={() => setSelectedAppointment(appointment)}
                      />
                    ))}
                  </div>
                </>
              )}
            </div>

          </section>

          {/* DAILY OPERATIONS */}
          <section className="operations-grid" aria-label="Daily operations">
              {/* TODAY'S STATUS */}
              <div className="card status-card">
                <div className="card-head">
                  <div>
                    <h3>Today's status</h3>
                    <p className="card-sub">{formatDateShort(stats?.today || toLocalISODate())}</p>
                  </div>
                </div>

                <div className="breakdown">
                  <div className="breakdown-total">
                    <strong>{todayTotal}</strong>
                    <span>appointments today</span>
                  </div>

                  <div className="breakdown-bar" role="img" aria-label="Today's appointments by status">
                    {todayTotal > 0 &&
                      ["scheduled", "completed", "cancelled"].map(
                        (key) =>
                          todayCounts[key] > 0 && (
                            <i key={key} className={key} style={{ flex: todayCounts[key] }} />
                          )
                      )}
                  </div>

                  <div className="breakdown-legend">
                    {["scheduled", "completed", "cancelled"].map((key) => (
                      <div key={key}>
                        <span className={`dot-${key}`}>{statusLabel(key)}</span>
                        <strong>{todayCounts[key]}</strong>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* QUEUE */}
              <div className="card queue-card">
                <div className="card-head">
                  <div>
                    <h3>Patient queue</h3>
                    <p className="card-sub">In order of patient number</p>
                  </div>
                </div>

                <div className="queue-list">
                  {todayAppointments.slice(0, 5).map((appointment) => (
                    <button
                      className="queue-item"
                      key={appointment.id}
                      onClick={() => setSelectedAppointment(appointment)}
                    >
                      <span className="queue-number">#{appointment.patient_number}</span>

                      <div className="cell-text" style={{ flex: 1 }}>
                        <strong>{appointment.patient_name}</strong>
                        <small>{appointment.doctor_name}</small>
                      </div>

                      <StatusPill status={appointment.status} />
                    </button>
                  ))}

                  {todayAppointments.length === 0 && (
                    <div className="queue-empty">No appointments today.</div>
                  )}
                </div>
              </div>

              {/* DOCTORS */}
              <div className="card doctor-card">
                <div className="card-head">
                  <div>
                    <h3>Doctor activity</h3>
                    <p className="card-sub">Upcoming appointments per doctor</p>
                  </div>
                </div>

                <div className="doctor-list">
                  {doctorSummary.slice(0, 4).map((doctor) => (
                    <div className="doctor-row" key={doctor.id}>
                      <div className="doctor-avatar">{getInitials(doctor.name)}</div>

                      <div className="doctor-info cell-text">
                        <strong>{doctor.name}</strong>
                        <small>{doctor.specialization}</small>
                      </div>

                      <span className="doctor-count">{doctor.scheduled} scheduled</span>
                    </div>
                  ))}

                  {doctorSummary.length === 0 && (
                    <div className="doctor-empty">No doctor activity yet.</div>
                  )}
                </div>
              </div>
          </section>

          {/* DOCTOR MANAGEMENT */}
          <section
            className="card doctor-management-card"
            id="doctors-section"
          >
            <div className="card-head doctor-management-head">
              <div>
                <div className="section-kicker">
                  Staff
                </div>

                <div className="section-title-line">
                  <h2>Doctors</h2>

                  {!doctorsLoading && (
                    <span className="doctor-count-chip">
                      {doctors.length} {doctors.length === 1 ? "doctor" : "doctors"}
                    </span>
                  )}
                </div>

                <p className="card-sub">
                  Manage doctors and daily appointment capacity.
                </p>
              </div>

              <button
                className="btn btn-primary"
                onClick={startCreateDoctor}
              >
                + Add doctor
              </button>
            </div>

            {doctorsError && (
              <div className="error-state">
                <div>
                  <strong>Doctor management error</strong>
                  <span>{doctorsError}</span>
                </div>
              </div>
            )}

            {doctorsLoading ? (
              <LoadingState />
            ) : doctors.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon">
                  <Icon name="user" />
                </div>

                <strong>No doctors found</strong>

                <span>
                  Add your first doctor to begin managing capacity.
                </span>
              </div>
            ) : (
              <div className="doctor-management-list">
                {doctors.map((doctor) => (
                  <div
                    className="doctor-management-row"
                    key={doctor.id}
                  >
                    <div className="doctor-management-person">
                      <div className="doctor-avatar">
                        {getInitials(doctor.name)}
                      </div>

                      <div className="cell-text">
                        <strong>{doctor.name}</strong>

                        <small>
                          {doctor.specialization}
                        </small>
                      </div>
                    </div>

                    <div className="doctor-management-stat">
                      <span>Daily capacity</span>
                      <strong>
                        {doctor.daily_capacity}
                      </strong>
                    </div>

                    <div className="doctor-management-stat">
                      <span>Today scheduled</span>
                      <strong>
                        {doctor.today_scheduled}
                      </strong>
                    </div>

                    <div className="doctor-management-stat">
                      <span>Remaining</span>
                      <strong>
                        {doctor.today_remaining_capacity}
                      </strong>
                    </div>

                    <div className="doctor-management-status">
                      <span
                        className={
                          doctor.active
                            ? "doctor-active"
                            : "doctor-inactive"
                        }
                      >
                        {doctor.active
                          ? "Active"
                          : "Inactive"}
                      </span>
                    </div>

                    <div className="doctor-management-actions">
                      <button
                        className="btn"
                        onClick={() =>
                          startEditDoctor(doctor)
                        }
                      >
                        Edit
                      </button>

                      <button
                        className="btn"
                        onClick={() =>
                          handleDoctorStatus(doctor)
                        }
                      >
                        {doctor.active
                          ? "Deactivate"
                          : "Activate"}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>

          {showDoctorForm && (
            <div
              className="sheet-overlay"
              onClick={resetDoctorForm}
            >
              <aside
                className="appointment-sheet doctor-form-sheet"
                role="dialog"
                aria-modal="true"
                onClick={(event) =>
                  event.stopPropagation()
                }
              >
                <div className="sheet-top">
                  <div>
                    <small>
                      {editingDoctorId
                        ? "Doctor management"
                        : "New doctor"}
                    </small>

                    <h2>
                      {editingDoctorId
                        ? "Edit doctor"
                        : "Add doctor"}
                    </h2>
                  </div>

                  <button
                    className="close-button"
                    aria-label="Close"
                    onClick={resetDoctorForm}
                  >
                    <Icon name="close" />
                  </button>
                </div>

                <form
                  className="doctor-form"
                  onSubmit={handleDoctorSubmit}
                >
                  <label>
                    <span>Doctor name</span>

                    <input
                      type="text"
                      value={doctorForm.name}
                      onChange={(event) =>
                        setDoctorForm({
                          ...doctorForm,
                          name: event.target.value,
                        })
                      }
                      placeholder="e.g. Dr. Rahman"
                      maxLength={100}
                      required
                    />
                  </label>

                  <label>
                    <span>Specialization</span>

                    <input
                      type="text"
                      value={doctorForm.specialization}
                      onChange={(event) =>
                        setDoctorForm({
                          ...doctorForm,
                          specialization:
                            event.target.value,
                        })
                      }
                      placeholder="e.g. General Dentistry"
                      maxLength={150}
                      required
                    />
                  </label>

                  <label>
                    <span>Daily appointment capacity</span>

                    <input
                      type="number"
                      min="1"
                      value={doctorForm.daily_capacity}
                      onChange={(event) =>
                        setDoctorForm({
                          ...doctorForm,
                          daily_capacity:
                            event.target.value,
                        })
                      }
                      required
                    />
                  </label>

                  <div className="sheet-actions">
                    <button
                      type="submit"
                      className="complete-button"
                    >
                      {editingDoctorId
                        ? "Save changes"
                        : "Create doctor"}
                    </button>

                    <button
                      type="button"
                      className="cancel-button"
                      onClick={resetDoctorForm}
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              </aside>
            </div>
          )}

          {/* REPORTS */}
          <section className="card reports-card" id="reports-section">
            <div className="card-head reports-head">
              <div>
                <div className="section-kicker">Analytics</div>
                <div className="section-title-line">
                  <h2>Appointment reports</h2>
                  {reportData.length > 0 && (
                    <span className="doctor-count-chip">
                      {reportData.length} {reportData.length === 1 ? "record" : "records"}
                    </span>
                  )}
                </div>
                <p className="card-sub">
                  Filter appointment history and export operational reports.
                </p>
              </div>

              <div className="report-actions">
                <button className="btn" onClick={exportExcel} disabled={reportLoading}>
                  Export Excel
                </button>
                <button className="btn" onClick={exportPDF} disabled={reportLoading}>
                  Export PDF
                </button>
              </div>
            </div>

            <div className="report-toolbar">
              <label className="filter-group">
                <span>From</span>
                <input
                  type="date"
                  value={reportFilters.start_date}
                  onChange={(event) =>
                    setReportFilters((current) => ({
                      ...current,
                      start_date: event.target.value,
                    }))
                  }
                />
              </label>

              <label className="filter-group">
                <span>To</span>
                <input
                  type="date"
                  value={reportFilters.end_date}
                  onChange={(event) =>
                    setReportFilters((current) => ({
                      ...current,
                      end_date: event.target.value,
                    }))
                  }
                />
              </label>

              <label className="filter-group">
                <span>Doctor</span>
                <select
                  value={reportFilters.doctor_id}
                  onChange={(event) =>
                    setReportFilters((current) => ({
                      ...current,
                      doctor_id: event.target.value,
                    }))
                  }
                >
                  <option value="">All doctors</option>
                  {doctors.map((doctor) => (
                    <option key={doctor.id} value={doctor.id}>
                      {doctor.name}
                    </option>
                  ))}
                </select>
              </label>

              <label className="filter-group">
                <span>Status</span>
                <select
                  value={reportFilters.status}
                  onChange={(event) =>
                    setReportFilters((current) => ({
                      ...current,
                      status: event.target.value,
                    }))
                  }
                >
                  <option value="">All statuses</option>
                  <option value="scheduled">Scheduled</option>
                  <option value="completed">Completed</option>
                  <option value="cancelled">Cancelled</option>
                </select>
              </label>

              <label className="filter-group report-search">
                <span>Patient</span>
                <input
                  type="search"
                  placeholder="Name or phone"
                  value={reportFilters.search}
                  onChange={(event) =>
                    setReportFilters((current) => ({
                      ...current,
                      search: event.target.value,
                    }))
                  }
                  onKeyDown={(event) => {
                    if (event.key === "Enter") loadReports();
                  }}
                />
              </label>

              <div className="report-filter-actions">
                <button className="btn btn-primary" onClick={loadReports} disabled={reportLoading}>
                  {reportLoading ? "Generating…" : "Generate report"}
                </button>
                <button className="btn" onClick={clearReportFilters} disabled={reportLoading}>
                  Clear
                </button>
              </div>
            </div>

            {reportError && (
              <div className="error-state" role="alert">
                <div>
                  <strong>Report unavailable</strong>
                  <span>{reportError}</span>
                </div>
                <button className="btn" onClick={loadReports}>
                  Try again
                </button>
              </div>
            )}

            {reportLoading ? (
              <LoadingState />
            ) : reportData.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon">
                  <Icon name="chart" />
                </div>
                <strong>No report data</strong>
                <span>
                  Select filters and generate a report to view appointment records.
                </span>
              </div>
            ) : (
              <div className="report-table-wrapper">
                <div className="report-table">
                  <div className="report-table-head">
                    <span>Patient</span>
                    <span>Doctor</span>
                    <span>Date</span>
                    <span>Status</span>
                  </div>

                  {reportData.map((appointment) => (
                    <button
                      className="report-table-row"
                      key={appointment.id}
                      type="button"
                      onClick={() => setSelectedAppointment(appointment)}
                    >
                      <div className="cell-person">
                        <div className={`avatar ${getPatientColor(appointment.patient_name)}`}>
                          {getInitials(appointment.patient_name)}
                        </div>
                        <div className="cell-text">
                          <strong>{appointment.patient_name}</strong>
                          <small>
                            Patient #{appointment.patient_number} · {appointment.patient_phone}
                          </small>
                        </div>
                      </div>

                      <div className="cell-text">
                        <strong>{appointment.doctor_name}</strong>
                        <small>{appointment.doctor_specialization}</small>
                      </div>

                      <div className="cell-date">
                        {formatDate(appointment.appointment_date)}
                      </div>

                      <StatusPill status={appointment.status} />
                    </button>
                  ))}
                </div>
              </div>
            )}
          </section>

          {/* SETTINGS */}
          <section className="card settings-card" id="settings-section">
            <div className="card-head settings-head">
              <div>
                <div className="section-kicker">Configuration</div>
                <div className="section-title-line">
                  <h2>Settings</h2>
                  <span className="doctor-count-chip">Clinic</span>
                </div>
                <p className="card-sub">
                  Clinic information used by the admin workspace and exported reports.
                </p>
              </div>
              <button
                className={`btn ${settingsLoading ? "spinning" : ""}`}
                onClick={loadSettings}
                disabled={settingsLoading}
              >
                <Icon name="refresh" />
                {settingsLoading ? "Refreshing" : "Refresh"}
              </button>
            </div>

            {settingsError ? (
              <div className="error-state" role="alert">
                <div>
                  <strong>Settings unavailable</strong>
                  <span>{settingsError}</span>
                </div>
                <button className="btn" onClick={loadSettings}>Try again</button>
              </div>
            ) : settingsLoading && !settings ? (
              <LoadingState />
            ) : (
              <div className="settings-grid">
                <div className="settings-panel settings-identity">
                  <div className="settings-panel-icon"><Icon name="smile" /></div>
                  <div>
                    <div className="section-kicker">Clinic identity</div>
                    <h3>{settings?.clinic_name || "—"}</h3>
                    <p>{settings?.address || "—"}</p>
                  </div>
                </div>

                <div className="settings-field">
                  <span>Clinic name</span>
                  <strong>{settings?.clinic_name || "—"}</strong>
                </div>

                <div className="settings-field">
                  <span>Address</span>
                  <strong>{settings?.address || "—"}</strong>
                </div>

                <div className="settings-field">
                  <span>Contact</span>
                  <strong>{settings?.contact || "—"}</strong>
                </div>

                <div className="settings-field">
                  <span>Report format</span>
                  <strong>Excel / PDF</strong>
                </div>

                <div className="settings-note">
                  <Icon name="check" />
                  <div>
                    <strong>Centralized clinic values</strong>
                    <span>
                      Clinic identity shown here and in exported PDF reports is read from the backend values file.
                    </span>
                  </div>
                </div>
              </div>
            )}
          </section>

          {/* LOWER SECTION */}
          <section className="bottom-grid">
            <div className="card capacity-card">
              <div className="capacity-visual">
                <div className="capacity-ring" style={{ "--progress": `${utilization}%` }}>
                  <div>
                    <strong>{utilization}%</strong>
                    <span>utilized</span>
                  </div>
                </div>
              </div>

              <div>
                <div className="capacity-copy">
                  <h2>Clinic utilization</h2>
                  <p>Today's appointment capacity across active doctors.</p>
                </div>

                <div className="capacity-meta">
                  <div>
                    <span>Booked</span>
                    <strong>{todayCounts.scheduled}</strong>
                  </div>
                  <div>
                    <span>Available</span>
                    <strong>{stats?.today_remaining_capacity ?? 0}</strong>
                  </div>
                  <div>
                    <span>Total</span>
                    <strong>{stats?.today_capacity ?? 0}</strong>
                  </div>
                </div>
              </div>
            </div>

            <div className="ai-card">
              <div className="ai-shape shape-a" />
              <div className="ai-shape shape-b" />

              <div className="ai-content">
                <div className="ai-badge">
                  <span />
                  Maya AI
                </div>

                <h2>
                  Your digital receptionist
                  <br />
                  is online.
                </h2>

                <p>
                  Maya is handling patient conversations and appointment requests
                  automatically.
                </p>

                <div className="ai-status">
                  <span className="ai-avatar">M</span>
                  <div>
                    <strong>Reception active</strong>
                    <small>Responding to patients</small>
                  </div>
                </div>
              </div>
            </div>
          </section>

          <footer className="footer">
            <span>BrightSmile AI Reception</span>
            <span>Secure clinic workspace</span>
            <span>{new Date().getFullYear()}</span>
          </footer>
        </div>
      </main>

      {/* APPOINTMENT DETAIL DRAWER */}
      {selectedAppointment && (
        <div className="sheet-overlay" onClick={() => setSelectedAppointment(null)}>
          <aside
            className="appointment-sheet"
            role="dialog"
            aria-modal="true"
            aria-label={`Appointment ${selectedAppointment.id}`}
            onClick={(event) => event.stopPropagation()}
          >
            <div className="sheet-top">
              <div>
                <small>Appointment</small>
                <h2>#{selectedAppointment.id}</h2>
              </div>

              <button
                className="close-button"
                aria-label="Close"
                onClick={() => setSelectedAppointment(null)}
              >
                <Icon name="close" />
              </button>
            </div>

            <div className="sheet-patient">
              <div className={`avatar lg ${getPatientColor(selectedAppointment.patient_name)}`}>
                {getInitials(selectedAppointment.patient_name)}
              </div>

              <div>
                <h3>{selectedAppointment.patient_name}</h3>
                <p>Patient #{selectedAppointment.patient_number}</p>
                <StatusPill status={selectedAppointment.status} />
              </div>
            </div>

            <div className="detail-section">
              <h4>Details</h4>

              <DetailRow label="Doctor" value={selectedAppointment.doctor_name} />
              <DetailRow label="Specialization" value={selectedAppointment.doctor_specialization} />
              <DetailRow label="Date" value={formatDate(selectedAppointment.appointment_date)} />
              <DetailRow label="Patient phone" value={selectedAppointment.patient_phone} />

              {selectedAppointment.patient_email && (
                <DetailRow label="Email" value={selectedAppointment.patient_email} />
              )}

              <DetailRow label="Booked" value={formatDateTime(selectedAppointment.created_at)} />
            </div>

            {selectedAppointment.status === "scheduled" && (
              <div className="sheet-actions">
                <button
                  className="complete-button"
                  disabled={actionLoading}
                  onClick={() => updateAppointment(selectedAppointment.id, "complete")}
                >
                  {actionLoading ? "Updating…" : "Mark completed"}
                </button>

                <button
                  className="cancel-button"
                  disabled={actionLoading}
                  onClick={() => updateAppointment(selectedAppointment.id, "cancel")}
                >
                  Cancel appointment
                </button>
              </div>
            )}
          </aside>
        </div>
      )}
    </div>
  );
}

/* ---------- Components ---------- */

function MetricCard({ label, value, detail, icon, accent }) {
  return (
    <div className="metric-card">
      <div className="metric-top">
        <span>{label}</span>
        <div className={`metric-icon ${accent}`}>
          <Icon name={icon} />
        </div>
      </div>

      <div className="metric-value">{value}</div>
      <div className="metric-detail">{detail}</div>
    </div>
  );
}

function StatusPill({ status }) {
  return (
    <div className={`appointment-status ${status}`}>
      <span />
      {statusLabel(status)}
    </div>
  );
}

function AppointmentRow({ appointment, onClick }) {
  const color = getPatientColor(appointment.patient_name);

  return (
    <button className="appointment-row" onClick={onClick}>
      <div className="cell-person">
        <div className={`avatar ${color}`}>{getInitials(appointment.patient_name)}</div>

        <div className="cell-text">
          <strong>{appointment.patient_name}</strong>
          <small>Patient #{appointment.patient_number}</small>
        </div>
      </div>

      <div className="cell-text">
        <strong>{appointment.doctor_name}</strong>
        <small>{appointment.doctor_specialization}</small>
      </div>

      <div className="cell-date">{formatDate(appointment.appointment_date)}</div>

      <StatusPill status={appointment.status} />

      <Icon name="chevron" className="row-arrow" />
    </button>
  );
}

function DetailRow({ label, value }) {
  return (
    <div className="detail-row">
      <span>{label}</span>
      <strong>{value || "—"}</strong>
    </div>
  );
}

function LoadingState() {
  return (
    <div className="loading-state" role="status">
      <div className="loader" />
      <span>Loading clinic activity…</span>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="empty-state">
      <div className="empty-icon">
        <Icon name="inbox" />
      </div>
      <strong>No appointments found</strong>
      <span>Try a different search, date or status.</span>
    </div>
  );
}

function ErrorState({ message, retry }) {
  return (
    <div className="error-state" role="alert">
      <div>
        <strong>Dashboard unavailable</strong>
        <span>{message}</span>
      </div>

      <button className="btn" onClick={retry}>
        Try again
      </button>
    </div>
  );
}


export default App;