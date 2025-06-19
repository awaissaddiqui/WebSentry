<template>
  <div class="dashboard-view p-6 min-h-screen bg-gray-50">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold">Dashboard</h1>
      <el-button type="primary" plain @click="refreshData" :loading="isRefreshing" size="small">
        <el-icon class="mr-1"><Refresh /></el-icon>
        Refresh data
      </el-button>
    </div>
    
    <!-- Overview card -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
      <div class="bg-white rounded-lg shadow-md p-4 flex items-center" v-loading="isLoading">
        <div class="rounded-full bg-blue-100 p-3 mr-4 text-blue-600">
          <el-icon :size="24"><Monitor /></el-icon>
        </div>
        <div class="min-w-0">
          <div class="text-sm text-gray-500">Total scans</div>
          <div class="text-2xl font-bold truncate">{{ stats.totalScans }}</div>
        </div>
      </div>
      
      <div class="bg-white rounded-lg shadow-md p-4 flex items-center" v-loading="isLoading">
        <div class="rounded-full bg-green-100 p-3 mr-4 text-green-600">
          <el-icon :size="24"><Connection /></el-icon>
        </div>
        <div class="min-w-0">
          <div class="text-sm text-gray-500">Active scans</div>
          <div class="text-2xl font-bold truncate">{{ activeScansCount }}</div>
          <div class="text-xs text-gray-400 truncate" v-if="activeScansCount > 0">{{ getActiveTimeRemaining() }}</div>
        </div>
      </div>
      
      <div class="bg-white rounded-lg shadow-md p-4 flex items-center" v-loading="isLoading">
        <div class="rounded-full bg-red-100 p-3 mr-4 text-red-600">
          <el-icon :size="24"><Warning /></el-icon>
        </div>
        <div class="min-w-0">
          <div class="text-sm text-gray-500">Vulnerabilities </div>
          <div class="text-2xl font-bold truncate">{{ stats.vulnerabilities }}</div>
          <div class="text-xs text-gray-400 truncate" v-if="stats.highRiskVulnerabilities > 0">
            {{ stats.highRiskVulnerabilities }} high risk
          </div>
        </div>
      </div>
      
      <div class="bg-white rounded-lg shadow-md p-4 flex items-center" v-loading="isLoading">
        <div class="rounded-full bg-yellow-100 p-3 mr-4 text-yellow-600">
          <el-icon :size="24"><Finished /></el-icon>
        </div>
        <div class="min-w-0">
          <div class="text-sm text-gray-500">Fixed</div>
          <div class="text-2xl font-bold truncate">{{ stats.fixed }}</div>
        </div>
      </div>
    </div>
    
    <!-- Security Score & Vulnerability Analysis -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
      <div class="bg-white rounded-lg shadow-md p-6 lg:col-span-1" v-loading="isLoading">
        <h2 class="text-lg font-semibold mb-4">Security Score</h2>
        <div class="flex flex-col items-center justify-center">
          <div class="relative mb-3">
            <el-progress 
              type="dashboard" 
              :percentage="securityScore" 
              :color="getScoreColor()" 
              :width="180"
              :stroke-width="15"
              :format="() => ''"
            />
            <div class="absolute inset-0 flex items-center justify-center">
              <div class="text-center">
                <span class="text-3xl font-bold">{{ securityScore }}</span>
              </div>
            </div>
          </div>
          <div class="text-center">
            <p class="text-sm text-gray-600">{{ getScoreMessage() }}</p>
          </div>
          
          <div class="mt-4 w-full">
            <div class="flex justify-between items-center mb-1">
              <span class="text-xs font-medium text-gray-500">Trend in the past 30 days</span>
            </div>
            <div class="h-10 w-full">
              <div class="flex items-end h-full space-x-1">
                <div 
                  v-for="(score, index) in scoreHistory" 
                  :key="index"
                  class="bg-blue-500 rounded-sm w-2"
                  :style="{ height: `${score}%`, opacity: 0.3 + (index / scoreHistory.length) * 0.7 }"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="bg-white rounded-lg shadow-md p-6 lg:col-span-2" v-loading="isLoading">
        <h2 class="text-lg font-semibold mb-4">Security Status</h2>
        <div 
          v-if="stats.vulnerabilities > 0" 
          class="border-l-4 border-red-500 bg-red-50 p-4 text-red-700 mb-4"
        >
          <div class="flex">
            <div class="flex-shrink-0">
              <el-icon :size="24"><Warning /></el-icon>
            </div>
            <div class="ml-3">
              <p class="text-sm">
                Your system has <strong>{{ stats.highRiskVulnerabilities }}</strong> high-risk vulnerabilities that need urgent attention!
              </p>
            </div>
          </div>
        </div>
        
        <!-- Vulnerability Type Distribution -->
        <div v-if="stats.vulnerabilities > 0" class="mb-4">
          <h3 class="text-sm font-medium text-gray-700 mb-2">Vulnerability Type Distribution</h3>
          <div class="flex flex-wrap items-center gap-3 mb-2">
            <div v-for="(item, index) in vulnerabilityTypes" :key="index" 
              class="flex items-center">
              <div class="w-3 h-3 rounded-sm mr-1" :style="{ backgroundColor: typeColors[index % typeColors.length] }"></div>
              <span class="text-xs text-gray-600">{{ item.name }}</span>
            </div>
          </div>
          <div class="h-40 w-full">
            <canvas ref="vulnerabilityChart"></canvas>
          </div>
          
          <!-- Vulnerability Type Details -->
          <div class="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
            <div v-if="hasVulnType('sql_injection')" class="border border-gray-200 rounded-md p-3">
              <div class="flex justify-between items-center mb-2">
                <h4 class="font-medium text-gray-800">SQL Injection</h4>
                <el-tag type="danger" size="small">{{ getVulnTypeCount('sql_injection') }}</el-tag>
              </div>
              <p class="text-xs text-gray-600 mb-2">SQL injection allows attackers to inject malicious SQL queries into the application, potentially leading to data leakage or corruption.</p>
              <router-link 
                v-if="getVulnTypeCount('sql_injection') > 0" 
                to="/reports?filter=sql_injection" 
                class="text-xs text-blue-500 hover:underline"
              >
                View details
              </router-link>
            </div>
            
            <div v-if="hasVulnType('xss')" class="border border-gray-200 rounded-md p-3">
              <div class="flex justify-between items-center mb-2">
                <h4 class="font-medium text-gray-800">XSS Cross-site Scripting</h4>
                <el-tag type="warning" size="small">{{ getVulnTypeCount('xss') }}</el-tag>
              </div>
              <p class="text-xs text-gray-600 mb-2">XSS allows attackers to inject malicious JavaScript code into web pages, which may execute in the user's browser and lead to session hijacking, etc.</p>
              <router-link 
                v-if="getVulnTypeCount('xss') > 0" 
                to="/reports?filter=xss" 
                class="text-xs text-blue-500 hover:underline"
              >
                View details
              </router-link>
            </div>
            
            <div v-if="hasVulnType('csrf') || hasVulnType('file_upload')" class="border border-gray-200 rounded-md p-3">
              <div class="flex justify-between items-center mb-2">
                <h4 class="font-medium text-gray-800">Other Vulnerabilities</h4>
                <el-tag type="info" size="small">{{ getVulnTypeCount('csrf') + getVulnTypeCount('file_upload') }}</el-tag>
              </div>
              <p class="text-xs text-gray-600 mb-2">Includes CSRF (Cross-site Request Forgery), insecure file upload, and other types.</p>
              <router-link 
                v-if="getVulnTypeCount('csrf') + getVulnTypeCount('file_upload') > 0" 
                to="/reports?filter=other" 
                class="text-xs text-blue-500 hover:underline"
              >
                View details
              </router-link>
            </div>
            
            <div class="border border-gray-200 rounded-md p-3 bg-gray-50">
              <div class="flex justify-between items-center mb-2">
                <h4 class="font-medium text-gray-800">Vulnerability Trend Analysis</h4>
                <el-tag type="success" size="small" v-if="vulnerabilityTrend < 0">Decreasing</el-tag>
                <el-tag type="danger" size="small" v-else-if="vulnerabilityTrend > 0">Increasing</el-tag>
                <el-tag type="info" size="small" v-else>Stable</el-tag>
              </div>
              <div class="flex items-end h-16 space-x-1 mb-1">
                <div 
                  v-for="(count, index) in vulnerabilityHistory" 
                  :key="index"
                  class="bg-blue-500 rounded-sm flex-1"
                  :style="{ 
                    height: `${count > 0 ? (count / Math.max(...vulnerabilityHistory) * 100) : 0}%`, 
                    opacity: 0.3 + (index / vulnerabilityHistory.length) * 0.7 
                  }"
                ></div>
              </div>
              <div class="text-xs text-gray-500 text-center">Vulnerability trend in the past 7 days</div>
            </div>
          </div>
        </div>
        <div v-else class="flex flex-col items-center justify-center py-8 bg-gray-50 rounded-lg">
          <el-icon :size="36" class="text-gray-400 mb-2"><CircleCheckFilled /></el-icon>
          <p class="text-gray-500">No vulnerabilities found, website security is good</p>
        </div>
        
        <el-collapse>
          <el-collapse-item title="Website Security Recommendations" name="1">
            <ul class="list-disc pl-5 space-y-2 text-gray-600">
              <li>Perform security scans regularly, at least once a week</li>
              <li>Update all software and dependencies to the latest version promptly</li>
              <li>Implement Content Security Policy (CSP) to prevent XSS attacks</li>
              <li>Use HTTPS and configure appropriate security response headers</li>
              <li>Add CSRF token protection to all forms</li>
              <li>Enable multi-factor authentication to enhance account security</li>
              <li>Strictly validate and filter all user input</li>
            </ul>
          </el-collapse-item>
        </el-collapse>
      </div>
    </div>
    
    <!-- Recent Scans & Quick Actions -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="bg-white rounded-lg shadow-md p-6 lg:col-span-2" v-loading="isLoading">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-lg font-semibold">Recent Scans</h2>
          <div class="flex items-center space-x-2">
            <el-select v-model="scanFilter" placeholder="Filter" size="small" style="width: 120px">
              <el-option label="All" value="all" />
              <el-option label="Vulnerable" value="vulnerable" />
              <el-option label="Secure" value="secure" />
            </el-select>
            <router-link to="/scan" class="text-blue-500 text-sm hover:underline">
              View all
            </router-link>
          </div>
        </div>
        
        <el-table 
          :data="filteredRecentScans" 
          style="width: 100%"
          :show-header="true"
          size="small"
          empty-text="No scan records"
          row-class-name="cursor-pointer hover:bg-gray-50"
          @row-click="handleScanClick"
        >
          <el-table-column prop="id" label="ID" width="120" />
          <el-table-column prop="url" label="Target URL" min-width="200">
            <template #default="{ row }">
              <el-link :href="row.url" target="_blank" type="primary" :underline="false" @click.stop>
                {{ row.url }}
              </el-link>
            </template>
          </el-table-column>
          <el-table-column label="Time" width="150">
            <template #default="{ row }">
              {{ formatDate(row.date || row.start_time) }}
            </template>
          </el-table-column>
          <el-table-column label="Status" width="120">
            <template #default="{ row }">
              <el-tag 
                :type="row.status === 'completed' ? 'success' : 
                       row.status === 'in_progress' || row.status === 'running' ? 'primary' : 
                       row.status === 'failed' ? 'danger' : 'info'"
                size="small"
              >
                {{ getStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="Vulnerabilities" width="80" align="center">
            <template #default="{ row }">
              <el-tag 
                v-if="row.status === 'completed'"
                :type="getVulnerabilityCount(row) > 0 ? 'danger' : 'success'"
                size="small"
              >
                {{ getVulnerabilityCount(row) }}
              </el-tag>
              <span v-else>-</span>
            </template>
          </el-table-column>
        </el-table>
        
        <div v-if="filteredRecentScans.length === 0 && !isLoading" class="flex flex-col items-center justify-center py-8">
          <el-empty description="No scan records" :image-size="100">
            <template #description>
              <p class="text-gray-500">{{ getEmptyTableText() }}</p>
            </template>
            <router-link to="/scan">
              <el-button type="primary">New Scan</el-button>
            </router-link>
          </el-empty>
        </div>
      </div>
      
      <div class="bg-white rounded-lg shadow-md p-6 lg:col-span-1">
        <h2 class="text-lg font-semibold mb-4">Quick Actions</h2>
        
        <div class="space-y-4">
          <div>
            <router-link to="/scan">
              <el-button type="primary" class="w-full flex justify-center items-center">
                <el-icon class="mr-2"><Plus /></el-icon>
                New Scan
              </el-button>
            </router-link>
          </div>
          
          <div>
            <router-link to="/reports">
              <el-button class="w-full flex justify-center items-center">
                <el-icon class="mr-2"><Document /></el-icon>
                View Reports
              </el-button>
            </router-link>
          </div>
          
          <div>
            <router-link to="/settings">
              <el-button class="w-full flex justify-center items-center">
                <el-icon class="mr-2"><Setting /></el-icon>
                Security Settings
              </el-button>
            </router-link>
          </div>
          
          <el-divider />
          
          <div class="bg-blue-50 p-4 rounded-lg">
            <h3 class="font-medium text-blue-700 mb-2">Security Tip</h3>
            <p class="text-sm text-blue-600">
              {{ dailyTip }}
            </p>
            <div class="mt-2 text-right">
              <el-button text size="small" @click="refreshTip">
                <el-icon class="mr-1"><Refresh /></el-icon>
                Change
              </el-button>
            </div>
          </div>
          
          <!-- Scan Calendar -->
          <div class="mt-4">
            <h3 class="font-medium text-gray-700 mb-2">Scan Calendar</h3>
            <div class="flex flex-wrap gap-1">
              <div 
                v-for="(day, i) in scanCalendar" 
                :key="i"
                class="w-4 h-4 rounded-sm"
                :class="day.count === 0 ? 'bg-gray-100' : 
                       day.count === 1 ? 'bg-green-200' : 
                       day.count <= 3 ? 'bg-green-400' : 'bg-green-600'"
                :title="`${day.date}: ${day.count} scans`"
              ></div>
            </div>
            <div class="flex justify-between mt-1 text-xs text-gray-500">
              <span>Past 30 days</span>
              <span>Today</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick, watch, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { 
  Monitor, 
  Connection, 
  Warning, 
  Finished, 
  Plus,
  Document,
  Setting,
  Refresh,
  CircleCheckFilled
} from '@element-plus/icons-vue'
import { useScanStore } from '../store/scanStore'
import { Chart, registerables } from 'chart.js'
import { ElMessage } from 'element-plus'

Chart.register(...registerables)

const router = useRouter()
const scanStore = useScanStore()
const vulnerabilityChart = ref(null)
let chart = null

// state
const isLoading = ref(true)
const isRefreshing = ref(false)
const scanFilter = ref('all')

// Statistics
const stats = reactive({
  totalScans: 0,
  activeScans: 0,
  vulnerabilities: 0,
  fixed: 0,
  highRiskVulnerabilities: 0
})

// Recent scans
const recentScans = ref([])

// Safety score history (simulated data)
const scoreHistory = ref(Array.from({ length: 30 }, () => Math.floor(Math.random() * 30) + 70))

// Vulnerability type statistics
const vulnerabilityTypes = ref([
  { name: 'SQL Injection', count: 0 },
  { name: 'XSS', count: 0 },
  { name: 'CSRF', count: 0 },
  { name: 'File Upload', count: 0 },
  { name: 'Other', count: 0 }
])

// chart color
const typeColors = [
  '#FF6384', 
  '#36A2EB', 
  '#FFCE56', 
  '#4BC0C0', 
  '#9966FF'
]

// Scan calendar data (analog)
const scanCalendar = ref(generateCalendarData())

// Vulnerability historical trends (simulated data)
const vulnerabilityHistory = ref([2, 5, 8, 6, 7, 5, 4])

// Vulnerability trend, positive number indicates increase, negative number indicates decrease, 0 indicates stability
const vulnerabilityTrend = computed(() => {
  if (vulnerabilityHistory.value.length < 2) return 0
  const lastValue = vulnerabilityHistory.value[vulnerabilityHistory.value.length - 1]
  const prevValue = vulnerabilityHistory.value[vulnerabilityHistory.value.length - 2]
  return lastValue - prevValue
})

// Computed properties
const activeScansCount = computed(() => {
  return scanStore.activeScansCount || 0
})

const securityScore = computed(() => {
  // Calculate security score based on number of vulnerabilities
  if (stats.vulnerabilities === 0) return 100
  
  // The base score is 100, and each vulnerability reduces the score. High-risk vulnerabilities have a greater impact.
  let score = 100 - (stats.vulnerabilities * 5) - (stats.highRiskVulnerabilities * 10)
  return Math.max(0, Math.min(100, Math.round(score)))
})

const filteredRecentScans = computed(() => {
  if (scanFilter.value === 'all') return recentScans.value
  
  if (scanFilter.value === 'vulnerable') {
    return recentScans.value.filter(scan => getVulnerabilityCount(scan) > 0)
  }
  
  if (scanFilter.value === 'secure') {
    return recentScans.value.filter(scan => 
      scan.status === 'completed' && getVulnerabilityCount(scan) === 0
    )
  }
  
  return recentScans.value
})

// Get empty table text
function getEmptyTableText() {
  if (scanFilter.value === 'vulnerable') {
    return 'No scan records with vulnerabilities found'
  } else if (scanFilter.value === 'secure') {
    return 'No scan records with good security status found'
  }
  return 'No scan records yet, click the button below to create a new scan'
}

// Safety tips
const securityTips = [
  'Update your website dependencies regularly to fix known security vulnerabilities',
  'Validate and sanitize all user input to prevent XSS and injection attacks',
  'Use HTTPS to ensure the security of all data transmissions',
  'Implement proper password policies and multi-factor authentication',
  'Regularly back up important data and test the recovery process',
  'Add CSRF token protection for sensitive operations',
  'Limit login attempts to prevent brute-force attacks',
  'Configure security response headers such as Content-Security-Policy and X-Frame-Options',
  'Use parameterized queries to prevent SQL injection attacks',
  'Implement the principle of least privilege and grant only necessary access permissions',
  'Regularly review access logs to detect suspicious activities',
  'Implement network segmentation to limit the impact of security incidents',
  'Use a Web Application Firewall (WAF) to defend against common attacks',
  'Regularly conduct penetration testing to discover potential vulnerabilities',
  'Ensure all API endpoints have proper authentication and authorization'
]

const dailyTip = ref('')

// Get the security score color
function getScoreColor() {
  console.log(securityScore.value)
  if (securityScore.value >= 90) return '#67C23A' // green
  if (securityScore.value >= 70) return '#E6A23C' // yellow
  return '#F56C6C' // red
}

// Get rating news
function getScoreMessage() {
  if (securityScore.value >= 90) return 'Your website is secure'
  if (securityScore.value >= 70) return 'Your website has serious security risks'
  return 'Your website has serious security risks'
}

// Format date
function formatDate(dateString) {
  if (!dateString) return '-'
  
  try {
    const date = new Date(dateString)
    return date.toLocaleString('en-US', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (e) {
    return dateString
  }
}

// Get status text
function getStatusText(status) {
  const statusMap = {
    'completed': 'Completed',
    'in_progress': 'in progress',
    'running': 'Running',
    'pending': 'Pending',
    'failed': 'Failed',
    'cancelled': 'Cancelled'
  }
  return statusMap[status] || status
}

// Get the number of vulnerabilities
function getVulnerabilityCount(scan) {
  if (typeof scan.vulnerabilities === 'number') {
    return scan.vulnerabilities
  }
  
  if (Array.isArray(scan.vulnerabilities)) {
    return scan.vulnerabilities.length
  }
  
  return 0
}

// Refresh security tips
function refreshTip() {
  const randomIndex = Math.floor(Math.random() * securityTips.length)
  dailyTip.value = securityTips[randomIndex]
}

// Get an estimate of the time remaining for an active scan
function getActiveTimeRemaining() {
  return 'Estimated time remaining: 5-10 minutes'
}

// Generate simulated calendar data
function generateCalendarData() {
  const days = 30
  const result = []
  
  for (let i = 0; i < days; i++) {
    const date = new Date()
    date.setDate(date.getDate() - (days - i - 1))
    
    result.push({
      date: `${date.getMonth() + 1}/${date.getDate()}`, 
      count: Math.floor(Math.random() * 5) // 0-4 scans
    })
  }
  
  return result
}

// Click on scan line
function handleScanClick(row) {
  if (row.status === 'completed') {
    router.push(`/report/${row.id}`)
  } else {
    router.push(`/scan?id=${row.id}`)
  }
}

// Initialize vulnerability type chart
function initVulnerabilityChart() {
  if (!vulnerabilityChart.value) return
  
  // Make sure the total is not 0 to avoid chart rendering issues
  const hasData = vulnerabilityTypes.value.some(type => type.count > 0)
  if (!hasData) {
    // If there is no data, add a dummy data to prevent chart rendering errors
    vulnerabilityTypes.value[4].count = 1
  }
  
  if (chart) {
    chart.destroy()
  }
  
  try {
    const ctx = vulnerabilityChart.value.getContext('2d')
    chart = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: vulnerabilityTypes.value.map(type => type.name),
        datasets: [{
          data: vulnerabilityTypes.value.map(type => type.count),
          backgroundColor: typeColors,
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                const label = context.label || ''
                const value = context.raw || 0
                const total = context.dataset.data.reduce((a, b) => a + b, 0)
                if (total === 0) return `${label}: 0 (0%)`
                const percentage = Math.round((value / total) * 100)
                return `${label}: ${value} (${percentage}%)`
              }
            }
          }
        },
        cutout: '65%'
      }
    })
  } catch (error) {
    console.error('Failed to initialize chart:', error)
  }
}

