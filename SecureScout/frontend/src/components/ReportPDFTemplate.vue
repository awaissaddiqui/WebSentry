<template>
  <div id="report-pdf-template" ref="pdfTemplate" class="pdf-template">
    <div class="report-header">
      <h1>Web Security Scan Report</h1>
      <div class="report-meta">
        <p><strong>Report ID:</strong> {{ report.id }}</p>
        <p><strong>Target URL:</strong> {{ report.url }}</p>
        <p><strong>Scan Time:</strong> {{ formatDate(report.start_time) }}</p>
        <p><strong>Status:</strong> {{ formatStatus(report.status) }}</p>
      </div>
    </div>

    <div class="vulnerability-summary">
      <h2>Vulnerability Summary</h2>
      <p>Total vulnerabilities found: {{ report.vulnerabilities?.length || 0 }}</p>
      
      <div v-if="vulnerabilitiesBySeverity && Object.keys(vulnerabilitiesBySeverity).length > 0">
        <h3>Vulnerability Severity Distribution:</h3>
        <ul>
          <li v-for="(count, severity) in vulnerabilitiesBySeverity" :key="severity">
            {{ severity }}: {{ count }}
          </li>
        </ul>
      </div>
    </div>

    <div v-if="report.vulnerabilities && report.vulnerabilities.length > 0" class="vulnerability-details">
      <h2>Vulnerability Details</h2>
      <div v-for="(vuln, index) in report.vulnerabilities" :key="index" class="vulnerability-item">
        <h3>{{ index + 1 }}. {{ getVulnTypeName(vuln.type) }} ({{ vuln.severity }})</h3>
        <p v-if="vuln.url"><strong>URL:</strong> {{ vuln.url }}</p>
        <p v-if="vuln.description"><strong>Description:</strong> {{ vuln.description }}</p>
      </div>
    </div>

    <div class="remediation-advice">
      <h2>Remediation Advice</h2>
      <div v-if="uniqueVulnTypes.length > 0">
        <div v-for="type in uniqueVulnTypes" :key="type" class="advice-item">
          <h3>{{ getVulnTypeName(type) }} Remediation Advice:</h3>
          <ul>
            <li v-for="(line, i) in getRemediationAdvice(type).split('\n')" :key="i">
              {{ line }}
            </li>
          </ul>
        </div>
      </div>
      <div v-else>
        <p>No security vulnerabilities found. Please continue to maintain good security practices.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  report: {
    type: Object,
    required: true
  }
})

// Vulnerability Type Name Mapping
const vulnTypeNames = {
  'sql_injection': 'SQL Injection',
  'xss': 'Cross-site scripting (XSS)',
  'csrf': 'Cross-site request forgery (CSRF)',
  'file_upload': 'File upload vulnerability',
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
  if (!props.report?.vulnerabilities) return null
  
  const result = {}
  
  props.report.vulnerabilities.forEach(vuln => {
    const severity = vuln.severity || 'Medium'
    if (result[severity]) {
      result[severity]++
    } else {
      result[severity] = 1
    }
  })
  
  return result
})

// Get vulnerability type name
function getVulnTypeName(type) {
  return vulnTypeNames[type] || type
}

// Get remediation advice
function getRemediationAdvice(type) {
  return remediationAdvice[type] || 'Please refer to security best practices for remediation.'
}

// Get unique vulnerability types
const uniqueVulnTypes = computed(() => {
  if (!props.report?.vulnerabilities) return []
  return [...new Set(props.report.vulnerabilities.map(v => v.type))]
})

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

// Format status
function formatStatus(status) {
  const statusMap = {
    'completed': 'Completed',
    'in_progress': 'In Progress',
    'pending': 'Pending',
    'failed': 'Failed'
  }
  return statusMap[status] || status
}
</script>

<style scoped>
.pdf-template {
  font-family: 'SimSun', 'Arial', sans-serif;
  max-width: 210mm; /* A4 paper width */
  margin: 0 auto;
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
</style>
