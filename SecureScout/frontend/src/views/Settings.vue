<template>
  <div class="settings-container p-6">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold">Security Settings</h1>
      <div>
        <el-button @click="goBack">
          <el-icon class="mr-1"><ArrowLeft /></el-icon>
          Back
        </el-button>
      </div>
    </div>

    <div class="bg-white rounded-lg shadow-md p-6 mb-6">
      <h2 class="text-xl font-semibold mb-4">Scan Configuration</h2>
      
      <el-form 
        :model="scanConfig" 
        label-position="top" 
        class="max-w-3xl"
      >
        <el-form-item label="Scan Timeout (seconds)">
          <el-slider 
            v-model="scanConfig.timeout" 
            :min="10" 
            :max="300" 
            :step="10"
            show-input
          />
        </el-form-item>
        
        <el-form-item label="Max Concurrent Scan Tasks">
          <el-radio-group v-model="scanConfig.concurrent_scans">
            <el-radio-button :label="1">1</el-radio-button>
            <el-radio-button :label="3">3</el-radio-button>
            <el-radio-button :label="5">5</el-radio-button>
            <el-radio-button :label="10">10</el-radio-button>
          </el-radio-group>
          <div class="text-sm text-gray-500 mt-1">
            Maximum number of scan tasks allowed at the same time. Higher settings may affect system performance.
          </div>
        </el-form-item>
        
        <el-form-item label="Browser User Agent">
          <el-input v-model="scanConfig.user_agent" />
          <div class="text-sm text-gray-500 mt-1">
            User agent string used during scanning.
          </div>
        </el-form-item>
        
        <el-divider />
        
        <h3 class="font-semibold mb-4">Default Enabled Scan Modules</h3>
        <div class="flex flex-wrap gap-3">
          <el-checkbox 
            v-for="(def, key) in scanConfig.vulnerability_definitions" 
            :key="key"
            v-model="scanConfig.default_modules"
            :label="key"
          >
            {{ moduleLabels[key] || key }}
            <el-tag size="small" class="ml-1" :type="getSeverityType(def.severity)">
              {{ def.severity }}
            </el-tag>
          </el-checkbox>
        </div>
        
        <el-divider />
        
        <div class="flex justify-between mt-4">
          <el-button @click="resetConfig">
            Restore Defaults
          </el-button>
          <el-button type="primary" @click="saveConfig">
            Save Settings
          </el-button>
        </div>
      </el-form>
    </div>
    
    <div class="bg-white rounded-lg shadow-md p-6 mb-6">
      <h2 class="text-xl font-semibold mb-4">Notification Settings</h2>
      
      <el-form label-position="top" class="max-w-3xl">
        <el-form-item label="Email Notifications">
          <el-switch v-model="notificationSettings.email.enabled" />
          <div class="text-sm text-gray-500 mt-1">
            When enabled, a report will be automatically sent to the specified email upon scan completion.
          </div>
        </el-form-item>
        
        <el-form-item label="Notification Email Address" v-if="notificationSettings.email.enabled">
          <el-input v-model="notificationSettings.email.address" placeholder="Enter the email address to receive notifications" />
        </el-form-item>
        
        <el-form-item label="Notification Conditions">
          <el-checkbox v-model="notificationSettings.onComplete">On scan completion</el-checkbox>
          <el-checkbox v-model="notificationSettings.onVulnerabilityFound">When a vulnerability is found</el-checkbox>
          <el-checkbox v-model="notificationSettings.onHighRisk">When a high-risk vulnerability is found</el-checkbox>
        </el-form-item>
        
        <div class="flex justify-end mt-4">
          <el-button type="primary" @click="saveNotificationSettings">
            Save Notification Settings
          </el-button>
        </div>
      </el-form>
    </div>
    
    <div class="bg-white rounded-lg shadow-md p-6">
      <h2 class="text-xl font-semibold mb-4">Account Security</h2>
      
      <el-form label-position="top" class="max-w-3xl">
        <el-form-item label="API Key">
          <div class="flex items-center">
            <el-input 
              v-model="apiKey" 
              placeholder="No API key" 
              :type="showApiKey ? 'text' : 'password'"
              class="mr-2"
              readonly
            />
            <el-button @click="showApiKey = !showApiKey">
              {{ showApiKey ? 'hide' : 'show' }}
            </el-button>
            <el-button type="primary" @click="regenerateApiKey">
              Regenerate
            </el-button>
          </div>
          <div class="text-sm text-gray-500 mt-1">
            Used for API access. Please keep it safe.
          </div>
        </el-form-item>
        
        <el-form-item label="Two-Factor Authentication">
          <el-switch v-model="securitySettings.twoFactor" />
          <div class="text-sm text-gray-500 mt-1">
            Enhance account security. Additional verification required at login.
          </div>
        </el-form-item>
        
        <div class="flex justify-end mt-4">
          <el-button type="primary" @click="saveSecuritySettings">
            Save Account Security Settings
          </el-button>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import { useScanStore } from '@/store/scanStore'

