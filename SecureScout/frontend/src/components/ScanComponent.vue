<template>
  <div class="scan-component">
    <div class="bg-white rounded-lg shadow-md p-6">
      <h2 class="text-xl font-semibold mb-4">Start the security scan</h2>
      
      <!-- Scan Form -->
      <el-form
        ref="scanFormRef"
        :model="scanForm"
        :rules="rules"
        label-position="top"
        class="mb-6"
      >
        <el-form-item label="Target URL" prop="url">
          <el-input 
            v-model="scanForm.url" 
            placeholder="Enter the target website URL (e.g.: https://example.com)" 
            :disabled="isScanning"
            clearable
          >
            <template #prefix>
              <el-icon><Link /></el-icon>
            </template>
            <template #append>
              <el-popover
                placement="top"
                width="200"
                trigger="click"
              >
                <template #reference>
                  <el-button>History</el-button>
                </template>
                <div>
                  <p class="text-xs text-gray-500 mb-2">Recently scanned websites:</p>
                  <div v-if="recentlyScannedUrls.length === 0" class="text-center text-gray-400 text-xs">No history</div>
                  <ul class="max-h-40 overflow-auto">
                    <li 
                      v-for="(url, idx) in recentlyScannedUrls" 
                      :key="idx"
                      class="cursor-pointer hover:bg-gray-100 p-1 text-sm text-blue-500 truncate"
                      @click="selectRecentUrl(url)"
                    >
                      {{ url }}
                    </li>
                  </ul>
                </div>
              </el-popover>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item label="Scan Options">
          <div class="flex flex-wrap gap-3">
            <el-checkbox 
              v-model="scanForm.options.xss" 
              label="XSS Detection" 
              :disabled="isScanning"
            />
            <el-checkbox 
              v-model="scanForm.options.sqlInjection" 
              label="SQL Injection Detection" 
              :disabled="isScanning"
            />
            <el-checkbox 
              v-model="scanForm.options.csrf" 
              label="CSRF Detection" 
              :disabled="isScanning"
            />
            <el-checkbox 
              v-model="scanForm.options.fileInclusion" 
              label="File Inclusion Detection" 
              :disabled="isScanning"
            />
            <el-checkbox 
              v-model="scanForm.options.directoryTraversal" 
              label="Directory Traversal Detection" 
              :disabled="isScanning"
            />
            <el-checkbox 
              v-model="scanForm.options.ssrf" 
              label="SSRF Detection" 
              :disabled="isScanning"
            />
          </div>
          
          <div class="flex justify-between mt-2">
            <el-button size="small" @click="selectBasicOptions" :disabled="isScanning">Basic Options</el-button>
            <el-button size="small" @click="selectAllOptions" :disabled="isScanning">Select All</el-button>
            <el-button size="small" @click="selectNoOptions" :disabled="isScanning">Clear</el-button>
            <el-popover
              placement="top"
              width="300"
              trigger="click"
            >
              <template #reference>
                <el-button size="small" type="primary" :disabled="isScanning">Load Template</el-button>
              </template>
              <div>
                <p class="font-medium mb-2">Scan Templates</p>
                <div class="mb-4 space-y-2">
                  <div 
                    v-for="template in scanTemplates" 
                    :key="template.name"
                    class="hover:bg-gray-50 p-2 rounded cursor-pointer"
                    @click="loadTemplate(template)"
                  >
                    <div class="flex justify-between">
                      <span class="font-medium">{{ template.name }}</span>
                      <el-tag size="small" :type="getTemplateTagType(template.level)">{{ template.level }}</el-tag>
                    </div>
                    <p class="text-xs text-gray-500 mt-1">{{ template.description }}</p>
                  </div>
                </div>
              </div>
            </el-popover>
          </div>
        </el-form-item>
        
        <el-form-item label="Scan Depth" prop="depth">
          <el-slider
            v-model="scanForm.depth"
            :min="1"
            :max="5"
            :disabled="isScanning"
            :marks="{
              1: 'Quick',
              3: 'Standard',
              5: 'Deep'
            }"
          />
          
          <div class="text-xs text-gray-500 pt-8">
            <span v-if="scanForm.depth === 1">Estimated time: 1-2 minutes</span>
            <span v-else-if="scanForm.depth === 2">Estimated time: 2-5 minutes</span>
            <span v-else-if="scanForm.depth === 3">Estimated time: 5-10 minutes</span>
            <span v-else-if="scanForm.depth === 4">Estimated time: 10-15 minutes</span>
            <span v-else>Estimated time: 15-30 minutes</span>
          </div>
        </el-form-item>
        
        <el-divider />
        
        <el-form-item>
          <div class="flex items-center">
            <el-button 
              type="primary" 
              :loading="isScanning" 
              @click="submitForm"
              class="mr-4"
            >
              {{ isScanning ? 'Scanning...' : 'Start Scan' }}
            </el-button>
            
            <el-button 
              @click="resetForm" 
              :disabled="isScanning"
            >
              Reset
            </el-button>
            
            <div v-if="isScanning" class="ml-auto flex items-center">
              <span class="text-primary mr-2">Scan Progress:</span>
              <el-progress 
                :percentage="scanProgress" 
                :status="scanProgress === 100 ? 'success' : ''"
                class="w-32"
              />
            </div>
          </div>
        </el-form-item>
      </el-form>
      
      <!-- Scan Status -->
      <div v-if="isScanning || lastScanResult" class="mt-4">
        <el-divider>
          {{ isScanning ? 'Real-time Scan Info' : 'Last Scan Result' }}
        </el-divider>
        
        <div v-if="isScanning" class="bg-gray-50 p-4 rounded-md">
          <div class="mb-2 flex items-center">
            <el-icon class="mr-2 text-primary animate-spin"><Loading /></el-icon>
            <span>Scanning {{ scanForm.url }}</span>
            <el-tag size="small" type="warning" class="ml-2">{{ getStageLabel() }}</el-tag>
          </div>
          
          <div class="relative my-4 border border-gray-200 rounded-md">
            <div class="absolute top-0 left-0 bg-blue-50 h-full transition-all duration-500" :style="{ width: `${scanProgress}%` }"></div>
            <div class="relative z-10 flex justify-between px-4 py-2">
              <div class="flex flex-col items-center">
                <div :class="scanStage >= 1 ? 'bg-blue-500' : 'bg-gray-300'" class="rounded-full w-6 h-6 flex items-center justify-center text-white text-xs mb-1">1</div>
                <span class="text-xs">Prepare</span>
              </div>
              <div class="flex flex-col items-center">
                <div :class="scanStage >= 2 ? 'bg-blue-500' : 'bg-gray-300'" class="rounded-full w-6 h-6 flex items-center justify-center text-white text-xs mb-1">2</div>
                <span class="text-xs">Crawling</span>
              </div>
              <div class="flex flex-col items-center">
                <div :class="scanStage >= 3 ? 'bg-blue-500' : 'bg-gray-300'" class="rounded-full w-6 h-6 flex items-center justify-center text-white text-xs mb-1">3</div>
                <span class="text-xs">Detection</span>
              </div>
              <div class="flex flex-col items-center">
                <div :class="scanStage >= 4 ? 'bg-blue-500' : 'bg-gray-300'" class="rounded-full w-6 h-6 flex items-center justify-center text-white text-xs mb-1">4</div>
                <span class="text-xs">Analysis</span>
              </div>
              <div class="flex flex-col items-center">
                <div :class="scanStage >= 5 ? 'bg-blue-500' : 'bg-gray-300'" class="rounded-full w-6 h-6 flex items-center justify-center text-white text-xs mb-1">5</div>
                <span class="text-xs">Complete</span>
              </div>
            </div>
          </div>
          
          <div class="text-sm text-gray-600 mt-3 h-40 overflow-auto border border-gray-200 rounded-md p-2 bg-white">
            <p v-for="(log, index) in scanLogs" :key="index" class="mb-1">
              <span class="text-gray-500 mr-2">[{{ log.time }}]</span>
              <span :class="{ 'text-red-500': log.type === 'error', 'text-yellow-500': log.type === 'warning', 'text-green-500': log.type === 'success' }">
                {{ log.message }}
              </span>
            </p>
          </div>
          
          <div class="mt-3 text-xs text-gray-500">
            <div class="flex justify-between">
              <span>Pages found: {{ pagesFound }}</span>
              <span>Forms detected: {{ formsScanned }}</span>
              <span>Elapsed time: {{ formatElapsedTime() }}</span>
            </div>
          </div>
        </div>
        
        <div v-else-if="lastScanResult" class="mt-4">
          <div class="bg-gray-50 p-4 rounded-md" :class="{
            'bg-red-50': lastScanResult.vulnerabilitiesFound > 0,
            'bg-green-50': lastScanResult.vulnerabilitiesFound === 0
          }">
            <div class="flex">
              <div class="mr-4">
                <el-icon class="text-3xl" :class="{
                  'text-red-500': lastScanResult.vulnerabilitiesFound > 0,
                  'text-green-500': lastScanResult.vulnerabilitiesFound === 0
                }">
                  <CircleCheckFilled v-if="lastScanResult.vulnerabilitiesFound === 0" />
                  <WarningFilled v-else />
                </el-icon>
              </div>
              
              <div class="flex-1">
                <h3 class="font-semibold text-lg">Scan Complete</h3>
                <div class="flex justify-between items-center mt-1">
                  <p v-if="lastScanResult.vulnerabilitiesFound === 0" class="text-green-600 font-medium">
                    Congratulations! No security vulnerabilities found
                  </p>
                  <p v-else class="text-red-600 font-medium">
                    Found {{ lastScanResult.vulnerabilitiesFound }} potential security vulnerabilities
                  </p>
                  <span class="text-sm text-gray-500">
                    Duration: {{ lastScanResult.duration }}
                  </span>
                </div>
                
                <div class="grid grid-cols-4 gap-3 mt-3 text-center">
                  <div class="bg-white rounded p-2 shadow-sm">
                    <div class="text-lg font-bold text-blue-600">{{ pagesScanned }}</div>
                    <div class="text-xs text-gray-500">Pages Scanned</div>
                  </div>
                  <div class="bg-white rounded p-2 shadow-sm">
                    <div class="text-lg font-bold text-blue-600">{{ formsScanned }}</div>
                    <div class="text-xs text-gray-500">Forms Detected</div>
                  </div>
                  <div class="bg-white rounded p-2 shadow-sm">
                    <div class="text-lg font-bold text-blue-600">{{ jsFilesScanned }}</div>
                    <div class="text-xs text-gray-500">JS Files</div>
                  </div>
                  <div class="bg-white rounded p-2 shadow-sm">
                    <div class="text-lg font-bold" :class="lastScanResult.vulnerabilitiesFound > 0 ? 'text-red-600' : 'text-green-600'">
                      {{ lastScanResult.vulnerabilitiesFound }}
                    </div>
                    <div class="text-xs text-gray-500">Vulnerabilities Found</div>
                  </div>
                </div>
                
                <div class="mt-3 flex justify-between">
                  <div>
                    <el-button type="primary" @click="viewScanReport">
                      View Full Report
                    </el-button>
                    <el-button @click="newScan">
                      New Scan
                    </el-button>
                  </div>
                  <el-button type="primary" plain :disabled="!lastScanResult.url" @click="rescanUrl">
                    Scan Again
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Security Scan Description -->
    <div class="bg-white rounded-lg shadow-md p-6 mt-6">
      <h2 class="text-xl font-semibold mb-4">Security Scan Description</h2>
      
      <div class="space-y-4 text-gray-700">
        <p>
          The website security scanning tool helps you discover potential security vulnerabilities in your website and provides a comprehensive security assessment. By simulating hacker attack methods, it checks for various common security risks.
        </p>
        
        <el-collapse>
          <el-collapse-item title="Supported Scan Types" name="1">
            <div class="space-y-2 pl-4">
              <p><strong>XSS</strong>: Detects cross-site scripting vulnerabilities that may allow attackers to execute malicious code in users' browsers.</p>
              <p><strong>SQL Injection</strong>: Detects SQL injection vulnerabilities that may allow attackers to access or modify database information without authorization.</p>
              <p><strong>CSRF</strong>: Detects cross-site request forgery vulnerabilities that may allow attackers to perform malicious actions as the user.</p>
              <p><strong>File Inclusion</strong>: Detects if the website allows unauthorized inclusion or access to sensitive files.</p>
              <p><strong>Directory Traversal</strong>: Detects if the website allows access to files outside the intended directory structure.</p>
              <p><strong>SSRF</strong>: Detects server-side request forgery vulnerabilities that may allow the server to access internal resources.</p>
            </div>
          </el-collapse-item>
          
          <el-collapse-item title="Scan Depth Explanation" name="2">
            <div class="space-y-2 pl-4">
              <p><strong>Quick Scan (Level 1)</strong>: Scans only the homepage and direct links, suitable for quick checks. Estimated time: 1-2 minutes.</p>
              <p><strong>Standard Scan (Level 3)</strong>: Scans main functions and common entry points, suitable for regular security checks. Estimated time: 5-10 minutes.</p>
              <p><strong>Deep Scan (Level 5)</strong>: Scans all accessible pages and functions for a detailed security analysis. Estimated time: 15-30 minutes.</p>
            </div>
          </el-collapse-item>
          
          <el-collapse-item title="Notes" name="3">
            <div class="space-y-2 pl-4">
              <p>1. It is recommended to scan in a non-production environment or during low-traffic periods to avoid impacting website performance.</p>
              <p>2. Deep scans may trigger website security mechanisms such as WAF or DDoS protection.</p>
              <p>3. Scan results are for reference only. It is recommended to combine with professional security team assessments for remediation.</p>
              <p>4. Unauthorized scanning of third-party websites may violate laws and regulations. Please ensure you have permission to scan the target website.</p>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted, defineProps, defineEmits } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  Link,
  Loading,
  CircleCheckFilled,
  WarningFilled
} from '@element-plus/icons-vue'
import { scanApi } from '@/api'
import { useScanStore } from '@/store/scanStore'

