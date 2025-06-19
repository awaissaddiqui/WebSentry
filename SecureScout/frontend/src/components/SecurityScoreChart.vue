<template>
  <div class="w-full h-full">
    <Doughnut
      v-if="loaded && !isEmpty"
      :data="chartData"
      :options="chartOptions"
    />
    <div v-else-if="isEmpty" class="flex items-center justify-center h-full">
      <p class="text-gray-500">No data available</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { Doughnut } from 'vue-chartjs'
import { Chart as ChartJS, ArcElement, Tooltip, Legend, Title } from 'chart.js'

// Register ChartJS component
ChartJS.register(ArcElement, Tooltip, Legend, Title)

const props = defineProps({
  severityCounts: {
    type: Object,
    required: true,
    default: () => ({})
  }
})

const loaded = ref(false)
const isEmpty = computed(() => {
  const counts = Object.values(props.severityCounts)
  return counts.length === 0 || counts.every(count => count === 0)
})

// Calculate security score
const securityScore = computed(() => {
  if (isEmpty.value) return 100
  
  const { 'low': low = 0, 'middle': medium = 0, 'high': high = 0, 'serious': critical = 0 } = props.severityCounts
  const totalVulnerabilities = low + medium + high + critical
  
  if (totalVulnerabilities === 0) return 100
  
  // Calculate the weight score based on the severity of the vulnerability.
  const weightedScore = (
    low * 0.1 + 
    medium * 0.3 + 
    high * 0.6 + 
    critical * 1.0
  ) / totalVulnerabilities
  
  // Convert weight scores to 0-100 ratings (higher the safer)
  return Math.max(0, Math.round(100 - (weightedScore * 100)))
})

// Set up chart data
const chartData = computed(() => {
  const score = securityScore.value
  
  return {
    labels: ['Security Score', 'Risk'],
    datasets: [
      {
        data: [score, 100 - score],
        backgroundColor: getScoreColors(score),
        borderWidth: 0,
        borderRadius: 5,
        cutout: '70%'
      }
    ]
  }
})

// Get colors based on score
function getScoreColors(score) {
  let color
  
  if (score >= 90) {
    color = '#52c41a' // Green - Safe
  } else if (score >= 70) {
    color = '#1890ff' // Blue - Good
  } else if (score >= 50) {
    color = '#faad14' // Yellow - Caution
  } else {
    color = '#f5222d' // Red - Danger
  }
  
  return [color, '#f0f0f0']
}

// Chart options
const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      enabled: false
    }
  }
}

// Set loaded state after component is mounted
onMounted(() => {
  loaded.value = true
})

// Recalculate security score when severity counts change
watch(() => props.severityCounts, () => {
  loaded.value = true
}, { deep: true })
</script>