const router = useRouter()
const scanStore = useScanStore()

// Scan configuration
const scanConfig = ref({
  timeout: 60,
  concurrent_scans: 3,
  user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
  default_modules: ['sql_injection', 'xss', 'csrf'],
  vulnerability_definitions: {
    'sql_injection': {
      severity: 'high',
      description: 'SQL injection vulnerability allows attackers to inject malicious SQL queries into the application, which may lead to data leakage or corruption.'
    },
    'xss': {
      severity: 'middle',
      description: 'Cross-site scripting attacks allow attackers to inject and execute malicious scripts in the victim\'s browser.'
    },
    'csrf': {
      severity: 'middle',
      description: 'Cross-site request forgery vulnerability allows attackers to trick users into performing unintended actions.'
    },
    'file_upload': {
      severity: 'high',
      description: 'Unsafe file upload allows attackers to upload malicious files, which may lead to remote code execution.'
    }
  }
})

// Module label mapping
const moduleLabels = {
  'sql_injection': 'SQL injection detection',
  'xss': 'Cross-site scripting (XSS) detection',
  'csrf': 'Cross-site request forgery detection',
  'file_upload': 'File upload vulnerability detection'
}

// Notification settings
const notificationSettings = reactive({
  email: {
    enabled: false,
    address: ''
  },
  onComplete: true,
  onVulnerabilityFound: true,
  onHighRisk: true
})

// Security settings
const securitySettings = reactive({
  twoFactor: false
})

// API key
const apiKey = ref('sk_test_abcdefghijklmnopqrstuvwxyz123456')
const showApiKey = ref(false)

// Get severity type
function getSeverityType(severity) {
  if (severity === 'serious' || severity === 'high') return 'danger'
  if (severity === 'middle') return 'warning'
  if (severity === 'Low') return 'info'
  return 'info'
}

// Load settings
async function loadScanConfig() {
  try {
    const config = await scanStore.loadConfig()
    if (config) {
      scanConfig.value = { ...config }
    }
  } catch (error) {
    console.error('Failed to load configuration:', error)
    ElMessage.error('Failed to load configuration')
  }
}

// Save scan configuration
async function saveConfig() {
  try {
    await scanStore.saveConfig(scanConfig.value)
    ElMessage.success('Configuration saved')
  } catch (error) {
    console.error('Failed to save configuration:', error)
    ElMessage.error('Failed to save configuration')
  }
}

// Reset configuration
function resetConfig() {
  scanConfig.value = {
    timeout: 60,
    concurrent_scans: 3,
    user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    default_modules: ['sql_injection', 'xss', 'csrf'],
    vulnerability_definitions: {
      'sql_injection': {
        severity: 'high',
        description: 'SQL injection vulnerability allows attackers to inject malicious SQL queries into the application, which may lead to data leakage or corruption.'
      },
      'xss': {
        severity: 'middle',
        description: 'Cross-site scripting attacks allow attackers to inject and execute malicious scripts in the victim\'s browser.'
      },
      'csrf': {
        severity: 'middle',
        description: 'Cross-site request forgery vulnerability allows attackers to trick users into performing unintended actions.'
      },
      'file_upload': {
        severity: 'high',
        description: 'Unsafe file upload allows attackers to upload malicious files, which may lead to remote code execution.'
      }
    }
  }
  ElMessage.info('Restored default settings')
}

// Save notification settings
function saveNotificationSettings() {
  ElMessage.success('Notification settings saved')
}

// Save security settings
function saveSecuritySettings() {
  ElMessage.success('Account security settings saved')
}

// Regenerate API key
function regenerateApiKey() {
  // Generate random API key
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
  let newKey = 'sk_test_'
  for (let i = 0; i < 32; i++) {
    newKey += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  apiKey.value = newKey
  ElMessage.success('API key regenerated')
}

// Go back to previous page
function goBack() {
  router.push('/')
}

// Load current config on component mount
onMounted(() => {
  loadScanConfig()
})
</script>

<style scoped>
.settings-container {
  min-height: calc(100vh - 64px);
  background-color: #f5f7fa;
}
</style>