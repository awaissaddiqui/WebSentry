<template>
  <div>
    <div class="flex items-center mb-6">
      <router-link to="/reports" class="text-primary hover:text-primary-dark mr-2">
        <el-icon><ArrowLeft /></el-icon>
      </router-link>
      <h1 class="text-2xl font-semibold text-gray-900">Scan Report Details</h1>
    </div>
    
    <div v-if="isLoading" class="flex justify-center items-center h-64">
      <el-skeleton style="width: 100%" :rows="6" animated />
    </div>
    
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-md p-4 text-red-700 mb-6">
      Failed to load report: {{ error }}
    </div>
    
    <div v-else-if="!report" class="bg-yellow-50 border border-yellow-200 rounded-md p-4 text-yellow-700 mb-6">
      No report found
    </div>
    
    <template v-else>
      <!-- Report title and overview -->
      <div class="card mb-6">
        <h2 class="text-lg font-medium text-gray-900 mb-4">
          <span v-if="report.url" class="max-w-full break-all">{{ report.url }}</span>
          <span v-else class="text-gray-500">Unknown URL</span>
        </h2>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-4">
          <div class="bg-gray-50 p-4 rounded-md">
            <div class="text-sm text-gray-500 mb-1">Scan Status</div>
            <div class="flex items-center">
              <ScanStatusBadge :status="report.status" size="large" />
              <span v-if="report.status === 'failed'" class="ml-2 text-red-600 text-sm">
                {{ report.error || 'Unknown error' }}
              </span>
            </div>
          </div>
          
          <div class="bg-gray-50 p-4 rounded-md">
            <div class="text-sm text-gray-500 mb-1">Scan Time</div>
            <div>
              <div>Start: {{ formatDate(report.start_time) }}</div>
              <div v-if="report.end_time">Finish: {{ formatDate(report.end_time) }}</div>
              <div v-if="report.start_time && report.end_time">
                Duration: {{ calculateDuration(report.start_time, report.end_time) }}
              </div>
            </div>
          </div>
          
          <div class="bg-gray-50 p-4 rounded-md">
            <div class="text-sm text-gray-500 mb-1">Vulnerability Statistics</div>
            <div class="flex items-center">
              <div class="text-lg font-semibold">{{ report.vulnerabilities?.length || 0 }}</div>
              <div class="ml-4 flex flex-wrap gap-1">
                <template v-if="vulnerabilitiesBySeverity">
                  <div v-for="(count, severity) in vulnerabilitiesBySeverity" :key="severity" class="flex items-center mr-3">
                    <VulnerabilityBadge :severity="severity" size="small" />
                    <span class="ml-1 text-sm">{{ count }}</span>
                  </div>
                </template>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Scan module information -->
      <div class="card mb-6" v-if="report.modules && report.modules.length > 0">
        <h3 class="text-lg font-medium text-gray-900 mb-2">Scan Modules</h3>
        <div class="flex flex-wrap gap-2">
          <el-tag v-for="module in report.modules" :key="module">
            {{ getModuleName(module) }}
          </el-tag>
        </div>
      </div>
      
      <!-- Vulnerability Visual Analysis Module -->
      <VulnerabilityVisualizer 
        v-if="report.vulnerabilities && report.vulnerabilities.length > 0"
        :vulnerabilities="report.vulnerabilities"
        title="Vulnerability Analysis & Visualization"
        class="mb-6"
      />
      
      <!-- Vulnerability Details Tabs -->
      <div v-if="report.vulnerabilities && report.vulnerabilities.length > 0" class="card mb-6">
        <el-tabs v-model="activeTab">
          <el-tab-pane label="All Vulnerabilities" name="all">
            <VulnerabilityTable :vulnerabilities="report.vulnerabilities" @view-details="showVulnDetails" />
          </el-tab-pane>
          
          <el-tab-pane 
            v-if="hasVulnType('sql_injection')" 
            label="SQL Injection" 
            name="sql_injection"
          >
            <div class="mb-4">
              <SQLInjectionGuidance />
            </div>
            <VulnerabilityTable 
              :vulnerabilities="getVulnerabilitiesByType('sql_injection')" 
              @view-details="showVulnDetails"
            />
          </el-tab-pane>
          
          <el-tab-pane 
            v-if="hasVulnType('xss')" 
            label="XSS" 
            name="xss"
          >
            <div class="mb-4">
              <XSSGuidance />
            </div>
            <VulnerabilityTable 
              :vulnerabilities="getVulnerabilitiesByType('xss')" 
              @view-details="showVulnDetails"
            />
          </el-tab-pane>
          
          <el-tab-pane 
            v-if="hasVulnType('csrf') || hasVulnType('file_upload')" 
            label="Other Vulnerabilities" 
            name="other"
          >
            <div class="mb-4">
              <OtherVulnerabilitiesGuidance />
            </div>
            <VulnerabilityTable 
              :vulnerabilities="getOtherVulnerabilities()" 
              @view-details="showVulnDetails"
            />
          </el-tab-pane>
        </el-tabs>
      </div>
      
      <!-- Action Buttons -->
      <div class="flex justify-end space-x-4">
        <el-popconfirm
          title="Are you sure you want to delete this report?"
          @confirm="deleteReport"
        >
          <template #reference>
            <el-button type="danger">Delete Report</el-button>
          </template>
        </el-popconfirm>
        
        <el-dropdown @command="exportReport" trigger="click">
          <el-button type="primary">
            Export Report <el-icon class="ml-1"><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="pdf">PDF</el-dropdown-item>
              <el-dropdown-item command="json">JSON</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
      
      <!-- Vulnerability Detail Dialog -->
      <el-dialog
        v-model="showDetailDialog"
        title="Vulnerability Details"
        width="70%"
        destroy-on-close
      >
        <template v-if="selectedVulnerability">
          <div class="vuln-detail">
            <div class="bg-gray-50 p-4 rounded-lg mb-4">
              <div class="flex justify-between items-center mb-2">
                <h3 class="text-lg font-medium">{{ getVulnTypeName(selectedVulnerability.type) }}</h3>
                <VulnerabilityBadge :severity="selectedVulnerability.severity" />
              </div>
              <p>{{ selectedVulnerability.description }}</p>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div v-if="selectedVulnerability.url">
                <div class="text-sm text-gray-500 mb-1">URL:</div>
                <div class="break-all">{{ selectedVulnerability.url }}</div>
              </div>
              
              <div v-if="selectedVulnerability.test_url">
                <div class="text-sm text-gray-500 mb-1">Test URL:</div>
                <div class="break-all">{{ selectedVulnerability.test_url }}</div>
              </div>
            </div>
            
            <div v-if="selectedVulnerability.details" class="mb-4">
              <div class="text-sm text-gray-500 mb-1">Details:</div>
              <div class="bg-gray-50 p-3 rounded font-mono text-sm overflow-auto max-h-40">
                {{ selectedVulnerability.details }}
              </div>
            </div>
            
            <el-divider>Remediation Advice</el-divider>
            
            <div v-if="selectedVulnerability.type === 'sql_injection'">
              <SQLInjectionGuidance />
            </div>
            <div v-else-if="selectedVulnerability.type === 'xss'">
              <XSSGuidance />
            </div>
            <div v-else-if="selectedVulnerability.type === 'csrf' || selectedVulnerability.type === 'file_upload'">
              <OtherVulnerabilitiesGuidance />
            </div>
            <div v-else>
              <div class="text-sm">
                {{ getRemediationAdvice(selectedVulnerability.type) }}
              </div>
            </div>
          </div>
        </template>
        
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="showDetailDialog = false">Close</el-button>
            <el-button type="primary" @click="exportReport('pdf')">Generate PDF</el-button>
          </span>
        </template>
      </el-dialog>
    </template>
    
    <!-- Add PDF template component, hidden by default -->
    <div v-show="showPdfTemplate" ref="pdfContainer" class="pdf-container">
      <ReportPDFTemplate :report="report" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, ArrowDown } from '@element-plus/icons-vue'
