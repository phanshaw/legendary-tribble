interface User {
  id: string
  name: string
  email: string
}

let currentUser: User | null = null
const API_BASE_URL = '/api'

export function initAuth() {
  const loginBtn = document.getElementById('loginBtn')
  const logoutBtn = document.getElementById('logoutBtn')
  const loginModal = document.getElementById('loginModal')
  const closeModal = document.querySelector('.close')
  const loginForm = document.getElementById('loginForm') as HTMLFormElement
  const registerForm = document.getElementById('registerForm') as HTMLFormElement
  const switchToRegister = document.getElementById('switchToRegister')
  const switchToLogin = document.getElementById('switchToLogin')

  // Check for existing session
  checkSession()

  // Event listeners
  loginBtn?.addEventListener('click', () => {
    loginModal?.classList.remove('hidden')
  })

  closeModal?.addEventListener('click', () => {
    loginModal?.classList.add('hidden')
  })

  logoutBtn?.addEventListener('click', logout)

  switchToRegister?.addEventListener('click', (e) => {
    e.preventDefault()
    loginForm?.classList.add('hidden')
    registerForm?.classList.remove('hidden')
  })

  switchToLogin?.addEventListener('click', (e) => {
    e.preventDefault()
    registerForm?.classList.add('hidden')
    loginForm?.classList.remove('hidden')
  })

  loginForm?.addEventListener('submit', handleLogin)
  registerForm?.addEventListener('submit', handleRegister)

  // Close modal on outside click
  window.addEventListener('click', (e) => {
    if (e.target === loginModal) {
      loginModal?.classList.add('hidden')
    }
  })
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
      document.getElementById('loginModal')?.classList.add('hidden')
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
      body: JSON.stringify({ name, email, password })
    })

    if (response.ok) {
      alert('Registration successful! Please login.')
      document.getElementById('switchToLogin')?.click()
    } else {
      const error = await response.json()
      alert(error.detail || 'Registration failed')
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

  if (currentUser) {
    loginBtn?.classList.add('hidden')
    userMenu?.classList.remove('hidden')
    if (username) {
      username.textContent = currentUser.name
    }
  }
}

function logout() {
  localStorage.removeItem('token')
  currentUser = null

  const loginBtn = document.getElementById('loginBtn')
  const userMenu = document.getElementById('userMenu')

  loginBtn?.classList.remove('hidden')
  userMenu?.classList.add('hidden')

  // Clear file list
  const fileList = document.getElementById('fileList')
  if (fileList) {
    fileList.innerHTML = ''
  }
}

export function getCurrentUser() {
  return currentUser
}

export function getAuthToken() {
  return localStorage.getItem('token')
}