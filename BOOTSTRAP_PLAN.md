# CAD Viewer Bootstrap Plan

## Project Overview
A BabylonJS-based single-page application for viewing CAD files with user authentication, file management, and cloud deployment via Vercel.

## Technology Stack
- **Frontend**: BabylonJS, TypeScript, Vite
- **Backend**: Python, FastAPI, SQLModel (SQLAlchemy + Pydantic)
- **Database**: PostgreSQL with JSONB fields (production), SQLite (development)
- **Authentication**: JWT tokens with refresh mechanism
- **File Storage**: Local (development), Vercel Blob/S3 (production)
- **Deployment**: Vercel (frontend + serverless backend)

---

## Phase 1: Project Foundation & Development Environment
**Goal**: Establish project structure and development tooling

### Tasks
- [x] Initialize Git repository
- [x] Set up frontend project with Vite + TypeScript
- [x] Set up Python backend with FastAPI
- [x] Configure development environment files (.env, .gitignore)
- [x] Create project structure directories
- [x] Install core dependencies
 
### Deliverables
- Basic project structure
- Package configuration files (package.json, requirements.txt)
- Development server scripts
- Environment configuration

### Success Criteria
- Frontend dev server runs on localhost:5173
- Backend API runs on localhost:8000
- Git repository initialized with proper .gitignore

---

## Phase 2: BabylonJS Viewer Core
**Goal**: Implement basic 3D viewer functionality

### Tasks
- [x] Create BabylonJS scene initialization
- [x] Implement camera controls (arc rotate camera)
- [x] Add lighting system (hemispheric + directional)
- [x] Add skybox /environment lighting. 
- [x] Create grid/ground helper
- [x] Implement basic file loader for GLTF/GLB
- [x] Add viewer controls (reset view, toggle grid)

### Deliverables
- Functional 3D viewer component
- File loading capability for GLTF/GLB formats
- Basic viewer controls UI

### Success Criteria
- Can load and display 3D models
- Camera controls work smoothly
- Grid toggle functionality works

---

## Phase 3: Frontend UI & File Management
**Goal**: Build user interface and file handling

### Tasks
- [ ] Design and implement navigation bar
- [x] Create file upload interface
- [x] Build basic file list sidebar
- [x] Implement drag-and-drop file upload
- [x] Add file format validation

### Deliverables
- Complete UI layout
- File upload system
- File management interface
- Responsive design

### Success Criteria
- Files can be uploaded via button or drag-and-drop
- File list displays uploaded files
- UI is responsive on desktop and tablet

---

## Phase 4: Backend Core Setup
**Goal**: Establish FastAPI backend with extensible database architecture

### Tasks
- [ ] Set up FastAPI application structure
- [ ] **CRITICAL: Configure SQLModel for type-safe, extensible models**
- [ ] **CRITICAL: Design extensible base model with JSON metadata fields**
- [ ] Create initial database models (User, File, Session) with metadata fields
- [ ] **CRITICAL: Design Scene and Component models with JSONB storage**
- [ ] **CRITICAL: Implement hybrid schema approach (stable fields + JSON for evolution)**
- [ ] Implement database migrations with Alembic
- [ ] **CRITICAL: Set up schema versioning system for backward compatibility**
- [ ] Set up CORS middleware
- [ ] Create API documentation with OpenAPI
- [ ] **CRITICAL: Document metadata field usage patterns for team**

### Deliverables
- FastAPI backend structure
- Extensible database schema with JSON fields
- Migration system with rollback support
- API documentation
- Schema evolution guidelines

### Success Criteria
- API endpoints are accessible
- Database migrations work
- Can add new fields without migrations (via metadata)
- Swagger documentation available at /docs
- Schema versioning system operational

---

## Phase 5: Authentication System
**Goal**: Implement secure user authentication

### Tasks
- [ ] Create user registration endpoint
- [ ] Implement login with JWT tokens
- [ ] Add password hashing (bcrypt)
- [ ] Create refresh token mechanism
- [ ] Implement user profile endpoints
- [ ] Add email verification (optional for MVP)

