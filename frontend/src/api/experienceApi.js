import axiosClient from "./axiosClient";

export const submitExperience = (payload) => axiosClient.post("/experiences", payload);
export const updateExperience = (id, payload) => axiosClient.put(`/experiences/${id}`, payload);
export const deleteExperience = (id) => axiosClient.delete(`/experiences/${id}`);
export const fetchExperience = (id) => axiosClient.get(`/experiences/${id}`);
export const fetchExperiences = (filters = {}) => {
  // strip empty-string/undefined values so we don't send useless query params
  const params = Object.fromEntries(
    Object.entries(filters).filter(([, v]) => v !== "" && v !== undefined && v !== null)
  );
  return axiosClient.get("/experiences", { params });
};
export const fetchMyExperiences = () => axiosClient.get("/experiences/mine");
export const updateExperienceStatus = (id, status) =>
  axiosClient.put(`/experiences/${id}/status`, { status });
export const toggleHelpful = (id) => axiosClient.post(`/experiences/${id}/helpful`);
