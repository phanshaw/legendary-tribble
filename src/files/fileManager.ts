import { loadModel } from '../viewer/scene'
import { getAuthToken } from '../auth/auth'

const API_BASE_URL = '/api'

export function initFileManager() {
  const uploadBtn = document.getElementById('uploadBtn')
  const fileInput = document.getElementById('fileInput') as HTMLInputElement
  const fileList = document.getElementById('fileList')
  const viewer = document.querySelector('.viewer-container')

  // Upload button click
  uploadBtn?.addEventListener('click', () => {
    fileInput?.click()
  })

  // File input change
  fileInput?.addEventListener('change', (e) => {
    const target = e.target as HTMLInputElement
    const file = target.files?.[0]
    if (file) {
      handleFileUpload(file)
    }
  })

  // Drag and drop
  viewer?.addEventListener('dragover', (e) => {
    e.preventDefault()
    viewer.classList.add('drag-over')
  })

  viewer?.addEventListener('dragleave', () => {
    viewer.classList.remove('drag-over')
  })

  viewer?.addEventListener('drop', (e) => {
    e.preventDefault()
    viewer.classList.remove('drag-over')

    const file = e.dataTransfer?.files[0]
    if (file) {
      handleFileUpload(file)
    }
  })

  // Load user files if logged in
  if (getAuthToken()) {
    loadUserFiles()
  }
}

async function handleFileUpload(file: File) {
  // Validate file type
  const validExtensions = ['.gltf', '.glb', '.babylon', '.obj', '.stl']
  const fileExt = '.' + file.name.split('.').pop()?.toLowerCase()

  if (!validExtensions.includes(fileExt)) {
    alert('Unsupported file type. Please upload GLTF, GLB, Babylon, OBJ, or STL files.')
    return
  }

  // Check file size (warn if > 50MB)
  if (file.size > 50 * 1024 * 1024) {
    const proceed = confirm('This file is larger than 50MB and may take time to load. Continue?')
    if (!proceed) return
  }

  // Check if file is empty
  if (file.size === 0) {
    alert('The selected file is empty.')
    return
  }

  // Load model locally first
  try {
    await loadModel(file)
  } catch (error) {
    console.error('Error loading model:', error)
    // Error is already handled in loadModel function
  }

  // Upload to server if logged in
  const token = getAuthToken()
  if (token) {
    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch(`${API_BASE_URL}/files/upload`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      })

      if (response.ok) {
        const fileData = await response.json()
        addFileToList(fileData)
      }
    } catch (error) {
      console.error('File upload failed:', error)
    }
  } else {
    // Local only - add to temporary list
    addFileToList({
      id: Date.now().toString(),
      name: file.name,
      size: file.size,
      local: true
    })
  }
}

async function loadUserFiles() {
  const token = getAuthToken()
  if (!token) return

  try {
    const response = await fetch(`${API_BASE_URL}/files`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (response.ok) {
      const files = await response.json()
      const fileList = document.getElementById('fileList')
      if (fileList) {
        fileList.innerHTML = ''
        files.forEach(addFileToList)
      }
    }
  } catch (error) {
    console.error('Failed to load files:', error)
  }
}

function addFileToList(file: any) {
  const fileList = document.getElementById('fileList')
  if (!fileList) return

  const fileItem = document.createElement('div')
  fileItem.className = 'file-item'
  fileItem.innerHTML = `
    <div style="display: flex; justify-content: space-between; align-items: center;">
      <span>${file.name}</span>
      <span style="font-size: 0.8rem; color: #666;">
        ${formatFileSize(file.size)}
      </span>
    </div>
  `

  fileItem.addEventListener('click', async () => {
    if (file.local) {
      // File is already loaded
      return
    }

    // Load file from server
    const token = getAuthToken()
    if (token) {
      try {
        const response = await fetch(`${API_BASE_URL}/files/${file.id}/download`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })

        if (response.ok) {
          const blob = await response.blob()
          const fileObj = new File([blob], file.name)
          await loadModel(fileObj)
        }
      } catch (error) {
        console.error('Failed to load file:', error)
      }
    }
  })

  fileList.appendChild(fileItem)
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}