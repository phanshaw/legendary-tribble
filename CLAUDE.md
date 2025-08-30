# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a WebGL CAD Viewer/Annotation System project in early development stages. The project aims to build a lightweight, high-performance CAD viewer with annotation capabilities using WebGL/WebXR technology.

## Project Structure

```
CadViewer/
├── main.py                        # FastAPI application entry point
├── test_main.http                 # HTTP test file for API endpoints
├── bootstrap_plan/                
│   └── bootstrap_plan.md          # Detailed project roadmap and architecture
└── example_data_input/
    └── radial-engine-assy.stp     # Example STEP CAD file for testing
```

## Current State

The project is in initial setup phase with a basic FastAPI application containing two endpoints:
- `GET /` - Root endpoint returning Hello World
- `GET /hello/{name}` - Parameterized greeting endpoint

## Development Commands

### Running the FastAPI Application
```bash
# Install FastAPI and Uvicorn if not already installed
pip install fastapi uvicorn

# Run the application with auto-reload
uvicorn main:app --reload

# The API will be available at http://127.0.0.1:8000
```

### Testing Endpoints
Use the `test_main.http` file with an HTTP client that supports `.http` files (like VS Code REST Client extension), or test manually:
- Root endpoint: `http://127.0.0.1:8000/`
- Hello endpoint: `http://127.0.0.1:8000/hello/YourName`

## Planned Architecture

According to the bootstrap plan, this project will evolve into:

### Backend (Python/FastAPI)
- **Core Technologies**: FastAPI, FreeCAD/OpenCASCADE, trimesh, Celery + Redis
- **Processing Pipeline**: STEP file → FreeCAD (tessellation) → trimesh (optimization) → GLB export
- **Key Features**: 
  - Async REST API with auth-ready structure
  - Background processing for CAD file conversion
  - Mesh optimization and LOD generation
  - Annotation persistence

### Frontend (TypeScript/Babylon.js)
- **Core Technologies**: TypeScript, Babylon.js (WebGL2), WebXR support
- **Key Features**:
  - High-performance mesh rendering (target: 60fps with 5000+ objects on mobile)
  - 3D annotations and measurements
  - Progressive loading for large assemblies

## Important Development Notes

1. **Performance First**: Every feature must maintain 60fps on mobile devices
2. **Auth Structure**: The project is designed to be auth-ready but authentication is not implemented initially. Auth dependencies return `None` until needed.
3. **CAD Processing**: The main technical challenge is STEP file conversion and mesh optimization
4. **Target Metrics**: 
   - Load 100MB STEP file in < 30 seconds
   - Maintain 60fps with 5000+ objects on mobile

## Next Steps

Refer to `bootstrap_plan/bootstrap_plan.md` for the detailed development roadmap. The immediate priorities are:
1. Setting up the Python environment with required dependencies
2. Implementing the STEP → GLB conversion pipeline
3. Creating the basic viewer with Babylon.js