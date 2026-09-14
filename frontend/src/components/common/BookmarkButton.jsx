import { useState } from "react";
import { useAuth } from "../../hooks/useAuth";
import { useBookmarks } from "../../hooks/useBookmarks";

export default function BookmarkButton({ targetType, targetId }) {
  const { user } = useAuth();
  const { isBookmarked, toggleBookmark } = useBookmarks();
  const [busy, setBusy] = useState(false);

  if (user?.role !== "student") return null; // bookmarking is a student-only feature, per spec

  const saved = isBookmarked(targetType, targetId);

  async function handleClick() {
    setBusy(true);
    try {
      await toggleBookmark(targetType, targetId);
    } finally {
      setBusy(false);
    }
  }

  return (
    <button
      type="button"
      onClick={handleClick}
      disabled={busy}
      className={saved ? "bookmark-btn saved" : "bookmark-btn"}
      title={saved ? "Remove from saved" : "Save this"}
    >
      {saved ? "★ Saved" : "☆ Save"}
    </button>
  );
}
