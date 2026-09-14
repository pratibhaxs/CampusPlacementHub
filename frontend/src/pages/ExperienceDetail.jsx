import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { fetchExperience } from "../api/experienceApi";
import BookmarkButton from "../components/common/BookmarkButton";
import HelpfulButton from "../components/common/HelpfulButton";
import ReportButton from "../components/common/ReportButton";

export default function ExperienceDetail() {
  const { id } = useParams();
  const [experience, setExperience] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchExperience(id)
      .then((res) => setExperience(res.data))
      .catch((err) => setError(err.response?.data?.error || "Could not load this experience."));
  }, [id]);

  if (error) return <div className="page"><p className="form-error">{error}</p></div>;
  if (!experience) return <div className="page"><p>Loading...</p></div>;

  return (
    <div className="page">
      <Link to={`/companies/${experience.company_id}`}>&larr; Back to {experience.company_name}</Link>

      <h2>{experience.company_name} — {experience.role_title} <BookmarkButton targetType="experience" targetId={Number(id)} /></h2>
      <p className="company-meta">
        {experience.college_name} &middot; Branch: {experience.branch || "—"} &middot;
        Placement year: {experience.placement_year} &middot;
        {experience.selected ? " Selected ✅" : " Not selected"}
        {experience.package && ` · Package: ${experience.package}`}
      </p>
      {experience.status !== "approved" && (
        <p className="hint">Status: <strong>{experience.status}</strong> — only visible to you and admins until approved.</p>
      )}

      <h3>Recruitment Process</h3>
      {experience.rounds.map((round) => (
        <div key={round.id} className="round-block">
          <h4>Round {round.round_number} — {round.round_type} {round.difficulty && <em>({round.difficulty})</em>}</h4>
          {round.description && <p>{round.description}</p>}
          {round.questions.length > 0 && (
            <ul>
              {round.questions.map((q) => (
                <li key={q.id}>
                  {q.question_text}
                  {q.topic && <span className="company-meta"> — {q.topic}</span>}
                </li>
              ))}
            </ul>
          )}
        </div>
      ))}

      <h3>Candidate's Overall Experience</h3>
      <p>{experience.overall_experience || "—"}</p>

      <h3>Preparation Tips</h3>
      <p>{experience.preparation_tips || "—"}</p>

      <h3>Additional Advice</h3>
      <p>{experience.additional_advice || "—"}</p>

      <p className="company-meta">Shared by {experience.user_name}</p>

      <div className="experience-actions">
        <HelpfulButton
          experienceId={Number(id)}
          initialCount={experience.helpful_count}
          initialVoted={experience.user_has_voted_helpful}
        />
        <ReportButton experienceId={Number(id)} />
      </div>
    </div>
  );
}
