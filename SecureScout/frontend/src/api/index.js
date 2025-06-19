import axios from 'axios'

// Create an Axios instance
const api = axios.create({
  baseURL: '/', // Use root path since backend already prefixes with /api
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Response interceptor
api.interceptors.response.use(
  response => response.data,
  error => {
    console.error('API request error:', error)
    return Promise.reject(error)
  }
)

// Scan API
export const scanApi = {
  // Start a scan for a single URL
  startScan(data) {
    return api.post('/api/scan/start', data)
  },

  // Start a batch scan for multiple URLs
  batchScan(data) {
    return api.post('/api/scan/batch', data)
  },

  // Get status of a scan
  getScanStatus(scanId) {
    return api.get(`/api/scan/status/${scanId}`)
  },

  // Get all active scans
  getActiveScans() {
    return api.get('/api/scan/active')
  }
}

// Report API
export const reportApi = {
  // Get all reports
  getAllReports() {
    return api.get('/api/report')
  },

  // Get a specific report's details
  getReport(reportId) {
    return api.get(`/api/report/${reportId}`)
  },

  // Get summary of recent reports (default: last 7 days)
  getRecentSummary(days = 7) {
    return api.get(`/api/report/summary/recent?days=${days}`)
  },

  // Delete a report
  deleteReport(reportId) {
    return api.delete(`/api/report/${reportId}`)
  },

  // Get statistics of vulnerability types
  getVulnerabilityStats() {
    return api.get('/api/report/stats/vulnerability_types')
  }
}

// Configuration API
export const configApi = {
  // Get configuration settings
  getConfig() {
    return api.get('/api/config')
  },

  // Update configuration
  updateConfig(data) {
    return api.patch('/api/config', data)
  },

  // Get vulnerability library
  getVulnerabilityLibrary() {
    return api.get('/api/config/vulnerabilities')
  },

  // Update rules for a specific vulnerability type
  updateVulnerabilityRule(vulnType, data) {
    return api.patch(`/api/config/vulnerabilities/${vulnType}`, data)
  },

  // Reset all configurations
  resetConfig() {
    return api.post('/api/config/reset')
  }
}
