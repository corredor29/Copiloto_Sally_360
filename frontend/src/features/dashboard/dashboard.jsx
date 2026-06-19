import { useState, useEffect } from 'react';
import { Car, FileText, ShieldAlert, AlertTriangle, CheckCircle2, RefreshCw } from 'lucide-react';
import { fetchVehicles, fetchAlerts, nivelColor } from '../../services/api.js';

export default function Dashboard() {
  const [vehicles, setVehicles] = useState(null);
  const [alerts,   setAlerts]   = useState(null);
  const [loading,  setLoading]  = useState(true);
  const [lastRefresh, setLastRefresh] = useState(new Date());

  const load = async () => {
    setLoading(true);
    try {
      const [vData, aData] = await Promise.all([fetchVehicles(), fetchAlerts()]);
      setVehicles(vData);
      setAlerts(aData);
      setLastRefresh(new Date());
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const totalVehiculos  = vehicles?.total ?? '—';
  const alertasCriticas = alerts?.alertas?.filter(a => a.nivel === 'critico').length ?? '—';
  const totalAlertas    = alerts?.total ?? '—';

  const stats = [
    { name: 'Vehículos registrados', value: totalVehiculos,  icon: Car,        color: 'text-blue-400',   bg: 'bg-blue-500/10'   },
    { name: 'Alertas críticas',      value: alertasCriticas, icon: ShieldAlert, color: 'text-red-400',    bg: 'bg-red-500/10'    },
    { name: 'Alertas totales',       value: totalAlertas,    icon: FileText,    color: 'text-purple-400', bg: 'bg-purple-500/10' },
  ];

  const recentAlerts = alerts?.alertas?.slice(0, 5) ?? [];

  return (
    <div className="flex-1 flex flex-col">
      {/* NAVBAR */}
      <header className="h-16 border-b border-zinc-800 bg-zinc-900/50 backdrop-blur-md px-4 md:px-8 flex items-center justify-between sticky top-0 z-10">
        <h2 className="text-xl font-semibold text-zinc-200">Panel de Inicio</h2>
        <div className="flex items-center gap-3">
          <span className="hidden sm:block text-sm text-zinc-400 bg-zinc-900 px-3 py-1.5 rounded-lg border border-zinc-800">
            {new Date().toLocaleDateString('es-CO', { weekday: 'long', day: 'numeric', month: 'short' })}
          </span>
          <button
            onClick={load}
            className="p-2 hover:bg-zinc-800 rounded-lg text-zinc-500 hover:text-zinc-300 transition-colors"
            title="Actualizar datos"
          >
            <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
          </button>
        </div>
      </header>

      {/* CONTENIDO */}
      <main className="p-4 md:p-8 max-w-7xl w-full mx-auto space-y-8">

        {/* TARJETAS KPI */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {stats.map((stat) => {
            const Icon = stat.icon;
            return (
              <div key={stat.name} className="p-6 bg-zinc-900 rounded-2xl border border-zinc-800 hover:border-zinc-700 transition-all duration-300 flex items-center justify-between group">
                <div className="space-y-2">
                  <p className="text-sm font-medium text-zinc-400">{stat.name}</p>
                  <p className="text-3xl font-bold text-zinc-100 tracking-tight">
                    {loading ? <span className="inline-block w-10 h-8 bg-zinc-800 rounded animate-pulse" /> : stat.value}
                  </p>
                </div>
                <div className={`p-4 rounded-xl ${stat.bg} ${stat.color} group-hover:scale-105 transition-transform duration-300`}>
                  <Icon size={24} />
                </div>
              </div>
            );
          })}
        </div>

        {/* CUADRÍCULA INFERIOR */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

          {/* ALERTAS RECIENTES */}
          <div className="lg:col-span-2 p-6 bg-zinc-900 rounded-2xl border border-zinc-800 flex flex-col">
            <div className="flex items-center justify-between mb-6">
              <h3 className="font-semibold text-zinc-200 flex items-center gap-2">
                <AlertTriangle size={18} className="text-amber-500" />
                Últimas Alertas
              </h3>
              {!loading && (
                <span className="text-xs font-medium text-indigo-400 bg-indigo-500/10 px-2.5 py-1 rounded-full border border-indigo-500/20">
                  {totalAlertas} total
                </span>
              )}
            </div>

            {loading ? (
              <div className="space-y-3">
                {[...Array(4)].map((_, i) => (
                  <div key={i} className="h-14 bg-zinc-800 rounded-xl animate-pulse" />
                ))}
              </div>
            ) : recentAlerts.length === 0 ? (
              <div className="flex-1 flex items-center justify-center text-zinc-500 text-sm">
                No hay alertas registradas
              </div>
            ) : (
              <div className="divide-y divide-zinc-800 flex-1">
                {recentAlerts.map((alert, i) => {
                  const c = nivelColor(alert.nivel);
                  return (
                    <div key={i} className="py-4 flex items-center justify-between first:pt-0 last:pb-0">
                      <div className="flex items-center gap-4 min-w-0">
                        <span className={`w-2 h-2 rounded-full flex-shrink-0 ${c.dot} ${alert.nivel === 'critico' ? 'shadow-lg shadow-red-500/50' : ''}`} />
                        <div className="min-w-0">
                          <p className="text-sm font-medium text-zinc-200">{alert.vehiculo_id}</p>
                          <p className="text-xs text-zinc-400 truncate max-w-xs">{alert.mensaje}</p>
                        </div>
                      </div>
                      <span className={`flex-shrink-0 text-xs font-semibold px-2 py-0.5 rounded-full ${c.bg} ${c.text} border ${c.border}`}>
                        {alert.nivel}
                      </span>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* ESTADO OPERATIVO */}
          <div className="p-6 bg-zinc-900 rounded-2xl border border-zinc-800 flex flex-col justify-between">
            <div>
              <h3 className="font-semibold text-zinc-200 mb-6 flex items-center gap-2">
                <CheckCircle2 size={18} className="text-emerald-500" />
                Estado Operativo
              </h3>

              {loading ? (
                <div className="space-y-4">
                  <div className="h-6 bg-zinc-800 rounded animate-pulse" />
                  <div className="h-6 bg-zinc-800 rounded animate-pulse" />
                </div>
              ) : (
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-xs font-medium text-zinc-400 mb-1.5">
                      <span>Vehículos OK</span>
                      <span className="text-zinc-200">
                        {vehicles?.vehiculos?.filter(v => v.estado_actual.nivel === 'bajo').length ?? 0} de {totalVehiculos}
                      </span>
                    </div>
                    <div className="w-full bg-zinc-800 h-2 rounded-full overflow-hidden">
                      <div
                        className="bg-gradient-to-r from-indigo-500 to-emerald-500 h-full rounded-full transition-all"
                        style={{
                          width: vehicles?.total
                            ? `${Math.round((vehicles.vehiculos.filter(v => v.estado_actual.nivel === 'bajo').length / vehicles.total) * 100)}%`
                            : '0%'
                        }}
                      />
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between text-xs font-medium text-zinc-400 mb-1.5">
                      <span>Alertas resueltas hoy</span>
                      <span className="text-zinc-200">—</span>
                    </div>
                    <div className="w-full bg-zinc-800 h-2 rounded-full overflow-hidden">
                      <div className="bg-indigo-500 h-full w-0" />
                    </div>
                  </div>
                </div>
              )}
            </div>

            <div className="mt-6 p-4 bg-zinc-950 rounded-xl border border-zinc-800/80 text-center">
              <p className="text-xs text-zinc-500">
                Última actualización: {lastRefresh.toLocaleTimeString('es-CO')}
              </p>
            </div>
          </div>

        </div>
      </main>
    </div>
  );
}
