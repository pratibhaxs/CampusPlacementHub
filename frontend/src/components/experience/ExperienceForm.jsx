import { useState, useEffect } from "react";
import { fetchCompanies, fetchCompanyDetail } from "../../api/companyApi";
import { fetchColleges } from "../../api/collegeApi";

const CATEGORIES = ["Aptitude", "Coding", "DSA", "OOP", "DBMS", "Operating Systems",
  "Computer Networks", "Python", "Java", "JavaScript", "HR", "Behavioral", "Other"];
const DIFFICULTIES = ["easy", "medium", "hard"];

const emptyQuestion = () => ({ question_text: "", category: "", topic: "", difficulty: "medium" });
const emptyRound = (n) => ({ round_number: n, round_type: "", description: "", difficulty: "medium", questions: [emptyQuestion()] });

function blankForm(defaultCollegeId) {
  return {
    company_id: "",
    role_id: "",
    college_id: defaultCollegeId || "",
    branch: "",
    graduation_year: "",
    placement_year: "",
    package: "",
    rounds: [emptyRound(1)],
    overall_experience: "",
    preparation_tips: "",
    additional_advice: "",
    selected: false,
  };
}

/**
 * Reusable structured form for both "submit new experience" and "edit experience".
 * Pass `initialData` (already in the payload shape) to pre-fill for editing.
 */