const router = useRouter()
const scanStore = useScanStore()
const scanFormRef = ref(null)

const props = defineProps({
  initialUrl: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['scan-complete', 'scan-started'])

// Scan the template
const scanTemplates = [
  {
    name: 'Basic safety inspection',
    description: 'Detect the most common XSS and SQL injection vulnerabilities',
    level: 'Base',
    options: {
      xss: true,
      sqlInjection: true,
      csrf: false,
      fileInclusion: false,
      directoryTraversal: false,
      ssrf: false
    },
    depth: 2
  },
  {
    name: 'Standard safety inspection',
    description: 'Detect common web application security vulnerabilities',
    level: 'standard',
    options: {
      xss: true,
      sqlInjection: true,
      csrf: true,
      fileInclusion: true,
      directoryTraversal: false,
      ssrf: false
    },
    depth: 3
  },
  {
    name: 'Comprehensive depth scan',
    description: 'Fully scan for all types of security vulnerabilities',
    level: 'advanced',
    options: {
      xss: true,
      sqlInjection: true,
      csrf: true,
      fileInclusion: true,
      directoryTraversal: true,
      ssrf: true
    },
    depth: 5
  }
]

// Get the template tag type
function getTemplateTagType(level) {
  if (level === 'Base') return 'info'
  if (level === 'standard') return 'warning'
  return 'danger'
}

// Loading templates
function loadTemplate(template) {
  scanForm.options = { ...template.options }
  scanForm.depth = template.depth
  ElMessage.success(`Loaded"${template.name}"template`)
}

// Scan the form
const scanForm = reactive({
  url: props.initialUrl,
  options: {
    xss: true,
    sqlInjection: true,
    csrf: false,
    fileInclusion: false,
    directoryTraversal: false,
    ssrf: false
  },
  depth: 3
})

// Monitor changes in initialUrl attribute, automatically fill the URL and optionally start scanning
watch(() => props.initialUrl, (newUrl) => {
  if (newUrl && !isScanning.value) {
    scanForm.url = newUrl
    // If the URL is redirected from "rescan", the scan will automatically start after a short delay of a while
    setTimeout(() => {
      submitForm()
    }, 1000)
  }
}, { immediate: true })

// form validation rules
const rules = {
  url: [
    { required: true, message: 'Please enter destination URL', trigger: 'blur' },
    { 
      pattern: /^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$/,
      message: 'Please enter a valid URL address',
      trigger: 'blur'
    }
  ]
}

// History
const recentlyScannedUrls = ref([
  'https://example.com',
  'https://test-site.org',
  'https://demo.websecurity.com'
])

// Select historical URL
function selectRecentUrl(url) {
  scanForm.url = url
  ElMessage.success('History URL selected')
}

// Scan status
const isScanning = ref(false)
const scanProgress = ref(0)
const scanStage = ref(0)
const scanStartTime = ref(null)
const scanLogs = ref([])
const lastScanResult = ref(null)

// Scan statistics
const pagesFound = ref(0)
const pagesScanned = ref(0)
const formsScanned = ref(0)
const jsFilesScanned = ref(0)

// Get the current stage label
function getStageLabel() {
  const stages = ['Preparing', 'Crawling', 'Detecting', 'Analyzing', 'Completed']
  return stages[scanStage.value - 1] || 'Waiting'
}

// Formatted elapsed time
function formatElapsedTime() {
  if (!scanStartTime.value) return '00:00:00'
  
  const elapsed = Date.now() - scanStartTime.value
  const seconds = Math.floor((elapsed / 1000) % 60)
  const minutes = Math.floor((elapsed / (1000 * 60)) % 60)
  const hours = Math.floor(elapsed / (1000 * 60 * 60))
  
  return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
}

// Select the basic options
function selectBasicOptions() {
  scanForm.options = {
    xss: true,
    sqlInjection: true,
    csrf: false,
    fileInclusion: false,
    directoryTraversal: false,
    ssrf: false
  }
  ElMessage.success('Basic Scan option selected')
}

// Select all options
function selectAllOptions() {
  Object.keys(scanForm.options).forEach(key => {
    scanForm.options[key] = true
  })
  ElMessage.success('All scan options selected')
}

// Clear all options
function selectNoOptions() {
  Object.keys(scanForm.options).forEach(key => {
    scanForm.options[key] = false
  })
  ElMessage.warning('All scan options have been cleared')
}

// Scan the last URL again
function rescanUrl() {
  if (lastScanResult.value && lastScanResult.value.url) {
    scanForm.url = lastScanResult.value.url
    lastScanResult.value = null
    submitForm()
  }
}

// Submit a form
function submitForm() {
  if (!scanFormRef.value) return
  
  scanFormRef.value.validate(async (valid) => {
    if (valid) {
      startScan()
    }
  })
}

// Reset the form
function resetForm() {
  if (!scanFormRef.value) return
  
  scanFormRef.value.resetFields()
  scanForm.options = {
    xss: true,
    sqlInjection: true,
    csrf: false,
    fileInclusion: false,
    directoryTraversal: false,
    ssrf: false
  }
  scanForm.depth = 3
  
  scanLogs.value = []
  lastScanResult.value = null
}

// Create a new scan
function newScan() {
  lastScanResult.value = null
}

// View the full report
function viewScanReport() {
  router.push('/reports')
}

// Start scanning
async function startScan() {
  try {
    isScanning.value = true
    scanStartTime.value = Date.now()
    scanProgress.value = 0
    scanStage.value = 1
    pagesFound.value = 0
    formsScanned.value = 0
    scanLogs.value = []
    
    // Log start log
    addScanLog('Start scanning: ' + scanForm.url, 'info')
    
    // Add URL to recent scan history
    addToRecentUrls(scanForm.url)
    
    // Get enabled modules
    const enabledModules = []
    for (const [key, value] of Object.entries(scanForm.options)) {
      if (value) {
        enabledModules.push(key)
      }
    }
    
    // Create a scan task
    const scanId = await scanStore.createScan(scanForm.url, enabledModules)
    
    // Trigger scan-started event
    emit('scan-started', { 
      scanId, 
      url: scanForm.url,
      modules: enabledModules 
    })
    
    // Simulate the scanning process
    simulateScanProcess(scanId)
  } catch (error) {
    console.error('Starting scan failed:', error)
    ElMessage.error('Starting scan failed: ' + (error.message || 'Unknown error'))
    isScanning.value = false
  }
}

// Functions that simulate scan progress
function simulateScanProcess(scanId) {
  // Adjust the scan time according to depth
  const totalTime = scanForm.depth * 20000 // 20 seconds per depth level
  const updateInterval = 500 // Update status every 500ms
  const totalUpdates = totalTime / updateInterval
  
  let currentUpdate = 0
  
  // Initial Phase - Preparation Phase
  scanStage.value = 1
  addScanLog('Initializing the scanning environment...', 'info')
  setTimeout(() => {
    addScanLog('Checking accessibility of target websites...', 'info')
  }, 1000)
  
  const intervalId = setInterval(() => {
    currentUpdate++
    const progress = Math.min(99, Math.floor((currentUpdate / totalUpdates) * 100))
    scanProgress.value = progress
    
    // Update phase and log according to progress
    if (progress >= 15 && scanStage.value < 2) {
      scanStage.value = 2 // Crawl phase
      addScanLog('The website is accessible and start crawling the page...', 'info')
      setTimeout(() => {
        pagesFound.value = Math.floor(Math.random() * 10) + 5
        addScanLog(`Discover ${pagesFound.value} Pages and links`, 'info')
      }, 1000)
    }
    
    if (progress >= 40 && scanStage.value < 3) {
      scanStage.value = 3 // Testing phase
      addScanLog('Start detecting potential vulnerabilities...', 'info')
      
      // Simulation Discovery Form
      formsScanned.value = Math.floor(Math.random() * 5) + 1
      addScanLog(`Detected ${formsScanned.value} A form`, 'info')
      
      // Simulate discovery of JS files
      jsFilesScanned.value = Math.floor(Math.random() * 8) + 3
      addScanLog(`analyze ${jsFilesScanned.value} JavaScript files`, 'info')
      
      // Generate vulnerability logs based on selected options
      setTimeout(() => {
        if (scanForm.options.xss) {
          if (Math.random() > 0.7) {
            addScanLog('Discover XSS vulnerabilities: Form input is not filtered', 'warning')
          }
        }
      }, 2000)
      
      setTimeout(() => {
        if (scanForm.options.sqlInjection) {
          if (Math.random() > 0.6) {
            addScanLog('Potential SQL injection vulnerabilities discovered: Query parameters are not preprocessed', 'warning')
          }
        }
      }, 3500)
      
      setTimeout(() => {
        if (scanForm.options.fileInclusion) {
          if (Math.random() > 0.8) {
            addScanLog('Potential fiPath stitching is not safeains vulnerabilities discovered: Path stitching is not safe', 'warning')
          }
        }
      }, 5000)
    }
    
    if (progress >= 70 && scanStage.value < 4) {
      scanStage.value = 4 // Analysis phase
      addScanLog('Analyzing collected data...', 'info')
      
      setTimeout(() => {
        // Calculate the number of scanned pages
        pagesScanned.value = pagesFound.value
        addScanLog(`Completed ${pagesScanned.value} Analysis of pages`, 'info')
      }, 1000)
    }
    
    if (progress >= 95) {
      scanStage.value = 5 // Complete phase
      clearInterval(intervalId)
      
      // Simulation completed
      setTimeout(() => {
        completeScan(scanId)
      }, 1000)
    }
  }, updateInterval)
}

// Complete the scan
function completeScan(scanId) {
  // Update status
  isScanning.value = false
  scanProgress.value = 100
  
  // Calculate the number of vulnerabilities found
  const vulnerabilitiesFound = scanLogs.value.filter(log => log.type === 'warning').length
  
  // Add the last log
  addScanLog(`Scan is complete.Discover ${vulnerabilitiesFound} A potential security vulnerability.`, 
    vulnerabilitiesFound > 0 ? 'warning' : 'success')
  
  // Update results
  lastScanResult.value = {
    scanId: scanId,
    url: scanForm.url,
    scanDate: new Date().toISOString(),
    vulnerabilitiesFound,
    duration: formatElapsedTime()
  }
  
  // Show notifications
  ElMessage({
    message: vulnerabilitiesFound > 0 
      ? `Scan completes and discovers ${vulnerabilitiesFound} A potential security vulnerability.` 
      : 'The scan was completed and no security vulnerabilities were found.',
    type: vulnerabilitiesFound > 0 ? 'warning' : 'success'
  })
  
  // Trigger scan completion event
  emit('scan-complete', lastScanResult.value)
}

// Add scan log
function addScanLog(message, type = 'info') {
  const now = new Date()
  const timeStr = now.toLocaleTimeString('en-US')
  
  scanLogs.value.push({
    time: timeStr,
    message,
    type
  })
  
  // Keep the log not too long
  if (scanLogs.value.length > 50) {
    scanLogs.value.shift()
  }
}

// Add URL to recent scan history
function addToRecentUrls(url) {
  if (!recentlyScannedUrls.value.includes(url)) {
    recentlyScannedUrls.value.unshift(url)
    if (recentlyScannedUrls.value.length > 5) {
      recentlyScannedUrls.value.pop()
    }
    // Save to localStorage
    localStorage.setItem('recentScannedUrls', JSON.stringify(recentlyScannedUrls.value))
  }
}

// Life cycle hook
onMounted(() => {
  // You can load history, etc. here
})
</script>

<style scoped>
.scan-component {
  width: 100%;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}
</style>