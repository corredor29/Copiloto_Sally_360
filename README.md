# 🚛 COPILOTO 360 — Sistema de Vigilancia Inteligente para Transporte

> Agente visual autónomo que detecta anomalías en conductores y vías usando YOLO + GPT-4o + FiftyOne, con dashboard en tiempo real para el centro de control.

---

## 📋 Requisitos previos — Instalar en TODAS las máquinas

### 1. Python 3.11.9
```
https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe
```
> ⚠️ Al instalar marcar **"Add Python to PATH"** ✅

Verificar:
```bash
py -3.11 --version
# Python 3.11.9 ✅
```

---

### 2. Node.js 20 LTS
```
https://nodejs.org/en
```
> Descargar el botón que dice **LTS**

Verificar:
```bash
node --version   # v20.x.x ✅
npm --version    # 10.x.x ✅
```

---

### 3. MongoDB 7.0.37
```
https://www.mongodb.com/try/download/community
```
> Elegir: Version 7.0 | Windows | msi
> Al instalar seleccionar **"Run service as Network Service user"** ✅

Verificar:
```bash
mongod --version
# db version v7.0.37 ✅

Get-Service -Name MongoDB
# Status: Running ✅
```

> Si no está corriendo:
```bash
Start-Service -Name MongoDB
```

---

### 4. Git
```
https://git-scm.com/downloads
```

Verificar:
```bash
git --version
# git version 2.x.x ✅
```

---

### 5. API Key de OpenAI
```
https://platform.openai.com/api-keys
```
> Crear cuenta → API Keys → Create new secret key
> Guardarla, la necesitan para el `.env`

---

## 🚀 Instalación del proyecto

### Clonar el repositorio

```bash
git clone https://github.com/equipo/copiloto-360.git
cd copiloto-360
```

---

## 🐍 Personas 1, 2 y 3 — Backend (Python)

```bash
# 1. Entrar a la carpeta backend
cd backend

# 2. Crear entorno virtual con Python 3.11
py -3.11 -m venv venv

# 3. Activar el entorno virtual
.\venv\Scripts\activate        # Windows
source venv/bin/activate       # Linux/Mac

# 4. Verificar que usa Python 3.11
python --version
# Python 3.11.9 ✅

# 5. Actualizar pip
pip install --upgrade pip

# 6. Instalar dependencias
pip install fiftyone ultralytics openai fastapi uvicorn python-dotenv pillow numpy opencv-python

# 7. Configurar variables de entorno
cp .env.example .env
# Abrir .env y rellenar OPENAI_API_KEY con la key real

# 8. Verificar instalaciones
python -c "import fiftyone; print('✅ FiftyOne:', fiftyone.__version__)"
python -c "import ultralytics; print('✅ YOLO:', ultralytics.__version__)"
python -c "import fastapi; print('✅ FastAPI:', fastapi.__version__)"
python -c "import cv2; print('✅ OpenCV:', cv2.__version__)"

# 9. Correr el backend
python main.py
# → API corriendo en http://localhost:8000 ✅
# → Docs en http://localhost:8000/docs ✅
```

---

## ⚛️ Personas 4 y 5 — Frontend (React + Tailwind)

```bash
# 1. Entrar a la carpeta frontend
cd frontend

# 2. Crear proyecto Vite + React
npm create vite@latest . -- --template react
# Cuando pregunte → "Ignore files and continue"

# 3. Instalar dependencias base
npm install

# 4. Instalar Tailwind
npm install -D tailwindcss @tailwindcss/vite

# 5. Instalar librerías del proyecto
npm install axios @tanstack/react-query react-router-dom

# 6. Configurar vite.config.js — reemplazar todo con:
```

```javascript
// vite.config.js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
})
```

```bash
# 7. Configurar src/index.css — borrar todo y dejar solo:
```

```css
@import "tailwindcss";
```

```bash
# 8. Configurar variables de entorno
cp .env.example .env.local
# Ya tiene todo configurado, no hay que cambiar nada

# 9. Correr el frontend
npm run dev
# → App corriendo en http://localhost:5173 ✅
```

---

## 🌐 Puertos de cada servicio

| Servicio | Puerto | URL |
|----------|--------|-----|
| **MongoDB** | 27017 | `mongodb://localhost:27017` |
| **FastAPI backend** | 8000 | `http://localhost:8000` |
| **FastAPI docs** | 8000 | `http://localhost:8000/docs` |
| **FiftyOne App** | 5151 | `http://localhost:5151` |
| **React frontend** | 5173 | `http://localhost:5173` |

---

## 🖥️ Orden para arrancar el proyecto

Abrir **4 terminales separadas**:

