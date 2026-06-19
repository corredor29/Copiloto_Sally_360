import { useState, useEffect } from 'react';
import { Car, Search, Plus, RefreshCw, Video, X, Loader2 } from 'lucide-react';
import { fetchVehicles, nivelColor, addVehicle } from '../../services/api.js';
import VehicleMonitor from './VehicleMonitor.jsx';

const STATUS_LABELS = {
  bajo:        { label: 'Operativo',   cls: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20', dot: 'bg-emerald-400' },
  medio:       { label: 'Precaución',  cls: 'bg-amber-500/10  text-amber-400  border-amber-500/20',    dot: 'bg-amber-400'  },
  alto:        { label: 'Alerta Alta', cls: 'bg-orange-500/10 text-orange-400 border-orange-500/20',   dot: 'bg-orange-400' },
  critico:     { label: 'Crítico',     cls: 'bg-red-500/10    text-red-400    border-red-500/20',      dot: 'bg-red-500 animate-pulse' },
  desconocido: { label: 'Sin datos',   cls: 'bg-zinc-800      text-zinc-400   border-zinc-700',        dot: 'bg-zinc-500'  },
};

const DEMO_VEHICLES = [
  { vehiculo_id: 'CAM-001', estado_actual: { nivel: 'bajo',    conductor: 'normal',    via: 'normal'  } },
  { vehiculo_id: 'CAM-004', estado_actual: { nivel: 'critico', conductor: 'dormido',   via: 'lluvia'  } },
  { vehiculo_id: 'FUR-009', estado_actual: { nivel: 'medio',   conductor: 'distraido', via: 'normal'  } },
  { vehiculo_id: 'BUS-012', estado_actual: { nivel: 'alto',    conductor: 'normal',    via: 'curva'   } },
  { vehiculo_id: 'CAM-003', estado_actual: { nivel: 'bajo',    conductor: 'normal',    via: 'normal'  } },
];

// ── Modal: Añadir Vehículo ────────────────────────────────────────────────────

function AddVehicleModal({ onClose, onAdd }) {
  const [form,   setForm]   = useState({ vehiculo_id: '', tipo: 'Camión Pesado', conductor: '', placa: '' });
  const [errors, setErrors] = useState({});
  const [saving, setSaving] = useState(false);

  // Cerrar con Escape
  useEffect(() => {
    const handler = (e) => { if (e.key === 'Escape') onClose() }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [onClose]);

  const validate = () => {
    const errs = {};
    if (!form.vehiculo_id.trim()) errs.vehiculo_id = 'El ID del vehículo es requerido';
    return errs;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const errs = validate();
    if (Object.keys(errs).length) { setErrors(errs); return; }
    setSaving(true);
    try {
      const nuevo = await addVehicle({
        vehiculo_id:   form.vehiculo_id.trim(),
        tipo:          form.tipo,
        conductor:     form.conductor.trim(),
        placa:         form.placa.trim(),
        estado_actual: { nivel: 'bajo', conductor: 'normal', via: 'normal' },
      });
      onAdd(nuevo);
      onClose();
    } finally {
      setSaving(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-stretch sm:items-center sm:justify-center bg-black/70 backdrop-blur-sm sm:p-4"
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div className="w-full h-full sm:h-auto sm:max-w-md bg-zinc-900 sm:rounded-3xl border border-zinc-700 shadow-2xl flex flex-col overflow-hidden">

        {/* Header */}
        <div className="flex items-center justify-between px-7 pt-6 pb-4 border-b border-zinc-800 flex-shrink-0">
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-zinc-800 rounded-xl border border-zinc-700">
              <Car size={20} className="text-indigo-400" />
            </div>
            <h2 className="font-bold text-zinc-100 text-base">Nuevo Vehículo</h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-zinc-800 rounded-xl text-zinc-500 hover:text-zinc-300 transition-colors"
          >
            <X size={18} />
          </button>
        </div>

        {/* Formulario scrollable */}
        <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto p-7 space-y-5">

          {/* ID del Vehículo */}
          <div>
            <label className="block text-xs font-medium text-zinc-400 mb-1.5">
              ID del Vehículo <span className="text-red-400">*</span>
            </label>
            <input
              type="text"
              placeholder="Ej: CAM-005, BUS-012"
              value={form.vehiculo_id}
              onChange={(e) => {
                setForm({ ...form, vehiculo_id: e.target.value.toUpperCase() });
                if (errors.vehiculo_id) setErrors({});
              }}
              className={`w-full px-4 py-2.5 bg-zinc-950 border rounded-xl text-sm text-zinc-200 placeholder-zinc-600 focus:outline-none focus:ring-1 transition-all ${
                errors.vehiculo_id
                  ? 'border-red-500 focus:border-red-500 focus:ring-red-500'
                  : 'border-zinc-800 focus:border-indigo-500 focus:ring-indigo-500'
              }`}
            />
            {errors.vehiculo_id && (
              <p className="mt-1 text-xs text-red-400">{errors.vehiculo_id}</p>
            )}
          </div>

          {/* Tipo de Vehículo */}
          <div>
            <label className="block text-xs font-medium text-zinc-400 mb-1.5">Tipo de Vehículo</label>
            <select
              value={form.tipo}
              onChange={(e) => setForm({ ...form, tipo: e.target.value })}
              className="w-full px-4 py-2.5 bg-zinc-950 border border-zinc-800 rounded-xl text-sm text-zinc-200 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all [color-scheme:dark]"
            >
              <option>Camión Pesado</option>
              <option>Furgón</option>
              <option>Camioneta</option>
              <option>Bus</option>
              <option>Otro</option>
            </select>
          </div>

          {/* Conductor Asignado */}
          <div>
            <label className="block text-xs font-medium text-zinc-400 mb-1.5">Conductor Asignado</label>
            <input
              type="text"
              placeholder="Nombre completo del conductor"
              value={form.conductor}
              onChange={(e) => setForm({ ...form, conductor: e.target.value })}
              className="w-full px-4 py-2.5 bg-zinc-950 border border-zinc-800 rounded-xl text-sm text-zinc-200 placeholder-zinc-600 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all"
            />
          </div>

          {/* Placa */}
          <div>
            <label className="block text-xs font-medium text-zinc-400 mb-1.5">Placa</label>
            <input
              type="text"
              placeholder="Ej: SJQ-456"
              value={form.placa}
              onChange={(e) => setForm({ ...form, placa: e.target.value.toUpperCase() })}
              className="w-full px-4 py-2.5 bg-zinc-950 border border-zinc-800 rounded-xl text-sm text-zinc-200 placeholder-zinc-600 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all"
            />
          </div>

          {/* Botones */}
          <div className="flex items-center justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-5 py-2.5 bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-sm font-medium rounded-xl border border-zinc-700 transition-colors"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={saving}
              className="flex items-center gap-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-60 text-white text-sm font-semibold rounded-xl transition-all duration-200 shadow-lg shadow-indigo-600/20 active:scale-95"
            >
              {saving
                ? <><Loader2 size={14} className="animate-spin" /> Guardando…</>
                : 'Guardar Vehículo'
              }
            </button>
          </div>

        </form>
      </div>
    </div>
  );
}

// ── Componente principal ──────────────────────────────────────────────────────

export default function Vehicles() {
  const [vehicles,     setVehicles]     = useState([]);
  const [loading,      setLoading]      = useState(true);
  const [search,       setSearch]       = useState('');
  const [monitored,    setMonitored]    = useState(null);
  const [showAddModal, setShowAddModal] = useState(false);

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

  const handleAddVehicle = (nuevoVehiculo) => {
    setVehicles(prev => [...prev, nuevoVehiculo]);
  };

  return (
    <>
      {/* MODAL MONITOREO */}
      {monitored && (
        <VehicleMonitor vehiculo={monitored} onClose={() => setMonitored(null)} />
      )}

      {/* MODAL AÑADIR VEHÍCULO */}
      {showAddModal && (
        <AddVehicleModal
          onClose={() => setShowAddModal(false)}
          onAdd={handleAddVehicle}
        />
      )}

      <div className="flex-1 flex flex-col">
        {/* NAVBAR */}
        <header className="h-16 border-b border-zinc-800 bg-zinc-900/50 backdrop-blur-md px-4 md:px-8 flex items-center justify-between sticky top-0 z-10">
          <h2 className="text-xl font-semibold text-zinc-200">Gestión de Vehículos</h2>
          <div className="flex items-center gap-3">
            <button
              onClick={load}
              className="p-2 hover:bg-zinc-800 rounded-lg text-zinc-500 hover:text-zinc-300 transition-colors"
            >
              <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
            </button>
            <button
              onClick={() => setShowAddModal(true)}
              className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm rounded-xl transition-all duration-200 shadow-lg shadow-indigo-600/20 active:scale-95"
            >
              <Plus size={16} />
              <span className="hidden sm:inline">Añadir Vehículo</span>
            </button>
          </div>
        </header>

        <main className="p-4 md:p-8 max-w-7xl w-full mx-auto space-y-6">

          {/* BÚSQUEDA */}
          <div className="flex items-center gap-4 bg-zinc-900 p-4 rounded-2xl border border-zinc-800">
            <div className="relative flex-1">
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
              <span className="text-xs text-zinc-500 flex-shrink-0">
                {filtered.length} vehículo{filtered.length !== 1 ? 's' : ''}
              </span>
            )}
          </div>

          {/* ── TABLA (md+) ─────────────────────────────────────────────────── */}
          <div className="hidden md:block bg-zinc-900 rounded-2xl border border-zinc-800 overflow-hidden">
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
                          <td className="py-4 px-6 text-zinc-300 capitalize">
                            {v.estado_actual?.conductor || '—'}
                          </td>
                          <td className="py-4 px-6 text-zinc-400 capitalize">
                            {v.estado_actual?.via || '—'}
                          </td>
                          <td className="py-4 px-6">
                            <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${estado.cls}`}>
                              <span className={`w-1.5 h-1.5 rounded-full ${estado.dot}`} />
                              {estado.label}
                            </span>
                          </td>
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

          {/* ── CARDS (mobile, < md) ─────────────────────────────────────────── */}
          <div className="md:hidden space-y-3">
            {loading ? (
              [...Array(4)].map((_, i) => (
                <div key={i} className="h-24 bg-zinc-900 rounded-2xl border border-zinc-800 animate-pulse" />
              ))
            ) : filtered.length === 0 ? (
              <div className="p-12 text-center bg-zinc-900 rounded-2xl border border-zinc-800 text-sm text-zinc-500">
                No se encontraron vehículos.
              </div>
            ) : (
              filtered.map((v) => {
                const nivel  = v.estado_actual?.nivel || 'desconocido';
                const estado = STATUS_LABELS[nivel] || STATUS_LABELS.desconocido;
                return (
                  <div
                    key={v.vehiculo_id}
                    className="p-4 bg-zinc-900 rounded-2xl border border-zinc-800 flex items-center gap-3"
                  >
                    {/* Ícono */}
                    <div className="p-2.5 bg-zinc-800 rounded-xl text-zinc-400 border border-zinc-700/50 flex-shrink-0">
                      <Car size={18} />
                    </div>

                    {/* Info */}
                    <div className="flex-1 min-w-0">
                      <span className="font-mono bg-zinc-950 px-2 py-0.5 rounded text-xs font-bold text-indigo-400 border border-zinc-800">
                        {v.vehiculo_id}
                      </span>
                      <p className="text-xs text-zinc-400 mt-1 capitalize">
                        {v.estado_actual?.conductor || '—'}
                      </p>
                    </div>

                    {/* Badge + botón */}
                    <div className="flex flex-col items-end gap-2 flex-shrink-0">
                      <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${estado.cls}`}>
                        <span className={`w-1.5 h-1.5 rounded-full ${estado.dot}`} />
                        {estado.label}
                      </span>
                      <button
                        onClick={() => setMonitored(v)}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-500 rounded-xl transition-all duration-200 shadow-md shadow-indigo-600/20 active:scale-95"
                      >
                        <Video size={12} />
                        Monitorear
                      </button>
                    </div>
                  </div>
                );
              })
            )}
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
