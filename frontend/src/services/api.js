/**
 * COPILOTO 360 — Capa de servicios API
 * services/api.js
 *
 * Todas las llamadas al backend pasan por aquí.
 * Si el backend no está disponible, se usan datos de demo para que el frontend funcione igual.
 */

// Con el proxy de Vite activo en dev, BASE_URL puede ser '' (relativo).
// En producción o sin proxy, se lee VITE_API_URL del .env.local.
const BASE_URL = import.meta.env.VITE_API_URL ?? '';

// ── Utilidad base ─────────────────────────────────────────────────────────────

async function apiFetch(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `Error ${res.status}`);
  }
  return res.json();
}

// ── DATOS DE DEMO (fallback cuando el backend no está corriendo) ──────────────

const DEMO = {
  vehicles: {
    total: 5,
    vehiculos: [
      { vehiculo_id: 'CAM-001', estado_actual: { nivel: 'bajo',    conductor: 'normal',   via: 'normal'   } },
      { vehiculo_id: 'FUR-009', estado_actual: { nivel: 'medio',   conductor: 'distraido', via: 'normal'   } },
      { vehiculo_id: 'CAM-004', estado_actual: { nivel: 'critico', conductor: 'dormido',  via: 'lluvia'   } },
      { vehiculo_id: 'BUS-012', estado_actual: { nivel: 'alto',    conductor: 'normal',   via: 'curva'    } },
      { vehiculo_id: 'CAM-003', estado_actual: { nivel: 'bajo',    conductor: 'normal',   via: 'normal'   } },
    ],
  },
  alerts: {
    total: 5,
    alertas: [
      { vehiculo_id: 'CAM-004', nivel: 'critico', mensaje: 'Conductor con somnolencia detectada',   conductor_estado: 'dormido',   via_estado: 'lluvia',  frame: 42  },
      { vehiculo_id: 'FUR-009', nivel: 'alto',    mensaje: 'Conductor distraído — ojos fuera de la vía', conductor_estado: 'distraido', via_estado: 'normal',  frame: 18  },
      { vehiculo_id: 'BUS-012', nivel: 'medio',   mensaje: 'Velocidad elevada en curva peligrosa', conductor_estado: 'normal',    via_estado: 'curva',   frame: 7   },
      { vehiculo_id: 'CAM-001', nivel: 'bajo',    mensaje: 'Mantenimiento preventivo sugerido',    conductor_estado: 'normal',    via_estado: 'normal',  frame: 91  },
      { vehiculo_id: 'CAM-003', nivel: 'bajo',    mensaje: 'GPS con batería al 12%',               conductor_estado: 'normal',    via_estado: 'normal',  frame: 3   },
    ],
  },
  reports: {
    total: 4,
    reportes: [
      { archivo: 'reporte_CAM-004_20260619.json', vehiculo_id: 'CAM-004', total_frames: 120, resumen: { critico: 3, alto: 5, medio: 8, bajo: 104 }, generado_en: '2026-06-19T14:30:00', tamaño_bytes: 24800 },
      { archivo: 'reporte_FUR-009_20260618.json', vehiculo_id: 'FUR-009', total_frames: 85,  resumen: { critico: 0, alto: 2, medio: 4, bajo: 79  }, generado_en: '2026-06-18T10:15:00', tamaño_bytes: 18200 },
      { archivo: 'reporte_BUS-012_20260617.json', vehiculo_id: 'BUS-012', total_frames: 200, resumen: { critico: 1, alto: 3, medio: 12, bajo: 184 }, generado_en: '2026-06-17T16:45:00', tamaño_bytes: 41000 },
      { archivo: 'reporte_CAM-001_20260615.json', vehiculo_id: 'CAM-001', total_frames: 60,  resumen: { critico: 0, alto: 0, medio: 1,  bajo: 59  }, generado_en: '2026-06-15T09:00:00', tamaño_bytes: 9600  },
    ],
  },
  agentStatus: {
    disponible: true, ocupado: false, vehiculo_id: null,
    frames_total: 0, frames_procesados: 0, progreso_pct: 0, ultimo_nivel: null, error: null,
  },
};

// ── API pública ───────────────────────────────────────────────────────────────

export async function fetchVehicles() {
  try {
    return await apiFetch('/vehicles/');
  } catch {
    console.warn('[API] Backend no disponible → usando datos de demo');
    return DEMO.vehicles;
  }
}

export async function fetchVehicleById(id) {
  try {
    return await apiFetch(`/vehicles/${id}`);
  } catch {
    const v = DEMO.vehicles.vehiculos.find(v => v.vehiculo_id === id);
    return { vehiculo_id: id, estado_actual: v?.estado_actual || {}, historial: [], resumen_alertas: {} };
  }
}

export async function fetchAlerts(filtros = {}) {
  try {
    const params = new URLSearchParams();
    if (filtros.vehiculo_id) params.set('vehiculo_id', filtros.vehiculo_id);
    if (filtros.nivel)       params.set('nivel', filtros.nivel);
    return await apiFetch(`/alerts/?${params}`);
  } catch {
    console.warn('[API] Backend no disponible → usando datos de demo');
    let alertas = DEMO.alerts.alertas;
    if (filtros.nivel) alertas = alertas.filter(a => a.nivel === filtros.nivel);
    return { total: alertas.length, alertas };
  }
}

export async function fetchCriticalAlerts() {
  try {
    return await apiFetch('/alerts/criticas');
  } catch {
    const criticas = DEMO.alerts.alertas.filter(a => a.nivel === 'critico');
    return { total: criticas.length, alertas: criticas };
  }
}

export async function fetchReports() {
  try {
    return await apiFetch('/reports/');
  } catch {
    console.warn('[API] Backend no disponible → usando datos de demo');
    return DEMO.reports;
  }
}

export async function generateReport(vehiculo_id, ruta_video, fps_deseados = 1.0) {
  return apiFetch('/reports/generate', {
    method: 'POST',
    body: JSON.stringify({ vehiculo_id, ruta_video, fps_deseados }),
  });
}

export async function fetchAgentStatus() {
  try {
    return await apiFetch('/agent/status');
  } catch {
    return DEMO.agentStatus;
  }
}

export async function runAgent(vehiculo_id, filepath) {
  return apiFetch('/agent/run', {
    method: 'POST',
    body: JSON.stringify({ vehiculo_id, filepath }),
  });
}

// ── Helpers ───────────────────────────────────────────────────────────────────

/** Devuelve clase de color Tailwind según nivel de alerta */
export function nivelColor(nivel) {
  switch (nivel) {
    case 'critico': return { text: 'text-red-400',    bg: 'bg-red-500/10',    border: 'border-red-500/20',    dot: 'bg-red-500'    };
    case 'alto':    return { text: 'text-orange-400', bg: 'bg-orange-500/10', border: 'border-orange-500/20', dot: 'bg-orange-500' };
    case 'medio':   return { text: 'text-amber-400',  bg: 'bg-amber-500/10',  border: 'border-amber-500/20',  dot: 'bg-amber-500'  };
    default:        return { text: 'text-blue-400',   bg: 'bg-blue-500/10',   border: 'border-blue-500/20',   dot: 'bg-blue-500'   };
  }
}

/** Formatea timestamp ISO a fecha legible en español */
export function formatDate(isoStr) {
  if (!isoStr) return '—';
  return new Date(isoStr).toLocaleDateString('es-CO', {
    day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit'
  });
}

/** Formatea bytes a texto legible */
export function formatBytes(bytes) {
  if (!bytes) return '—';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}
