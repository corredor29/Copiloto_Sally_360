/**
 * COPILOTO 360 — Monitor de Vehículo en Tiempo Real
 * VehicleMonitor.jsx
 *
 * Panel que se abre al hacer click en un vehículo.
 * Permite subir un video y ver el análisis de IA en vivo.
 */
import { useState, useEffect, useRef, useCallback } from 'react';
import {
  X, Upload, Play, RefreshCw, ShieldAlert, AlertTriangle,
  Info, CheckCircle2, Activity, Video, Loader2, Eye
} from 'lucide-react';

const BASE_URL = import.meta.env.VITE_API_URL ?? '';

// ── Colores por nivel ──────────────────────────────────────────────────────
const NIVEL = {
  critico: { label: 'CRÍTICO',   ring: 'ring-red-500',    bg: 'bg-red-500/15',    text: 'text-red-400',    icon: ShieldAlert,    dot: 'bg-red-500 animate-pulse'    },
  alto:    { label: 'ALTO',      ring: 'ring-orange-500', bg: 'bg-orange-500/15', text: 'text-orange-400', icon: AlertTriangle,  dot: 'bg-orange-500'                },
  medio:   { label: 'PRECAUCIÓN',ring: 'ring-amber-500',  bg: 'bg-amber-500/15',  text: 'text-amber-400',  icon: AlertTriangle,  dot: 'bg-amber-400'                 },
  bajo:    { label: 'NORMAL',    ring: 'ring-emerald-500',bg: 'bg-emerald-500/15',text: 'text-emerald-400',icon: CheckCircle2,   dot: 'bg-emerald-400'               },
};
const nv = (n) => NIVEL[n] || NIVEL.bajo;

