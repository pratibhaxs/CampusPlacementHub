import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
import { fetchAdminStatistics } from "../../api/statsApi";

export default function AdminDashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);

  useEffect(() => {
    fetchAdminStatistics().then((res) => setStats(res.data));
  }, []);

  return (
    <div className="page">
      <h2>Welcome, {user?.name}</h2>

      {stats && (
        <div className="stats-cards">
          <div className="stat-card"><span className="stat-value">{stats.total_students}</span><span className="stat-label">Students</span></div>
          <div className="stat-card"><span className="stat-value">{stats.total_alumni}</span><span className="stat-label">Alumni</span></div>
          <div className="stat-card"><span className="stat-value">{stats.total_companies}</span><span className="stat-label">Companies</span></div>
          <div className="stat-card"><span className="stat-value">{stats.pending_experiences}</span><span className="stat-label">Awaiting approval</span></div>
        </div>
      )}

      <div className="dashboard-cards">
        <Link to="/admin/experiences" className="dashboard-card">
          <h3>Approve Experiences</h3>
          <p>{stats ? `${stats.pending_experiences} pending review` : "Review submitted experiences."}</p>
        </Link>
        <Link to="/admin/reports" className="dashboard-card">
          <h3>Reports</h3>
          <p>Review content flagged by students.</p>
        </Link>
        <Link to="/admin/companies" className="dashboard-card">
          <h3>Manage Companies</h3>
          <p>Add companies, roles, and manage the catalog.</p>
        </Link>
        <Link to="/admin/statistics" className="dashboard-card">
          <h3>Platform Statistics</h3>
          <p>Full breakdown with charts.</p>
        </Link>
      </div>
    </div>
  );
}
