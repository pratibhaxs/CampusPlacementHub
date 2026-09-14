import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { fetchExperiences, updateExperienceStatus } from "../../api/experienceApi";

export default function ApproveExperiences() {
  const [experiences, setExperiences] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState("pending");

  function load() {
    setLoading(true);
    fetchExperiences({ status: statusFilter }).then((res) => setExperiences(res.data)).finally(() => setLoading(false));
  }

  useEffect(() => { load(); }, [statusFilter]);

  async function handleDecision(id, status) {
    await updateExperienceStatus(id, status);
    load();
  }

  return (
    <div className="page">
      <h2>Approve Experiences</h2>

      <div className="filter-bar">
        <label className="filter-field">
          <span>Status</span>
          <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            <option value="pending">Pending</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
          </select>
        </label>
      </div>

      {loading ? (
        <p>Loading...</p>
      ) : experiences.length === 0 ? (
        <p>No {statusFilter} experiences.</p>
      ) : (
        <table className="admin-table">
          <thead>
            <tr><th>Company</th><th>Role</th><th>College</th><th>Submitted by</th><th>Year</th><th>Actions</th></tr>
          </thead>
          <tbody>
            {experiences.map((e) => (
              <tr key={e.id}>
                <td>{e.company_name}</td>
                <td>{e.role_title}</td>
                <td>{e.college_name}</td>
                <td>{e.user_name}</td>
                <td>{e.placement_year}</td>
                <td>
                  <Link to={`/experiences/${e.id}`}>View</Link>{" | "}
                  {statusFilter !== "approved" && (
                    <button onClick={() => handleDecision(e.id, "approved")} className="secondary-btn">Approve</button>
                  )}{" "}
                  {statusFilter !== "rejected" && (
                    <button onClick={() => handleDecision(e.id, "rejected")} className="danger-btn small">Reject</button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
