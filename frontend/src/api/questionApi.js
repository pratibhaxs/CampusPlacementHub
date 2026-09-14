import axiosClient from "./axiosClient";

export const fetchQuestions = (filters = {}) => {
  const params = Object.fromEntries(
    Object.entries(filters).filter(([, v]) => v !== "" && v !== undefined && v !== null)
  );
  return axiosClient.get("/questions", { params });
};

export const fetchFrequentTopics = (companyId, limit = 10) => {
  const params = { limit };
  if (companyId) params.company_id = companyId;
  return axiosClient.get("/questions/frequent", { params });
};
