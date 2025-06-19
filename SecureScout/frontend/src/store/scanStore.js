import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { scanApi, reportApi } from '../api'

export const useScanStore = defineStore('scan', () => {
  // State
  const isLoading = ref(false)
  const error = ref(null)
  const scanResults = ref([])
  const scans = ref([])
  const scanConfig = ref({
    timeout: 60,
    concurrent_scans: 3,
    user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    default_modules: ['sql_injection', 'xss', 'csrf'],
    vulnerability_definitions: {
      'sql_injection': {
        severity: 'High',
        description: 'SQL injection vulnerability allows attackers to inject malicious SQL queries into the application, potentially leading to data leakage or corruption',
        patterns: [
          'SQL syntax', 'mysql_fetch_array', 'You have an error in your SQL syntax',
          'ORA-', 'PostgreSQL', 'SQLite3::', 'microsoft JET Database'
        ]
      },
      'xss': {
        severity: 'Medium',
        description: 'Cross-site scripting attacks allow attackers to inject and execute malicious scripts in the victim\'s browser',
        patterns: [
          '<script>alert', 'javascript:alert', 'onerror=alert', 'document.cookie',
          'eval(', 'document.domain', 'document.write'
        ]
      },
      'csrf': {
        severity: 'Medium',
        description: 'Cross-site request forgery vulnerabilities allow attackers to trick users into performing unintended actions',
        patterns: [
          'no CSRF token', 'missing CSRF', 'csrf verification failed'
        ]
      },
      'file_upload': {
        severity: 'High',
        description: 'Insecure file upload allows attackers to upload malicious files, potentially leading to remote code execution',
        patterns: [
          '.php', '.jsp', '.asp', '.exe', '.sh', '.py'
        ]
      }
    }
  })

  // Get active scan task count
  const activeScansCount = computed(() => {
    return scans.value.filter(scan => ['pending', 'running'].includes(scan.status)).length
  })

  // Save config to backend
  async function saveConfig(newConfig) {
    try {
      isLoading.value = true
      error.value = null

      // Simulate API request - replace with real API call in production
      await new Promise(resolve => setTimeout(resolve, 500))

      // Save to local state
      scanConfig.value = { ...scanConfig.value, ...newConfig }

      // Save to local storage
      localStorage.setItem('scanConfig', JSON.stringify(scanConfig.value))

      return true
    } catch (err) {
      error.value = 'Failed to save config: ' + (err.message || 'Unknown error')
      console.error('Failed to save config:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // Load config
  async function loadConfig() {
    try {
      isLoading.value = true
      error.value = null

      // Try to load from local storage
      const savedConfig = localStorage.getItem('scanConfig')
      if (savedConfig) {
        scanConfig.value = JSON.parse(savedConfig)
      }

      return scanConfig.value
    } catch (err) {
      error.value = 'Failed to load config: ' + (err.message || 'Unknown error')
      console.error('Failed to load config:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // Create new scan
  async function createScan(url, modules = []) {
    try {
      isLoading.value = true
      error.value = null

      // Check if there is already an active scan for the same URL
      const existingScan = scans.value.find(
        scan => scan.url === url && ['pending', 'running'].includes(scan.status)
      )

      if (existingScan) {
        throw new Error('This URL is already in the scan queue')
      }

      // Check if max concurrent scans exceeded
      if (activeScansCount.value >= scanConfig.value.concurrent_scans) {
        throw new Error(`Maximum concurrent scans reached (${scanConfig.value.concurrent_scans})`)
      }

      // Create new scan object
      const date = new Date();
      const formattedDate =
        date.getFullYear().toString().substring(2) +
        (date.getMonth() + 1).toString().padStart(2, '0') +
        date.getDate().toString().padStart(2, '0');

      // Ensure scan ID is unique, format: SCN-YYYYMMDD-xxx
      const todayScans = scans.value.filter(scan => scan.id.includes(`SCN-${formattedDate}`));
      const sequenceNumber = (todayScans.length + 1).toString().padStart(3, '0');
      const scanId = `SCN-${formattedDate}-${sequenceNumber}`;

      const newScan = {
        id: scanId,
        url: url,
        modules: modules.length > 0 ? modules : scanConfig.value.default_modules,
        status: 'pending',
        progress: 0,
        start_time: new Date().toISOString(),
        end_time: null,
        vulnerabilities: [],
        error: null
      }

      // Add to scan list
      scans.value.push(newScan)

      // Sync to local storage
      saveScansToLocalStorage()

      // Simulate API call - replace with real API call in production
      setTimeout(() => {
        // Update status to running
        updateScanStatus(scanId, { status: 'running' })

        // Simulate scan progress update
        simulateScanProgress(scanId)
      }, 500)

      return scanId
    } catch (err) {
      error.value = 'Failed to create scan: ' + (err.message || 'Unknown error')
      console.error('Failed to create scan:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // Simulate scan progress
  function simulateScanProgress(scanId) {
    const scan = scans.value.find(s => s.id === scanId)
    if (!scan || scan.status !== 'running') return

    let progress = 0
    const interval = setInterval(() => {
      // Increase progress
      progress += Math.random() * 15

      if (progress >= 100) {
        // Scan complete
        progress = 100
        clearInterval(interval)

        // Generate mock vulnerabilities
        const vulnerabilities = generateMockVulnerabilities(scan.url, scan.modules)

        // Update scan status
        updateScanStatus(scanId, {
          status: 'completed',
          progress: 100,
          end_time: new Date().toISOString(),
          vulnerabilities
        })

        // Add to scan results
        scanResults.value.push({
          ...scan,
          status: 'completed',
          progress: 100,
          end_time: new Date().toISOString(),
          vulnerabilities
        })

        // Save results to local storage
        saveScanResultsToLocalStorage()
      } else {
        // Update progress
        updateScanStatus(scanId, {
          progress: Math.min(Math.round(progress), 99)
        })
      }
    }, 1000)
  }

  // Update scan status
  function updateScanStatus(scanId, updates) {
    const scanIndex = scans.value.findIndex(s => s.id === scanId)
    if (scanIndex === -1) return false

    // Update scan object
    scans.value[scanIndex] = {
      ...scans.value[scanIndex],
      ...updates
    }

    // Sync to local storage
    saveScansToLocalStorage()

    return true
  }

  // Get scan status
  async function getScanStatus(scanId) {
    try {
      isLoading.value = true
      error.value = null

      // Try to get from local scan list
      const scan = scans.value.find(s => s.id === scanId)
      if (scan) return { ...scan }

      // Try to get from results list
      const result = scanResults.value.find(r => r.id === scanId)
      if (result) return { ...result }

      throw new Error('Scan record not found')
    } catch (err) {
      error.value = 'Failed to get scan status: ' + (err.message || 'Unknown error')
      console.error('Failed to get scan status:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // Get all scans
  async function getAllScans() {
    try {
      isLoading.value = true
      error.value = null

      // Simulate API request - replace with real API call in production
      await new Promise(resolve => setTimeout(resolve, 300))

      return [...scans.value]
    } catch (err) {
      error.value = 'Failed to get scan list: ' + (err.message || 'Unknown error')
      console.error('Failed to get scan list:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // Get all scan results
  async function getAllResults() {
    try {
      isLoading.value = true
      error.value = null

      // Simulate API request - replace with real API call in production
      await new Promise(resolve => setTimeout(resolve, 800))

      // Return mock data
      return [
        {
          id: 'SCN-2023-0001',
          url: 'https://example.com',
          scanDate: '2023-10-15T08:30:00Z',
          status: 'Completed',
          vulnerabilities: [
            {
              type: 'xss',
              severity: 'High',
              location: '/search?q=',
              description: 'XSS vulnerability'
            },
            {
              type: 'sql_injection',
              severity: 'Critical',
              location: '/user?id=',
              description: 'SQL injection vulnerability'
            },
            {
              type: 'info_leak',
              severity: 'Medium',
              location: '/js/main.js',
              description: 'Sensitive information disclosure'
            }
          ]
        },
        {
          id: 'SCN-2023-0002',
          url: 'https://secure-demo.org',
          scanDate: '2023-10-20T14:15:00Z',
          status: 'Completed',
          vulnerabilities: []
        }
      ]
    } catch (error) {
      console.error('Failed to get scan results:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  // Cancel scan
  async function cancelScan(scanId) {
    try {
      isLoading.value = true
      error.value = null

      const scanIndex = scans.value.findIndex(s => s.id === scanId)
      if (scanIndex === -1) {
        throw new Error('No scan task found')
      }

      const scan = scans.value[scanIndex]
      if (!['pending', 'running'].includes(scan.status)) {
        throw new Error('Only pending or running scans can be cancelled')
      }

      // Update scan status
      scans.value[scanIndex] = {
        ...scan,
        status: 'cancelled',
        end_time: new Date().toISOString()
      }

      // Sync to local storage
      saveScansToLocalStorage()

      return true
    } catch (err) {
      error.value = 'Failed to cancel scan: ' + (err.message || 'Unknown error')
      console.error('Failed to cancel scan:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // Delete scan
  async function deleteScan(scanId) {
    try {
      isLoading.value = true
      error.value = null

      // Remove from scan list
      const scanIndex = scans.value.findIndex(s => s.id === scanId)
      if (scanIndex !== -1) {
        const scan = scans.value[scanIndex]
        if (['pending', 'running'].includes(scan.status)) {
          throw new Error('Cannot delete a scan that is in progress')
        }

        scans.value.splice(scanIndex, 1)
        saveScansToLocalStorage()

        // Also check and remove from results list if present
        const resultIndex = scanResults.value.findIndex(r => r.id === scanId)
        if (resultIndex !== -1) {
          scanResults.value.splice(resultIndex, 1)
          saveScanResultsToLocalStorage()
        }
      }

      return true
    } catch (err) {
      error.value = 'Failed to delete scan: ' + (err.message || 'Unknown error')
      console.error('Failed to delete scan:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // Clear all scan records
  async function clearAllScans() {
    try {
      isLoading.value = true
      error.value = null

      // Clear scan list (keep pending/running scans)
      scans.value = scans.value.filter(s => ['pending', 'running'].includes(s.status))
      saveScansToLocalStorage()

      // Clear results list
      scanResults.value = []
      saveScanResultsToLocalStorage()

      return true
    } catch (err) {
      error.value = 'Failed to clear scan records: ' + (err.message || 'Unknown error')
      console.error('Failed to clear scan records:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // Delete report
  async function deleteReport(reportId) {
    try {
      isLoading.value = true
      error.value = null

      // Remove from results list
      const resultIndex = scanResults.value.findIndex(r => r.id === reportId)
      if (resultIndex !== -1) {
        scanResults.value.splice(resultIndex, 1)
        saveScanResultsToLocalStorage()
      } else {
        throw new Error('Report not found')
      }

      return true
    } catch (err) {
      error.value = 'Failed to delete report: ' + (err.message || 'Unknown error')
      console.error('Failed to delete report:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // Generate mock vulnerabilities
  function generateMockVulnerabilities(url, modules) {
    const vulnerabilities = []

    // Generate 0-3 vulnerabilities for each enabled module
    modules.forEach(module => {
      // Randomly decide whether to find vulnerabilities
      const vulnerabilityCount = Math.floor(Math.random() * 4) // 0-3 vulnerabilities

      for (let i = 0; i < vulnerabilityCount; i++) {
        const moduleConfig = scanConfig.value.vulnerability_definitions[module]
        if (!moduleConfig) continue

        // Randomly select a pattern
        const randomPatternIndex = Math.floor(Math.random() * moduleConfig.patterns.length)
        const pattern = moduleConfig.patterns[randomPatternIndex]

        // Create vulnerability object
        vulnerabilities.push({
          type: module,
          severity: moduleConfig.severity,
          description: moduleConfig.description,
          url: url,
          test_url: `${url}?id=${module}_test_${i + 1}`,
          details: `A possible ${moduleConfig.description} was found during testing. Detected pattern: "${pattern}"`
        })
      }
    })

    return vulnerabilities
  }

  // Save scans to local storage
  function saveScansToLocalStorage() {
    try {
      localStorage.setItem('scans', JSON.stringify(scans.value))
    } catch (e) {
      console.error('Failed to save scans to local storage:', e)
    }
  }

  // Save scan results to local storage
  function saveScanResultsToLocalStorage() {
    try {
      localStorage.setItem('scanResults', JSON.stringify(scanResults.value))
    } catch (e) {
      console.error('Failed to save scan results to local storage:', e)
    }
  }

  // Load data from local storage
  function loadFromLocalStorage() {
    try {
      // Load scans
      const savedScans = localStorage.getItem('scans')
      if (savedScans) {
        scans.value = JSON.parse(savedScans)
      }

      // Load scan results
      const savedResults = localStorage.getItem('scanResults')
      if (savedResults) {
        scanResults.value = JSON.parse(savedResults)
      }

      // Load config
      const savedConfig = localStorage.getItem('scanConfig')
      if (savedConfig) {
        scanConfig.value = JSON.parse(savedConfig)
      }
    } catch (e) {
      console.error('Failed to load data from local storage:', e)
    }
  }

  // Initial load
  loadFromLocalStorage()

  // Initialize mock data if empty
  function initMockDataIfEmpty() {
    // If there is no scan data in local storage, initialize mock data
    if (scans.value.length === 0) {
      const mockScans = [
        {
          id: 'SCN-20231020-001',
          url: 'https://secure-demo.org',
          start_time: '2023-10-20T22:15:00Z',
          end_time: '2023-10-20T22:18:30Z',
          status: 'completed',
          vulnerabilities: []
        },
        {
          id: 'SCN-20231010-003',
          url: 'https://test-site.com',
          start_time: '2023-10-10T14:20:00Z',
          end_time: '2023-10-10T14:22:15Z',
          status: 'failed',
          error: 'Connection timed out'
        },
        {
          id: 'SCN-20231005-004',
          url: 'https://blog.example.org',
          start_time: '2023-10-05T09:30:00Z',
          end_time: '2023-10-05T09:38:22Z',
          status: 'completed',
          vulnerabilities: [
            { type: 'CSRF', severity: 'Medium' },
            { type: 'Configuration error', severity: 'Low' }
          ]
        },
        {
          id: 'SCN-20231001-005',
          url: 'https://shop.example.com',
          start_time: '2023-10-01T11:45:00Z',
          end_time: '2023-10-01T11:52:10Z',
          status: 'completed',
          vulnerabilities: [
            { type: 'XSS', severity: 'Medium' },
            { type: 'File inclusion', severity: 'High' },
            { type: 'Directory traversal', severity: 'High' },
            { type: 'Sensitive information disclosure', severity: 'Medium' }
          ]
        },
        {
          id: 'SCN-20230925-006',
          url: 'https://api.test.com',
          start_time: '2023-09-25T15:20:00Z',
          end_time: '2023-09-25T15:23:45Z',
          status: 'completed',
          vulnerabilities: []
        },
        {
          id: 'SCN-20230920-007',
          url: 'https://admin.example.org',
          start_time: '2023-09-20T08:10:00Z',
          end_time: '2023-09-20T08:15:32Z',
          status: 'failed',
          error: 'Authentication failed'
        }
      ]

      scans.value = mockScans
      saveScansToLocalStorage()
    }
  }

  // Call the initialization function
  initMockDataIfEmpty()

  return {
    // state
    isLoading,
    error,
    scanResults,
    scans,
    scanConfig,
    activeScansCount,

    // method
    createScan,
    getScanStatus,
    getAllScans,
    getAllResults,
    cancelScan,
    deleteScan,
    clearAllScans,
    deleteReport,
    saveConfig,
    loadConfig,
    updateScanStatus,
    initMockDataIfEmpty,
    saveScansToLocalStorage,
    saveScanResultsToLocalStorage
  }
})