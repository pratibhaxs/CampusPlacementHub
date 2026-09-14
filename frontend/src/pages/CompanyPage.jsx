import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { fetchCompanyDetail } from "../api/companyApi";
import { fetchExperiences } from "../api/experienceApi";
import FrequentTopicsList from "../components/common/FrequentTopicsList";
import BookmarkButton from "../components/common/BookmarkButton";
import CompanyStatsPanel from "../components/charts/CompanyStatsPanel";
import RecommendationPanel from "../components/charts/RecommendationPanel";

export default function CompanyPage() {
  const { id } = useParams();
  const [company, setCompany] = useState(null);
  const [experiences, setExperiences] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchCompanyDetail(id)
      .then((res) => setCompany(res.data))
      .catch(() => setError("Could not load this company."));
    fetchExperiences({ company_id: id })
      .then((res) => setExperiences(res.data))
      .catch(() => {});
  }, [id]);

  if (error) return <div className="page"><p className="form-error">{error}</p></div>;
  if (!company) return <div className="page"><p>Loading...</p></div>;

  return (
    <div className="page">
      <Link to="/companies">&larr; Back to companies</Link>
      <h2>{company.name} <BookmarkButton targetType="company" targetId={Number(id)} /></h2>
      {company.description && <p>{company.description}</p>}

      <h3>Available Roles</h3>
      {company.roles.length === 0 ? (
        <p><em>No roles added yet.</em></p>
      ) : (
        <ul>
          {company.roles.map((r) => <li key={r.id}>{r.title}</li>)}
        </ul>
      )}

      <h3>🔥 Frequently Asked Topics</h3>
      <FrequentTopicsList companyId={id} limit={5} />

      <h3>Placement Intelligence Dashboard</h3>
      <CompanyStatsPanel companyId={id} />

      <h3>Recommended Preparation</h3>
      <RecommendationPanel companyId={id} roles={company.roles} />

      <h3>Placement Experiences ({company.experience_count})</h3>
      {experiences.length === 0 ? (
        <p><em>No experiences shared for this company yet.</em></p>
      ) : (
        <div className="card-grid">
          {experiences.map((e) => (
            <Link to={`/experiences/${e.id}`} key={e.id} className="company-card">
              <h3>{e.role_title}</h3>
              <p className="company-desc">{e.college_name} &middot; {e.placement_year}</p>
              <p className="company-meta">{e.selected ? "Selected" : "Not selected"}{e.package ? ` · ${e.package}` : ""}</p>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