export default function ExperienceForm({ initialData, defaultCollegeId, onSubmit, submitLabel = "Submit Experience" }) {
  const [step, setStep] = useState(1);
  const [form, setForm] = useState(initialData || blankForm(defaultCollegeId));
  const [companies, setCompanies] = useState([]);
  const [roles, setRoles] = useState([]);
  const [colleges, setColleges] = useState([]);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchCompanies().then((res) => setCompanies(res.data));
    fetchColleges().then((res) => setColleges(res.data));
  }, []);

  // load roles whenever the selected company changes
  useEffect(() => {
    if (!form.company_id) { setRoles([]); return; }
    fetchCompanyDetail(form.company_id).then((res) => setRoles(res.data.roles));
  }, [form.company_id]);

  function updateField(field, value) {
    setForm({ ...form, [field]: value });
  }

  function updateRound(index, field, value) {
    const rounds = [...form.rounds];
    rounds[index] = { ...rounds[index], [field]: value };
    setForm({ ...form, rounds });
  }

  function addRound() {
    setForm({ ...form, rounds: [...form.rounds, emptyRound(form.rounds.length + 1)] });
  }

  function removeRound(index) {
    const rounds = form.rounds.filter((_, i) => i !== index)
      .map((r, i) => ({ ...r, round_number: i + 1 }));
    setForm({ ...form, rounds });
  }

  function updateQuestion(roundIndex, qIndex, field, value) {
    const rounds = [...form.rounds];
    const questions = [...rounds[roundIndex].questions];
    questions[qIndex] = { ...questions[qIndex], [field]: value };
    rounds[roundIndex] = { ...rounds[roundIndex], questions };
    setForm({ ...form, rounds });
  }

  function addQuestion(roundIndex) {
    const rounds = [...form.rounds];
    rounds[roundIndex] = { ...rounds[roundIndex], questions: [...rounds[roundIndex].questions, emptyQuestion()] };
    setForm({ ...form, rounds });
  }

  function removeQuestion(roundIndex, qIndex) {
    const rounds = [...form.rounds];
    rounds[roundIndex] = { ...rounds[roundIndex], questions: rounds[roundIndex].questions.filter((_, i) => i !== qIndex) };
    setForm({ ...form, rounds });
  }

  function validateStep1() {
    return form.company_id && form.role_id && form.college_id && form.placement_year;
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      const payload = {
        ...form,
        company_id: Number(form.company_id),
        role_id: Number(form.role_id),
        college_id: Number(form.college_id),
        graduation_year: form.graduation_year ? Number(form.graduation_year) : undefined,
        placement_year: Number(form.placement_year),
        rounds: form.rounds.map((r) => ({
          ...r,
          questions: r.questions.filter((q) => q.question_text.trim() !== ""),
        })),
      };
      await onSubmit(payload);
    } catch (err) {
      const details = err.response?.data?.details;
      setError(details ? JSON.stringify(details) : err.response?.data?.error || "Something went wrong.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="experience-form">
      {error && <p className="form-error">{error}</p>}

      <div className="step-indicator">
        <span className={step === 1 ? "active" : ""}>1. Basic Info</span>
        <span className={step === 2 ? "active" : ""}>2. Recruitment Process</span>
        <span className={step === 3 ? "active" : ""}>3. Final Experience</span>
      </div>

      {step === 1 && (
        <fieldset>
          <legend>Basic Information</legend>
          <label>Company
            <select value={form.company_id} onChange={(e) => updateField("company_id", e.target.value)} required>
              <option value="" disabled>Select company</option>
              {companies.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
          </label>
          <label>Job Role
            <select value={form.role_id} onChange={(e) => updateField("role_id", e.target.value)} required disabled={!form.company_id}>
              <option value="" disabled>Select role</option>
              {roles.map((r) => <option key={r.id} value={r.id}>{r.title}</option>)}
            </select>
          </label>
          {form.company_id && roles.length === 0 && (
            <p className="hint">No roles set up for this company yet — ask an admin to add one first.</p>
          )}
          <label>College
            <select value={form.college_id} onChange={(e) => updateField("college_id", e.target.value)} required>
              <option value="" disabled>Select college</option>
              {colleges.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
          </label>
          <label>Branch
            <input type="text" value={form.branch} onChange={(e) => updateField("branch", e.target.value)} placeholder="e.g. CSE" />
          </label>
          <label>Graduation Year
            <input type="number" value={form.graduation_year} onChange={(e) => updateField("graduation_year", e.target.value)} placeholder="e.g. 2026" />
          </label>
          <label>Placement Year
            <input type="number" value={form.placement_year} onChange={(e) => updateField("placement_year", e.target.value)} required placeholder="e.g. 2026" />
          </label>
          <label>Package (optional)
            <input type="text" value={form.package} onChange={(e) => updateField("package", e.target.value)} placeholder="e.g. 12 LPA" />
          </label>
          <div className="step-nav">
            <button type="button" onClick={() => setStep(2)} disabled={!validateStep1()}>Next: Recruitment Process</button>
          </div>
        </fieldset>
      )}

      {step === 2 && (
        <fieldset>
          <legend>Recruitment Process</legend>
          {form.rounds.map((round, ri) => (
            <div key={ri} className="round-block">
              <div className="round-header">
                <h4>Round {round.round_number}</h4>
                {form.rounds.length > 1 && (
                  <button type="button" onClick={() => removeRound(ri)} className="danger-btn small">Remove round</button>
                )}
              </div>
              <label>Round Type
                <input type="text" value={round.round_type} onChange={(e) => updateRound(ri, "round_type", e.target.value)}
                  placeholder="e.g. Aptitude, Coding, Technical, HR" required />
              </label>
              <label>Round Description
                <textarea value={round.description} onChange={(e) => updateRound(ri, "description", e.target.value)}
                  placeholder="What happened in this round?" rows={2} />
              </label>
              <label>Difficulty
                <select value={round.difficulty} onChange={(e) => updateRound(ri, "difficulty", e.target.value)}>
                  {DIFFICULTIES.map((d) => <option key={d} value={d}>{d}</option>)}
                </select>
              </label>

              <h5>Questions asked in this round</h5>
              {round.questions.map((q, qi) => (
                <div key={qi} className="question-block">
                  <input type="text" value={q.question_text}
                    onChange={(e) => updateQuestion(ri, qi, "question_text", e.target.value)}
                    placeholder="Question text" />
                  <select value={q.category} onChange={(e) => updateQuestion(ri, qi, "category", e.target.value)}>
                    <option value="">Category</option>
                    {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
                  </select>
                  <input type="text" value={q.topic} onChange={(e) => updateQuestion(ri, qi, "topic", e.target.value)}
                    placeholder="Topic (e.g. SQL JOIN)" />
                  <select value={q.difficulty} onChange={(e) => updateQuestion(ri, qi, "difficulty", e.target.value)}>
                    {DIFFICULTIES.map((d) => <option key={d} value={d}>{d}</option>)}
                  </select>
                  {round.questions.length > 1 && (
                    <button type="button" onClick={() => removeQuestion(ri, qi)} className="danger-btn small">&times;</button>
                  )}
                </div>
              ))}
              <button type="button" onClick={() => addQuestion(ri)} className="secondary-btn">+ Add question</button>
            </div>
          ))}
          <button type="button" onClick={addRound} className="secondary-btn">+ Add another round</button>

          <div className="step-nav">
            <button type="button" onClick={() => setStep(1)}>Back</button>
            <button type="button" onClick={() => setStep(3)}>Next: Final Experience</button>
          </div>
        </fieldset>
      )}

      {step === 3 && (
        <fieldset>
          <legend>Final Experience</legend>
          <label>Overall Experience
            <textarea value={form.overall_experience} onChange={(e) => updateField("overall_experience", e.target.value)} rows={4} />
          </label>
          <label>Preparation Tips
            <textarea value={form.preparation_tips} onChange={(e) => updateField("preparation_tips", e.target.value)} rows={3} />
          </label>
          <label>Additional Advice
            <textarea value={form.additional_advice} onChange={(e) => updateField("additional_advice", e.target.value)} rows={3} />
          </label>
          <label className="checkbox-label">
            <input type="checkbox" checked={form.selected} onChange={(e) => updateField("selected", e.target.checked)} />
            I was selected
          </label>

          <div className="step-nav">
            <button type="button" onClick={() => setStep(2)}>Back</button>
            <button type="submit" disabled={submitting}>{submitting ? "Submitting..." : submitLabel}</button>
          </div>
        </fieldset>
      )}
    </form>
  );
}
