# WebGL CAD Viewer/Annotation System - Bootstrap Plan

## Project Vision
Build a lightweight, high-performance CAD viewer with annotation capabilities, focusing on WebGL/WebXR technology. Differentiate through superior mobile performance (proven 3500+ PBR objects at 60fps on iPhone 13) and focused feature set.

## Core Technology Stack

### Supported File Formats
- **STEP/STP** - Primary format with full assembly structure, parts hierarchy, metadata
- **IGES** - Secondary format with hierarchy support
- **GLTF/GLB** - Direct web delivery with scene graph and PBR materials
- *Explicitly not supporting STL/OBJ* - No hierarchy = not suitable for intelligent CAD viewing

### Frontend
- **TypeScript** + **Babylon.js** (WebGL2 rendering)
- WebXR support built-in for future spatial computing
- Your proprietary mesh optimization techniques
- Focus on performance over features

### Backend
- **FastAPI** (async, lightweight, modern Python)
- **FreeCAD**/OpenCASCADE for STEP/IGES conversion (preserves assembly structure)
- **trimesh** for mesh manipulation (scene-aware operations)
- **Celery** + **Redis** for background processing
- Output GLB/glTF with preserved hierarchy for web delivery
- Auth-ready structure (add later when needed)

## Phase 1: MVP (Weeks 1-4)
*Goal: End-to-end pipeline with basic functionality*

### Week 1-2: Backend Pipeline
```python
# Assembly-aware pipeline
STEP file → FreeCAD (preserve hierarchy) → trimesh (scene processing) → GLB with structure
```
- [ ] Setup Python environment with FastAPI, FreeCAD, trimesh
- [ ] Create auth-ready project structure:
  ```
  /app
    /api
      /auth (empty, for future)
      /routers
        conversion.py
        viewer.py
      /models
      /dependencies
    /processing
      step_converter.py
      mesh_processor.py
    /core
      config.py
      security.py (placeholder)
  ```
- [ ] Implement REST API with FastAPI:
  ```python
  from fastapi import FastAPI, UploadFile, Depends
  from typing import Optional
  
  async def get_current_user(token: Optional[str] = None):
      return None  # Auth ready, but returns None for now
  
  @app.post("/convert")
  async def convert(file: UploadFile, user=Depends(get_current_user)):
      # Validate format
      if not file.filename.lower().endswith(('.step', '.stp', '.iges', '.igs')):
          raise HTTPException(400, "Only STEP and IGES files supported")
      # Process file with hierarchy preservation
  ```
- [ ] Setup Celery + Redis for background processing
- [ ] Implement STEP → hierarchical mesh conversion:
  ```python
  # Preserve assembly structure
  doc = FreeCAD.open("assembly.step")
  parts = {}
  for obj in doc.Objects:
      parts[obj.Name] = {
          'mesh': tessellate(obj),
          'transform': obj.Placement.Matrix,
          'parent': obj.InList[0] if obj.InList else None
      }
  ```
- [ ] Add trimesh scene processing:
  - Clean meshes while preserving structure
  - Generate LODs per part
  - Export as GLB with scene graph

### Week 3-4: Frontend Foundation
- [ ] TypeScript + Babylon.js project setup
- [ ] Port your mesh optimization techniques
- [ ] Basic viewer with:
  - Model loading from backend
  - Camera controls (orbit, zoom, pan)
  - PBR material support
  - Performance monitoring overlay
- [ ] Verify 60fps performance with test models

## Phase 2: Core Features (Weeks 5-8)
*Goal: Differentiated functionality*

### Annotation System
- [ ] Part-level annotations (not just arbitrary 3D points)
- [ ] Assembly tree navigation
- [ ] Part selection/highlighting by hierarchy
- [ ] Measurement tools (distance, angle) between parts
- [ ] Cross-section views with assembly awareness
- [ ] BOM generation from assembly structure
- [ ] Annotation persistence linked to part IDs

### Performance Optimizations
- [ ] Implement your proprietary mesh management
- [ ] Progressive loading for large assemblies
- [ ] Frustum culling improvements
- [ ] Instance rendering for repeated parts

## Phase 3: Polish & Differentiation (Weeks 9-12)
*Goal: Something demo-worthy*

### UI/UX
- [ ] Clean, minimal interface
- [ ] Mobile-optimized controls
- [ ] Dark/light mode
- [ ] Loading states and progress indicators

### Advanced Features (Choose 2-3)
- [ ] WebXR mode for VR/AR viewing of assemblies
- [ ] Collaborative sessions with part-level permissions
- [ ] Assembly diff/version comparison
- [ ] Automated BOM extraction with material rollup
- [ ] Kinematic simulation playback (if STEP contains constraints)
- [ ] Part property editing and re-export to STEP

## Technical Architecture

### Backend Structure
```
/app
  /api
    /auth              # Empty initially, ready for FastAPI-Users
      __init__.py      # Placeholder for future auth
    /routers
      conversion.py    # Upload/conversion endpoints (STEP/IGES only)
      viewer.py        # Viewer-specific endpoints
      annotations.py   # Part-based annotation CRUD
      assembly.py      # Assembly tree, BOM endpoints
    /models
      file.py          # Pydantic models
      annotation.py    
      assembly.py      # Part hierarchy models
    /dependencies
      auth.py          # get_current_user (returns None initially)
  
  /processing
    step_converter.py  # FreeCAD wrapper (preserves hierarchy)
    mesh_processor.py  # trimesh scene operations
    hierarchy_extractor.py  # Extract assembly structure
    tasks.py          # Celery tasks
    
  /core
    config.py         # Settings, env variables
    security.py       # Placeholder for JWT/auth logic
    
  main.py            # FastAPI app initialization
  celery_app.py      # Celery configuration
```

