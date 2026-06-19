import { StrictMode, useState, useEffect } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'

import Dashboard from './features/dashboard/dashboard.jsx'
import Vehicles  from './features/vehicles/Vehicles.jsx'
import Alerts    from './features/alerts/Alerts.jsx'
import Reports   from './features/reports/Reports.jsx'

import { LayoutDashboard, Car, Bell, FileText, Wifi, WifiOff, Menu, X } from 'lucide-react'

const NAV = [
  { key: 'inicio',    label: 'Inicio',     icon: LayoutDashboard },
  { key: 'vehiculos', label: 'Vehículos',  icon: Car             },
  { key: 'alertas',   label: 'Alertas',    icon: Bell            },
  { key: 'reportes',  label: 'Reportes',   icon: FileText        },
]

function App() {
  const [tab,         setTab]         = useState('inicio')
  const [online,      setOnline]      = useState(null)
  const [sidebarOpen, setSidebarOpen] = useState(false)

  useEffect(() => {
    const base = import.meta.env.VITE_API_URL ?? ''
    fetch(`${base}/health`)
      .then(() => setOnline(true))
      .catch(() => setOnline(false))
  }, [])

  // Cerrar drawer con Escape
  useEffect(() => {
    if (!sidebarOpen) return
    const handler = (e) => { if (e.key === 'Escape') setSidebarOpen(false) }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [sidebarOpen])

  const navigate = (key) => {
    setTab(key)
    setSidebarOpen(false)
  }

  const renderContent = () => {
    switch (tab) {
      case 'vehiculos': return <Vehicles />
      case 'alertas':   return <Alerts />
      case 'reportes':  return <Reports />
      default:          return <Dashboard />
    }
  }

  const connectionBadge = (
    <div className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-medium ${
      online === null ? 'text-zinc-500' :
      online          ? 'text-emerald-400 bg-emerald-500/10' : 'text-amber-400 bg-amber-500/10'
    }`}>
      {online === null
        ? <span className="w-2 h-2 rounded-full bg-zinc-600 animate-pulse" />
        : online ? <Wifi size={14} /> : <WifiOff size={14} />
      }
      <span>{online === null ? 'Conectando…' : online ? 'Backend activo' : 'Modo demo (offline)'}</span>
    </div>
  )

  const navMenu = (
    <nav className="space-y-1">
      {NAV.map(({ key, label, icon: Icon }) => (
        <button
          key={key}
          onClick={() => navigate(key)}
          className={`w-full flex items-center gap-3 px-4 py-3 font-medium rounded-xl transition-all duration-200 ${
            tab === key
              ? 'bg-zinc-800 text-indigo-400'
              : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50'
          }`}
        >
          <Icon size={20} />
          <span>{label}</span>
          {tab === key && <span className="ml-auto w-1.5 h-1.5 rounded-full bg-indigo-400" />}
        </button>
      ))}
    </nav>
  )

  const sidebarFooter = (
    <div className="p-4 border-t border-zinc-800 space-y-3 flex-shrink-0">
      {connectionBadge}
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
  )

  return (
    <div className="flex flex-col h-screen bg-zinc-950 text-zinc-100 font-sans selection:bg-indigo-500 selection:text-white">

      {/* TOP BAR MOBILE */}
      <header className="lg:hidden h-14 bg-zinc-900 border-b border-zinc-800 px-4 flex items-center justify-between flex-shrink-0 z-30">
        <button
          onClick={() => setSidebarOpen(true)}
          className="p-2 rounded-xl text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 transition-colors"
          aria-label="Abrir menú"
        >
          <Menu size={20} />
        </button>

        <div className="flex items-center gap-2">
          <div className="h-6 w-6 bg-indigo-600 rounded flex items-center justify-center font-bold text-xs text-white shadow-md shadow-indigo-600/30">
            S
          </div>
          <span className="font-bold text-sm text-white">Copiloto Sally</span>
        </div>

        <div className={`flex items-center ${
          online === null ? 'text-zinc-500' : online ? 'text-emerald-400' : 'text-amber-400'
        }`}>
          {online === null
            ? <span className="w-2 h-2 rounded-full bg-zinc-600 animate-pulse block" />
            : online ? <Wifi size={16} /> : <WifiOff size={16} />
          }
        </div>
      </header>

      {/* LAYOUT PRINCIPAL */}
      <div className="flex flex-1 overflow-hidden">

        {/* SIDEBAR DESKTOP (lg+) */}
        <aside className="hidden lg:flex w-64 bg-zinc-900 border-r border-zinc-800 flex-col justify-between flex-shrink-0">
          <div className="p-6">
            <div className="flex items-center gap-3 mb-8">
              <div className="h-9 w-9 bg-indigo-600 rounded-lg flex items-center justify-center font-bold text-lg text-white tracking-wider shadow-lg shadow-indigo-600/30">
                S
              </div>
              <div>
                <h1 className="font-bold text-sm leading-tight tracking-tight text-white">Copiloto Sally</h1>
                <p className="text-[10px] text-zinc-500 tracking-widest uppercase">360 Monitor</p>
              </div>
            </div>
            {navMenu}
          </div>
          {sidebarFooter}
        </aside>

        {/* OVERLAY DRAWER MOBILE */}
        {sidebarOpen && (
          <div
            className="fixed inset-0 z-40 bg-black/70 backdrop-blur-sm lg:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}

        {/* DRAWER PANEL MOBILE */}
        <aside className={`
          fixed inset-y-0 left-0 z-50 w-64 bg-zinc-900 border-r border-zinc-800
          flex flex-col flex-shrink-0
          transform transition-transform duration-300 ease-in-out lg:hidden
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        `}>
          {/* Header drawer con logo + botón cerrar */}
          <div className="flex items-center justify-between px-6 py-4 border-b border-zinc-800 flex-shrink-0">
            <div className="flex items-center gap-3">
              <div className="h-9 w-9 bg-indigo-600 rounded-lg flex items-center justify-center font-bold text-lg text-white shadow-lg shadow-indigo-600/30">
                S
              </div>
              <div>
                <h1 className="font-bold text-sm leading-tight tracking-tight text-white">Copiloto Sally</h1>
                <p className="text-[10px] text-zinc-500 tracking-widest uppercase">360 Monitor</p>
              </div>
            </div>
            <button
              onClick={() => setSidebarOpen(false)}
              className="p-2 rounded-xl text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 transition-colors"
              aria-label="Cerrar menú"
            >
              <X size={18} />
            </button>
          </div>

          {/* Nav scrollable */}
          <div className="flex-1 overflow-y-auto p-6">
            {navMenu}
          </div>

          {sidebarFooter}
        </aside>

        {/* CONTENIDO DINÁMICO */}
        <div className="flex-1 flex flex-col overflow-y-auto min-w-0">
          {renderContent()}
        </div>

      </div>
    </div>
  )
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
