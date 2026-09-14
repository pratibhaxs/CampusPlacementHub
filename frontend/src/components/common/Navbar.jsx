import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";

const LINKS = {
  student: [
    { to: "/student", label: "Dashboard" },
    { to: "/search", label: "Search" },
    { to: "/questions", label: "Questions" },
    { to: "/companies", label: "Companies" },
    { to: "/student/saved", label: "Saved" },
  ],
  alumni: [
    { to: "/alumni", label: "Dashboard" },
    { to: "/alumni/my-experiences", label: "My Experiences" },
    { to: "/alumni/submit-experience", label: "Submit" },
    { to: "/companies", label: "Companies" },
  ],
  admin: [
    { to: "/admin", label: "Dashboard" },
    { to: "/admin/experiences", label: "Approvals" },
    { to: "/admin/reports", label: "Reports" },
    { to: "/admin/companies", label: "Companies" },
    { to: "/admin/statistics", label: "Statistics" },
  ],
};

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);

  if (!user) return null; // Login/Register pages render without a navbar

  const links = LINKS[user.role] || [];

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <nav className="navbar">
      <div className="navbar-inner">
        <Link to={`/${user.role}`} className="navbar-brand">Placement Hub</Link>

        <button className="navbar-toggle" onClick={() => setMenuOpen(!menuOpen)} aria-label="Toggle menu">
          ☰
        </button>

        <div className={menuOpen ? "navbar-links open" : "navbar-links"}>
          {links.map((l) => (
            <Link key={l.to} to={l.to} onClick={() => setMenuOpen(false)}>{l.label}</Link>
          ))}
          <span className="navbar-user">{user.name} ({user.role})</span>
          <button onClick={handleLogout} className="navbar-logout">Log out</button>
        </div>
      </div>
    </nav>
  );
}
