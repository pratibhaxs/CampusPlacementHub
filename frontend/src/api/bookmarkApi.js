import axiosClient from "./axiosClient";

export const fetchBookmarks = (targetType) =>
  axiosClient.get("/bookmarks", { params: targetType ? { target_type: targetType } : {} });

export const createBookmark = (targetType, targetId) =>
  axiosClient.post("/bookmarks", { target_type: targetType, target_id: targetId });

export const deleteBookmark = (id) => axiosClient.delete(`/bookmarks/${id}`);
