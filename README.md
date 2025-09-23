# CAD Viewer

A BabylonJS-based single-page application for viewing CAD files with user authentication and file management.

## Tech Stack

- **Frontend**: BabylonJS, TypeScript, Vite
- **Backend**: Python, FastAPI, SQLModel
- **Database**: SQLite (dev), PostgreSQL (production)
- **Deployment**: Vercel

## Quick Start

### Prerequisites

- Node.js 18+
- Python 3.9+
- Git

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd CadViewer
```

2. Install frontend dependencies:
```bash
npm install
```

3. Install backend dependencies:
```bash
cd backend
pip install -r requirements.txt
cd ..
```

### Development

Run both frontend and backend servers:

#### Terminal 1 - Frontend (Vite):
```bash
npm run dev
```
The frontend will be available at http://localhost:5173

#### Terminal 2 - Backend (FastAPI):
```bash
cd backend
python main.py
```
The API will be available at http://localhost:8000
API documentation at http://localhost:8000/docs

## Features

### Current (Phase 1)
- ✅ BabylonJS 3D viewer
- ✅ GLTF/GLB file support
- ✅ User authentication (JWT)
- ✅ File upload and management
- ✅ Basic viewer controls (reset view, toggle grid)

### Planned
- 🎭 Interactive Scene Builder (Phase 9)
- 🧩 Component System (Phase 10)
- ⚡ Performance optimizations (Phase 11)

## Project Structure

```
CadViewer/
├── src/                    # Frontend source
│   ├── viewer/            # BabylonJS viewer
│   ├── auth/              # Authentication
│   ├── files/             # File management
│   └── styles/            # CSS styles
├── backend/               # FastAPI backend
│   ├── main.py           # API entry point
│   ├── models.py         # Database models
│   ├── auth.py           # Authentication logic
│   └── uploads/          # Uploaded files
├── package.json          # Frontend dependencies
├── requirements.txt      # Backend dependencies
└── BOOTSTRAP_PLAN.md     # Detailed development plan
```

## Supported File Formats

- GLTF (.gltf)
- GLB (.glb)
- Babylon (.babylon)
- OBJ (.obj)
- STL (.stl)

## Environment Variables

Create a `.env` file in the backend directory:

```env
DATABASE_URL=sqlite:///./cadviewer.db
SECRET_KEY=your-secret-key-change-in-production
```

## License

MIT