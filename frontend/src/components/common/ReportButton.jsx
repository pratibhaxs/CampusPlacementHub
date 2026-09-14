import { useState } from "react";
import { useAuth } from "../../hooks/useAuth";
import { createReport } from "../../api/reportApi";

const REASONS = [
  { value: "fake", label: "Fake experience" },
  { value: "inappropriate", label: "Inappropriate content" },
  { value: "spam", label: "Spam" },
  { value: "incorrect", label: "Incorrect information" },
];

export default function ReportButton({ experienceId }) {
  const { user } = useAuth();
  const [open, setOpen] = useState(false);
  const [reason, setReason] = useState("fake");
  const [status, setStatus] = useState(""); // "", "submitting", "done", "error"

  if (user?.role !== "student") return null;

  async function handleSubmit(e) {
    e.preventDefault();
    setStatus("submitting");
    try {
      await createReport(experienceId, reason);
      setStatus("done");
    } catch {
      setStatus("error");
    }
  }

  if (!open) {
    return <button type="button" onClick={() => setOpen(true)} className="report-link">Report this experience</button>;
  }

  return (
    <div className="report-popover">
      {status === "done" ? (
        <p>Thanks — an admin will review this.</p>
      ) : (
        <form onSubmit={handleSubmit}>
          <label>
            Reason
            <select value={reason} onChange={(e) => setReason(e.target.value)}>
              {REASONS.map((r) => <option key={r.value} value={r.value}>{r.label}</option>)}
            </select>
          </label>
          {status === "error" && <p className="form-error">You may have already reported this for this reason.</p>}
          <div className="step-nav">
            <button type="button" onClick={() => setOpen(false)}>Cancel</button>
            <button type="submit" disabled={status === "submitting"}>Submit report</button>
          </div>
        </form>
      )}
    </div>
  );
}
