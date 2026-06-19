/**
 * COPILOTO 360 — Gestión de Vehículos
 * Conectado al backend: GET /vehicles/
 * Abre VehicleMonitor para analizar video en vivo por vehículo.
 */
import { useState, useEffect } from 'react';
import { Car, Search, Plus, AlertTriangle, RefreshCw, Video } from 'lucide-react';
import { fetchVehicles, nivelColor } from '../../services/api.js';
import VehicleMonitor from './VehicleMonitor.jsx';

const STATUS_LABELS = {
  bajo:        { label: 'Operativo',   cls: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20', dot: 'bg-emerald-400' },
  medio:       { label: 'Precaución',  cls: 'bg-amber-500/10  text-amber-400  border-amber-500/20',    dot: 'bg-amber-400'  },
  alto:        { label: 'Alerta Alta', cls: 'bg-orange-500/10 text-orange-400 border-orange-500/20',   dot: 'bg-orange-400' },
  critico:     { label: 'Crítico',     cls: 'bg-red-500/10    text-red-400    border-red-500/20',      dot: 'bg-red-500 animate-pulse' },
  desconocido: { label: 'Sin datos',   cls: 'bg-zinc-800      text-zinc-400   border-zinc-700',        dot: 'bg-zinc-500'  },
};

// Vehículos de demo que se muestran cuando el backend no tiene datos
const DEMO_VEHICLES = [
  { vehiculo_id: 'CAM-001', estado_actual: { nivel: 'bajo',    conductor: 'normal',    via: 'normal'  } },
  { vehiculo_id: 'CAM-004', estado_actual: { nivel: 'critico', conductor: 'dormido',   via: 'lluvia'  } },
  { vehiculo_id: 'FUR-009', estado_actual: { nivel: 'medio',   conductor: 'distraido', via: 'normal'  } },
  { vehiculo_id: 'BUS-012', estado_actual: { nivel: 'alto',    conductor: 'normal',    via: 'curva'   } },
  { vehiculo_id: 'CAM-003', estado_actual: { nivel: 'bajo',    conductor: 'normal',    via: 'normal'  } },
];

export default function Vehicles() {
  const [vehicles,  setVehicles]  = useState([]);
  const [loading,   setLoading]   = useState(true);
  const [search,    setSearch]    = useState('');
  const [monitored, setMonitored] = useState(null); // vehículo seleccionado para monitorear

  const load = async () => {
    setLoading(true);
    try {
      const data = await fetchVehicles();
      const lista = data.vehiculos || [];
      setVehicles(lista.length > 0 ? lista : DEMO_VEHICLES);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const filtered = vehicles.filter(v =>
    v.vehiculo_id.toLowerCase().includes(search.toLowerCase()) ||
    (v.estado_actual?.conductor || '').toLowerCase().includes(search.toLowerCase())
  );

  return (
    <>
      {/* MODAL DE MONITOREO */}
      {monitored && (
        <VehicleMonitor
          vehiculo={monitored}
          onClose={() => setMonitored(null)}
        />
      )}

      <div className="flex-1 flex flex-col">
        {/* NAVBAR */}
        <header className="h-16 border-b border-zinc-800 bg-zinc-900/50 backdrop-blur-md px-8 flex items-center justify-between sticky top-0 z-10">
          <h2 className="text-xl font-semibold text-zinc-200">Gestión de Vehículos</h2>
          <div className="flex items-center gap-3">
            <button
              onClick={load}
              className="p-2 hover:bg-zinc-800 rounded-lg text-zinc-500 hover:text-zinc-300 transition-colors"
            >
              <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
            </button>
            <button className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm rounded-xl transition-all duration-200 shadow-lg shadow-indigo-600/20 active:scale-95">
              <Plus size={16} />
              <span>Añadir Vehículo</span>
            </button>
          </div>
        </header>

        <main className="p-8 max-w-7xl w-full mx-auto space-y-6">

          {/* BÚSQUEDA */}
          <div className="flex items-center gap-4 bg-zinc-900 p-4 rounded-2xl border border-zinc-800">
            <div className="relative flex-1 max-w-sm">
              <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 text-zinc-500" size={18} />
              <input
                type="text"
                placeholder="Buscar por ID o estado del conductor..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full pl-11 pr-4 py-2.5 bg-zinc-950 border border-zinc-800 rounded-xl text-sm text-zinc-200 placeholder-zinc-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all"
              />
            </div>
            {!loading && (
              <span className="text-xs text-zinc-500">
                {filtered.length} vehículo{filtered.length !== 1 ? 's' : ''}
              </span>
            )}
          </div>

          {/* TABLA */}
          <div className="bg-zinc-900 rounded-2xl border border-zinc-800 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-zinc-800 text-xs font-semibold text-zinc-400 uppercase tracking-wider">
                    <th className="py-4 px-6">ID Vehículo</th>
                    <th className="py-4 px-6">Estado Conductor</th>
                    <th className="py-4 px-6">Estado Vía</th>
                    <th className="py-4 px-6">Nivel Alerta</th>
                    <th className="py-4 px-6 text-center">Monitorear</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-zinc-800/60 text-sm">
                  {loading ? (
                    [...Array(5)].map((_, i) => (
                      <tr key={i}>
                        {[...Array(5)].map((_, j) => (
                          <td key={j} className="py-4 px-6">
                            <div className="h-4 bg-zinc-800 rounded animate-pulse" />
                          </td>
                        ))}
                      </tr>
                    ))
                  ) : filtered.length === 0 ? (
                    <tr>
                      <td colSpan="5" className="py-12 text-center text-sm text-zinc-500">
                        No se encontraron vehículos.
                      </td>
                    </tr>
                  ) : (
                    filtered.map((v) => {
                      const nivel  = v.estado_actual?.nivel || 'desconocido';
                      const estado = STATUS_LABELS[nivel] || STATUS_LABELS.desconocido;

                      return (
                        <tr
                          key={v.vehiculo_id}
                          className="hover:bg-zinc-800/30 transition-colors duration-150"
                        >
                          {/* ID */}
                          <td className="py-4 px-6">
                            <div className="flex items-center gap-3">
                              <div className="p-2.5 bg-zinc-800 rounded-xl text-zinc-400 border border-zinc-700/50">
                                <Car size={18} />
                              </div>
                              <span className="font-mono bg-zinc-950 px-2 py-0.5 rounded text-xs font-bold text-indigo-400 border border-zinc-800">
                                {v.vehiculo_id}
                              </span>
                            </div>
                          </td>

                          {/* Conductor */}
                          <td className="py-4 px-6 text-zinc-300 capitalize">
                            {v.estado_actual?.conductor || '—'}
                          </td>

                          {/* Vía */}
                          <td className="py-4 px-6 text-zinc-400 capitalize">
                            {v.estado_actual?.via || '—'}
                          </td>

                          {/* Nivel */}
                          <td className="py-4 px-6">
                            <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${estado.cls}`}>
                              <span className={`w-1.5 h-1.5 rounded-full ${estado.dot}`} />
                              {estado.label}
                            </span>
                          </td>

                          {/* Acción: Monitorear */}
                          <td className="py-4 px-6 text-center">
                            <button
                              onClick={() => setMonitored(v)}
                              className="inline-flex items-center gap-1.5 px-4 py-2 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-500 rounded-xl transition-all duration-200 shadow-md shadow-indigo-600/20 active:scale-95"
                            >
                              <Video size={13} />
                              Monitorear
                            </button>
                          </td>
                        </tr>
                      );
                    })
                  )}
                </tbody>
              </table>
            </div>
          </div>

          {/* LEYENDA */}
          {!loading && filtered.length > 0 && (
            <div className="flex flex-wrap gap-4 text-xs text-zinc-500">
              {Object.entries(STATUS_LABELS).map(([key, v]) => (
                <span key={key} className="flex items-center gap-1.5">
                  <span className={`w-2 h-2 rounded-full ${v.dot.split(' ')[0]}`} />
                  {v.label}
                </span>
              ))}
            </div>
          )}
        </main>
      </div>
    </>
  );
}
