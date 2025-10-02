import * as BABYLON from '@babylonjs/core'
import '@babylonjs/loaders/glTF'
import '@babylonjs/loaders/OBJ'
import '@babylonjs/loaders/STL'
import { renameRootNodes } from './sceneHelpers'

let engine: BABYLON.Engine | null = null
let scene: BABYLON.Scene | null = null
let camera: BABYLON.ArcRotateCamera | null = null

export function initBabylonScene(canvas: HTMLCanvasElement) {
  // Create engine with high DPI support
  engine = new BABYLON.Engine(canvas, true, {
    preserveDrawingBuffer: true,
    stencil: true,
    adaptToDeviceRatio: true
  })

  // Create scene
  scene = new BABYLON.Scene(engine)
  scene.clearColor = new BABYLON.Color4(0.1, 0.1, 0.1, 1)

  // Create camera
  camera = new BABYLON.ArcRotateCamera(
    'camera',
    Math.PI / 4,
    Math.PI / 3,
    10,
    BABYLON.Vector3.Zero(),
    scene
  )
  camera.attachControl(canvas, true)
  camera.wheelPrecision = 50
  camera.minZ = 0.1
  camera.maxZ = 5000 // Increased to ensure skybox (size 1000) is always visible

  // Create enhanced lighting system
  const hemisphericLight = new BABYLON.HemisphericLight(
    'hemisphericLight',
    new BABYLON.Vector3(0, 1, 0),
    scene
  )
  hemisphericLight.intensity = 0.5
  hemisphericLight.diffuse = new BABYLON.Color3(1, 1, 1)
  hemisphericLight.specular = new BABYLON.Color3(0, 0, 0)
  hemisphericLight.groundColor = new BABYLON.Color3(0.1, 0.1, 0.15)

  const directionalLight1 = new BABYLON.DirectionalLight(
    'directionalLight1',
    new BABYLON.Vector3(-1, -2, -1),
    scene
  )
  directionalLight1.intensity = 0.4
  directionalLight1.diffuse = new BABYLON.Color3(1, 0.98, 0.95)

  const directionalLight2 = new BABYLON.DirectionalLight(
    'directionalLight2',
    new BABYLON.Vector3(1, -1, 0.5),
    scene
  )
  directionalLight2.intensity = 0.2
  directionalLight2.diffuse = new BABYLON.Color3(0.95, 0.95, 1)

  // Setup environment and skybox
  setupEnvironment(scene)

  // Create grid
  createGrid(scene)

  // Setup controls
  setupViewerControls()

  // Resize handling
  window.addEventListener('resize', () => {
    engine?.resize()
  })

  // Render loop
  engine.runRenderLoop(() => {
    scene?.render()
  })
}

function setupEnvironment(scene: BABYLON.Scene) {
  // Following BabylonJS best practices for HDR environment setup
  // Using CreateFromPrefilteredData for optimal performance with .env files
  const hdrTexture = BABYLON.CubeTexture.CreateFromPrefilteredData(
    'https://playground.babylonjs.com/textures/environment.env',
    scene
  )

  // Set as scene environment texture for IBL (Image Based Lighting)
  scene.environmentTexture = hdrTexture

  // Create skybox using the built-in helper method for consistency
  // Parameters: texture, pbr mode, scale, blur, setGlobal
  const skybox = scene.createDefaultSkybox(
      hdrTexture,
      true,
      1000,
      0.5, false)

  if (skybox) {
    skybox.name = 'skybox'
    skybox.isPickable = false

    // Store reference for toggle functionality
    scene.metadata = scene.metadata || {}
    scene.metadata.skybox = skybox
  }

  // Optional: Set environment intensity for PBR materials
  scene.environmentIntensity = 1.0
}

function createGrid(scene: BABYLON.Scene) {
  const gridMaterial = new BABYLON.StandardMaterial('gridMaterial', scene)
  gridMaterial.wireframe = true
  gridMaterial.emissiveColor = new BABYLON.Color3(0.2, 0.2, 0.2)
  gridMaterial.disableLighting = true

  const ground = BABYLON.MeshBuilder.CreateGround(
    'ground',
    { width: 20, height: 20, subdivisions: 20 },
    scene
  )
  ground.material = gridMaterial
  ground.isPickable = false
  ground.id = 'grid'
}

function setupViewerControls() {
  const resetBtn = document.getElementById('resetView')
  const toggleGridBtn = document.getElementById('toggleGrid')
  const toggleSkyboxBtn = document.getElementById('toggleSkybox')

  resetBtn?.addEventListener('click', resetCamera)
  toggleGridBtn?.addEventListener('click', toggleGrid)
  toggleSkyboxBtn?.addEventListener('click', toggleSkybox)
}

export function resetCamera() {
  if (!camera) return
  camera.alpha = Math.PI / 4
  camera.beta = Math.PI / 3
  camera.radius = 10
  camera.target = BABYLON.Vector3.Zero()
}

export function toggleGrid() {
  if (!scene) return
  const grid = scene.getMeshById('grid')
  if (grid) {
    grid.isVisible = !grid.isVisible
  }
}

export function toggleSkybox() {
  if (!scene) return
  // The skybox created by createDefaultSkybox is stored in scene metadata
  const skybox = scene.metadata?.skybox || scene.getMeshByName('skybox')
  if (skybox) {
    skybox.isVisible = !skybox.isVisible
  }
}

