import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
import { fetchMyExperiences } from "../../api/experienceApi";

export default function AlumniDashboard() {
  const { user } = useAuth();
  const [experiences, setExperiences] = useState([]);

  useEffect(() => {
    fetchMyExperiences().then((res) => setExperiences(res.data));
  }, []);

  const pendingCount = experiences.filter((e) => e.status === "pending").length;
  const approvedCount = experiences.filter((e) => e.status === "approved").length;

  return (
    <div className="page">
      <h2>Welcome, {user?.name}</h2>
      <p className="hint">{user?.college_name}{user?.branch && ` · ${user.branch}`}</p>

      <div className="stats-cards">
        <div className="stat-card"><span className="stat-value">{experiences.length}</span><span className="stat-label">Total submitted</span></div>
        <div className="stat-card"><span className="stat-value">{approvedCount}</span><span className="stat-label">Approved</span></div>
        <div className="stat-card"><span className="stat-value">{pendingCount}</span><span className="stat-label">Pending review</span></div>
      </div>

      <div className="dashboard-cards">
        <Link to="/alumni/submit-experience" className="dashboard-card">
          <h3>Submit an Experience</h3>
          <p>Share your placement process to help juniors prepare.</p>
        </Link>
        <Link to="/alumni/my-experiences" className="dashboard-card">
          <h3>My Experiences</h3>
          <p>View, edit, or delete what you've submitted.</p>
        </Link>
        <Link to="/companies" className="dashboard-card">
          <h3>Browse Companies</h3>
          <p>See what other alumni have shared.</p>
        </Link>
      </div>
    </div>
  );
}