import { useScanStore } from '../store/scanStore'
import ScanStatusBadge from '../components/ScanStatusBadge.vue'
import VulnerabilityBadge from '../components/VulnerabilityBadge.vue'
import VulnerabilityVisualizer from '../components/VulnerabilityVisualizer.vue'
import VulnerabilityTable from '../components/VulnerabilityTable.vue'
import SQLInjectionGuidance from '../components/guidance/SQLInjectionGuidance.vue'
import XSSGuidance from '../components/guidance/XSSGuidance.vue'
import OtherVulnerabilitiesGuidance from '../components/guidance/OtherVulnerabilitiesGuidance.vue'
import ReportPDFTemplate from '../components/ReportPDFTemplate.vue'

const route = useRoute()
const router = useRouter()
const scanStore = useScanStore()

// Report data
const reportId = computed(() => route.params.id)
const report = ref(null)

// State
const isLoading = ref(true)
const error = ref(null)
const vulnSearchQuery = ref('')
const activeTab = ref('all')
const showDetailDialog = ref(false)
const selectedVulnerability = ref(null)

// PDF generation
const pdfContainer = ref(null)
const showPdfTemplate = ref(false)

// Module name mapping
const moduleNames = {
  'sql_injection': 'SQL Injection Detection',
  'xss': 'Cross-site Scripting (XSS)',
  'csrf': 'Cross-site Request Forgery',
  'file_upload': 'File Upload Vulnerability'
}