// Analyze the distribution of vulnerability types
function analyzeVulnerabilityTypes() {
  // Reset statistics
  vulnerabilityTypes.value.forEach(type => type.count = 0)

  // Collect all vulnerabilities
  let allVulnerabilities = []

  recentScans.value.forEach(scan => {
    if (Array.isArray(scan.vulnerabilities)) {
      allVulnerabilities = allVulnerabilities.concat(scan.vulnerabilities)
    }
  })

  // Count the number of each type
  allVulnerabilities.forEach(vuln => {
    if (vuln.type === 'sql_injection') {
      vulnerabilityTypes.value[0].count++
    } else if (vuln.type === 'xss') {
      vulnerabilityTypes.value[1].count++
    } else if (vuln.type === 'csrf') {
      vulnerabilityTypes.value[2].count++
    } else if (vuln.type === 'file_upload') {
      vulnerabilityTypes.value[3].count++
    } else {
      vulnerabilityTypes.value[4].count++
    }
  })
  
  // update the chart
  nextTick(() => {
    initVulnerabilityChart()
  })
}

// Load Data
async function loadDashboardData() {
  try {
    isLoading.value = true
    
    // Get data from Store
    let allScans = []
    let allResults = []
    
    try {
      allScans = await scanStore.getAllScans() || []
    } catch (e) {
      console.error('Failed to obtain scan list:', e)
      allScans = []
    }
    
    try {
      allResults = await scanStore.getAllResults() || []
    } catch (e) {
      console.error('Failed to obtain the result list:', e)
      allResults = []
    }
    
    // Get recent scan results (combine ongoing and completed)
    const activeScans = allScans.filter(scan => 
      ['pending', 'running', 'in_progress'].includes(scan.status)
    )
    
    const completedScans = [...allResults]
    
     // Merge and sort by time, newest first
    recentScans.value = [...activeScans, ...completedScans]
      .filter(scan => scan && (scan.start_time || scan.date)) // Ensure scan object is valid
      .sort((a, b) => {
        const dateA = new Date(a.start_time || a.date)
        const dateB = new Date(b.start_time || b.date)
        return dateB - dateA
      })
      .slice(0, 10) // / Ensure scan object is valid
    
    // Calculate stats
    stats.totalScans = allScans.length + allResults.length
    stats.activeScans = activeScansCount.value
    
    // Count Vulnerabilities
    let totalVulnerabilities = 0
    let highRiskCount = 0
    
    allScans.forEach(scan => {
      if (Array.isArray(scan.vulnerabilities)) {
        totalVulnerabilities += scan.vulnerabilities.length
        scan.vulnerabilities.forEach(vuln => {
          if (vuln.severity === 'high') {
            highRiskCount++
          }
        })
      }
    })
    
    allResults.forEach(result => {
      if (Array.isArray(result.vulnerabilities)) {
        totalVulnerabilities += result.vulnerabilities.length
        result.vulnerabilities.forEach(vuln => {
          if (vuln.severity === 'high') {
            highRiskCount++
          }
        })
      } else if (typeof result.vulnerabilities === 'number') {
        totalVulnerabilities += result.vulnerabilities
        // Assume high-risk vulnerabilities account for 30%
        highRiskCount += Math.ceil(result.vulnerabilities * 0.3)
      }
    })
    
    stats.vulnerabilities = totalVulnerabilities
    stats.highRiskVulnerabilities = highRiskCount
    stats.fixed = Math.floor(totalVulnerabilities * 0.65)// Simulated fixed data

    // Analyze vulnerability type distribution
    analyzeVulnerabilityTypes()
    
   // Show a random security tip
    refreshTip()
  } catch (error) {
    console.error('Failed to load dashboard data:', error)
    ElMessage.error('Failed to load data, please refresh and try again')

    // Use default data if loading fails
    stats.totalScans = 0
    stats.activeScans = 0
    stats.vulnerabilities = 0
    stats.fixed = 0
    stats.highRiskVulnerabilities = 0
    recentScans.value = []
  } finally {
    isLoading.value = false
  }
}

