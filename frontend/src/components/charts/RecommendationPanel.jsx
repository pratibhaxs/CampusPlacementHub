import { useState, useEffect } from "react";
import { fetchCompanyRecommendation } from "../../api/statsApi";

const Stars = ({ count }) => (
  <span className="stars" aria-label={`${count} out of 5`}>
    {"⭐".repeat(count)}{"☆".repeat(5 - count)}
  </span>
);

export default function RecommendationPanel({ companyId, roles }) {
  const [roleId, setRoleId] = useState("");
  const [data, setData] = useState(null);

  useEffect(() => {
    fetchCompanyRecommendation(companyId, roleId || undefined).then((res) => setData(res.data));
  }, [companyId, roleId]);

  if (!data) return <p className="hint">Loading...</p>;

  if (data.based_on === 0) {
    return <p className="hint">Not enough approved experiences yet for a recommendation.</p>;
  }

  return (
    <div className="stats-panel">
      {roles && roles.length > 0 && (
        <label className="filter-field" style={{ marginBottom: "1rem" }}>
          <span>Filter by role</span>
          <select value={roleId} onChange={(e) => setRoleId(e.target.value)}>
            <option value="">All roles</option>
            {roles.map((r) => <option key={r.id} value={r.id}>{r.title}</option>)}
          </select>
        </label>
      )}

      <p className="hint">Based on {data.based_on} approved experience{data.based_on !== 1 ? "s" : ""}.</p>

      <h4>Recommended Preparation</h4>
      {data.recommended_topics.length === 0 ? (
        <p className="hint">No topics reported yet.</p>
      ) : (
        <ul className="recommendation-list">
          {data.recommended_topics.map((t) => (
            <li key={t.topic}>
              <span className="topic-name">{t.topic}</span>
              <Stars count={t.stars} />
            </li>
          ))}
        </ul>
      )}

      <h4>Most Frequently Reported Questions</h4>
      {data.frequent_questions.length === 0 ? (
        <p className="hint">No questions reported yet.</p>
      ) : (
        <ul className="question-list">
          {data.frequent_questions.map((q, i) => (
            <li key={i} className="question-item">
              <p className="question-text">{q.question_text}</p>
              <p className="company-meta">
                {q.category}{q.topic && ` · ${q.topic}`} · reported {q.count} time{q.count !== 1 ? "s" : ""}
              </p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
