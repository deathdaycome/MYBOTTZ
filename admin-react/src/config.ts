export const API_BASE_URL = window.location.hostname === 'localhost'
  ? 'http://localhost:8001/admin'
  : '/admin'

// API endpoints (not admin)
export const API_URL = window.location.hostname === 'localhost'
  ? 'http://localhost:8001'
  : window.location.origin
