import './styles/main.css'
import './styles/sceneView.css'
import { initBabylonScene } from './viewer/scene'
import { initAuth } from './auth/auth'
import { initFileManager } from './files/fileManager'
import { SceneView } from './ui/sceneView'

document.addEventListener('DOMContentLoaded', () => {
  console.log('CAD Viewer initializing...')
  console.log('initFileManager type:', typeof initFileManager)
  console.log('initFileManager value:', initFileManager)

  // Initialize BabylonJS scene
  const canvas = document.getElementById('renderCanvas') as HTMLCanvasElement
  if (canvas) {
    initBabylonScene(canvas)
  }

  // Initialize Scene View Inspector
  const sceneView = new SceneView()

  // Initialize authentication
  initAuth()

  // Initialize file management
  try {
    if (typeof initFileManager === 'function') {
      initFileManager()
      console.log('File manager initialized successfully')
    } else {
      console.error('initFileManager is not a function:', initFileManager)
    }
  } catch (error) {
    console.error('Error initializing file manager:', error)
  }

  // Make scene view globally accessible for debugging
  (window as any).sceneView = sceneView

  console.log('CAD Viewer ready with Scene Inspector')
})