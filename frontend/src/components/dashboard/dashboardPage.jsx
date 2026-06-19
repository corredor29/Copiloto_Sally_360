import AgentPanel from "../agent/AgentPanel";
import ReportsPanel from "../reports/ReportsPanel";

function DashboardPage() {
  return (
    <div className="min-h-screen bg-gray-100">

      <header className="bg-white shadow-md border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-8 py-6 flex justify-between items-center">

          <div>
            <h1 className="text-3xl font-bold text-gray-800">
              🚗 Sally AI Dashboard
            </h1>

            <p className="text-gray-500 mt-1">
              Sistema inteligente de monitoreo y generación de reportes
            </p>
          </div>

          <div className="flex items-center gap-3">
            <div className="w-3 h-3 rounded-full bg-green-500 animate-pulse"></div>

            <span className="text-gray-700 font-medium">
              Sistema Activo
            </span>
          </div>

        </div>
      </header>

      <main className="max-w-7xl mx-auto p-8">

        <div className="grid lg:grid-cols-3 gap-8">

          <div className="lg:col-span-1">
            <AgentPanel />
          </div>

          <div className="lg:col-span-2">
            <ReportsPanel />
          </div>

        </div>

      </main>

    </div>
  );
}

export default DashboardPage;