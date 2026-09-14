import axiosClient from "./axiosClient";

export const fetchColleges = () => axiosClient.get("/colleges");
