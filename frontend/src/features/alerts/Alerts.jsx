import { useState, useEffect } from 'react';
import {
  ShieldAlert, AlertTriangle, Info, CheckCircle2, ShieldCheck, Eye, RefreshCw
} from 'lucide-react';
import { fetchAlerts, nivelColor } from '../../services/api.js';

const NIVEL_LABELS = { critico: 'Crítica', alto: 'Alta', medio: 'Media', bajo: 'Baja' };

export default function Alerts() {
  const [activeFilter, setActiveFilter] = useState('all');
  const [alerts,   setAlerts]   = useState([]);
  const [loading,  setLoading]  = useState(true);
  const [resolved, setResolved] = useState(new Set());

  const load = async () => {
    setLoading(true);
    try {
      const data = await fetchAlerts();
      setAlerts(data.alertas || []);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const visible = alerts.filter((a, i) => {
    if (resolved.has(i)) return false;
    if (activeFilter === 'all') return true;
    return a.nivel === activeFilter;
  });

  const countByNivel = (n) => alerts.filter((_, i) => !resolved.has(i) && alerts[i]?.nivel === n).length;

  const handleResolve = (idx) => setResolved(prev => new Set([...prev, idx]));

  const filterBtns = [
    { key: 'all',     label: `Todas (${alerts.filter((_, i) => !resolved.has(i)).length})`, icon: null,          active: 'bg-zinc-100 text-zinc-950', inactive: 'text-zinc-400'   },
    { key: 'critico', label: `Críticas (${countByNivel('critico')})`,  icon: ShieldAlert,   active: 'bg-red-500 text-white',     inactive: 'text-red-400'    },
    { key: 'alto',    label: `Altas (${countByNivel('alto')})`,        icon: AlertTriangle, active: 'bg-orange-500 text-white',  inactive: 'text-orange-400' },
    { key: 'medio',   label: `Medias (${countByNivel('medio')})`,      icon: AlertTriangle, active: 'bg-amber-500 text-zinc-950',inactive: 'text-amber-400'  },
    { key: 'bajo',    label: `Bajas (${countByNivel('bajo')})`,        icon: Info,          active: 'bg-blue-500 text-white',    inactive: 'text-blue-400'   },
  ];

  const criticalCount = countByNivel('critico');

  return (
    <div className="flex-1 flex flex-col">
      {/* NAVBAR */}
      <header className="h-16 border-b border-zinc-800 bg-zinc-900/50 backdrop-blur-md px-4 md:px-8 flex items-center justify-between sticky top-0 z-10">
        <h2 className="text-xl font-semibold text-zinc-200">Centro de Incidentes</h2>
        <div className="flex items-center gap-3">
          {criticalCount > 0 && (
            <span className="flex items-center gap-2 text-xs font-medium text-red-400 bg-red-500/10 px-3 py-1.5 rounded-xl border border-red-500/20">
              <span className="w-1.5 h-1.5 rounded-full bg-red-500 animate-ping" />
              {criticalCount} Crítica{criticalCount > 1 ? 's' : ''}
            </span>
          )}
          <button
            onClick={load}
            className="p-2 hover:bg-zinc-800 rounded-lg text-zinc-500 hover:text-zinc-300 transition-colors"
            title="Actualizar"
          >
            <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
          </button>
        </div>
      </header>

      <main className="p-4 md:p-8 max-w-7xl w-full mx-auto space-y-6">

        {/* FILTROS — scroll horizontal en mobile */}
        <div className="overflow-x-auto -mx-4 md:mx-0 px-4 md:px-0 pb-1">
          <div className="flex gap-2.5 flex-nowrap md:flex-wrap">
            {filterBtns.map(({ key, label, icon: Icon, active, inactive }) => (
              <button
                key={key}
                onClick={() => setActiveFilter(key)}
                className={`flex-shrink-0 flex items-center gap-1.5 px-4 py-2 text-xs font-semibold rounded-xl border transition-all duration-200 ${
                  activeFilter === key
                    ? `${active} border-transparent shadow-md`
                    : `bg-zinc-900 ${inactive} border-zinc-800 hover:bg-zinc-800/60`
                }`}
              >
                {Icon && <Icon size={14} />}
                {label}
              </button>
            ))}
          </div>
        </div>

        {/* LISTA */}
        <div className="space-y-3">
          {loading ? (
            [...Array(4)].map((_, i) => (
              <div key={i} className="h-20 bg-zinc-900 rounded-2xl border border-zinc-800 animate-pulse" />
            ))
          ) : visible.length === 0 ? (
            <div className="p-12 text-center bg-zinc-900 rounded-2xl border border-zinc-800 space-y-3">
              <div className="h-12 w-12 bg-emerald-500/10 text-emerald-400 rounded-full flex items-center justify-center mx-auto border border-emerald-500/20">
                <ShieldCheck size={24} />
              </div>
              <div>
                <h3 className="font-semibold text-zinc-200 text-sm">¡Todo bajo control!</h3>
                <p className="text-xs text-zinc-500 mt-1">No hay alertas activas en esta categoría.</p>
              </div>
            </div>
          ) : (
            visible.map((alert, rawIdx) => {
              const realIdx = alerts.findIndex((a, i) => a === alert && !resolved.has(i));
              const c = nivelColor(alert.nivel);
              const isCritical = alert.nivel === 'critico';
              const isAlto     = alert.nivel === 'alto';

              return (
                <div
                  key={rawIdx}
                  className={`p-5 bg-zinc-900 rounded-2xl border transition-all duration-300 ${
                    isCritical ? 'border-red-500/20 hover:border-red-500/40' :
                    isAlto     ? 'border-orange-500/20 hover:border-orange-500/40' :
                    'border-zinc-800 hover:border-zinc-700'
                  }`}
                >
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                    {/* Contenido de la alerta */}
                    <div className="flex items-start gap-4">
                      <div className={`p-3 rounded-xl border mt-0.5 flex-shrink-0 ${c.bg} ${c.text} ${c.border}`}>
                        {isCritical ? <ShieldAlert size={20} /> : isAlto ? <AlertTriangle size={20} /> : <Info size={20} />}
                      </div>
                      <div className="space-y-1 min-w-0">
                        <div className="flex items-center gap-2.5 flex-wrap">
                          <h4 className="text-sm font-semibold text-zinc-200">{alert.vehiculo_id}</h4>
                          <span className={`text-[11px] font-semibold px-2 py-0.5 rounded-full ${c.bg} ${c.text} border ${c.border}`}>
                            {NIVEL_LABELS[alert.nivel] || alert.nivel}
                          </span>
                        </div>
                        <p className="text-sm text-zinc-400">{alert.mensaje}</p>
                        <p className="text-xs text-zinc-500">
                          {alert.conductor_estado && `Conductor: ${alert.conductor_estado}`}
                          {alert.via_estado && ` · Vía: ${alert.via_estado}`}
                          {alert.frame != null && ` · Frame #${alert.frame}`}
                        </p>
                      </div>
                    </div>

                    {/* Botones de acción — debajo en mobile, a la derecha en desktop */}
                    <div className="flex items-center gap-2 self-end sm:self-center flex-shrink-0">
                      <button
                        className="p-2 bg-zinc-950 hover:bg-zinc-800 text-zinc-400 hover:text-zinc-200 rounded-xl border border-zinc-800 transition-colors"
                        title="Ver detalles"
                      >
                        <Eye size={16} />
                      </button>
                      <button
                        onClick={() => handleResolve(realIdx === -1 ? rawIdx : realIdx)}
                        className="flex items-center gap-1.5 px-3 py-2 bg-zinc-950 hover:bg-emerald-500/10 text-zinc-400 hover:text-emerald-400 rounded-xl border border-zinc-800 hover:border-emerald-500/20 transition-all duration-200 font-medium text-xs"
                      >
                        <CheckCircle2 size={14} />
                        <span>Resolver</span>
                      </button>
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </main>
    </div>
  );
}