### Deliverables
- Authentication endpoints
- JWT token management
- User registration/login forms
- Protected route middleware

### Success Criteria
- Users can register and login
- JWT tokens are properly validated
- Protected endpoints require authentication

---

## Phase 6: File Tracking & Storage
**Goal**: Implement file upload and tracking system

### Tasks
- [ ] Create file upload endpoint
- [ ] Implement file metadata storage
- [ ] Add file ownership tracking
- [ ] Create file listing endpoints
- [ ] Implement file deletion
- [ ] Add file sharing capabilities (Phase 2 feature)

### Deliverables
- File upload/download API
- File metadata database
- User file management

### Success Criteria
- Files upload successfully
- File metadata is tracked
- Users can only access their own files

---

## Phase 7: Frontend-Backend Integration
**Goal**: Connect frontend to backend API

### Tasks
- [ ] Implement API client with Axios
- [ ] Add authentication interceptors
- [ ] Create auth state management
- [ ] Integrate file upload with backend
- [ ] Implement user session management
- [ ] Add error handling and retry logic

### Deliverables
- API integration layer
- Authentication flow
- File management integration
- Error handling system

### Success Criteria
- Login/logout flow works end-to-end
- Files upload to backend
- Authentication persists across page refreshes

---

## Phase 8: Vercel Deployment Configuration & Serialization Infrastructure
**Goal**: Deploy application to production and prepare component serialization foundation

### Tasks
- [ ] Configure Vercel project settings
- [ ] Set up environment variables
- [ ] Configure serverless functions for FastAPI
- [ ] Set up PostgreSQL database (Vercel Postgres/Supabase)
- [ ] Configure file storage (Vercel Blob/S3)
- [ ] Set up CI/CD pipeline
- [ ] **NEW: Implement core serialization infrastructure for future components**
- [ ] **NEW: Create component registry system with type registration**
- [ ] **NEW: Build migration runner for data version upgrades**

### Deliverables
- vercel.json configuration
- Serverless function setup
- Database migration scripts
- Deployment documentation
- **Component serialization base classes**
- **Migration testing framework**

### Success Criteria
- Application deploys successfully
- All features work in production
- Database connects properly
- **Serialization infrastructure tested and ready for Phase 9-10**

---

## Phase 9: Interactive Scene Builder
**Goal**: Enable users to create interactive presentations with their models

### Tasks
- [ ] **CRITICAL: Design scene state management architecture**
- [ ] Implement Scene entity with multiple states support
- [ ] Add performant scene hierarchy view with ui element pooling.
- [ ] Create state snapshot system (capture scene configuration)
- [ ] Build state transition/animation system
- [ ] Develop scene editor UI (add/remove models, position objects)
- [ ] Create state timeline/navigator UI
- [ ] Implement scene serialization/deserialization
- [ ] Add presentation mode (play through states)
- [ ] Create scene sharing/export functionality
- [ ] Build scene templates/presets system
- [ ] **CRITICAL: Implement undo/redo for scene editing**
- [ ] **NEW: Implement SceneStateV2 format with state-based structure**
- [ ] **NEW: Create migration from V1 (simple) to V2 (state-based) scenes**

### Deliverables
- Scene management system
- State-based presentation engine
- Scene editor interface
- Presentation player
- **Versioned scene state format (V2)**
- **Scene migration system**

### Success Criteria
- Users can create multi-state scenes
- Smooth transitions between states
- Scenes persist and reload correctly
- Presentation mode works smoothly
- **Old scenes auto-upgrade to new format**

---

## Phase 10: Component Architecture System
**Goal**: Build extensible component system for scene behaviors with robust versioning

