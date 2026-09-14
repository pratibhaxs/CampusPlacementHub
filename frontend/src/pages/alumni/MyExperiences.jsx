import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { fetchMyExperiences, deleteExperience } from "../../api/experienceApi";

const statusColors = { pending: "#e6a817", approved: "#2f9e44", rejected: "#e5484d" };

export default function MyExperiences() {
  const [experiences, setExperiences] = useState([]);
  const [loading, setLoading] = useState(true);

  function load() {
    setLoading(true);
    fetchMyExperiences().then((res) => setExperiences(res.data)).finally(() => setLoading(false));
  }

  useEffect(() => { load(); }, []);

  async function handleDelete(id) {
    if (!window.confirm("Delete this experience?")) return;
    await deleteExperience(id);
    load();
  }

  if (loading) return <div className="page"><p>Loading...</p></div>;

  return (
    <div className="page">
      <h2>My Experiences</h2>
      <p><Link to="/alumni/submit-experience">+ Submit a new experience</Link></p>

      {experiences.length === 0 ? (
        <p>You haven't submitted any experiences yet.</p>
      ) : (
        <table className="admin-table">
          <thead>
            <tr><th>Company</th><th>Role</th><th>Year</th><th>Status</th><th>Actions</th></tr>
          </thead>
          <tbody>
            {experiences.map((e) => (
              <tr key={e.id}>
                <td>{e.company_name}</td>
                <td>{e.role_title}</td>
                <td>{e.placement_year}</td>
                <td><span style={{ color: statusColors[e.status], fontWeight: 600 }}>{e.status}</span></td>
                <td>
                  <Link to={`/experiences/${e.id}`}>View</Link>{" | "}
                  <Link to={`/alumni/edit-experience/${e.id}`}>Edit</Link>{" | "}
                  <button onClick={() => handleDelete(e.id)} className="danger-btn small">Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