// Vulnerability type name mapping
const vulnTypeNames = {
  'sql_injection': 'SQL Injection',
  'xss': 'Cross-site Scripting (XSS)',
  'csrf': 'Cross-site Request Forgery (CSRF)',
  'file_upload': 'File Upload Vulnerability',
  'error': 'Error'
}

// Remediation advice
const remediationAdvice = {
  'sql_injection': '1. Use parameterized queries or prepared statements\n2. Strictly validate all user input\n3. Use ORM frameworks\n4. Restrict database account permissions\n5. Implement input/output filtering at the application layer',
  'xss': '1. HTML-escape all user input\n2. Implement Content Security Policy (CSP)\n3. Use secure data binding in modern frameworks\n4. Set appropriate X-XSS-Protection headers\n5. Avoid inserting user input directly into JavaScript',
  'csrf': '1. Use CSRF tokens in all forms\n2. Verify the Referer header in requests\n3. Use CAPTCHAs for sensitive operations\n4. Use the SameSite cookie attribute\n5. Implement double submit cookie pattern',
  'file_upload': '1. Validate file type, size, and content\n2. Use secure file names and storage paths\n3. Never execute uploaded files\n4. Store files outside the web root directory\n5. Use a CDN or dedicated server to handle files',
  'error': 'Check system logs for more information'
}

// Vulnerabilities grouped by severity
const vulnerabilitiesBySeverity = computed(() => {
  if (!report.value?.vulnerabilities) return null
  
  const result = {}
  
  report.value.vulnerabilities.forEach(vuln => {
    const severity = vuln.severity || 'Medium'
    if (result[severity]) {
      result[severity]++
    } else {
      result[severity] = 1
    }
  })
  
  return result
})

// Get module name
function getModuleName(moduleId) {
  return moduleNames[moduleId] || moduleId
}

// Get vulnerability type name
function getVulnTypeName(type) {
  return vulnTypeNames[type] || type
}

// Get remediation advice
function getRemediationAdvice(type) {
  return remediationAdvice[type] || 'Please refer to security best practices for remediation.'
}

// Check if a specific type of vulnerability exists
function hasVulnType(type) {
  if (!report.value?.vulnerabilities) return false
  return report.value.vulnerabilities.some(vuln => vuln.type === type)
}

// Get vulnerabilities by type
function getVulnerabilitiesByType(type) {
  if (!report.value?.vulnerabilities) return []
  return report.value.vulnerabilities.filter(vuln => vuln.type === type)
}

// Get other vulnerabilities
function getOtherVulnerabilities() {
  if (!report.value?.vulnerabilities) return []
  return report.value.vulnerabilities.filter(vuln => 
    vuln.type === 'csrf' || vuln.type === 'file_upload'
  )
}

// Show vulnerability details
function showVulnDetails(vuln) {
  selectedVulnerability.value = vuln
  showDetailDialog.value = true
}

// Format date
function formatDate(dateStr) {
  if (!dateStr) return 'Unknown'
  const date = new Date(dateStr)
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  }).format(date)
}

// Calculate duration
function calculateDuration(startStr, endStr) {
  if (!startStr || !endStr) return '--'
  
  const start = new Date(startStr)
  const end = new Date(endStr)
  const diffMs = end - start
  
  const diffSec = Math.floor(diffMs / 1000)
  if (diffSec < 60) return `${diffSec} seconds`
  
  const diffMin = Math.floor(diffSec / 60)
  const remainSec = diffSec % 60
  if (diffMin < 60) return `${diffMin} min ${remainSec} sec`
  
  const diffHour = Math.floor(diffMin / 60)
  const remainMin = diffMin % 60
  return `${diffHour} hr ${remainMin} min`
}

// Delete report
async function deleteReport() {
  try {
    await scanStore.deleteReport(reportId.value)
    ElMessage.success('Report deleted')
    router.push('/reports')
  } catch (err) {
    ElMessage.error('Failed to delete report: ' + (err.message || 'Unknown error'))
  }
}

