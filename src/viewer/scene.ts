import * as BABYLON from '@babylonjs/core'
import '@babylonjs/loaders/glTF'
import '@babylonjs/loaders/OBJ'
import '@babylonjs/loaders/STL'

let engine: BABYLON.Engine | null = null
let scene: BABYLON.Scene | null = null
let camera: BABYLON.ArcRotateCamera | null = null

export function initBabylonScene(canvas: HTMLCanvasElement) {
  // Create engine
  engine = new BABYLON.Engine(canvas, true, {
    preserveDrawingBuffer: true,
    stencil: true
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
  camera.maxZ = 1000

  // Create lights
  const light1 = new BABYLON.HemisphericLight(
    'light1',
    new BABYLON.Vector3(0, 1, 0),
    scene
  )
  light1.intensity = 0.7

  const light2 = new BABYLON.DirectionalLight(
    'light2',
    new BABYLON.Vector3(-1, -2, -1),
    scene
  )
  light2.intensity = 0.3

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

  resetBtn?.addEventListener('click', resetCamera)
  toggleGridBtn?.addEventListener('click', toggleGrid)
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

export async function loadModel(file: File) {
  if (!scene) return

  // Remove existing models (except grid and ground)
  const meshesToRemove = scene.meshes.filter(mesh =>
    mesh.name !== 'ground' && mesh.id !== 'grid'
  )
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
      // Calculate bounding box for all loaded meshes
      let minX = Infinity, minY = Infinity, minZ = Infinity
      let maxX = -Infinity, maxY = -Infinity, maxZ = -Infinity

      result.meshes.forEach(mesh => {
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

export function getScene() {
  return scene
}

export function getEngine() {
  return engine
}