### Tasks
- [ ] **CRITICAL: Design component base architecture (ECS pattern)**
- [ ] **CRITICAL: Implement reliable component serialization/deserialization**
- [ ] Create Transform component (position, rotation, scale)
- [ ] Create Annotation component (text labels, callouts)
- [ ] Build component property editor UI
- [ ] Implement component state recording per scene state
- [ ] Create component animation/interpolation system
- [ ] **CRITICAL: Design component plugin architecture for extensibility**
- [ ] Add visibility component (show/hide objects)
- [ ] Create material/appearance component
- [ ] Build component templates/library system
- [ ] **CRITICAL: Implement component versioning for backward compatibility**
- [ ] **NEW: Implement per-component versioning (not scene-level)**
- [ ] **NEW: Create forward-only migration system for each component type**
- [ ] **NEW: Build UnknownComponent handler for future/unrecognized types**
- [ ] **NEW: Add comprehensive migration testing framework**

### Deliverables
- Component base classes and interfaces
- Core component implementations (Transform, Annotation)
- Component editor UI
- Component serialization system with versioning
- Component plugin framework
- **Component-specific migration chains**
- **SerializedData wrapper format with type/version metadata**
- **Component registry with type registration**

### Success Criteria
- Components serialize/deserialize reliably
- Transform and Annotation components fully functional
- Component states record per scene state
- Easy to add new component types
- Backward compatibility maintained
- **Old component data auto-migrates to current version**
- **Unknown components preserved without data loss**
- **All migrations have test coverage**

---

## Phase 11: Enhancement & Optimization
**Goal**: Improve performance and add advanced features

### Tasks
- [ ] Implement file caching strategy
- [ ] Add support for more file formats (STL, OBJ, STEP)
- [ ] Optimize 3D rendering performance
- [ ] Add measurement tools
- [ ] Implement collaborative features
- [ ] Add file conversion capabilities
- [ ] Create advanced annotation types (dimensions, arrows)
- [ ] Build animation timeline editor
- [ ] Add camera path components for cinematic presentations

### Deliverables
- Performance improvements
- Extended file format support
- Advanced viewer tools
- Enhanced component library

### Success Criteria
- Large files load efficiently
- Multiple file formats supported
- Performance metrics improved
- Professional presentation capabilities

---

## Development Workflow

### Local Development
```bash
# Frontend
npm run dev

# Backend
cd backend
python -m uvicorn main:app --reload
```

### Database Extensibility Strategy
**Core Principle**: Start flexible, stabilize gradually

1. **Development Phase**:
   - Use JSON metadata fields for all experimental features
   - No migrations needed for new fields
   - Rapid iteration and experimentation

2. **Stabilization Phase**:
   - Identify frequently used metadata fields
   - Promote stable fields to dedicated columns
   - Maintain backward compatibility via schema versions

3. **Production Phase**:
   - Core fields as columns for query performance
   - Extended/custom data remains in JSON
   - Feature flags for gradual rollout

### Component Architecture Design
**Pattern**: Entity-Component System (ECS) adapted for scene editing

1. **Core Concepts**:
   - **Entity**: Any object in the scene (model, group, camera)
   - **Component**: Reusable behavior/property (Transform, Annotation)
   - **State**: Snapshot of all component values at a point in time
   - **Scene**: Container for entities, components, and states

2. **Component Interface**:
```typescript
interface Component {
  id: string
  type: string
  version: number
  entityId: string

  // Serialization
  serialize(): ComponentData
  deserialize(data: ComponentData): void

  // State management
  captureState(): ComponentState
  applyState(state: ComponentState): void
  interpolate(from: ComponentState, to: ComponentState, t: number): void

  // Lifecycle
  onAttach(entity: Entity): void
  onDetach(): void
  onUpdate(deltaTime: number): void
}
```