// Export report
async function exportReport(format = 'json') {
  if (!report.value) return
  
  if (format === 'json') {
    // Create report content
    const reportContent = {
      id: report.value.id,
      url: report.value.url,
      scanDate: report.value.start_time,
      status: report.value.status,
      modules: report.value.modules,
      vulnerabilities: report.value.vulnerabilities
    }
    
    // Convert to JSON
    const jsonStr = JSON.stringify(reportContent, null, 2)
    
    // Create Blob object
    const blob = new Blob([jsonStr], { type: 'application/json' })
    
    // Create download link
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `security-report-${report.value.id}.json`
    
    // Trigger download
    document.body.appendChild(a)
    a.click()
    
    // Cleanup
    setTimeout(() => {
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    }, 0)
    
    ElMessage.success('JSON report exported')
  } else if (format === 'pdf') {
    try {
      ElMessage.info('Preparing to print PDF report, please wait...')
      
      // Show PDF template
      showPdfTemplate.value = true
      
      // Wait for component to render
      await new Promise(resolve => setTimeout(resolve, 500))
      
      // Use browser native print function
      const printWindow = window.open('', '_blank')
      
      if (!printWindow) {
        throw new Error('Please allow the browser to open pop-ups to generate PDF')
      }
      
      // Get PDF template element
      const element = pdfContainer.value.querySelector('.pdf-template')
      if (!element) {
        throw new Error('Cannot find PDF template element')
      }
      
      // Set print window content
      printWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
          <title>Security scan report - ${report.value.id}</title>
          <style>
            body {
              font-family: 'SimSun', 'Arial', sans-serif;
              margin: 0;
              padding: 20px;
              background-color: white;
            }
            .report-header {
              text-align: center;
              margin-bottom: 20px;
              padding-bottom: 15px;
              border-bottom: 1px solid #eee;
            }
            .report-header h1 {
              font-size: 24px;
              margin-bottom: 15px;
            }
            .report-meta {
              text-align: left;
            }
            .report-meta p {
              margin: 5px 0;
            }
            h2 {
              font-size: 18px;
              margin-top: 25px;
              margin-bottom: 10px;
              padding-bottom: 5px;
              border-bottom: 1px solid #eee;
            }
            h3 {
              font-size: 16px;
              margin-top: 15px;
              margin-bottom: 10px;
            }
            .vulnerability-item {
              margin-bottom: 20px;
              padding: 10px;
              background-color: #f9f9f9;
              border-radius: 5px;
            }
            .vulnerability-item h3 {
              margin-top: 0;
            }
            .advice-item {
              margin-bottom: 15px;
            }
            ul {
              padding-left: 20px;
            }
            li {
              margin-bottom: 5px;
            }
            @media print {
              body {
                padding: 0;
              }
              .print-controls {
                display: none !important;
              }
            }
          </style>
        </head>
        <body>
          <div class="print-controls" style="margin-bottom: 20px; text-align: center;">
            <button onclick="window.print()" style="padding: 8px 16px; background-color: #409EFF; color: white; border: none; border-radius: 4px; cursor: pointer; margin-right: 10px;">Print PDF</button>
            <button onclick="window.close()" style="padding: 8px 16px; background-color: #F56C6C; color: white; border: none; border-radius: 4px; cursor: pointer;">Close Window</button>
          </div>
          ${element.outerHTML}
        </body>
        </html>
      `)
      
      printWindow.document.close()
      
      // Auto trigger print
      setTimeout(() => {
        try {
          printWindow.focus() // Ensure window is focused
          printWindow.print() // Open print dialog
        } catch (e) {
          console.error('Auto print failed:', e)
        }
      }, 1000)
      
      // Hide PDF template
      showPdfTemplate.value = false
      
      ElMessage.success('PDF print window opened, please select "Save as PDF"')
    } catch (error) {
      console.error('Error generating PDF:', error)
      ElMessage.error('Failed to generate PDF: ' + error.message)
      
      // Ensure PDF template is hidden
      showPdfTemplate.value = false
    }
  }
}

// Load report data
async function loadReport() {
  try {
    isLoading.value = true
    error.value = null
    
    // Simulate actual API call - in real environment use scanStore.getReport(reportId.value)
    const result = await scanStore.getAllResults()
    const foundReport = result.find(r => r.id === reportId.value)
    
    if (foundReport) {
      report.value = foundReport
    } else {
      error.value = 'Specified report not found'
    }
  } catch (err) {
    error.value = 'Failed to load report: ' + (err.message || 'Unknown error')
    console.error('Failed to load report:', err)
  } finally {
    isLoading.value = false
  }
}

// Initial load
onMounted(() => {
  loadReport()
})

// Watch for route changes, reload data
watch(
  () => route.params.id,
  () => {
    if (route.name === 'report-detail') {
      loadReport()
    }
  }
)
</script>

<style scoped>
.card {
  @apply bg-white rounded-lg shadow-md p-6;
}

/* PDF container style */
.pdf-container {
  position: absolute;
  left: -9999px;
  top: 0;
  width: 210mm; /* A4 width */
  z-index: -1000;
}
</style>