// Refresh data
async function refreshData() {
  try {
    isRefreshing.value = true
    await loadDashboardData()
    ElMessage.success('Data has been refreshed successfully')
  } finally {
    isRefreshing.value = false
  }
}

// Watch for filter changes
watch(scanFilter, () => {
  // Optional: add filter animation effects here
})

// Lifecycle mount
onMounted(() => {
  loadDashboardData()

  // Check if routes are available
  try {
    const routes = router.getRoutes().map(route => route.path)
    console.log('Available routes:', routes)
  } catch (e) {
    console.error('Failed to obtain route:', e)
  }
  
   // Periodically refresh active scan status
  const timer = setInterval(() => {
    if (activeScansCount.value > 0) {
      loadDashboardData()
    }
  }, 15000) // Refresh every 15 seconds

  // Clear the timer when the component is unmounted
  onUnmounted(() => {
    clearInterval(timer)
    if (chart) {
      chart.destroy()
    }
  })
})

// Check if there are any vulnerabilities of a specific type
function hasVulnType(type) {
  const index = vulnerabilityTypes.value.findIndex(item => {
    return (type === 'sql_injection' && item.name === 'SQL injection') ||
           (type === 'xss' && item.name === 'XSS') ||
           (type === 'csrf' && item.name === 'CSRF') ||
           (type === 'file_upload' && item.name === 'File upload')
  })
  
  return index >= 0 && vulnerabilityTypes.value[index].count > 0
}

// Get the count of a specific type of vulnerability
function getVulnTypeCount(type) {
  const index = vulnerabilityTypes.value.findIndex(item => {
    return (type === 'sql_injection' && item.name === 'SQL injection') ||
           (type === 'xss' && item.name === 'XSS') ||
           (type === 'csrf' && item.name === 'CSRF') ||
           (type === 'file_upload' && item.name === 'File upload')
  })
  
  return index >= 0 ? vulnerabilityTypes.value[index].count : 0
}
</script>

<style scoped>
.dashboard-view {
  min-height: calc(100vh - 64px);
}

/* Card hover effect */
.bg-white {
  transition: transform 0.2s, box-shadow 0.2s;
}

.bg-white:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

/* Prevent long text from overflowing */
.truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>