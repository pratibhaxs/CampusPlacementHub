import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { fetchReports, resolveReport } from "../../api/reportApi";

export default function Reports() {
  const [reports, setReports] = useState([]);
  const [statusFilter, setStatusFilter] = useState("open");
  const [loading, setLoading] = useState(true);

  function load() {
    setLoading(true);
    fetchReports(statusFilter).then((res) => setReports(res.data)).finally(() => setLoading(false));
  }

  useEffect(() => { load(); }, [statusFilter]);

  async function handleResolve(id) {
    await resolveReport(id, "reviewed");
    load();
  }

  return (
    <div className="page">
      <h2>Reports</h2>

      <div className="filter-bar">
        <label className="filter-field">
          <span>Status</span>
          <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            <option value="open">Open</option>
            <option value="reviewed">Reviewed</option>
          </select>
        </label>
      </div>

      {loading ? (
        <p>Loading...</p>
      ) : reports.length === 0 ? (
        <p>No {statusFilter} reports.</p>
      ) : (
        <table className="admin-table">
          <thead>
            <tr><th>Experience</th><th>Reason</th><th>Reported by</th><th>Actions</th></tr>
          </thead>
          <tbody>
            {reports.map((r) => (
              <tr key={r.id}>
                <td><Link to={`/experiences/${r.experience_id}`}>{r.experience_title || "(deleted)"}</Link></td>
                <td>{r.reason}</td>
                <td>{r.reporter_name}</td>
                <td>
                  {statusFilter === "open" && (
                    <button onClick={() => handleResolve(r.id)} className="secondary-btn">Mark reviewed</button>
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
