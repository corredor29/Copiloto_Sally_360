import api from "../../services/api";

export const runAgent = async () => {
  try {
    const response = await api.post("/agent/run");
    return response.data;
  } catch (error) {
    console.error("Error al ejecutar el agente:", error);
    throw error;
  }
};

export const getAgentStatus = async () => {
  try {
    const response = await api.get("/agent/status");
    return response.data;
  } catch (error) {
    console.error("Error al obtener el estado del agente:", error);
    throw error;
  }
};

export const stopAgent = async () => {
  try {
    const response = await api.post("/agent/stop");
    return response.data;
  } catch (error) {
    console.error("Error al detener el agente:", error);
    throw error;
  }
};