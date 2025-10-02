import { clearLoadedModels } from '../viewer/scene'
import { loadUserFiles } from '../files/fileManager'

interface User {
  id: string
  name: string
  email: string
}

let currentUser: User | null = null
const API_BASE_URL = 'http://localhost:8000/api/v1'

export function initAuth() {
  const landingPage = document.getElementById('landingPage')
  const mainApp = document.getElementById('mainApp')
  const loginBtn = document.getElementById('loginBtn')
  const logoutBtn = document.getElementById('logoutBtn')
  const authModal = document.getElementById('authModal')
  const closeModal = document.querySelector('.close')
  const loginFormContainer = document.getElementById('loginFormContainer')
  const registerFormContainer = document.getElementById('registerFormContainer')
  const loginForm = document.getElementById('loginForm') as HTMLFormElement
  const registerForm = document.getElementById('registerForm') as HTMLFormElement
  const switchToRegister = document.getElementById('switchToRegister')
  const switchToLogin = document.getElementById('switchToLogin')
  const uploadBtn = document.getElementById('uploadBtn')

  // Landing page buttons
  const landingLoginBtn = document.getElementById('landingLoginBtn')
  const landingGetStartedBtn = document.getElementById('landingGetStartedBtn')
  const heroCTABtn = document.getElementById('heroCTABtn')

  // Disable upload button by default (will be enabled after login)
  if (uploadBtn) {
    uploadBtn.setAttribute('disabled', 'true')
    uploadBtn.style.opacity = '0.5'
    uploadBtn.style.cursor = 'not-allowed'
  }

  // Check for existing session
  checkSession()

  // Landing page event listeners
  landingLoginBtn?.addEventListener('click', () => {
    showAuthModal('login')
  })

  landingGetStartedBtn?.addEventListener('click', () => {
    showAuthModal('register')
  })

  heroCTABtn?.addEventListener('click', () => {
    showAuthModal('register')
  })

  // Main app event listeners
  loginBtn?.addEventListener('click', () => {
    showAuthModal('login')
  })

  closeModal?.addEventListener('click', () => {
    authModal?.classList.add('hidden')
  })

  logoutBtn?.addEventListener('click', logout)

  switchToRegister?.addEventListener('click', (e) => {
    e.preventDefault()
    showAuthModal('register')
  })

  switchToLogin?.addEventListener('click', (e) => {
    e.preventDefault()
    showAuthModal('login')
  })

  loginForm?.addEventListener('submit', handleLogin)
  registerForm?.addEventListener('submit', handleRegister)

  // Close modal on outside click
  window.addEventListener('click', (e) => {
    if (e.target === authModal) {
      authModal?.classList.add('hidden')
    }
  })

  // Helper function to show auth modal
  function showAuthModal(type: 'login' | 'register') {
    if (type === 'login') {
      loginFormContainer?.classList.remove('hidden')
      registerFormContainer?.classList.add('hidden')
    } else {
      loginFormContainer?.classList.add('hidden')
      registerFormContainer?.classList.remove('hidden')
    }
    authModal?.classList.remove('hidden')
  }

  // Helper function to show main app
  function showMainApp() {
    landingPage?.classList.add('hidden')
    mainApp?.classList.remove('hidden')
  }

  // Store showMainApp for use in other functions
  (window as any).showMainApp = showMainApp
}

async function handleLogin(e: Event) {
  e.preventDefault()
  const form = e.target as HTMLFormElement
  const email = (form.querySelector('#email') as HTMLInputElement).value
  const password = (form.querySelector('#password') as HTMLInputElement).value

  try {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    })

    if (response.ok) {
      const data = await response.json()
      localStorage.setItem('token', data.access_token)
      currentUser = data.user
      updateUIForLoggedInUser()
      document.getElementById('authModal')?.classList.add('hidden')

      // Transition to main app
      if ((window as any).showMainApp) {
        (window as any).showMainApp()
      }
    } else {
      alert('Invalid credentials')
    }
  } catch (error) {
    console.error('Login failed:', error)
    alert('Login failed. Please try again.')
  }
}

async function handleRegister(e: Event) {
  e.preventDefault()
  const form = e.target as HTMLFormElement
  const name = (form.querySelector('#regName') as HTMLInputElement).value
  const email = (form.querySelector('#regEmail') as HTMLInputElement).value
  const password = (form.querySelector('#regPassword') as HTMLInputElement).value

  try {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name,
        email,
        password,
        password_confirm: password,  // Add password confirmation
        is_active: true,
        role: 'user'
      })
    })

    if (response.ok) {
      alert('Registration successful! Please login.')
      document.getElementById('switchToLogin')?.click()
    } else {
      const error = await response.json()
      console.error('Registration error:', error)
      // Handle validation errors
      if (error.error === 'INVALID_PASSWORD') {
        alert(`Password requirements: ${error.detail}`)
      } else if (error.detail) {
        alert(error.detail)
      } else {
        alert('Registration failed. Please check your information.')
      }
    }
  } catch (error) {
    console.error('Registration failed:', error)
    alert('Registration failed. Please try again.')
  }
}

async function checkSession() {
  const token = localStorage.getItem('token')
  if (!token) return

  try {
    const response = await fetch(`${API_BASE_URL}/auth/me`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })

    if (response.ok) {
      currentUser = await response.json()
      updateUIForLoggedInUser()

      // If user is logged in, show main app instead of landing page
      if ((window as any).showMainApp) {
        (window as any).showMainApp()
      }
    } else {
      localStorage.removeItem('token')
    }
  } catch (error) {
    console.error('Session check failed:', error)
  }
}

function updateUIForLoggedInUser() {
  const loginBtn = document.getElementById('loginBtn')
  const userMenu = document.getElementById('userMenu')
  const username = document.getElementById('username')
  const uploadBtn = document.getElementById('uploadBtn')

  if (currentUser) {
    loginBtn?.classList.add('hidden')
    userMenu?.classList.remove('hidden')
    if (username) {
      username.textContent = currentUser.name
    }

    // Enable upload button
    if (uploadBtn) {
      uploadBtn.removeAttribute('disabled')
      uploadBtn.style.opacity = '1'
      uploadBtn.style.cursor = 'pointer'
    }

    // Load user's files after successful login
    loadUserFiles()
  }
}

function logout() {
  localStorage.removeItem('token')
  currentUser = null

  const loginBtn = document.getElementById('loginBtn')
  const userMenu = document.getElementById('userMenu')
  const uploadBtn = document.getElementById('uploadBtn')

  loginBtn?.classList.remove('hidden')
  userMenu?.classList.add('hidden')

  // Disable upload button
  if (uploadBtn) {
    uploadBtn.setAttribute('disabled', 'true')
    uploadBtn.style.opacity = '0.5'
    uploadBtn.style.cursor = 'not-allowed'
  }

  // Clear file list
  const fileList = document.getElementById('fileList')
  if (fileList) {
    fileList.innerHTML = ''
  }

  // Clear loaded models from the 3D scene
  clearLoadedModels()
}

export function getCurrentUser() {
  return currentUser
}

export function getAuthToken() {
  return localStorage.getItem('token')
}