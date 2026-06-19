function ReportCard({ title, status, time, description }) {
  const statusStyle = {
    Completado: {
      color: "text-green-600",
      bg: "bg-green-100",
      icon: "✅",
    },
    Analizando: {
      color: "text-blue-600",
      bg: "bg-blue-100",
      icon: "🤖",
    },
    Pendiente: {
      color: "text-yellow-600",
      bg: "bg-yellow-100",
      icon: "⏳",
    },
    Error: {
      color: "text-red-600",
      bg: "bg-red-100",
      icon: "❌",
    },
  };

  const current = statusStyle[status] || {
    color: "text-gray-600",
    bg: "bg-gray-100",
    icon: "📄",
  };

  return (
    <div className="bg-white rounded-2xl shadow-md border border-gray-200 p-5 hover:shadow-xl hover:-translate-y-1 transition-all duration-300">

      <div className="flex justify-between items-start">

        <div>
          <h2 className="text-lg font-bold text-gray-800">
            {title}
          </h2>

          <p className="text-sm text-gray-500 mt-1">
            {description}
          </p>
        </div>

        <span
          className={`px-3 py-1 rounded-full text-sm font-semibold ${current.bg} ${current.color}`}
        >
          {current.icon} {status}
        </span>

      </div>

      <div className="mt-5 flex justify-between items-center">

        <span className="text-gray-400 text-sm">
          🕒 {time}
        </span>

        <button
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition"
        >
          Ver
        </button>

      </div>

    </div>
  );
}

export default ReportCard;