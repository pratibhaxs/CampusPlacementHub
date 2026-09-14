import axiosClient from "./axiosClient";

export const createReport = (experienceId, reason) =>
  axiosClient.post("/reports", { experience_id: experienceId, reason });

export const fetchReports = (status) =>
  axiosClient.get("/reports", { params: status ? { status } : {} });

export const resolveReport = (id, status = "reviewed") =>
  axiosClient.put(`/reports/${id}`, { status });