```bash
# ── Terminal 1: MongoDB (si no corre como servicio) ──
Start-Service -Name MongoDB

# ── Terminal 2: Backend Python ───────────────────────
cd backend
.\venv\Scripts\activate
python main.py
# → http://localhost:8000 ✅

# ── Terminal 3: FiftyOne App ─────────────────────────
cd backend
.\venv\Scripts\activate
python -c "
import fiftyone as fo
session = fo.launch_app(port=5151)
session.wait()
"
# → http://localhost:5151 ✅

# ── Terminal 4: Frontend React ───────────────────────
cd frontend
npm run dev
# → http://localhost:5173 ✅
```

---

## 👥 División del equipo

| Persona | Rama | Módulo | Responsabilidad |
|---------|------|--------|-----------------|
| **Persona 1** | `feature/agent-vision` | `modules/agent/` + `modules/vision/` | YOLO + GPT-4o + lógica de alertas |
| **Persona 2** | `feature/dataset` | `modules/dataset/` | FiftyOne — carga y etiquetado |
| **Persona 3** | `feature/api` | `modules/api/` | FastAPI — todos los endpoints |
| **Persona 4** | `feature/alerts-vehicles` | `features/alerts/` + `features/vehicles/` | Alertas y vehículos en React |
| **Persona 5** | `feature/dashboard` | `features/dashboard/` + `features/reports/` | Dashboard y reportes |

---

## 🌿 Git Workflow

```bash
# Setup inicial (una persona)
git checkout -b develop
git push origin develop

# Cada persona crea su rama desde develop
git checkout develop
git pull origin develop
git checkout -b feature/tu-rama
git push origin feature/tu-rama
```

### Reglas del equipo
- ✅ Todo entra a `develop` por **Pull Request** — nunca merge directo
- ✅ Un integrante aprueba antes de mergear
- ✅ Al final del día → PR de `develop` a `main`
- ❌ Nunca push directo a `develop` ni `main`

> # 🚨 REGLA DE ORO
> **Cuando tu PR entre a develop → AVISA AL EQUIPO INMEDIATAMENTE**
> Los otros 4 deben hacer:
> ```bash
> git fetch origin
> git rebase origin/develop
> git push origin feature/tu-rama --force-with-lease
> ```

---

## 📂 Estructura del proyecto

```
copiloto-360/
│
├── backend/
│   ├── modules/
│   │   ├── agent/              # Persona 1 — orquesta YOLO + GPT-4o
│   │   ├── vision/             # Persona 1 — YOLO + GPT-4o + parser
│   │   ├── dataset/            # Persona 2 — FiftyOne
│   │   └── api/                # Persona 3 — FastAPI
│   ├── data/
│   │   ├── raw/                # Frames de cámaras (no va a git)
│   │   └── outputs/            # Reportes generados
│   ├── plugins/
│   ├── .env.example            # ✅ Va a git
│   ├── .env                    # ❌ NUNCA a git
│   ├── requirements.txt
│   └── main.py
│
├── frontend/
│   ├── src/
│   │   ├── features/
│   │   │   ├── alerts/         # Persona 4
│   │   │   ├── vehicles/       # Persona 4
│   │   │   ├── dashboard/      # Persona 5
│   │   │   ├── reports/        # Persona 5
│   │   │   └── agent/          # Persona 5
│   │   ├── components/
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── .env.example            # ✅ Va a git
│   ├── .env.local              # ❌ NUNCA a git
│   ├── package.json
│   └── vite.config.js
│
├── .gitignore
└── README.md
```

---

## 🔑 Variables de entorno

### `backend/.env`
```env
OPENAI_API_KEY=sk-...
FIFTYONE_DATABASE_URI=mongodb://localhost:27017
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
RELOAD=True
ALLOWED_ORIGINS=http://localhost:5173
DATA_DIR=./data
```

### `frontend/.env.local`
```env
VITE_API_URL=http://localhost:8000
VITE_FIFTYONE_URL=http://localhost:5151
```

---

## ✅ Checklist de versiones

| Herramienta | Versión | Verificar con |
|-------------|---------|---------------|
| **Python** | 3.11.9 | `py -3.11 --version` |
| **Node.js** | 20.x LTS | `node --version` |
| **npm** | 10.x | `npm --version` |
| **MongoDB** | 7.0.37 | `mongod --version` |
| **Git** | 2.40+ | `git --version` |
| **fiftyone** | latest | `pip show fiftyone` |
| **ultralytics** | latest | `pip show ultralytics` |
| **openai** | ≥1.0.0 | `pip show openai` |
| **fastapi** | ≥0.110.0 | `pip show fastapi` |

---

## ⚠️ Notas importantes

- **Python 3.14 NO funciona** con FiftyOne — usar siempre `py -3.11`
- **Nunca subir `.env`** ni `.env.local` a git
- **Avisar al equipo** cada vez que se mergee a `develop`
- Los frames en `data/raw/` **no se suben a git** — son pesados
- Los modelos YOLO (`.pt`) **no se suben a git** — se descargan automáticamente

---

> 🐍 Python 3.11.9 | ⚛️ React + Vite + Tailwind | 🍃 MongoDB 7.0.37 | ⚡ FastAPI | 🎯 YOLO + GPT-4o + FiftyOne