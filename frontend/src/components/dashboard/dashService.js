import api from "../../services/api";

// Obtener toda la información del dashboard
export const getDashboardData = async () => {
  try {
    const response = await api.get("/dashboard");
    return response.data;
  } catch (error) {
    console.error("Error al obtener la información del dashboard:", error);
    throw error;
  }
};

// Obtener estadísticas del dashboard
export const getDashboardStats = async () => {
  try {
    const response = await api.get("/dashboard/stats");
    return response.data;
  } catch (error) {
    console.error("Error al obtener las estadísticas:", error);
    throw error;
  }
};