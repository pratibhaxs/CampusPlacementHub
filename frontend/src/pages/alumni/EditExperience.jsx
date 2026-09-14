import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import ExperienceForm from "../../components/experience/ExperienceForm";
import { fetchExperience, updateExperience } from "../../api/experienceApi";

export default function EditExperience() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [initialData, setInitialData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchExperience(id)
      .then((res) => {
        const e = res.data;
        setInitialData({
          company_id: e.company_id,
          role_id: e.role_id,
          college_id: e.college_id,
          branch: e.branch || "",
          graduation_year: e.graduation_year || "",
          placement_year: e.placement_year,
          package: e.package || "",
          rounds: e.rounds.map((r) => ({
            round_number: r.round_number,
            round_type: r.round_type,
            description: r.description || "",
            difficulty: r.difficulty || "medium",
            questions: r.questions.length
              ? r.questions.map((q) => ({
                  question_text: q.question_text, category: q.category || "",
                  topic: q.topic || "", difficulty: q.difficulty || "medium",
                }))
              : [{ question_text: "", category: "", topic: "", difficulty: "medium" }],
          })),
          overall_experience: e.overall_experience || "",
          preparation_tips: e.preparation_tips || "",
          additional_advice: e.additional_advice || "",
          selected: e.selected,
        });
      })
      .catch(() => setError("Could not load this experience."));
  }, [id]);

  async function handleSubmit(payload) {
    await updateExperience(id, payload);
    navigate(`/experiences/${id}`);
  }

  if (error) return <div className="page"><p className="form-error">{error}</p></div>;
  if (!initialData) return <div className="page"><p>Loading...</p></div>;

  return (
    <div className="page">
      <h2>Edit Experience</h2>
      <p className="hint">Editing will send this experience back for admin re-approval.</p>
      <ExperienceForm initialData={initialData} onSubmit={handleSubmit} submitLabel="Save Changes" />
    </div>
  );
}