export default function VehicleMonitor({ vehiculo, onClose }) {
  const [file,       setFile]       = useState(null);
  const [dragging,   setDragging]   = useState(false);
  const [status,     setStatus]     = useState(null);   // respuesta de /agent/status/{id}
  const [uploading,  setUploading]  = useState(false);
  const [error,      setError]      = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const intervalRef  = useRef(null);
  const fileInputRef = useRef(null);

  const vid = vehiculo.vehiculo_id;

  // ── Polling del estado ────────────────────────────────────────────────────
  const fetchStatus = useCallback(async () => {
    try {
      const r = await fetch(`${BASE_URL}/agent/status/${vid}`);
      if (r.ok) setStatus(await r.json());
    } catch { /* silencioso */ }
  }, [vid]);

  useEffect(() => {
    fetchStatus();
    return () => clearInterval(intervalRef.current);
  }, [fetchStatus]);

  useEffect(() => {
    clearInterval(intervalRef.current);
    if (status?.estado === 'procesando' || status?.estado === 'iniciando') {
      intervalRef.current = setInterval(fetchStatus, 1500);
    }
    return () => clearInterval(intervalRef.current);
  }, [status?.estado, fetchStatus]);

  // ── Manejo de archivo ─────────────────────────────────────────────────────
  const handleFile = (f) => {
    if (!f) return;
    const ext = f.name.split('.').pop().toLowerCase();
    if (!['mp4','avi','mov','mkv','webm'].includes(ext)) {
      setError('Formato no soportado. Usa MP4, AVI, MOV, MKV o WEBM.');
      return;
    }
    setError(null);
    setFile(f);
    setPreviewUrl(URL.createObjectURL(f));
  };

  const onDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    handleFile(e.dataTransfer.files[0]);
  };

  // ── Subir y analizar ──────────────────────────────────────────────────────
  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setError(null);

    const form = new FormData();
    form.append('vehiculo_id', vid);
    form.append('fps_deseados', '1.0');
    form.append('video', file);

    try {
      const r = await fetch(`${BASE_URL}/agent/upload-video`, {
        method: 'POST',
        body: form,
      });
      const data = await r.json();
      if (!r.ok) throw new Error(data.detail || 'Error al subir el video');

      // Empezar polling inmediatamente
      setStatus({ estado: 'iniciando', progreso: 0, nivel: null, mensaje: 'Video recibido...' });
      intervalRef.current = setInterval(fetchStatus, 1500);
    } catch (e) {
      setError(e.message);
    } finally {
      setUploading(false);
    }
  };

  // ── UI helpers ────────────────────────────────────────────────────────────
  const isRunning  = status?.estado === 'procesando' || status?.estado === 'iniciando';
  const isDone     = status?.estado === 'completado';
  const isError    = status?.estado === 'error';
  const nivel      = status?.nivel || 'bajo';
  const c          = nv(nivel);
  const NivelIcon  = c.icon;
  const metricas   = status?.resultado?.metricas_globales || {};

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
      <div className={`
        relative w-full max-w-2xl bg-zinc-900 rounded-3xl border shadow-2xl overflow-hidden
        transition-all duration-300
        ${isDone ? `${c.ring} ring-1` : 'border-zinc-700'}
      `}>

        {/* HEADER */}
        <div className="flex items-center justify-between px-7 pt-6 pb-4 border-b border-zinc-800">
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-zinc-800 rounded-xl border border-zinc-700">
              <Video size={20} className="text-indigo-400" />
            </div>
            <div>
              <h2 className="font-bold text-zinc-100 text-base">Monitor en Vivo</h2>
              <p className="text-xs text-zinc-500 font-mono">{vid}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-zinc-800 rounded-xl text-zinc-500 hover:text-zinc-300 transition-colors"
          >
            <X size={18} />
          </button>
        </div>

        <div className="p-7 space-y-6">

          {/* ESTADO EN VIVO — aparece cuando hay algo procesando o completado */}
          {status && status.estado !== 'idle' && (
            <div className={`p-5 rounded-2xl border ${c.bg} ${c.ring.replace('ring-','border-').replace('500','500/30')}`}>
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <span className={`w-2.5 h-2.5 rounded-full ${c.dot}`} />
                  <span className={`text-sm font-bold tracking-wider ${c.text}`}>
                    {isDone ? nivel.toUpperCase() : isRunning ? 'ANALIZANDO' : isError ? 'ERROR' : 'INICIANDO'}
                  </span>
                </div>
                {isRunning && <Loader2 size={16} className="text-zinc-400 animate-spin" />}
                {isDone && <NivelIcon size={18} className={c.text} />}
              </div>

              <p className="text-sm text-zinc-300 mb-3">{status.mensaje}</p>

              {/* Barra de progreso */}
              {(isRunning || isDone) && (
                <div className="w-full bg-zinc-800 rounded-full h-2 overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${
                      isDone ? 'bg-gradient-to-r from-indigo-500 to-emerald-500' : 'bg-indigo-500'
                    }`}
                    style={{ width: `${status.progreso || (isDone ? 100 : 5)}%` }}
                  />
                </div>
              )}

              {/* Métricas finales */}
              {isDone && Object.keys(metricas).length > 0 && (
                <div className="mt-4 grid grid-cols-4 gap-2">
                  {[
                    { key: 'critico', label: 'Críticos', color: 'text-red-400'    },
                    { key: 'alto',    label: 'Altos',    color: 'text-orange-400' },
                    { key: 'medio',   label: 'Medios',   color: 'text-amber-400'  },
                    { key: 'bajo',    label: 'Normales', color: 'text-emerald-400'},
                  ].map(({ key, label, color }) => (
                    <div key={key} className="bg-zinc-900/80 rounded-xl p-3 text-center border border-zinc-700/50">
                      <p className={`text-xl font-bold ${color}`}>{metricas[key] ?? 0}</p>
                      <p className="text-[10px] text-zinc-500 mt-0.5">{label}</p>
                    </div>
                  ))}
                </div>
              )}

              {isError && (
                <p className="mt-2 text-xs text-red-400 bg-red-500/10 px-3 py-2 rounded-lg border border-red-500/20">
                  {status.mensaje}
                </p>
              )}
            </div>
          )}

          {/* ZONA DE UPLOAD — siempre visible si no está procesando */}
          {!isRunning && (
            <div>
              {/* Preview del video seleccionado */}
              {previewUrl ? (
                <div className="relative rounded-2xl overflow-hidden border border-zinc-700 bg-black aspect-video mb-4">
                  <video
                    src={previewUrl}
                    controls
                    className="w-full h-full object-contain"
                  />
                  <button
                    onClick={() => { setFile(null); setPreviewUrl(null); setError(null); }}
                    className="absolute top-2 right-2 p-1.5 bg-black/70 hover:bg-black rounded-lg text-zinc-300 transition-colors"
                  >
                    <X size={14} />
                  </button>
                </div>
              ) : (
                /* Drop zone */
                <div
                  onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
                  onDragLeave={() => setDragging(false)}
                  onDrop={onDrop}
                  onClick={() => fileInputRef.current?.click()}
                  className={`
                    flex flex-col items-center justify-center gap-3 p-10 rounded-2xl border-2 border-dashed
                    cursor-pointer transition-all duration-200
                    ${dragging
                      ? 'border-indigo-500 bg-indigo-500/10'
                      : 'border-zinc-700 hover:border-zinc-500 bg-zinc-950 hover:bg-zinc-800/40'
                    }
                  `}
                >
                  <div className="p-4 bg-zinc-800 rounded-2xl border border-zinc-700">
                    <Upload size={28} className="text-zinc-400" />
                  </div>
                  <div className="text-center">
                    <p className="text-sm font-medium text-zinc-300">
                      Arrastra el video aquí o <span className="text-indigo-400 underline">selecciónalo</span>
                    </p>
                    <p className="text-xs text-zinc-500 mt-1">MP4, AVI, MOV, MKV · El agente analizará 1 frame/seg</p>
                  </div>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="video/mp4,video/avi,video/quicktime,video/x-matroska,video/webm"
                    className="hidden"
                    onChange={(e) => handleFile(e.target.files[0])}
                  />
                </div>
              )}

              {/* Error */}
              {error && (
                <p className="mt-2 text-xs text-red-400 bg-red-500/10 px-3 py-2 rounded-lg border border-red-500/20">
                  {error}
                </p>
              )}

              {/* Botón de análisis */}
              <button
                onClick={handleUpload}
                disabled={!file || uploading}
                className={`
                  mt-4 w-full flex items-center justify-center gap-2 py-3 rounded-xl font-semibold text-sm
                  transition-all duration-200 active:scale-[0.98]
                  ${file && !uploading
                    ? 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-600/25'
                    : 'bg-zinc-800 text-zinc-500 cursor-not-allowed'
                  }
                `}
              >
                {uploading
                  ? <><Loader2 size={16} className="animate-spin" /> Subiendo video…</>
                  : <><Play size={16} /> Iniciar Análisis IA</>
                }
              </button>

              {/* Si hay análisis completado, mostrar botón para analizar otro */}
              {isDone && (
                <button
                  onClick={() => { setStatus(null); setFile(null); setPreviewUrl(null); }}
                  className="mt-2 w-full flex items-center justify-center gap-2 py-2.5 rounded-xl text-sm text-zinc-400 hover:text-zinc-200 bg-zinc-800 hover:bg-zinc-700 transition-colors border border-zinc-700/50"
                >
                  <RefreshCw size={14} />
                  Analizar otro video
                </button>
              )}
            </div>
          )}

          {/* Si está procesando, mostrar botón de actualizar manualmente */}
          {isRunning && (
            <button
              onClick={fetchStatus}
              className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl text-sm text-zinc-400 hover:text-zinc-200 bg-zinc-800 hover:bg-zinc-700 transition-colors"
            >
              <RefreshCw size={14} />
              Actualizar estado
            </button>
          )}

        </div>
      </div>
    </div>
  );
}
