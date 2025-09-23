import './styles/main.css'
import { initBabylonScene } from './viewer/scene'
import { initAuth } from './auth/auth'
import { initFileManager } from './files/fileManager'

document.addEventListener('DOMContentLoaded', () => {
  console.log('CAD Viewer initializing...')

  // Initialize BabylonJS scene
  const canvas = document.getElementById('renderCanvas') as HTMLCanvasElement
  if (canvas) {
    initBabylonScene(canvas)
  }

  // Initialize authentication
  initAuth()

  // Initialize file management
  initFileManager()

  console.log('CAD Viewer ready')
})