export async function loadModel(file: File) {
  if (!scene) return

  // Remove existing models (except grid, ground, and skybox)
  const meshesToRemove = scene.meshes.filter(mesh => {
    // Keep these system meshes
    if (mesh.name === 'ground' ||
        mesh.id === 'grid' ||
        mesh.name === 'skybox' ||
        mesh.name === 'BackgroundSkybox' || // Default name from createDefaultSkybox
        mesh.name === 'BackgroundPlane' ||   // Potential background plane
        mesh === scene.metadata?.skybox) {   // Check stored reference
      return false
    }
    // Remove all other meshes (previous models)
    return true
  })
  meshesToRemove.forEach(mesh => mesh.dispose())

  const url = URL.createObjectURL(file)

  // Get file extension with dot prefix
  const extension = '.' + file.name.split('.').pop()?.toLowerCase()

  try {
    console.log(`Loading model: ${file.name} (${extension})`)

    const result = await BABYLON.SceneLoader.AppendAsync(
      '',
      url,
      scene,
      undefined,
      extension  // Pass extension with dot prefix
    )

    // Center and scale model
    if (result.meshes.length > 0) {
      // Rename __root__ nodes to be more descriptive
      renameRootNodes(result.meshes, result.transformNodes, file.name)

      // Calculate bounding box for all loaded meshes (excluding skybox and grid)
      let minX = Infinity, minY = Infinity, minZ = Infinity
      let maxX = -Infinity, maxY = -Infinity, maxZ = -Infinity

      result.meshes.forEach(mesh => {
        // Skip system meshes in bounding box calculation
        if (mesh.name === 'skybox' ||
            mesh.name === 'BackgroundSkybox' ||
            mesh.name === 'BackgroundPlane' ||
            mesh.name === 'ground' ||
            mesh.id === 'grid' ||
            mesh === scene.metadata?.skybox) {
          return
        }

        mesh.computeWorldMatrix(true)
        const boundingInfo = mesh.getBoundingInfo()
        const min = boundingInfo.boundingBox.minimumWorld
        const max = boundingInfo.boundingBox.maximumWorld

        minX = Math.min(minX, min.x)
        minY = Math.min(minY, min.y)
        minZ = Math.min(minZ, min.z)
        maxX = Math.max(maxX, max.x)
        maxY = Math.max(maxY, max.y)
        maxZ = Math.max(maxZ, max.z)
      })

      const center = new BABYLON.Vector3(
        (minX + maxX) / 2,
        (minY + maxY) / 2,
        (minZ + maxZ) / 2
      )
      const size = new BABYLON.Vector3(
        maxX - minX,
        maxY - minY,
        maxZ - minZ
      )
      const maxDimension = Math.max(size.x, size.y, size.z)

      // Create a parent transform node for the model
      const modelContainer = new BABYLON.TransformNode('modelContainer', scene)

      // Parent all root meshes to the container
      result.meshes.forEach(mesh => {
        if (!mesh.parent) {
          mesh.parent = modelContainer
        }
      })

      // Center and scale via the container
      modelContainer.position = center.negate()
      if (maxDimension > 0) {
        const scaleFactor = 10 / maxDimension
        modelContainer.scaling = new BABYLON.Vector3(scaleFactor, scaleFactor, scaleFactor)
      }

      // Frame the camera on the model
      if (camera) {
        camera.setTarget(BABYLON.Vector3.Zero())
        camera.radius = 15
        camera.alpha = Math.PI / 4
        camera.beta = Math.PI / 3
      }

      console.log(`Model loaded successfully: ${result.meshes.length} meshes`)
    } else {
      console.warn('Model loaded but contains no meshes')
    }
  } catch (error: any) {
    console.error('Failed to load model:', error)

    // Provide more specific error messages
    let errorMessage = 'Failed to load model. '

    if (error?.message?.includes('importScene has failed JSON parse')) {
      errorMessage += 'The file appears to be corrupted or is not a valid 3D model format. Please ensure the file is a valid GLTF, GLB, Babylon, OBJ, or STL file.'
    } else if (error?.message?.includes('Unable to load from')) {
      errorMessage += 'Unable to read the file. It may be corrupted or in an unsupported format.'
    } else if (error?.message?.includes('loader for')) {
      errorMessage += `No loader available for ${extension} files. Supported formats: GLTF, GLB, Babylon, OBJ, STL.`
    } else {
      errorMessage += error?.message || 'Please check the file format.'
    }

    alert(errorMessage)
  } finally {
    URL.revokeObjectURL(url)
  }
}

export function clearLoadedModels() {
  if (!scene) return

  // Remove all loaded models (except grid, ground, and skybox)
  const meshesToRemove = scene.meshes.filter(mesh => {
    // Keep these system meshes (grid has both name='ground' and id='grid')
    if (mesh.name === 'ground' ||
        mesh.id === 'grid' ||
        mesh.name === 'skybox' ||
        mesh.name === 'BackgroundSkybox' ||
        mesh.name === 'BackgroundPlane' ||
        mesh === scene?.metadata?.skybox) {
      return false
    }
    // Remove all other meshes (loaded models)
    return true
  })

  meshesToRemove.forEach(mesh => mesh.dispose())

  // Only remove the modelContainer transform node used for loaded models
  const transformNodesToRemove = scene.transformNodes.filter(node => {
    return node.name === 'modelContainer'
  })

  transformNodesToRemove.forEach(node => node.dispose())

  // Reset camera to default position
  resetCamera()
}

export function getScene() {
  return scene
}

export function getEngine() {
  return engine
}