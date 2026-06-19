import { useState } from "react";
import AgentStatus from "./AgentStatus";

function AgentPanel() {
  const [status, setStatus] = useState("Online");
  const [progress, setProgress] = useState(0);
  const [running, setRunning] = useState(false);

  const runAgent = () => {
    if (running) return;

    setRunning(true);
    setStatus("Analizando");
    setProgress(0);

    let value = 0;

    const interval = setInterval(() => {
      value += 10;
      setProgress(value);

      if (value >= 100) {
        clearInterval(interval);
        setStatus("Online");
        setRunning(false);
      }
    }, 300);
  };

  return (
    <div className="bg-white rounded-2xl shadow-lg p-6">

      <div className="flex justify-between items-center mb-6">

        <div>
          <h1 className="text-2xl font-bold text-gray-800">
            🤖 Sally AI
          </h1>

          <p className="text-gray-500">
            Copiloto inteligente de monitoreo
          </p>
        </div>

        <button
          onClick={runAgent}
          disabled={running}
          className={`px-6 py-3 rounded-xl text-white font-semibold transition ${
            running
              ? "bg-gray-400 cursor-not-allowed"
              : "bg-blue-600 hover:bg-blue-700"
          }`}
        >
          {running ? "Analizando..." : "Ejecutar Agente"}
        </button>

      </div>

      <AgentStatus status={status} />

      <div className="mt-8">

        <div className="flex justify-between mb-2">

          <span className="font-semibold text-gray-700">
            Progreso
          </span>

          <span className="text-gray-500">
            {progress}%
          </span>

        </div>

        <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">

          <div
            className="bg-blue-600 h-4 rounded-full transition-all duration-300"
            style={{
              width: `${progress}%`,
            }}
          />

        </div>

      </div>

      <div className="grid grid-cols-3 gap-4 mt-8">

        <div className="bg-gray-100 rounded-xl p-4 text-center">

          <p className="text-sm text-gray-500">
            Estado
          </p>

          <h2 className="font-bold mt-2">
            {status}
          </h2>

        </div>

        <div className="bg-gray-100 rounded-xl p-4 text-center">

          <p className="text-sm text-gray-500">
            Progreso
          </p>

          <h2 className="font-bold mt-2">
            {progress}%
          </h2>

        </div>

        <div className="bg-gray-100 rounded-xl p-4 text-center">

          <p className="text-sm text-gray-500">
            Agente
          </p>

          <h2 className="font-bold mt-2">
            Sally
          </h2>

        </div>

      </div>

    </div>
  );
}

export default AgentPanel;