function AgentStatus({ status }) {
  const statusConfig = {
    Online: {
      color: "text-green-600",
      bg: "bg-green-100",
      dot: "bg-green-500",
      message: "El agente está funcionando correctamente.",
    },

    Analizando: {
      color: "text-blue-600",
      bg: "bg-blue-100",
      dot: "bg-blue-500",
      message: "Procesando información en tiempo real.",
    },

    Esperando: {
      color: "text-yellow-600",
      bg: "bg-yellow-100",
      dot: "bg-yellow-500",
      message: "Esperando una nueva tarea.",
    },

    Error: {
      color: "text-red-600",
      bg: "bg-red-100",
      dot: "bg-red-500",
      message: "Se produjo un error durante el análisis.",
    },
  };

  const current = statusConfig[status] || {
    color: "text-gray-600",
    bg: "bg-gray-100",
    dot: "bg-gray-500",
    message: "Estado desconocido.",
  };

  return (
    <div className="bg-white rounded-2xl shadow-lg p-6">

      <h2 className="text-xl font-bold text-gray-800 mb-5">
        🤖 Estado del Agente
      </h2>

      <div className="flex items-center gap-4">

        <div
          className={`w-5 h-5 rounded-full animate-pulse ${current.dot}`}
        ></div>

        <div>

          <span
            className={`px-3 py-1 rounded-full font-semibold ${current.bg} ${current.color}`}
          >
            {status}
          </span>

          <p className="text-gray-500 mt-2">
            {current.message}
          </p>

        </div>

      </div>

    </div>
  );
}

export default AgentStatus;