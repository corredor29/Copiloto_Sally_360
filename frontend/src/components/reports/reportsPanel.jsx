import ReportCard from "./ReportCard";

function ReportsPanel() {
  const reports = [
    {
      id: 1,
      title: "Reporte #001",
      status: "Completado",
      time: "11:35 AM",
      description: "Análisis finalizado correctamente.",
    },
    {
      id: 2,
      title: "Reporte #002",
      status: "Analizando",
      time: "11:42 AM",
      description: "Procesando imágenes del vehículo.",
    },
    {
      id: 3,
      title: "Reporte #003",
      status: "Pendiente",
      time: "11:50 AM",
      description: "Esperando información del agente.",
    },
    {
      id: 4,
      title: "Reporte #004",
      status: "Error",
      time: "12:03 PM",
      description: "No fue posible analizar el video.",
    },
  ];

  return (
    <div className="bg-white rounded-2xl shadow-lg p-6">

      <div className="flex justify-between items-center mb-8">

        <div>
          <h2 className="text-2xl font-bold text-gray-800">
            📄 Reportes
          </h2>

          <p className="text-gray-500">
            Últimos análisis realizados por Sally AI
          </p>
        </div>

        <button className="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2 rounded-lg transition">
          Actualizar
        </button>

      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-2 gap-6">

        {reports.map((report) => (
          <ReportCard
            key={report.id}
            title={report.title}
            status={report.status}
            time={report.time}
            description={report.description}
          />
        ))}

      </div>

    </div>
  );
}

export default ReportsPanel;