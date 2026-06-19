/**
 * COPILOTO 360 — Reportes y Estadísticas
 * Conectado al backend: GET /reports/, POST /reports/generate
 */
import { useState, useEffect } from 'react';
import {
  Calendar, Download, FileText, BarChart3, TrendingUp, Clock,
  AlertTriangle, RefreshCw, FileSpreadsheet
} from 'lucide-react';
import { fetchReports, formatDate, formatBytes } from '../../services/api.js';

export default function Reports() {
  const [reports,  setReports]  = useState([]);
  const [loading,  setLoading]  = useState(true);
  const [dateRange, setDateRange] = useState({ start: '', end: '' });
  const [generating, setGenerating] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const data = await fetchReports();
      setReports(data.reportes || []);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  // KPIs derivados de los reportes reales
  const totalFrames   = reports.reduce((s, r) => s + (r.total_frames || 0), 0);
  const totalCriticos = reports.reduce((s, r) => s + (r.resumen?.critico || 0), 0);
  const totalAlertas  = reports.reduce((s, r) => s + Object.values(r.resumen || {}).reduce((a, b) => a + b, 0), 0);
  const pctAtendidas  = totalAlertas > 0 ? Math.round(((totalAlertas - totalCriticos) / totalAlertas) * 100) : 100;

  const kpis = [
    { label: 'Frames analizados',   value: totalFrames.toLocaleString('es-CO'), sub: 'Total flota',              color: 'text-emerald-400', bg: 'bg-emerald-500/10', icon: TrendingUp  },
    { label: 'Horas estimadas',     value: Math.round(totalFrames / 3600) + ' hrs', sub: 'A 1 frame/seg',       color: 'text-zinc-300',    bg: 'bg-zinc-800',       icon: Clock       },
    { label: 'Alertas atendidas',   value: `${pctAtendidas}%`,             sub: 'Tasa de respuesta',            color: 'text-amber-400',   bg: 'bg-amber-500/10',   icon: AlertTriangle },
  ];

  return (
    <div className="flex-1 flex flex-col">
      {/* NAVBAR */}
      <header className="h-16 border-b border-zinc-800 bg-zinc-900/50 backdrop-blur-md px-8 flex items-center justify-between sticky top-0 z-10">
        <h2 className="text-xl font-semibold text-zinc-200">Reportes y Estadísticas</h2>
        <div className="flex items-center gap-3">
          <span className="text-xs text-zinc-500">Módulo de Exportación</span>
          <button
            onClick={load}
            className="p-2 hover:bg-zinc-800 rounded-lg text-zinc-500 hover:text-zinc-300 transition-colors"
          >
            <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
          </button>
        </div>
      </header>

      <main className="p-8 max-w-7xl w-full mx-auto space-y-6">

        {/* FILTRO DE FECHAS */}
        <div className="bg-zinc-900 p-6 rounded-2xl border border-zinc-800 space-y-4">
          <h3 className="text-sm font-semibold text-zinc-300 uppercase tracking-wider flex items-center gap-2">
            <Calendar size={16} className="text-indigo-400" />
            Configurar Reporte Personalizado
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
            <div>
              <label className="block text-xs font-medium text-zinc-400 mb-1.5">Fecha Inicial</label>
              <input
                type="date"
                className="w-full px-4 py-2 bg-zinc-950 border border-zinc-800 rounded-xl text-sm text-zinc-200 focus:outline-none focus:border-indigo-500 transition-all [color-scheme:dark]"
                onChange={(e) => setDateRange({ ...dateRange, start: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-zinc-400 mb-1.5">Fecha Final</label>
              <input
                type="date"
                className="w-full px-4 py-2 bg-zinc-950 border border-zinc-800 rounded-xl text-sm text-zinc-200 focus:outline-none focus:border-indigo-500 transition-all [color-scheme:dark]"
                onChange={(e) => setDateRange({ ...dateRange, end: e.target.value })}
              />
            </div>
            <div>
              <button
                disabled={generating}
                className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-medium text-sm rounded-xl transition-all duration-200 shadow-lg shadow-indigo-600/20 active:scale-95"
              >
                <BarChart3 size={16} />
                <span>{generating ? 'Generando…' : 'Generar'}</span>
              </button>
            </div>
          </div>
        </div>

        {/* KPIs */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {kpis.map(({ label, value, sub, color, bg, icon: Icon }) => (
            <div key={label} className="p-6 bg-zinc-900 rounded-2xl border border-zinc-800 flex items-center justify-between">
              <div className="space-y-1">
                <p className="text-xs font-medium text-zinc-400">{label}</p>
                <p className={`text-2xl font-bold ${color}`}>
                  {loading ? <span className="inline-block w-16 h-6 bg-zinc-800 rounded animate-pulse" /> : value}
                </p>
                <p className="text-[11px] text-zinc-500">{sub}</p>
              </div>
              <div className={`p-3 ${bg} ${color} rounded-xl`}>
                <Icon size={20} />
              </div>
            </div>
          ))}
        </div>

        {/* HISTORIAL */}
        <div className="bg-zinc-900 rounded-2xl border border-zinc-800 overflow-hidden">
          <div className="p-5 border-b border-zinc-800 flex items-center justify-between">
            <h3 className="font-semibold text-zinc-200 text-sm uppercase tracking-wider">Reportes Generados</h3>
            {!loading && <span className="text-xs text-zinc-500">{reports.length} archivo{reports.length !== 1 ? 's' : ''}</span>}
          </div>

          {loading ? (
            <div className="p-6 space-y-4">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="h-16 bg-zinc-800 rounded-xl animate-pulse" />
              ))}
            </div>
          ) : reports.length === 0 ? (
            <div className="p-12 text-center text-zinc-500 text-sm">
              No hay reportes generados aún. Procesa un video desde el Agente para crear el primero.
            </div>
          ) : (
            <div className="divide-y divide-zinc-800/60">
              {reports.map((r, i) => {
                const criticos = r.resumen?.critico ?? 0;
                return (
                  <div key={i} className="p-5 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 hover:bg-zinc-800/20 transition-colors">
                    <div className="flex items-center gap-4">
                      <div className="p-3 rounded-xl border bg-indigo-500/10 text-indigo-400 border-indigo-500/20">
                        <FileText size={20} />
                      </div>
                      <div>
                        <h4 className="text-sm font-medium text-zinc-200 font-mono">{r.archivo}</h4>
                        <p className="text-xs text-zinc-500 mt-0.5">
                          Vehículo: <span className="text-zinc-400">{r.vehiculo_id}</span>
                          {' · '}{r.total_frames} frames
                          {' · '}{formatBytes(r.tamaño_bytes)}
                          {' · '}{formatDate(r.generado_en)}
                        </p>
                        {/* Resumen de alertas */}
                        <div className="flex items-center gap-3 mt-1.5">
                          {criticos > 0 && (
                            <span className="text-[11px] text-red-400 font-semibold">{criticos} crítico{criticos > 1 ? 's' : ''}</span>
                          )}
                          {(r.resumen?.alto ?? 0) > 0 && (
                            <span className="text-[11px] text-orange-400">{r.resumen.alto} alto{r.resumen.alto > 1 ? 's' : ''}</span>
                          )}
                          {(r.resumen?.medio ?? 0) > 0 && (
                            <span className="text-[11px] text-amber-400">{r.resumen.medio} medio{r.resumen.medio > 1 ? 's' : ''}</span>
                          )}
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-3 w-full sm:w-auto justify-end">
                      <button className="flex items-center gap-1.5 px-3 py-2 bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-xs font-medium rounded-lg border border-zinc-700/50 transition-colors">
                        <Download size={14} />
                        <span>Descargar</span>
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

      </main>
    </div>
  );
}
