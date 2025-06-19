<template>
  <div class="scan-container p-6">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold">Start the scan</h1>
      <div>
        <el-button @click="goBack">
          <el-icon class="mr-1"><ArrowLeft /></el-icon>
          Scan History
        </el-button>
      </div>
    </div>
    
    <div class="bg-white rounded-lg shadow-md p-6 mb-6">
      <ScanComponent 
        :initial-url="initialUrl" 
        @scan-complete="handleScanComplete" 
        @scan-started="handleScanStarted"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import ScanComponent from '@/components/ScanComponent.vue'
import { useScanStore } from '@/store/scanStore'

const route = useRoute()
const router = useRouter()
const scanStore = useScanStore()

// Use the initial URL if passed from URL parameters
const initialUrl = computed(() => route.query.url || '')
const currentScanId = ref(null)

// Handle scan started event
function handleScanStarted(data) {
  currentScanId.value = data.scanId
  ElMessage({
    message: `Scan task ${data.scanId} started`,
    type: 'success'
  })
}

// Handle scan complete event
function handleScanComplete(result) {
  if (result.scanId) {
    ElMessage({
      message: 'Scan completed, redirecting to report page...',
      type: 'success'
    })
    
    // Delay redirect to scan center page
    setTimeout(() => {
      router.push('/scan-center')
    }, 1500)
  }
}

// Go back to previous page
function goBack() {
  if (currentScanId.value) {
    ElMessageBox.confirm(
      'The scan is still in progress and will continue running in the background if you go back. Are you sure you want to return?',
      'Confirm Return',
      {
        confirmButtonText: 'Confirm',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
    ).then(() => {
      router.push('/scan-center')
    }).catch(() => {})
  } else {
    router.push('/scan-center')
  }
}

// On component mount, check if URL parameters were passed from another page
onMounted(() => {
  // If navigated from another page, load scan config
  scanStore.loadConfig()
  
  // If there is a URL parameter, it means it was redirected from the "Rescan" button
  // Delay to ensure ScanComponent is fully loaded
  if (route.query.url) {
    ElMessage.info(`Preparing to scan: ${route.query.url}`)
  }
})
</script>

<style scoped>
.scan-container {
  min-height: calc(100vh - 64px);
  background-color: #f5f7fa;
}
</style>