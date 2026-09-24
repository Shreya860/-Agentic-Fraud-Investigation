import { NavLink, Outlet, useLocation } from "react-router-dom";
import {
  LayoutDashboard,
  FolderSearch,
  Users,
  CreditCard,
  Network,
  Brain,
  BarChart3,
  FileText,
  Settings as SettingsIcon,
  Bell,
  Search,
  ShieldCheck,
} from "lucide-react";
import ToastStack from "../components/Toast";

const navItems = [
  { to: "/dashboard",      label: "Dashboard",       icon: LayoutDashboard },
  { to: "/investigations", label: "Investigations",  icon: FolderSearch },
  { to: "/customers",      label: "Customers",       icon: Users },
  { to: "/transactions",   label: "Transactions",    icon: CreditCard },
  { to: "/graph",          label: "Knowledge Graph", icon: Network },
  { to: "/case-memory",    label: "Case Memory",     icon: Brain },
  { to: "/analytics",      label: "Analytics",       icon: BarChart3 },
  { to: "/reports",        label: "Reports",         icon: FileText },
  { to: "/settings",       label: "Settings",        icon: SettingsIcon },
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

        <div className="sidebar-user">
          <div className="sidebar-user-avatar">AK</div>
          <div style={{ minWidth: 0 }}>
            <div className="sidebar-user-name">A. Kapoor</div>
            <div className="sidebar-user-role">Senior Fraud Analyst</div>
          </div>
        </div>
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
        </header>

        <main className="content">
          <Outlet />
        </main>

        <ToastStack />
      </div>
    </div>
  );
}