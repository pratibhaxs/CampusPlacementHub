import { useNavigate } from "react-router-dom";
import ExperienceForm from "../../components/experience/ExperienceForm";
import { submitExperience } from "../../api/experienceApi";
import { useAuth } from "../../hooks/useAuth";

export default function SubmitExperience() {
  const navigate = useNavigate();
  const { user } = useAuth();

  async function handleSubmit(payload) {
    const res = await submitExperience(payload);
    navigate(`/experiences/${res.data.id}`);
  }

  return (
    <div className="page">
      <h2>Submit a Placement Experience</h2>
      <p className="hint">Your submission will be reviewed by an admin before it appears publicly.</p>
      <ExperienceForm defaultCollegeId={user?.college_id} onSubmit={handleSubmit} />
    </div>
  );
}
