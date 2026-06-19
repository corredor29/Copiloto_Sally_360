import api from "../../services/api";

export const getReports = async () => {
  try {
    const response = await api.get("/reports");
    return response.data;
  } catch (error) {
    console.error("Error al obtener los reportes:", error);
    throw error;
  }
};

export const getReportById = async (id) => {
  try {
    const response = await api.get(`/reports/${id}`);
    return response.data;
  } catch (error) {
    console.error("Error al obtener el reporte:", error);
    throw error;
  }
};

export const createReport = async (reportData) => {
  try {
    const response = await api.post("/reports", reportData);
    return response.data;
  } catch (error) {
    console.error("Error al crear el reporte:", error);
    throw error;
  }
};