import { useState } from "react";
import { useAuth } from "../../hooks/useAuth";
import { toggleHelpful } from "../../api/experienceApi";

export default function HelpfulButton({ experienceId, initialCount, initialVoted }) {
  const { user } = useAuth();
  const [count, setCount] = useState(initialCount ?? 0);
  const [voted, setVoted] = useState(!!initialVoted);
  const [busy, setBusy] = useState(false);

  if (user?.role !== "student") {
    // still show the count (read-only) for non-students so it's not misleading
    return <span className="helpful-count-static">👍 {count} found this helpful</span>;
  }

  async function handleClick() {
    setBusy(true);
    try {
      const res = await toggleHelpful(experienceId);
      setCount(res.data.helpful_count);
      setVoted(res.data.user_has_voted_helpful);
    } finally {
      setBusy(false);
    }
  }

  return (
    <button type="button" onClick={handleClick} disabled={busy} className={voted ? "helpful-btn voted" : "helpful-btn"}>
      👍 {voted ? "Helpful" : "Mark as helpful"} ({count})
    </button>
  );
}
