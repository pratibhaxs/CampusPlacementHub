import { Link } from "react-router-dom";
import { useBookmarks } from "../../hooks/useBookmarks";

const targetLink = (b) => {
  if (b.target_type === "company") return `/companies/${b.target_id}`;
  if (b.target_type === "experience") return `/experiences/${b.target_id}`;
  if (b.target_type === "question") return `/experiences/${b.preview?.experience_id}`;
  return "#";
};

const typeLabel = { experience: "Experience", question: "Question", company: "Company" };

export default function SavedItems() {
  const { bookmarks, loaded, toggleBookmark } = useBookmarks();

  if (!loaded) return <div className="page"><p>Loading...</p></div>;

  return (
    <div className="page">
      <h2>Saved Items</h2>

      {bookmarks.length === 0 ? (
        <p>You haven't saved anything yet. Look for the ☆ Save button on companies, experiences, and questions.</p>
      ) : (
        <ul className="question-list">
          {bookmarks.map((b) => (
            <li key={b.id} className="question-item">
              <p className="question-text">
                <Link to={targetLink(b)}>{b.preview?.title || "(unavailable)"}</Link>
              </p>
              <p className="company-meta">
                {typeLabel[b.target_type]}{b.preview?.subtitle && ` · ${b.preview.subtitle}`}
              </p>
              <button onClick={() => toggleBookmark(b.target_type, b.target_id)} className="danger-btn small">
                Remove
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
