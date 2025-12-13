export const API_BASE_URL = window.location.hostname === 'localhost'
  ? 'http://localhost:8000/admin'
  : '/admin'

// API endpoints (not admin)
export const API_URL = window.location.hostname === 'localhost'
  ? 'http://localhost:8000'
  : window.location.origin
