import { NavLink, Outlet, useLocation } from "react-router-dom";
import {
  LayoutDashboard,
  FolderSearch,
  Network,
  Users,
  CreditCard,
  Brain,
  BarChart3,
  Bell,
  Search,
  ShieldCheck,
  Sun,
  Moon,
} from "lucide-react";
import ToastStack from "../components/Toast";
import { useTheme } from "../context/ThemeContext";

const navItems = [
  { to: "/dashboard",      label: "Dashboard",       icon: LayoutDashboard },
  { to: "/investigations", label: "Investigations",  icon: FolderSearch },
  { to: "/graph",          label: "Knowledge Graph", icon: Network },
  { to: "/customers",      label: "Customers",       icon: Users },
  { to: "/transactions",   label: "Transactions",    icon: CreditCard },
  { to: "/case-memory",    label: "Case Memory",     icon: Brain },
  { to: "/analytics",      label: "Analytics",       icon: BarChart3 },
];

function pageTitle(pathname: string): string {
  if (pathname.startsWith("/dashboard"))      return "Dashboard";
  if (pathname.startsWith("/investigations")) return "Investigations";
  if (pathname.startsWith("/customers"))      return "Customers";
  if (pathname.startsWith("/transactions"))   return "Transactions";
  if (pathname.startsWith("/graph"))          return "Knowledge Graph";
  if (pathname.startsWith("/case-memory"))    return "Case Memory";
  if (pathname.startsWith("/analytics"))      return "Analytics";
  if (pathname.startsWith("/reports"))        return "Reports";
  if (pathname.startsWith("/settings"))       return "Settings";
  return "Fraud Investigation";
}

export default function AppLayout() {
  const { pathname } = useLocation();
  const { theme, toggleTheme } = useTheme();

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <div className="sidebar-brand-mark">FI</div>
          <div className="sidebar-brand-name">Fraud Investigation</div>
        </div>

        <nav className="sidebar-nav">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  "sidebar-link" + (isActive ? " active" : "")
                }
              >
                <Icon />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </nav>

      </aside>

      <div className="main">
        <header className="topbar">
          <div>
            <div className="topbar-title">{pageTitle(pathname)}</div>
            <div className="topbar-breadcrumb">
              Fraud Investigation / {pageTitle(pathname)}
            </div>
          </div>
          <div className="topbar-spacer" />
          <div className="topbar-search">
            <Search size={14} color="var(--text-3)" />
            <input placeholder="Search cases, customers, transactions…" />
          </div>
          <button className="topbar-icon-btn" aria-label="Notifications">
            <Bell size={16} />
            <span className="dot" />
          </button>
          <button className="topbar-icon-btn" aria-label="Policy">
            <ShieldCheck size={16} />
          </button>
          <button
            className="topbar-icon-btn"
            aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} theme`}
            onClick={toggleTheme}
          >
            {theme === "dark" ? <Sun size={16} /> : <Moon size={16} />}
          </button>
        </header>

        <main className="content">
          <Outlet />
        </main>

        <ToastStack />
      </div>
    </div>
  );
}