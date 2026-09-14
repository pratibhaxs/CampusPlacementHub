import { createContext, useState, useEffect, useCallback } from "react";
import { useAuth } from "../hooks/useAuth";
import { fetchBookmarks, createBookmark, deleteBookmark } from "../api/bookmarkApi";

export const BookmarksContext = createContext(null);

export function BookmarksProvider({ children }) {
  const { user } = useAuth();
  const [bookmarks, setBookmarks] = useState([]);
  const [loaded, setLoaded] = useState(false);

  const load = useCallback(() => {
    if (user?.role !== "student") {
      setBookmarks([]);
      setLoaded(true);
      return;
    }
    fetchBookmarks().then((res) => {
      setBookmarks(res.data);
      setLoaded(true);
    });
  }, [user]);

  useEffect(() => { load(); }, [load]);

  function findBookmark(targetType, targetId) {
    return bookmarks.find((b) => b.target_type === targetType && b.target_id === targetId);
  }

  function isBookmarked(targetType, targetId) {
    return !!findBookmark(targetType, targetId);
  }

  async function toggleBookmark(targetType, targetId) {
    const existing = findBookmark(targetType, targetId);
    if (existing) {
      await deleteBookmark(existing.id);
      setBookmarks(bookmarks.filter((b) => b.id !== existing.id));
    } else {
      const res = await createBookmark(targetType, targetId);
      setBookmarks([res.data, ...bookmarks]);
    }
  }

  return (
    <BookmarksContext.Provider value={{ bookmarks, loaded, isBookmarked, toggleBookmark, reload: load }}>
      {children}
    </BookmarksContext.Provider>
  );
}
