import { useState, useEffect, Fragment } from "react";
import { fetchCompanies, createCompany, deleteCompany, addRole, deleteRole, fetchCompanyDetail } from "../../api/companyApi";

export default function ManageCompanies() {
  const [companies, setCompanies] = useState([]);
  const [form, setForm] = useState({ name: "", description: "" });
  const [error, setError] = useState("");
  const [expandedId, setExpandedId] = useState(null);
  const [expandedDetail, setExpandedDetail] = useState(null);
  const [roleTitle, setRoleTitle] = useState("");

  function loadCompanies() {
    fetchCompanies().then((res) => setCompanies(res.data));
  }

  useEffect(() => { loadCompanies(); }, []);

  async function handleCreate(e) {
    e.preventDefault();
    setError("");
    try {
      await createCompany(form);
      setForm({ name: "", description: "" });
      loadCompanies();
    } catch (err) {
      setError(err.response?.data?.error || "Could not create company.");
    }
  }

  async function handleDelete(id) {
    if (!window.confirm("Delete this company and all its roles?")) return;
    await deleteCompany(id);
    loadCompanies();
    if (expandedId === id) setExpandedId(null);
  }

  async function toggleExpand(id) {
    if (expandedId === id) {
      setExpandedId(null);
      return;
    }
    setExpandedId(id);
    const res = await fetchCompanyDetail(id);
    setExpandedDetail(res.data);
  }

  async function handleAddRole(companyId) {
    if (!roleTitle.trim()) return;
    await addRole(companyId, roleTitle.trim());
    setRoleTitle("");
    const res = await fetchCompanyDetail(companyId);
    setExpandedDetail(res.data);
    loadCompanies();
  }

  async function handleDeleteRole(roleId, companyId) {
    await deleteRole(roleId);
    const res = await fetchCompanyDetail(companyId);
    setExpandedDetail(res.data);
  }

  return (
    <div className="page">
      <h2>Manage Companies</h2>

      <form onSubmit={handleCreate} className="inline-form">
        {error && <p className="form-error">{error}</p>}
        <input
          type="text"
          placeholder="Company name"
          value={form.name}
          onChange={(e) => setForm({ ...form, name: e.target.value })}
          required
        />
        <input
          type="text"
          placeholder="Description (optional)"
          value={form.description}
          onChange={(e) => setForm({ ...form, description: e.target.value })}
        />
        <button type="submit">Add Company</button>
      </form>

      <table className="admin-table">
        <thead>
          <tr><th>Name</th><th>Roles</th><th>Actions</th></tr>
        </thead>
        <tbody>
          {companies.map((c) => (
            <Fragment key={c.id}>
              <tr>
                <td>{c.name}</td>
                <td>
                  <button onClick={() => toggleExpand(c.id)}>
                    {expandedId === c.id ? "Hide roles" : "Manage roles"}
                  </button>
                </td>
                <td>
                  <button onClick={() => handleDelete(c.id)} className="danger-btn">Delete</button>
                </td>
              </tr>
              {expandedId === c.id && expandedDetail && (
                <tr>
                  <td colSpan={3}>
                    <ul>
                      {expandedDetail.roles.map((r) => (
                        <li key={r.id}>
                          {r.title}{" "}
                          <button onClick={() => handleDeleteRole(r.id, c.id)} className="danger-btn small">Remove</button>
                        </li>
                      ))}
                    </ul>
                    <input
                      type="text"
                      placeholder="New role title"
                      value={roleTitle}
                      onChange={(e) => setRoleTitle(e.target.value)}
                    />
                    <button onClick={() => handleAddRole(c.id)}>Add Role</button>
                  </td>
                </tr>
              )}
            </Fragment>
          ))}
        </tbody>
      </table>
    </div>
  );
}
