<template>
  <span :class="statusClass">
    {{ statusLabel }}
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: {
    type: String,
    required: true,
    validator: (value) => ['pending', 'in_progress', 'completed', 'failed'].includes(value)
  }
})

// Status Tag Mapping
const statusLabels = {
  'pending': 'waiting',
  'in_progress': 'scanning',
  'completed': 'Completed',
  'failed': 'fail'
}

// State class name mapping
const statusClasses = {
  'pending': 'bg-blue-100 text-blue-800',
  'in_progress': 'bg-yellow-100 text-yellow-800',
  'completed': 'bg-green-100 text-green-800',
  'failed': 'bg-red-100 text-red-800'
}

// Get labels based on status
const statusLabel = computed(() => {
  return statusLabels[props.status] || props.status
})

// Get class name based on status
const statusClass = computed(() => {
  const baseClass = 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium'
  return `${baseClass} ${statusClasses[props.status] || 'bg-gray-100 text-gray-800'}`
})
</script> 