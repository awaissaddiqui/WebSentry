<template>
  <div class="reports-view min-h-screen bg-gray-50 p-6">
    <h1 class="text-2xl font-bold mb-6">Security Scan Reports</h1>
    <!-- Loading status -->
    <div v-if="isLoading" class="bg-white rounded-lg shadow-md p-6">
      <div class="flex justify-between items-center mb-4">
        <div>
          <h2 class="text-xl font-semibold mb-1">Loading report...</h2>
          <p class="text-gray-500">Please wait for a moment</p>
        </div>
      </div>
      
<!-- Skeleton Screen -->      <el-skeleton :rows="5" animated />
    </div>
    
    <!-- No report prompt -->
    <div v-else-if="reports.length === 0" class="bg-white rounded-lg shadow-md p-8 text-center">
      <el-empty 
        description="No scan report yet" 
        :image-size="200"
      >
        <template #extra>
          <el-button type="primary" @click="startNewScan">Start a new scan</el-button>
        </template>
      </el-empty>
    </div>
    
    <!-- Report list -->

<div v-else class="bg-white rounded-lg shadow-md p-6">
  <div class="flex justify-between items-center mb-6">
    <h2 class="text-xl font-semibold">Scan the report list</h2>
    <el-button type="primary" @click="startNewScan">Create a new scan</el-button>
  </div>
  
  <!-- Add a wrapper with horizontal scroll -->
  <div style="overflow-x: auto;">
    <el-table 
      :data="reports" 
      style=" min-width: 900px;" 
      border 
      stripe 
      highlight-current-row
      @row-click="(row) => viewReport(row.id)"
    >
      <el-table-column label="ID" prop="id" width="80" />
      <el-table-column label="Destination URL" prop="url" min-width="100">
        <template #default="{ row }">
          <el-link 
            type="primary" 
            :href="row.url" 
            target="_blank" 
            @click.stop
          >
            {{ row.url }}
          </el-link>
        </template>
      </el-table-column>
      <el-table-column label="Scan time" width="180">
        <template #default="{ row }">
          {{ formatDate(row.scanDate) }}
        </template>
      </el-table-column>
      <el-table-column label="state" width="120">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)">
            {{ row.status }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="Number of vulnerabilities" width="120" align="center">
        <template #default="{ row }">
          <el-tag 
            :type="row.vulnerabilities > 0 ? 'danger' : 'success'"
            effect="dark"
          >
            {{ row.vulnerabilities }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="operation" width="220">
        <template #default="{ row }">
          <div class="flex space-x-2">
            <el-button 
              size="small" 
              type="primary" 
              plain
              @click.stop="viewReport(row.id)"
            >
              check the details
            </el-button>
            <el-button 
              size="small" 
              type="danger" 
              plain
              @click.stop="confirmDelete(row.id)"
            >
              delete
            </el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>
  </div>
</div>
    
    <!-- Report Details Dialog -->
    <el-dialog
      v-model="showReportDialog"
      title="Scan the report details"
      width="70%"
      destroy-on-close
    >
      <div v-if="selectedReport" class="report-detail">
        <!-- Basic information -->
        <div class="mb-6 p-4 bg-gray-50 rounded-md">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p class="text-gray-600">Scan ID:<span class="font-medium text-gray-800">{{ selectedReport.id }}</span></p>
              <p class="text-gray-600">Destination URL:
                <el-link 
                  type="primary" 
                  :href="selectedReport.url" 
                  target="_blank"
                >
                  {{ selectedReport.url }}
                </el-link>
              </p>
              <p class="text-gray-600">Scan time:<span class="font-medium text-gray-800">{{ formatDate(selectedReport.scanDate) }}</span></p>
            </div>
            <div>
              <p class="text-gray-600">
                state:
                <el-tag :type="getStatusType(selectedReport.status)">{{ selectedReport.status }}</el-tag>
              </p>
              <p class="text-gray-600">Scan Depth:<span class="font-medium text-gray-800">{{ selectedReport.depth || 'standard' }}</span></p>
            <p class="text-gray-600">
  Scan duration:
  <span class="font-medium text-gray-800">
    {{
      selectedReport.start_time && selectedReport.end_time
        ? formatDuration(selectedReport.start_time, selectedReport.end_time)
        : (selectedReport.duration || '--')
    }}
  </span>
</p>
            </div>
          </div>
        </div>
        
        <!-- Vulnerability Overview -->
        <div class="mb-6">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-semibold">Vulnerability Overview</h3>
            <div>
              <el-tag 
                :type="selectedReport.vulnerabilities > 0 ? 'danger' : 'success'"
                size="large"
              >
                {{ selectedReport.vulnerabilities > 0 
                  ? `Discover ${selectedReport.vulnerabilities} A loophole` 
                  : 'No loopholes found' 
                }}
              </el-tag>
            </div>
          </div>
          
          <div v-if="selectedReport.vulnerabilities > 0" class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Vulnerability distribution map -->
            <div>
              <div ref="vulnChartRef" style="height: 250px;"></div>
            </div>
            
            <!-- Safety rating -->
            <div class="flex flex-col items-center justify-center p-4 bg-gray-50 rounded-lg">
              <div class="mb-2 text-lg font-semibold">Website security rating</div>
              <div class="relative">
                <el-progress 
                  type="dashboard" 
                  :percentage="Math.max(0, 100 - selectedReport.vulnerabilities * (selectedReport.vulnerabilities > 3 ? 15 : 10))" 
                  :color="selectedReport.vulnerabilities > 3 ? '#F56C6C' : selectedReport.vulnerabilities > 0 ? '#E6A23C' : '#67C23A'"
                  :width="150"
                />
                <!-- <div class="absolute  flex items-center justify-center">
                  <span class="text-3xl font-bold text-red-800">
                    {{ Math.max(0, 100 - selectedReport.vulnerabilities * (selectedReport.vulnerabilities > 3 ? 15 : 10)) }}
                  </span>
                </div> -->
              </div>
              <p class="text-sm text-gray-500 mt-2">
                {{ selectedReport.vulnerabilities > 3 ? 'The website has serious security risks' : 
                   selectedReport.vulnerabilities > 0 ? 'Potential security risks on the website' : 
                   'The website is in good security' }}
              </p>
            </div>
          </div>
          
          <div v-if="selectedReport.vulnerabilities === 0" class="text-center p-8">
            <el-result
              icon="success"
              title="Congratulations! No security vulnerabilities were found"
              sub-title="Your website has not found any security vulnerabilities in this scan, and you can perform security scans regularly to maintain a good security state."
            />
          </div>
        </div>
        
        <!-- Vulnerability details -->
        <div v-if="selectedReport.vulnerabilityDetails && selectedReport.vulnerabilityDetails.length > 0">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-semibold">Vulnerability details</h3>
            <el-radio-group v-model="selectedFilter" size="small">
              <el-radio-button label="all">all</el-radio-button>
              <el-radio-button label="high">High risk</el-radio-button>
              <el-radio-button label="medium">Medium risk</el-radio-button>
              <el-radio-button label="low">Low risk</el-radio-button>
            </el-radio-group>
          </div>
          
          <div v-if="filteredVulnerabilities.length === 0" class="text-center p-4 bg-gray-50 rounded">
            <p class="text-gray-500">There are no vulnerabilities under the current filter conditions</p>
          </div>
          
          <el-collapse accordion v-else>
            <el-collapse-item 
              v-for="(vuln, index) in filteredVulnerabilities" 
              :key="index"
              :title="vuln.type"
              :name="index"
            >
              <template #title>
                <div class="flex items-center">
                  <el-tag 
                    :type="getSeverityType(vuln.severity)" 
                    size="small" 
                    class="mr-2"
                  >
                    {{ vuln.severity }}
                  </el-tag>
                  <span>{{ vuln.type }}</span>
                </div>
              </template>
              
              <div class="vuln-detail pl-2">
                <!-- <p class="mb-2"><strong>Location:</strong> {{ vuln.location }}</p> -->
               <p class="mb-2">
  <strong>Location:</strong>
  {{
    (() => {
      const ref = vulnerabilityDetailsArray.find(v =>
        v.type.toLowerCase().includes(vuln.type.toLowerCase()) ||
        vuln.type.toLowerCase().includes(v.type.toLowerCase())
      );
      return ref?.location || vuln.location || '--';
    })()
  }}
</p>
                <p class="mb-2"><strong>describe:</strong> {{ vuln.description }}</p>
                
                <el-divider>Details</el-divider>
                
                <p class="mb-2"><strong>Risk level:</strong> {{ vuln.severity }}</p>
                <!-- <p class="mb-2"><strong>Influence:</strong> {{ vuln.impact }}</p> -->
                
                <!-- <div v-if="vuln.evidence" class="mt-4">
                  <p class="font-medium mb-1">evidence:dence:</p>
                  <div class="bg-gray-100 p-3 rounded font-mono text-sm overflow-auto max-h-40">
                    {{ vuln.evidence }}
                  </div>
                </div> -->
                
                <!-- <div v-if="vuln.type.toLowerCase().includes('xss')">
        <p class="font-medium mb-1">evidence:</p>
        <div class="bg-gray-100 p-3 rounded font-mono text-sm overflow-auto max-h-40">
          {{
            vulnerabilityDetailsArray.find(v => v.type.toLowerCase().includes('xss'))?.evidence || vuln.evidence
          }}
        </div>
      </div>
      <div v-else-if="vuln.evidence">
        <p class="font-medium mb-1">evidence:</p>
        <div class="bg-gray-100 p-3 rounded font-mono text-sm overflow-auto max-h-40">
          {{ vuln.evidence }}
        </div>
      </div>

                
                <el-divider>Repair suggestions</el-divider>
                <p class="mb-3">{{ vuln.remediation }}</p> -->
                <p class="mb-2">
  <strong>Evidence:</strong>
  {{
    (() => {
      const ref = vulnerabilityDetailsArray.find(v =>
        v.type.toLowerCase().includes(vuln.type.toLowerCase()) ||
        vuln.type.toLowerCase().includes(v.type.toLowerCase())
      );
      return ref?.evidence || vuln.evidence || '--';
    })()
  }}
</p>
<p class="mb-2">
  <strong>Repair suggestions:</strong>
  {{
    (() => {
      const ref = vulnerabilityDetailsArray.find(v =>
        v.type.toLowerCase().includes(vuln.type.toLowerCase()) ||
        vuln.type.toLowerCase().includes(v.type.toLowerCase())
      );
      return vuln.remediation || ref?.remediation || '--';
    })()
  }}
</p>
                
                <div class="flex justify-end">
                  <el-button size="small" type="success" @click.stop="viewRemediationGuide(vuln.type)">
                    View detailed repair guide
                  </el-button>
                </div>
              </div>
            </el-collapse-item>
          </el-collapse>
        </div>
      </div>
      
      <template #footer>
        <div class="flex justify-between">
          <el-button @click="showReportDialog = false">Close</el-button>
          <div class="space-x-2">
            <el-dropdown @command="exportReport" trigger="click">
              <el-button type="primary" :loading="isExporting">
                Export the reportrt the report <el-icon class="el-icon--right"><arrow-down /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="pdf">PDF format</el-dropdown-item>
                  <el-dropdown-item command="html">HTML format</el-dropdown-item>
                  <el-dropdown-item command="csv">CSV format</el-dropdown-item>
                  <el-dropdown-item command="docx">Word format</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
            <el-button type="success" @click="shareReport">
              Share the report
            </el-button>
            <el-button type="primary" plain @click="generatePdfReport">
              Generate PDF
            </el-button>
            <el-button type="danger" @click="confirmDelete(selectedReport?.id)" plain>
              Delete the report
            </el-button>
          </div>
        </div>
      </template>
    </el-dialog>
    
    <!-- Delete Confirmation dialog box -->
    <el-dialog
      v-model="showDeleteDialog"
      title="Confirm deletion"
      width="30%"
    >
      <p>Are you sure you want to delete this scan report?This operation cannot be cancelled. to delete this scan report?This operation cannot be cancelled.</p>
      <template #footer>
        <div class="flex justify-end space-x-2">
          <el-button @click="showDeleteDialog = false">Cancel</el-button>
          <el-button type="danger" @click="deleteReport" :loading="isDeleting">
            Confirm deletion
          </el-button>
        </div>
      </template>
    </el-dialog>
    
    <!-- Share dialog box -->
    <el-dialog
      v-model="showShareDialog"
      title="Share a security report"
      width="40%"
    >
      <div class="share-dialog-content">
        <p class="mb-4">You can share this security report in the following ways:</p>
        
        <div class="mb-6">
          <h4 class="font-medium mb-2">Send by mail</h4>
          <el-form>
            <el-form-item>
              <el-input
                v-model="emailAddresses"
                placeholder="Please enter the recipient's email address, please separate multiple email addresses with commas."
                type="textarea"
                :rows="2"
              />
            </el-form-item>
          </el-form>
        </div>
        
        <div class="mb-6">
          <h4 class="font-medium mb-2">Or share via link</h4>
          <div class="flex space-x-2">
            <el-input
              v-model="reportLink"
              readonly
            />
            <el-button type="primary" @click="ElMessage.success('Link copied to clipboard')">
              copy
            </el-button>
          </div>
          <p class="text-xs text-gray-500 mt-1">This link is valid for 7 days and authorization is required to access it</p>
        </div>
        
        <div>
          <h4 class="font-medium mb-2">Export format options</h4>
          <el-radio-group v-model="shareFormat">
            <el-radio label="pdf">PDF format</el-radio>
            <el-radio label="html">HTML format</el-radio>
            <el-radio label="docx">Word format</el-radio>
          </el-radio-group>
        </div>
      </div>
      
      <template #footer>
        <div class="flex justify-between">
          <el-button @click="showShareDialog = false">Cancel</el-button>
          <el-button type="primary" @click="sendEmailReport" :loading="isSendingEmail">
            send
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import { Delete, Refresh, DocumentRemove, View } from '@element-plus/icons-vue'
import ScanStatusBadge from '@/components/ScanStatusBadge.vue'
import { useScanStore } from '@/store/scanStore'
import { onActivated } from 'vue';
import logo from '../../imgs/logo.jpg'

onActivated(() => {
  loadReports();
});

const scanStore = useScanStore()
const router = useRouter()

// state
const isLoading = ref(true)
const reports = ref([])
const showReportDialog = ref(false)
const showDeleteDialog = ref(false)
const selectedReport = ref(null)
const reportToDelete = ref(null)
const isDeleting = ref(false)
const isExporting = ref(false)
const showShareDialog = ref(false)
const emailAddresses = ref('')
const isSendingEmail = ref(false)
const vulnChartRef = ref(null)
const selectedFilter = ref('all')
const shareFormat = ref('pdf')
const reportLink = ref('')
let vulnChart = null

// initialization
onMounted(() => {
  loadReports()
})

// Format the duration
function formatDuration(start, end) {
  if (!start || !end) return '--'
  const startDate = new Date(start)
  const endDate = new Date(end)
  const ms = endDate - startDate
  if (isNaN(ms) || ms < 0) return '--'
  const totalSeconds = Math.floor(ms / 1000)
  const hours = Math.floor(totalSeconds / 3600)
  const minutes = Math.floor((totalSeconds % 3600) / 60)
  const seconds = totalSeconds % 60
  return [
    hours > 0 ? String(hours).padStart(2, '0') : null,
    String(minutes).padStart(2, '0'),
    String(seconds).padStart(2, '0')
  ].filter(Boolean).join(':')
}

// Loading report list
async function loadReports() {
  isLoading.value = true
  try {
    // Fetch real scan results from localStorage
    const allScans = JSON.parse(localStorage.getItem('scans') || '[]');
    // Filter for completed scans and map to table structure
    reports.value = allScans
      .filter(scan => scan.status === 'Completed' || scan.status === 'completed')
      .map(scan => ({
        id: scan.id,
        url: scan.url,
        scanDate: scan.scanDate || scan.scan_time || scan.start_time,
        status: scan.status,
        vulnerabilities: Array.isArray(scan.vulnerabilities)
          ? scan.vulnerabilities.length
          : (typeof scan.vulnerabilities === 'number'
              ? scan.vulnerabilities
              : 0),
        vulnerabilityDetails: scan.vulnerabilityDetails || scan.vulnerabilities || [],
        depth: scan.depth || 'standard',
        duration: (scan.start_time && scan.end_time)
      ? formatDuration(scan.start_time, scan.end_time)
      : (scan.duration || '--')
      }))
  } catch (error) {
    console.error('Failed to load reports:', error)
    ElMessage.error('Failed to load reports, please try again later')
  } finally {
    isLoading.value = false
  }
}

// Computational properties: Filter by vulnerability severity
const filteredVulnerabilities = computed(() => {
  if (!selectedReport.value) return []
  
  const vulns = selectedReport.value.vulnerabilityDetails || []
  console.log('Filtered vulnerabilities:', vulns)
  
  if (selectedFilter.value === 'all') {
    return vulns
  } else {
    return vulns.filter(v => {
      if (selectedFilter.value === 'High') return v.severity === 'high' || v.severity =='severe'
      if (selectedFilter.value === 'Medium') return v.severity === 'middle'
      if (selectedFilter.value === 'Low') return v.severity === 'low'
      return true
    })
  }
})

// View report details
function viewReport(id) {
  const report = reports.value.find(r => r.id === id)
  if (report) {
    selectedReport.value = report
    showReportDialog.value = true
    selectedFilter.value = 'all'
    
    // Initialize the chart
    setTimeout(() => {
      initVulnerabilityChart()
    }, 300)
  }
}

// Confirm deletion
function confirmDelete(id) {
  if (!id) return
  
  reportToDelete.value = id
  showReportDialog.value = false
  showDeleteDialog.value = true
}

// Delete the report
async function deleteReport() {
  if (!reportToDelete.value) return
  
  isDeleting.value = true
  
  try {
    // Use scanStore to delete reports and make sure to sync to localStorage
    await scanStore.deleteReport(reportToDelete.value)
    
    // Update interface display
    reports.value = reports.value.filter(r => r.id !== reportToDelete.value)
    console.log(reports.value)
    
    ElMessage({
      type: 'success',
      message: 'Report has been successfully deleted'
    })
    
    showDeleteDialog.value = false
    reportToDelete.value = null
  } catch (error) {
    console.error('Failed to delete the report:', error)
 ElMessage.error('Failed to delete report: ' + (error.message || 'Unknown error'))
  } finally {
    isDeleting.value = false
  }
}

// Export the report
async function exportReport(format = 'pdf') {
  if (!selectedReport.value) return
  
  isExporting.value = true
  
  try {
    // Simulate the export process
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    ElMessage({
      type: 'success',
      message: `The report has been successfully Formated exported as${format.toUpperCase()}Format`
    })
  } catch (error) {
    console.error('Export report failed:', error)
    ElMessage.error('The export report failed, please try again later')
  } finally {
    isExporting.value = false
  }
}

// Share the report
function shareReport() {
  if (!selectedReport.value) return
  showReportDialog.value = false
  showShareDialog.value = true
  emailAddresses.value = ''
  // Set a sharing link
  reportLink.value = 'https://CySmart-ai.example.com/reports/' + selectedReport.value.id
}

// Send email reports
async function sendEmailReport() {
  if (!emailAddresses.value.trim()) {
    ElMessage.warning('Please enter a valid email address')
    return
  }
  
  isSendingEmail.value = true
  
  try {
    // Simulate the process of sending emails
    await new Promise(resolve => setTimeout(resolve, 1200))
    
    ElMessage({
      type: 'success',
      message: `The report has been sent successfully to: ${emailAddresses.value}`
    })
    
    showShareDialog.value = false
  } catch (error) {
    console.error('Failed to send an email:', error)
    ElMessage.error('The email has failed, please try again later')
  } finally {
    isSendingEmail.value = false
  }
}

// Start a new scan
function startNewScan() {
  router.push('/scan')
}

// Format date
function formatDate(dateString) {
  if (!dateString) return '-'
  
  try {
    const date = new Date(dateString)
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch (e) {
    return dateString
  }
}

// Get the status type
// remember comment
function getStatusType(status) {
  if (status === 'completed') return 'success'
  if (status === 'in_progress') return 'primary'
  if (status === 'failed') return 'danger'
  return 'info'
}

// Obtain severity type
function getSeverityType(severity) {
  if (severity === 'critical' || severity == 'high') return 'danger'
  if (severity === 'middle') return 'warning'
  if (severity === 'low') return 'info'
  return 'info'
}

// Initialize vulnerability chart
function initVulnerabilityChart() {
  if (!vulnChartRef.value || !selectedReport.value) return
  
  const vulns = selectedReport.value.vulnerabilityDetails || []
  if (vulns.length === 0) return
  
  // Destroy old chart instances
  if (vulnChart) {
    vulnChart.dispose()
  }
  
  // Make sure the DOM elements are visible
  if (vulnChartRef.value && vulnChartRef.value.offsetHeight > 0) {
    // Create a new chart instance
    vulnChart = echarts.init(vulnChartRef.value)
    
    // Prepare data
    const severityCounts = {
      'Critical': 0,
      'High': 0,
      'Medium': 0,
      'Low': 0
    }
    
    const typeCounts = {}
    
    vulns.forEach(vuln => {
      // Calculate the severity distribution
      if (vuln.severity === 'Critical' || vuln.severity == 'High') {
        severityCounts[vuln.severity]++
      } else {
        severityCounts[vuln.severity]++
      }
      
      // Calculate type distribution
      typeCounts[vuln.type] = (typeCounts[vuln.type] || 0) + 1
    })
    
    // Prepare chart data
    const severityData = Object.entries(severityCounts)
      .filter(([_, count]) => count > 0)
      .map(([name, value]) => ({ name, value }))
    
    const typeData = Object.entries(typeCounts)
      .map(([name, value]) => ({ name, value }))
    
    // Set up chart configuration
    const option = {
      tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b}: {c} ({d}%)'
      },
      legend: {
        orient: 'vertical',
        right: 10,
        top: 'center',
        data: typeData.map(item => item.name)
      },
      series: [
        {
          name: 'Vulnerability severity',
          type: 'pie',
          radius: ['40%', '60%'],
          center: ['30%', '50%'],
          avoidLabelOverlap: false,
          label: {
            show: false,
            position: 'center'
          },
          emphasis: {
            label: {
              show: true,
              fontSize: '18',
              fontWeight: 'bold'
            }
          },
          data: severityData.map(item => ({
            name: item.name,
            value: item.value,
            itemStyle: {
              color: item.name === 'Critical' || item.name === 'High' ? '#F56C6C' : 
                    item.name === 'Medium' ? '#E6A23C' : '#67C23A'
            }
          }))
        },
        {
          name: 'Vulnerability Type',
          type: 'pie',
          radius: ['0%', '30%'],
          center: ['30%', '50%'],
          label: {
            position: 'inner',
            fontSize: 12
          },
          data: typeData
        }
      ]
    }
    
    // Application configurationication configuration
    vulnChart.setOption(option)
    
    // Add window zoom listeningow zoom listening
    window.addEventListener('resize', () => {
      vulnChart && vulnChart.resize()
    })
  }
}

// my vulnerability chart
const vulnerabilityDetailsArray = [
          {
            type: 'XSS cross-site scripting attack',
            severity: 'high',
            location: '/search?q=',
            description: 'The search function has a reflected XSS vulnerability, which may lead to malicious script injection.',
            impact: 'Attackers can execute malicious scripts in the user\'s browser, steal session information, or perform other malicious actions.',
            evidence: 'XSS was directly inserted into the page without being escaped.',
            remediation: 'Properly escape and filter all user input, and use Content-Security-Policy headers to prevent untrusted script execution.'
          },
          {
            type: 'SQL Injection Vulnerability',
            severity: 'critical',
            location: '/user?id=',
            description: 'The user query page has a SQL injection vulnerability, which may lead to unauthorized database access.',
            impact: 'Attackers can execute arbitrary SQL queries, obtain sensitive data, modify database content, or even gain server privileges in some cases.',
            evidence: 'id=1 OR 1=1 returned all user records, indicating the SQL query was not parameterized.',
            remediation: 'Use parameterized queries or prepared statements, restrict database user permissions, and implement input validation and filtering.'
          },
          {
            type: 'Sensitive Information Disclosure',
            severity: 'medium',
            location: '/js/main.js',
            description: 'API keys and other sensitive configuration information were found in the frontend JavaScript code.',
            impact: 'Attackers can use leaked API keys or configuration information to access restricted resources or services.',
            evidence: 'const API_KEY = "sk_test_abcdef123456";\nconst DB_CONFIG = { host: "db.example.com", user: "admin" };',
            remediation: 'Avoid storing sensitive information in frontend code. Use environment variables and backend APIs to manage keys and configuration. Consider using code obfuscation and minification tools.'
          }
        ]

        // end of vulnerability details
// Generate PDF report
async function generatePdfReport() {
  if (!selectedReport.value) return
  
  try {
    ElMessage.info('Preparing to print a PDF report, please wait...')
    
    // Use browser native printing function
    const printWindow = window.open('', '_blank')
    
    if (!printWindow) {
      throw new Error('Please allow the browser to open pop-up windows to generate PDF')
    }
    
    // Build report HTML
   const reportHtml = `
  <div class="pdf-template">
    <div class="report-branding" style="display: flex; align-items: center; gap: 10px; margin-bottom: 20px;">
     <img src="${logo}" alt="CySmart.ai Logo" style="height: 50px;" />
      <h1 style="margin: 0; font-size: 24px;">CySmart.ai Web Security Scan Report</h1>
    </div>

    <div class="report-header">
      <div class="report-meta">
        <p><strong>Report ID:</strong> ${selectedReport.value.id}</p>
        <p><strong>Target URL:</strong> ${selectedReport.value.url}</p>
        <p><strong>Scan time:</strong> ${formatDate(selectedReport.value.scanDate)}</p>
        <p><strong>Scan status:</strong> ${selectedReport.value.status}</p>
        <p><strong>Scan Depth:</strong> ${selectedReport.value.depth}</p>
        <p><strong>Scan duration:</strong> ${selectedReport.value.duration}</p>
      </div>
    </div>

    <div class="vulnerability-summary">
      <h2>Vulnerability statistics</h2>
      <p>Total number of vulnerabilities found: ${selectedReport.value.vulnerabilities || 0}</p>
    </div>

    ${
      selectedReport.value.vulnerabilityDetails && selectedReport.value.vulnerabilityDetails.length > 0
        ? `<div class="vulnerability-details">
            <h2>Vulnerability details</h2>
            ${selectedReport.value.vulnerabilityDetails.map((vuln, index) => {
              const ref = vulnerabilityDetailsArray.find(v =>
                v.type.toLowerCase().includes(vuln.type.toLowerCase()) ||
                vuln.type.toLowerCase().includes(v.type.toLowerCase())
              );
              return `
                <div class="vulnerability-item">
                  <h3>${index + 1}. ${vuln.type} (${vuln.severity})</h3>
                  <p><strong>describe:</strong> ${vuln.description}</p>
                  <p><strong>Location:</strong> ${ref?.location || vuln.location || '--'}</p>
                  <p><strong>evidence:</strong> ${ref?.evidence || vuln.evidence || '--'}</p>
                  <p><strong>Repair suggestions:</strong> ${vuln.remediation || ref?.remediation || '--'}</p>
                </div>
              `;
            }).join('')}
          </div>`
        : `<div class="no-vulnerabilities">
             <p>No security vulnerabilities were found, please continue to maintain good security practices.</p>
           </div>`
    }
  </div>
`;

                  /*
                  <p><strong>evidence:</strong> ${vuln.evidence}</p>
                  <p><strong>Influence:</strong> ${vuln.impact}</p>
                  <p><strong>Repair suggestions:</strong> ${vuln.remediation}</p>
                  
    */
    // Set the contents of the print window
    printWindow.document.write(`
      <!DOCTYPE html>
      <html>
      <head>
        <title>Security scan report - ${selectedReport.value.id}</title>
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
          .no-vulnerabilities {
            padding: 20px;
            background-color: #f0f9eb;
            border-radius: 5px;
            color: #67c23a;
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
          <button onclick="window.close()" style="padding: 8px 16px; background-color: #F56C6C; color: white; border: none; border-radius: 4px; cursor: pointer;">Close the window</button>
        </div>
        ${reportHtml}
      </body>
      </html>
    `)


    
    printWindow.document.close()
    
    // Automatically trigger printing
    setTimeout(() => {
      try {
        printWindow.focus() // Make sure the window gets focus
        printWindow.print() // Open the print dialog box directly
      } catch (e) {
        console.error('Automatic printing failed:', e)
      }
    }, 1000)
    
    ElMessage.success('The PDF print in Save as Options is open, please select"Save as PDF" option')
  } catch (error) {
    console.error('An error occurred while generating PDF:', error)
    ElMessage.error('Failed to generate PDF: ' + error.message)
  }
}

// Skip to vulnerability repair guide
function viewRemediationGuide(vulnType) {
  ElMessage({
    type: 'info',
    message: `Openinging${vulnType}Repair Guide...`
  })
}
</script>

<style scoped>
.reports-view {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.vuln-detail {
  font-size: 14px;
  line-height: 1.6;
}
</style>

