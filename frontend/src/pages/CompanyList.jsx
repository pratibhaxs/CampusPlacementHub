import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { fetchCompanies } from "../api/companyApi";

export default function CompanyList() {
  const [companies, setCompanies] = useState([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    // simple debounce so we don't fire a request on every keystroke
    const timer = setTimeout(() => {
      fetchCompanies(search)
        .then((res) => setCompanies(res.data))
        .finally(() => setLoading(false));
    }, 300);
    return () => clearTimeout(timer);
  }, [search]);

  return (
    <div className="page">
      <h2>Browse Companies</h2>
      <input
        type="text"
        placeholder="Search by company name..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="search-input"
      />

      {loading ? (
        <p>Loading...</p>
      ) : companies.length === 0 ? (
        <p>No companies found.</p>
      ) : (
        <div className="card-grid">
          {companies.map((c) => (
            <Link to={`/companies/${c.id}`} key={c.id} className="company-card">
              <h3>{c.name}</h3>
              {c.description && <p className="company-desc">{c.description}</p>}
              <p className="company-meta">{c.experience_count} experiences shared</p>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
