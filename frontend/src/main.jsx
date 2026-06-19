/**
 * COPILOTO 360 — App principal
 * main.jsx es el punto de entrada: contiene el sidebar global y renderiza
 * la vista activa según la pestaña seleccionada.
 */
import { StrictMode, useState, useEffect } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'

import Dashboard from './features/dashboard/dashboard.jsx'
import Vehicles  from './features/vehicles/Vehicles.jsx'
import Alerts    from './features/alerts/Alerts.jsx'
import Reports   from './features/reports/Reports.jsx'

import { LayoutDashboard, Car, Bell, FileText, Wifi, WifiOff } from 'lucide-react'

const NAV = [
  { key: 'inicio',    label: 'Inicio',     icon: LayoutDashboard },
  { key: 'vehiculos', label: 'Vehículos',  icon: Car             },
  { key: 'alertas',   label: 'Alertas',    icon: Bell            },
  { key: 'reportes',  label: 'Reportes',   icon: FileText        },
]

function App() {
  const [tab, setTab]         = useState('inicio')
  const [online, setOnline]   = useState(null) // null = checking

  // Verificar si el backend está corriendo
  useEffect(() => {
    const base = import.meta.env.VITE_API_URL ?? ''
    fetch(`${base}/health`)
      .then(() => setOnline(true))
      .catch(() => setOnline(false))
  }, [])

  const renderContent = () => {
    switch (tab) {
      case 'vehiculos': return <Vehicles />
      case 'alertas':   return <Alerts />
      case 'reportes':  return <Reports />
      default:          return <Dashboard />
    }
  }

  return (
    <div className="flex h-screen bg-zinc-950 text-zinc-100 font-sans selection:bg-indigo-500 selection:text-white">

      {/* SIDEBAR GLOBAL */}
      <aside className="w-64 bg-zinc-900 border-r border-zinc-800 flex flex-col justify-between flex-shrink-0">
        <div className="p-6">
          {/* Logo */}
          <div className="flex items-center gap-3 mb-8">
            <div className="h-9 w-9 bg-indigo-600 rounded-lg flex items-center justify-center font-bold text-lg text-white tracking-wider shadow-lg shadow-indigo-600/30">
              S
            </div>
            <div>
              <h1 className="font-bold text-sm leading-tight tracking-tight text-white">Copiloto Sally</h1>
              <p className="text-[10px] text-zinc-500 tracking-widest uppercase">360 Monitor</p>
            </div>
          </div>

          {/* Navegación */}
          <nav className="space-y-1">
            {NAV.map(({ key, label, icon: Icon }) => (
              <button
                key={key}
                onClick={() => setTab(key)}
                className={`w-full flex items-center gap-3 px-4 py-3 font-medium rounded-xl transition-all duration-200 ${
                  tab === key
                    ? 'bg-zinc-800 text-indigo-400'
                    : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50'
                }`}
              >
                <Icon size={20} />
                <span>{label}</span>
                {tab === key && (
                  <span className="ml-auto w-1.5 h-1.5 rounded-full bg-indigo-400" />
                )}
              </button>
            ))}
          </nav>
        </div>

        {/* Footer con estado del backend */}
        <div className="p-4 border-t border-zinc-800 space-y-3">
          {/* Indicador de conexión */}
          <div className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-medium ${
            online === null ? 'text-zinc-500' :
            online          ? 'text-emerald-400 bg-emerald-500/10' : 'text-amber-400 bg-amber-500/10'
          }`}>
            {online === null ? (
              <span className="w-2 h-2 rounded-full bg-zinc-600 animate-pulse" />
            ) : online ? (
              <Wifi size={14} />
            ) : (
              <WifiOff size={14} />
            )}
            <span>
              {online === null ? 'Conectando…' : online ? 'Backend activo' : 'Modo demo (offline)'}
            </span>
          </div>

          {/* Usuario */}
          <div className="flex items-center gap-3 p-2">
            <div className="w-9 h-9 rounded-full bg-zinc-800 border border-zinc-700 flex items-center justify-center font-semibold text-zinc-300 text-sm flex-shrink-0">
              AF
            </div>
            <div className="min-w-0">
              <p className="text-sm font-medium text-zinc-200 truncate">Andrés Navas</p>
              <p className="text-xs text-zinc-500">Administrador</p>
            </div>
          </div>
        </div>
      </aside>

      {/* CONTENIDO DINÁMICO */}
      <div className="flex-1 flex flex-col overflow-y-auto min-w-0">
        {renderContent()}
      </div>

    </div>
  )
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
