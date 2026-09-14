import { useState, useEffect } from "react";
import { fetchFrequentTopics } from "../../api/questionApi";

export default function FrequentTopicsList({ companyId, limit = 5 }) {
  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetchFrequentTopics(companyId, limit)
      .then((res) => setTopics(res.data))
      .finally(() => setLoading(false));
  }, [companyId, limit]);

  if (loading) return <p className="hint">Loading...</p>;
  if (topics.length === 0) return <p className="hint">Not enough approved experiences yet to show trends.</p>;

  return (
    <ol className="topic-list">
      {topics.map((t) => (
        <li key={t.topic}>
          <span className="topic-name">{t.topic}</span>
          <span className="topic-count">{t.count} report{t.count !== 1 ? "s" : ""}</span>
        </li>
      ))}
    </ol>
  );
}