### Example Assembly-Aware Endpoint
```python
from fastapi import APIRouter, HTTPException
from typing import List, Dict

router = APIRouter()

@router.get("/model/{model_id}/assembly")
async def get_assembly_tree(model_id: str):
    """Return hierarchical assembly structure"""
    # Returns actual CAD structure, not just mesh blob
    return {
        "root": {
            "id": "assembly_1",
            "name": "Main Assembly",
            "children": [
                {
                    "id": "part_1", 
                    "name": "Bracket",
                    "transform": [...],
                    "material": "steel"
                },
                {
                    "id": "subassembly_1",
                    "name": "Motor Assembly",
                    "children": [...]
                }
            ]
        }
    }

@router.post("/model/{model_id}/part/{part_id}/annotate")
async def annotate_part(model_id: str, part_id: str, annotation: dict):
    """Annotations linked to actual parts, not arbitrary positions"""
    # This is what makes it powerful for engineering
    pass
```

### Frontend Structure
```
/src
  /viewer
    BabylonViewer.ts - Main viewer class
    MeshOptimizer.ts - Your performance tricks
    AnnotationManager.ts
  /ui
    Controls.tsx
    AnnotationPanel.tsx
  /api
    ApiClient.ts
```

## Development Principles

1. **Performance First**: Every feature must maintain 60fps on mobile
2. **Start Simple**: File upload → view → annotate. Nothing more initially.
3. **Cache Aggressively**: STEP conversion is slow, cache everything
4. **Fail Fast**: If it doesn't work in 2 weeks, pivot
5. **Dog Food**: Use it for your own CAD files immediately
6. **Auth When Needed**: Build auth-ready, but don't implement until you have users
7. **Assembly-Aware**: Preserve CAD hierarchy - we're not another dumb mesh viewer

## MVP Success Metrics
- Loads 100MB STEP file in < 30 seconds
- Maintains 60fps with 5000+ objects on mobile
- Basic annotations work reliably
- Cleaner UX than current employer's product
- You enjoy working on it

## Resource Requirements

### Minimal Costs
- Domain name: $12/year
- Basic VPS for backend: $20/month (DigitalOcean/Linode)
- Object storage for cache: $5/month
- Total: ~$25/month until you need scale

### Time Investment
- 10-15 hours/week on nights/weekends
- Focus on 2-hour focused sessions
- One feature per session

## Risk Mitigation

### Technical Risks
- **STEP conversion complexity**: Start with simple parts, not assemblies
- **Performance regression**: Automated performance tests from day 1
- **Browser compatibility**: Target Chrome/Edge first, others later

### Business Risks
- **Current employer IP concerns**: 
  - Different tech stack (TypeScript vs their JS, Python vs Go)
  - Different focus (lightweight vs broad)
  - Document all work done on personal time
- **Market timing**: If you're not excited to use it yourself, pivot

## Phase 4: Authentication & User Management (When Needed)
*Goal: Add auth only when you have something worth protecting*

### Trigger Points for Adding Auth (any of these):
- You have 10+ regular users
- Someone wants to pay for private models
- You need to track usage per user
- You want to sell subscriptions

### Implementation Plan (1 weekend when ready):
- [ ] Install FastAPI-Users or similar
- [ ] Update `get_current_user` dependency
- [ ] Add registration/login endpoints
- [ ] Add JWT token handling
- [ ] Update frontend with login flow
- [ ] Migrate anonymous uploads to user accounts

```python
# The beauty: Your existing code barely changes
from fastapi_users import FastAPIUsers

# Update the dependency
async def get_current_user(token: str = Depends(oauth2_scheme)):
    # Now returns actual user instead of None
    return await user_manager.get_current_user(token)

# Your existing endpoints just start working with auth!
```

### Week 4 Checkpoint
- Can you load and view a STEP file end-to-end?
- Is performance acceptable on mobile?
- Are you enjoying the development?

If no to any → reassess approach

### Week 8 Checkpoint  
- Do you have something better than your work's viewer?
- Has anyone else tried it and been impressed?
- Can you see a path to charging money for this?

If no to all → keep as hobby project only

### Week 12 Checkpoint
- Is this good enough to show potential customers?
- Could this replace your salary if needed?
- Do you want to continue?

If yes → consider next steps (incorporation, serious customer development)

## Next Steps

### This Weekend
1. Setup development environment
2. Get "Hello World" with Babylon.js + TypeScript
3. Get "Hello World" with FastAPI (with auth-ready structure)
4. Test FreeCAD + trimesh pipeline with one STEP file
5. Create GitHub repo (private initially)

### Example Day 1 FastAPI Setup
```bash
# Setup project
pip install fastapi uvicorn celery redis trimesh
mkdir cad-viewer && cd cad-viewer

# Create main.py
from fastapi import FastAPI
from app.api.routers import conversion, viewer

app = FastAPI(title="CAD Viewer API")
app.include_router(conversion.router)
app.include_router(viewer.router)

# Run it
uvicorn main:app --reload
```

### Next Week
1. Wire up basic upload/convert/download flow
2. Display first CAD model in browser
3. Verify performance meets expectations

### Success Looks Like
- You're excited to work on it after your day job
- Each session produces visible progress
- In 3 months, you have something you're proud to show
- Your "parachute" is packed and ready if needed

---

*Remember: This is a marathon, not a sprint. Small, consistent progress beats burnout. The goal is to build something you're proud of that could potentially become your next venture - or just remain an enjoyable technical challenge that keeps your skills sharp.*