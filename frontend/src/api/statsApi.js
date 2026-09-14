import axiosClient from "./axiosClient";

export const fetchCompanyStats = (companyId) => axiosClient.get(`/companies/${companyId}/stats`);
export const fetchCompanyRecommendation = (companyId, roleId) =>
  axiosClient.get(`/companies/${companyId}/recommendation`, { params: roleId ? { role_id: roleId } : {} });
export const fetchAdminStatistics = () => axiosClient.get("/admin/statistics");