3. **Serialization Strategy (Per-Component Versioning)**:
```typescript
// Core serialization wrapper - each component self-versions
interface SerializedData<T = any> {
  _type: string;      // Component type identifier
  _version: number;   // Schema version for THIS component
  _data: T;          // Actual component data
}

// Scene format uses component-agnostic storage
interface SceneData {
  version: number  // Scene format version (rarely changes)
  entities: EntityData[]
  components: SerializedData[]  // Each component self-versioned
  states: StateData[]
  metadata: {
    created: Date
    modified: Date
    author: string
    [key: string]: any
  }
}

// Component migration example
class TransformComponent {
  static version = 3;
  static migrations = {
    1: (data) => ({ ...data, rotation: {x:0, y:0, z:0} }),  // v1→v2
    2: (data) => ({  // v2→v3: restructure
      position: {x: data.x, y: data.y, z: data.z},
      rotation: data.rotation,
      scale: {x: 1, y: 1, z: 1}
    })
  };

  static deserialize(data: SerializedData) {
    let migrated = data._data;
    for (let v = data._version; v < this.version; v++) {
      if (this.migrations[v]) migrated = this.migrations[v](migrated);
    }
    return new TransformComponent(migrated);
  }
}
```

4. **Component Examples**:
   - **Transform**: position, rotation, scale
   - **Annotation**: text, position, style, visibility
   - **Visibility**: show/hide with fade options
   - **Material**: color, opacity, texture overrides
   - **Animation**: keyframe sequences
   - **Interaction**: click/hover behaviors

### Component Serialization Evolution Strategy
**Key Principle**: Component-level versioning, not scene-level

1. **MVP Phase (1-8)**: Simple scene state without components
   ```typescript
   interface SceneStateV1 {
     version: 1;
     camera: CameraState;
     models: ModelState[];
     metadata: Record<string, any>;
   }
   ```

2. **Scene Builder Phase (9)**: Add multi-state support
   ```typescript
   interface SceneStateV2 {
     version: 2;
     states: Array<{ name: string; camera: CameraState; models: ModelState[] }>;
   }
   ```

3. **Component Phase (10)**: Introduce self-versioned components
   - Each component manages its own schema evolution
   - Scene format remains stable
   - Forward-only migrations (old → new on load)
   - Unknown components preserved as-is

4. **Migration Testing Requirements**:
   - Test every component migration path
   - Verify unknown component preservation
   - Ensure no data loss during upgrades
   - Validate cross-component references

### Database Schema Evolution Process
1. **Add new feature**: Store in `metadata` JSON field first
2. **Validate with users**: Gather feedback, iterate quickly
3. **Stabilize schema**: Create migration for proven fields
4. **Version tracking**: Update schema_version for compatibility
5. **Rollback ready**: Keep reverse migrations available

### Testing Strategy
- Unit tests for API endpoints
- Integration tests for auth flow
- E2E tests for critical user paths
- Performance testing for file uploads
- Schema migration tests (forward and rollback)

### Security Considerations
- JWT token expiration and refresh
- File upload size limits
- Rate limiting on API endpoints
- SQL injection prevention via ORM
- XSS protection in frontend
- CORS configuration

### Scalability Considerations
- Stateless backend design
- Database connection pooling
- CDN for static assets
- Lazy loading for large file lists
- WebGL optimization for complex models
- Background job processing for file conversion

---

## MVP Definition (Phases 1-8)
The minimum viable product includes:
- ✅ BabylonJS viewer for GLTF/GLB files
- ✅ User registration and authentication
- ✅ File upload and management
- ✅ Basic viewer controls
- ✅ Deployed to Vercel

## Post-MVP Features (Phases 9-11)
Advanced features after initial release:
- 🎭 **Interactive Scene Builder** (Phase 9)
  - Multi-state scenes for presentations
  - State transitions and animations
  - Scene templates and sharing
- 🧩 **Component System** (Phase 10)
  - Transform components for object manipulation
  - Annotation components for documentation
  - Extensible plugin architecture
  - Component state recording
- ⚡ **Enhancements** (Phase 11)
  - Extended file format support (STL, OBJ, STEP)
  - Performance optimizations
  - Advanced annotation types
  - Measurement tools

## Future Roadmap
- Real-time collaboration on scenes
- Advanced CAD tools (cross-sections, exploded views)
- File conversion service
- Team/organization features
- API for third-party integrations
- Mobile application
- VR/AR support for presentations