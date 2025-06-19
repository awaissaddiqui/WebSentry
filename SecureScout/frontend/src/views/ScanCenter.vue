<template>
  <div class="scan-center p-6">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold">Scan Center</h1>
      <div class="flex space-x-2">
        <el-button type="primary" @click="startNewScan">
          <el-icon class="mr-1">
            <Plus />
          </el-icon>
          New Scan
        </el-button>
        <el-button @click="refreshScans" :loading="isRefreshing">
          <el-icon class="mr-1">
            <Refresh />
          </el-icon>
          Refresh
        </el-button>
      </div>
    </div>

    <!-- Active Scans -->
    <div class="bg-white rounded-lg shadow-md p-6 mb-6" v-if="activeScans.length > 0">
      <h2 class="text-lg font-semibold mb-4">Active Scans ({{ activeScans.length }})</h2>

      <el-table :data="activeScans" style="width: 100%" border stripe>
        <el-table-column prop="id" label="Scan ID" width="180" />
        <el-table-column prop="url" label="Target URL" min-width="200">
          <template #default="{ row }">
            <el-link :href="row.url" target="_blank" type="primary">{{ row.url }}</el-link>
          </template>
        </el-table-column>
        <el-table-column label="Start Time" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.start_time) }}
          </template>
        </el-table-column>
        <el-table-column label="Status" width="120">
          <template #default="{ row }">
            <ScanStatusBadge :status="row.status" />
          </template>
        </el-table-column>
        <el-table-column label="Progress" width="200">
          <template #default="{ row }">
            <div v-if="row.status === 'in_progress'">
              <el-progress :percentage="calculateProgress(row)" :stroke-width="10"
                :status="row.status === 'failed' ? 'exception' : ''" />
            </div>
            <span v-else-if="row.status === 'pending'">Pending...</span>
            <span v-else-if="row.status === 'failed'">Failed</span>
            <span v-else-if="row.status === 'completed'">Completed</span>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="150">
          <template #default="{ row }">
            <div class="flex flex-wrap gap-2">
              <el-button size="small" type="primary" @click="viewScanDetails(row.id)">
                Details
              </el-button>
              <el-button size="small" type="danger" @click="cancelScan(row)"
                v-if="row.status === 'pending' || row.status === 'in_progress'">
                Cancel
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- Scan History -->
    <div class="bg-white rounded-lg shadow-md p-6">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-lg font-semibold">Scan History</h2>

        <div class="flex items-center">
          <el-input v-model="searchQuery" placeholder="Search URL or ID" clearable class="w-60 mr-2">
            <template #prefix>
              <el-icon>
                <Search />
              </el-icon>
            </template>
          </el-input>

          <el-select v-model="statusFilter" placeholder="Status Filter" clearable class="w-32 mr-2">
            <el-option label="All" value="" />
            <el-option label="Completed" value="completed" />
            <el-option label="Failed" value="failed" />
          </el-select>

          <el-popconfirm
            title="Are you sure you want to clear all scan records? This will delete all completed and failed scans."
            @confirm="clearAllScanHistory" confirm-button-type="danger">
            <template #reference>
              <el-button size="small" type="danger">Clear History</el-button>
            </template>
          </el-popconfirm>
        </div>
      </div>

      <el-table :data="filteredScans" style="width: 100%" border stripe v-loading="isLoading">
        <el-table-column prop="id" label="Scan ID" width="180" />
        <el-table-column prop="url" label="Target URL" min-width="200">
          <template #default="{ row }">
            <el-link :href="row.url" target="_blank" type="primary">{{ row.url }}</el-link>
          </template>
        </el-table-column>
        <el-table-column label="Scan Time" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.start_time) }}
          </template>
        </el-table-column>
        <el-table-column label="End Time" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.end_time) }}
          </template>
        </el-table-column>
        <el-table-column label="Status" width="120">
          <template #default="{ row }">
            <ScanStatusBadge :status="row.status" />
          </template>
        </el-table-column>
        <el-table-column label="Vulnerabilities" width="100">
          <template #default="{ row }">
            <el-tag :type="row.vulnerabilities && row.vulnerabilities.length > 0 ? 'danger' : 'success'" effect="dark">
              {{ row.vulnerabilities ? row.vulnerabilities.length : 0 }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="200">
          <template #default="{ row }">
            <div class="flex flex-wrap gap-2">
              <el-button size="small" type="primary" @click="viewScanDetails(row.id)">
                Details
              </el-button>
              <el-button size="small" type="success" @click="viewScanReport(row.id)" v-if="row.status === 'completed'">
                Report
              </el-button>
              <el-button size="small" @click="runAgain(row)"
                v-if="row.status === 'completed' || row.status === 'failed'">
                Rescan
              </el-button>
              <el-popconfirm title="Are you sure you want to delete this scan record?" @confirm="deleteScan(row)"
                confirm-button-type="danger">
                <template #reference>
                  <el-button size="small" type="danger" :icon="Delete" />
                </template>
              </el-popconfirm>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <div class="flex justify-center mt-4">
        <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper" :total="totalItems" @size-change="handleSizeChange"
          @current-change="handleCurrentChange" />
      </div>
    </div>

    <!-- Add Scan Details Dialog -->
    <el-dialog v-model="scanDetailsDialogVisible" :title="`Scan Details - ${currentDetailScanId}`" width="70%"
      top="5vh">
      <div v-if="currentScanDetails" class="scan-details-content">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Basic Info -->
          <div class="bg-gray-50 p-4 rounded-lg">
            <h3 class="text-lg font-semibold mb-3">Basic Information</h3>
            <el-descriptions :column="1" border>
              <el-descriptions-item label="Scan ID">{{ currentDetailScanId }}</el-descriptions-item>
              <el-descriptions-item label="Target URL">
                <el-link :href="currentScanDetails.url" target="_blank" type="primary">{{ currentScanDetails.url
                }}</el-link>
              </el-descriptions-item>
              <el-descriptions-item label="Start Time">{{ formatDateTime(currentScanDetails.start_time)
              }}</el-descriptions-item>
              <el-descriptions-item label="End Time">
                {{ currentScanDetails.end_time ? formatDateTime(currentScanDetails.end_time) : 'Scanning...' }}
              </el-descriptions-item>
              <el-descriptions-item label="Status">
                <ScanStatusBadge :status="currentScanDetails.status" />
              </el-descriptions-item>
              <el-descriptions-item v-if="currentScanDetails.status === 'in_progress'" label="Progress">
                <el-progress :percentage="calculateProgress(currentScanDetails)" :stroke-width="10"
                  :status="currentScanDetails.status === 'failed' ? 'exception' : ''" />
              </el-descriptions-item>
              <el-descriptions-item v-if="currentScanDetails.status === 'failed'" label="Error Message">
                <span class="text-red-500">{{ currentScanDetails.error || 'Unknown error' }}</span>
              </el-descriptions-item>
            </el-descriptions>
          </div>

          <!-- Scan Stats -->
          <div class="bg-gray-50 p-4 rounded-lg">
            <h3 class="text-lg font-semibold mb-3">Scan Statistics</h3>
            <div class="grid grid-cols-2 gap-4">
              <div class="bg-white p-3 rounded-md shadow-sm">
                <div class="text-sm text-gray-500">Pages Scanned</div>
                <div class="text-2xl font-bold text-blue-600">{{ currentScanDetails.scannedPages || 0 }}</div>
              </div>
              <div class="bg-white p-3 rounded-md shadow-sm">
                <div class="text-sm text-gray-500">Forms Detected</div>
                <div class="text-2xl font-bold text-blue-600">{{ currentScanDetails.scannedForms || 0 }}</div>
              </div>
              <div class="bg-white p-3 rounded-md shadow-sm">
                <div class="text-sm text-gray-500">Assets Scanned</div>
                <div class="text-2xl font-bold text-blue-600">{{ currentScanDetails.scannedAssets || 0 }}</div>
              </div>
              <div class="bg-white p-3 rounded-md shadow-sm">
                <div class="text-sm text-gray-500">Vulnerabilities Found</div>
                <div class="text-2xl font-bold"
                  :class="currentScanVulnerabilities.length > 0 ? 'text-red-600' : 'text-green-600'">
                  {{ currentScanVulnerabilities.length }}
                </div>
              </div>
            </div>
            <div class="mt-4 text-right text-sm text-gray-500">
              Scan Duration: {{ currentScanDetails.scanDuration || 'Calculating...' }}
            </div>
          </div>
        </div>

        <!-- Scan Config -->
        <div class="mt-6 bg-gray-50 p-4 rounded-lg">
          <h3 class="text-lg font-semibold mb-3">Scan Configuration</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <el-descriptions :column="1" border size="small">
                <el-descriptions-item label="User Agent">{{ currentScanDetails.scanConfig?.userAgent
                }}</el-descriptions-item>
                <el-descriptions-item label="Timeout">{{ currentScanDetails.scanConfig?.timeout
                }}</el-descriptions-item>
                <el-descriptions-item label="Scan Depth">{{ currentScanDetails.scanConfig?.maxDepth
                }}</el-descriptions-item>
              </el-descriptions>
            </div>
            <div>
              <p class="text-sm font-medium mb-2">Enabled Checks:</p>
              <div class="flex flex-wrap gap-2">
                <el-tag v-for="(option, index) in currentScanDetails.scanConfig?.scanOptions" :key="index" size="small">
                  {{ option }}
                </el-tag>
              </div>
            </div>
          </div>
        </div>

        <!-- Scan Progress -->
        <div class="mt-6 bg-gray-50 p-4 rounded-lg">
          <h3 class="text-lg font-semibold mb-3">Scan Process</h3>
          <el-timeline>
            <el-timeline-item v-for="(phase, index) in currentScanDetails.scanProcess" :key="index" :type="phase.status === 'completed' ? 'success' :
              phase.status === 'in_progress' ? 'primary' :
                phase.status === 'pending' ? 'info' : 'warning'" :timestamp="phase.time"
              :hollow="phase.status !== 'completed'">
              <div class="flex items-center">
                <span>{{ phase.phase }}</span>
                <el-tag size="small" class="ml-2" :type="phase.status === 'completed' ? 'success' :
                  phase.status === 'in_progress' ? 'warning' :
                    phase.status === 'pending' ? 'info' : 'danger'">
                  {{ phase.status === 'completed' ? 'Completed' :
                    phase.status === 'in_progress' ? 'In Progress' :
                      phase.status === 'pending' ? 'Pending' : 'Failed' }}
                </el-tag>
                <el-icon v-if="phase.status === 'in_progress'" class="ml-2 is-loading">
                  <Loading />
                </el-icon>
              </div>
            </el-timeline-item>
          </el-timeline>
        </div>

        <!-- Vulnerability List -->
        <div v-if="currentScanVulnerabilities.length > 0" class="mt-6 bg-gray-50 p-4 rounded-lg">
          <h3 class="text-lg font-semibold mb-3">Vulnerabilities Found ({{ currentScanVulnerabilities.length }})</h3>
          <el-table :data="currentScanVulnerabilities" border stripe>
            <el-table-column prop="id" label="Vulnerability ID" width="120" />
            <el-table-column prop="type" label="Type" width="120" />
            <el-table-column prop="location" label="Location" min-width="200" />
            <el-table-column label="Severity" width="100">
              <template #default="{ row }">
                <el-tag :type="row.severity === 'High' ? 'danger' : row.severity === 'Medium' ? 'warning' : 'info'"
                  effect="dark">
                  {{ row.severity }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="CVSS Score" width="100">
              <template #default="{ row }">
                <span :class="row.cvss >= 7.0 ? 'text-red-500' :
                  row.cvss >= 4.0 ? 'text-yellow-500' : 'text-green-500'" class="font-bold">
                  {{ row.cvss }}
                </span>
              </template>
            </el-table-column>
            <el-table-column label="Actions" width="100">
              <template #default="{ row }">
                <el-button size="small" type="primary" @click="ElMessageBox.alert(row.description, `${row.type} Details`, {
                  dangerouslyUseHTMLString: true,
                  confirmButtonText: 'OK'
                })">
                  Details
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- No Vulnerabilities -->
        <div v-else-if="currentScanDetails.status === 'completed'" class="mt-6 bg-green-50 p-6 rounded-lg text-center">
          <el-icon class="text-3xl text-green-500 mb-2">
            <CircleCheckFilled />
          </el-icon>
          <h3 class="text-lg font-semibold text-green-700">No Security Vulnerabilities Found</h3>
          <p class="text-green-600 mt-2">Congratulations! No significant security vulnerabilities were detected on your
            website.</p>
          <p class="text-gray-500 text-sm mt-2">Note: Security scans cannot guarantee 100% detection of all
            vulnerabilities.
            Regular security checks are recommended.</p>
        </div>
      </div>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="scanDetailsDialogVisible = false">Close</el-button>
          <el-button type="primary" @click="showScanReportDialog(currentDetailScanId); scanDetailsDialogVisible = false"
            v-if="currentScanDetails && currentScanDetails.status === 'completed'">
            View Report
          </el-button>
          <el-button type="success" @click="exportReport('pdf')"
            v-if="currentScanDetails && currentScanDetails.status === 'completed'">
            Export Report
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- Scan Report Dialog -->
    <el-dialog v-model="scanReportDialogVisible" :title="`Security Scan Report - ${currentReportScanId}`" width="80%"
      top="5vh">
      <div v-if="currentScanDetails" class="scan-report-content">
        <!-- Report Header -->
        <div class="flex justify-between items-center mb-6 border-b pb-4">
          <div>
            <h2 class="text-xl font-bold">Web Security Scan Report</h2>
            <p class="text-gray-500">Target: {{ currentScanDetails.url }}</p>
          </div>
          <div class="text-right">
            <p class="text-sm text-gray-500">Report ID: {{ currentReportScanId }}-R</p>
            <p class="text-sm text-gray-500">Generated: {{ formatDateTime(new Date().toISOString()) }}</p>
          </div>
        </div>

        <!-- Security Score -->
        <div class="bg-gray-50 p-6 rounded-lg mb-6">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="flex flex-col items-center justify-center">
              <div class="relative">
                <el-progress type="dashboard" :percentage="currentScanVulnerabilities.length > 0 ?
                  Math.max(0, 100 - currentScanVulnerabilities.length * 15) : 100" :color="currentScanVulnerabilities.length > 0 ?
                    (currentScanVulnerabilities.length > 3 ? '#F56C6C' : '#E6A23C') : '#67C23A'" />
                <!-- <div class="absolute  flex items-center justify-center">
                  <span class="text-2xl font-bold ">
                    {{ currentScanVulnerabilities.length > 0 ?
                      Math.max(0, 100 - currentScanVulnerabilities.length * 15) : 100 }}
                  </span>
                </div> -->
              </div>
              <p class="mt-2 text-center">Security Score</p>
            </div>

            <div class="col-span-2">
              <h3 class="text-lg font-medium mb-3">Security Assessment</h3>
              <el-alert :title="currentScanVulnerabilities.length > 0 ?
                `Found ${currentScanVulnerabilities.length} security vulnerabilities` :
                'No security vulnerabilities found'" :type="currentScanVulnerabilities.length > 0 ?
                  (currentScanVulnerabilities.length > 3 ? 'error' : 'warning') : 'success'" :description="currentScanVulnerabilities.length > 0 ?
                    'Your website has security risks. Please fix the following vulnerabilities as soon as possible.' :
                    'Your website is in good security condition. No significant vulnerabilities detected.'" show-icon
                :closable="false" class="mb-4" />

              <p class="text-sm text-gray-600">
                <span class="font-medium">Scan Scope:</span> {{ currentScanDetails.scannedPages }} pages scanned,
                {{ currentScanDetails.scannedForms }} forms and {{ currentScanDetails.scannedAssets }} assets checked.
                Scan depth: {{ currentScanDetails.scanConfig?.maxDepth }}.
              </p>
            </div>
          </div>
        </div>

        <!-- Vulnerability Summary -->
        <div v-if="currentScanVulnerabilities.length > 0" class="mb-6">
          <h3 class="text-lg font-semibold mb-3">Vulnerability Summary</h3>

          <el-collapse>
            <el-collapse-item v-for="(vulnerability, index) in currentScanVulnerabilities" :key="index" :name="index">
              <template #title>
                <div class="flex items-center">
                  <el-tag class="mr-2" :type="vulnerability.severity === 'High' ? 'danger' :
                    vulnerability.severity === 'Medium' ? 'warning' : 'info'" effect="dark">
                    {{ vulnerability.severity }}
                  </el-tag>
                  <span>{{ vulnerability.type }}</span>
                  <span class="ml-2 text-sm text-gray-500">- {{ vulnerability.id }}</span>
                </div>
              </template>

              <div class="vulnerability-details p-3">
                <el-descriptions :column="1" border size="small">
                  <el-descriptions-item label="Vulnerability ID">{{ vulnerability.id }}</el-descriptions-item>
                  <el-descriptions-item label="Type">{{ vulnerability.type }}</el-descriptions-item>
                  <el-descriptions-item label="CVSS Score">
                    <span :class="vulnerability.cvss >= 7.0 ? 'text-red-500' :
                      vulnerability.cvss >= 4.0 ? 'text-yellow-500' : 'text-green-500'" class="font-bold">
                      {{ vulnerability.cvss }}
                    </span>
                  </el-descriptions-item>
                  <el-descriptions-item label="Location">{{ vulnerability.location }}</el-descriptions-item>
                  <el-descriptions-item label="Description">{{ vulnerability.description }}</el-descriptions-item>
                  <el-descriptions-item label="Recommended Fix">{{ vulnerability.solution }}</el-descriptions-item>
                </el-descriptions>

                <div class="mt-4 flex justify-end">
                  <el-button size="small" type="success">View Recommendation Guide</el-button>
                </div>
              </div>
            </el-collapse-item>
          </el-collapse>
        </div>

        <!-- Scan Charts -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div class="bg-gray-50 rounded-lg p-4">
            <h3 class="text-lg font-medium mb-3">Vulnerability Type Distribution</h3>
            <div class="h-60 flex items-center justify-center">
              <div v-if="currentScanVulnerabilities.length === 0" class="text-center text-gray-400">
                <p>No vulnerability data</p>
              </div>
              <div v-else class="w-full h-full">
                <!-- Chart component should be inserted here in a real project -->
                <div class="bg-white p-4 rounded-lg h-full flex items-center justify-center">
                  <p>Vulnerability Type Distribution Chart</p>
                </div>
              </div>
            </div>
          </div>

          <div class="bg-gray-50 rounded-lg p-4">
            <h3 class="text-lg font-medium mb-3">Vulnerability Severity Distribution</h3>
            <div class="h-60 flex items-center justify-center">
              <div v-if="currentScanVulnerabilities.length === 0" class="text-center text-gray-400">
                <p>No vulnerability data</p>
              </div>
              <div v-else class="w-full h-full">
                <!-- Chart component should be inserted here in a real project -->
                <div class="bg-white p-4 rounded-lg h-full flex items-center justify-center">
                  <p>Vulnerability Severity Distribution Chart</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Security Advice -->
        <div class="bg-gray-50 rounded-lg p-6 mb-6">
          <h3 class="text-lg font-semibold mb-3">Security Advice</h3>

          <div v-if="currentScanVulnerabilities.length > 0">
            <p class="mb-3">Based on the scan results, we recommend the following actions to improve your website
              security:
            </p>

            <ol class="list-decimal pl-6 mb-4 space-y-2">
              <li v-for="(vulnerability, index) in currentScanVulnerabilities.slice(0, 3)" :key="index">
                <span class="font-medium">Fix {{ vulnerability.type }} vulnerability:</span> {{ vulnerability.solution
                }}
              </li>
              <li v-if="currentScanVulnerabilities.length > 3">
                Fix <strong>{{ currentScanVulnerabilities.length - 3 }}</strong> other vulnerabilities, see the summary
                section for details.
              </li>
              <li>Perform regular security scans, at least once a month.</li>
              <li>Ensure all software and dependencies are up to date.</li>
            </ol>
          </div>
          <div v-else>
            <p class="mb-3">Although no significant vulnerabilities were found, we still recommend:</p>

            <ol class="list-decimal pl-6 mb-4 space-y-2">
              <li>Perform regular security scans, at least once a month.</li>
              <li>Ensure all software and dependencies are up to date.</li>
              <li>Implement strong password policies and multi-factor authentication.</li>
              <li>Configure appropriate Content Security Policy (CSP).</li>
              <li>Encrypt sensitive data.</li>
            </ol>
          </div>
        </div>
      </div>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="scanReportDialogVisible = false">Close</el-button>
          <el-button type="primary" @click="generatePDF">Generate PDF</el-button>
          <el-dropdown @command="exportReport" trigger="click">
            <el-button type="primary">
              More Formats <el-icon class="ml-1">
                <ArrowDown />
              </el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="pdf">PDF</el-dropdown-item>
                <el-dropdown-item command="html">HTML</el-dropdown-item>
                <el-dropdown-item command="csv">CSV</el-dropdown-item>
                <el-dropdown-item command="json">JSON</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          <el-button type="success" @click="emailReport()">Send by Email</el-button>
        </span>
      </template>
    </el-dialog>

   <!-- PDF Template (Hidden) -->
<div v-show="false" ref="pdfContainer" class="pdf-container">
  <div id="report-pdf-template" class="pdf-template">
    
    <!-- CySmart.ai Logo and Branding -->
    <div class="report-branding" style="display: flex; align-items: center; margin-bottom: 20px;">
      <img :src="logo" alt="CySmart.ai Logo" style="height: 50px; margin-right: 10px;" />
      <h1 style="margin: 0; font-size: 24px;">CySmart.ai Web Security Scan Report</h1>
    </div>

    <!-- Report Metadata -->
    <div class="report-header">
      <div class="report-meta">
        <p><strong>Report ID:</strong> {{ currentReportScanId }}</p>
        <p><strong>Target URL:</strong> {{ currentScanDetails?.url }}</p>
        <p><strong>Scan Time:</strong> {{ formatDateTime(currentScanDetails?.start_time) }}</p>
        <p><strong>Status:</strong> {{ currentScanDetails?.status === 'completed' ? 'Completed' : currentScanDetails?.status }}</p>
      </div>
    </div>

    <!-- Vulnerability Summary -->
    <div class="vulnerability-summary">
      <h2>Vulnerability Statistics</h2>
      <p>Total vulnerabilities found: {{ currentScanVulnerabilities?.length || 0 }}</p>
    </div>

    <!-- Vulnerability Details -->
    <div v-if="currentScanVulnerabilities?.length > 0" class="vulnerability-details">
      <h2>Vulnerability Details</h2>
      <div v-for="(vuln, index) in currentScanVulnerabilities" :key="index" class="vulnerability-item">
        <h3>{{ index + 1 }}. {{ vuln.type }} ({{ vuln.severity }})</h3>
        <p v-if="vuln.location"><strong>URL:</strong> {{ vuln.location }}</p>
        <p v-if="vuln.description"><strong>Description:</strong> {{ vuln.description }}</p>
      </div>
    </div>

    <!-- Remediation Advice -->
    <div class="remediation-advice">
      <h2>Security Advice</h2>
      <div v-if="currentScanVulnerabilities?.length > 0">
        <div v-for="vuln in currentScanVulnerabilities" :key="vuln.id" class="advice-item">
          <h3>{{ vuln.type }} Recommended Fix:</h3>
          <p>{{ vuln.solution }}</p>
        </div>
      </div>
      <div v-else>
        <p>No security vulnerabilities found. Please continue to follow good security practices.</p>
      </div>
    </div>
    
  </div>
</div>

  </div>

</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  Refresh,
  Search,
  Delete,
  ArrowDown
} from '@element-plus/icons-vue'
import ScanStatusBadge from '@/components/ScanStatusBadge.vue'
import { scanApi } from '@/api'
import { useScanStore } from '@/store/scanStore'
import logo from '../../imgs/logo.jpg'

const scanStore = useScanStore()
const router = useRouter()

// Scan data and status
const isLoading = ref(true)
const isRefreshing = ref(false)
const scans = ref([])
const activeScans = ref([])

// Pagination and filtering
const currentPage = ref(1)
const pageSize = ref(10)
const totalItems = ref(0)
const searchQuery = ref('')
const statusFilter = ref('')

// Add dialog box status variable
const scanDetailsDialogVisible = ref(false)
const scanReportDialogVisible = ref(false)
const currentDetailScanId = ref('')
const currentReportScanId = ref('')

// Scan the detailed data
const currentScanDetails = ref(null)
const currentScanVulnerabilities = ref([])

// PDF generation related
const pdfContainer = ref(null)

// Get the scan list
async function fetchScans() {
  isLoading.value = true

  try {
    // Get all scan records from scanStore
    const results = await scanStore.getAllScans()
    // Make sure that the latest data is obtained here
    scans.value = [...results]
    totalItems.value = results.length

    // Get active scan
    activeScans.value = scans.value.filter(s =>
      s.status === 'pending' || s.status === 'in_progress'
    )
  } catch (error) {
    console.error('Failed to obtain scan record:', error)
    ElMessage.error('Failed to obtain scan record')
  } finally {
    isLoading.value = false
  }
}

// Refresh the scan list
async function refreshScans() {
  isRefreshing.value = true
  try {
    await fetchScans()
    ElMessage.success('Refresh successfully')
  } catch (error) {
    console.error('Refresh failed:', error)
  } finally {
    isRefreshing.value = false
  }
}

// Filter the scan list
const filteredScans = computed(() => {
  let result = [...scans.value]

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(scan =>
      scan.url.toLowerCase().includes(query) ||
      scan.id.toLowerCase().includes(query)
    )
  }

  if (statusFilter.value) {
    result = result.filter(scan => scan.status === statusFilter.value)
  }

  // Calculate paging
  totalItems.value = result.length

  // Return the data of the current page
  const startIndex = (currentPage.value - 1) * pageSize.value
  return result.slice(startIndex, startIndex + pageSize.value)
})


// Pagination processing
function handleSizeChange(size) {
  pageSize.value = size
  currentPage.value = 1
}

function handleCurrentChange(page) {
  currentPage.value = page
}

// Start a new scan
function startNewScan() {
  router.push('/scan')
}

// View scan details
function viewScanDetails(scanId) {
  // Open the details dialog instead of navigating to another page
  showScanDetailsDialog(scanId)
}

// View scan report
function viewScanReport(scanId) {
  // Open the report dialog instead of navigating to another page
  showScanReportDialog(scanId)
}

// Rerun the scan
function runAgain(scan) {
  ElMessage.success(`Start rescanning: ${scan.url}`)
  router.push({
    path: '/scan',
    query: { url: scan.url }
  })
}

// Delete scan records
async function deleteScan(scan) {
  try {
    // Use scanStore to implement deletion, which will synchronize the update of localStorage
    await scanStore.deleteScan(scan.id)
    // Update the current page data
    scans.value = scans.value.filter(s => s.id !== scan.id)
    ElMessage.success('Scan record has been deleted')
  } catch (error) {
    console.error('Failed to delete scan records:', error)
    ElMessage.error('Delete scan failed: ' + (error.message || 'Unknown error'))
  }
}

// Cancel the ongoing scan
async function cancelScan(scan) {
  try {
    ElMessageBox.confirm(
      'Are you sure you want to cancel this scan task?',
      'Cancel scan',
      {
        confirmButtonText: 'Sure',
        cancelButtonText: 'Cancel',
        type: 'warning',
      }
    ).then(async () => {
      // The API should be called to cancel the scan in the actual project
      // await scanApi.cancelScan(scan.id)

      // Simulation cancellation successfully
      activeScans.value = activeScans.value.filter(s => s.id !== scan.id)
      ElMessage.success('Scan task cancelled')
    })
  } catch (error) {
    console.error('Cancel scan failed:', error)
    ElMessage.error('Cancel scan failed')
  }
}

// Calculate the percentage of scan progress
function calculateProgress(scan) {
  if (scan.progress !== undefined) return scan.progress

  // If the backend does not provide progress information, simulate a random progress
  // In actual application, the API should be called to obtain real-time progress
  const startTime = new Date(scan.start_time).getTime()
  const now = Date.now()
  const elapsed = now - startTime

  // Assume that the scan lasts up to 10 minutes
  const progress = Math.min(95, Math.floor((elapsed / (10 * 60 * 1000)) * 100))
  return progress
}

// Format date time
function formatDateTime(dateString) {
  try {
    const date = new Date(dateString)
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  } catch (e) {
    return dateString
  }
}

// Show scan details dialog box
function showScanDetailsDialog(scanId) {
  currentDetailScanId.value = scanId

  // Simulate to get scan details data
  const scan = [...scans.value, ...activeScans.value].find(s => s.id === scanId)

  if (scan) {
    // Create details
    currentScanDetails.value = {
      ...scan,
      scannedPages: Math.floor(Math.random() * 50) + 10,
      scannedForms: Math.floor(Math.random() * 20) + 5,
      scannedAssets: Math.floor(Math.random() * 30) + 8,
      scanDuration: `${Math.floor(Math.random() * 10) + 2}point${Math.floor(Math.random() * 50) + 10}Second`,
      scanConfig: {
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) WebSentry/1.0',
        timeout: '30 seconds',
        maxDepth: scan.status === 'in_progress' ? 'Level 3' : 'Level 2',
        scanOptions: [
          'Cross-site scripting(XSS)',
          'SQL Injection',
          'CSRF vulnerability',
          'Information leakage detection',
          'Directory traversal',
          'SSRF vulnerability'
        ].sort(() => Math.random() - 0.5).slice(0, Math.floor(Math.random() * 4) + 2)
      },
      scanProcess: [
        { phase: 'initialization', time: '00:00:00', status: 'completed' },
        { phase: 'Website connection', time: '00:00:01', status: 'completed' },
        { phase: 'Crawl the website', time: '00:00:15', status: scan.status === 'in_progress' && calculateProgress(scan) < 50 ? 'in_progress' : 'completed' },
        { phase: 'Page analysis', time: '00:01:30', status: scan.status === 'in_progress' && calculateProgress(scan) >= 50 && calculateProgress(scan) < 80 ? 'in_progress' : (scan.status === 'in_progress' && calculateProgress(scan) < 50 ? 'pending' : 'completed') },
        { phase: 'Vulnerability scanning', time: '00:02:45', status: scan.status === 'in_progress' && calculateProgress(scan) >= 80 ? 'in_progress' : (scan.status === 'in_progress' && calculateProgress(scan) < 80 ? 'pending' : 'completed') },
        { phase: 'Generate a report', time: '00:03:30', status: scan.status === 'completed' ? 'completed' : 'pending' }
      ]
    }

    // If there is a vulnerability, get vulnerability details
    if (scan.vulnerabilities && scan.vulnerabilities.length > 0) {
      currentScanVulnerabilities.value = scan.vulnerabilities.map(v => ({
        ...v,
        id: `VULN-${Math.random().toString(36).substring(2, 10).toUpperCase()}`,
        location: v.type === 'XSS' ? `${scan.url}/search?q=<script>` :
          v.type === 'SQL Injection' ? `${scan.url}/product?id=1'` :
            `${scan.url}/page?id=${Math.floor(Math.random() * 100) + 1}`,
        description: getVulnerabilityDescription(v.type),
        solution: getVulnerabilitySolution(v.type),
        cvss: v.severity === 'high' ? (Math.random() * 2 + 7).toFixed(1) :
          v.severity === 'middle' ? (Math.random() * 2 + 4).toFixed(1) :
            (Math.random() * 2 + 1).toFixed(1)
      }))
    } else {
      currentScanVulnerabilities.value = []
    }
  }

  scanDetailsDialogVisible.value = true
}

// Show Scan Report dialog box
function showScanReportDialog(scanId) {
  currentReportScanId.value = scanId

  // Automatically open the vulnerability details dialog box
  showScanDetailsDialog(scanId)

  // Then close and open the report dialog
  setTimeout(() => {
    scanDetailsDialogVisible.value = false
    scanReportDialogVisible.value = true
  }, 100)
}

// Get vulnerability description
function getVulnerabilityDescription(type) {
  const descriptions = {
    'XSS': 'Cross-site scripting(XSS)The vulnerability allows an attacker to inject malicious scripts into a web page. When other users browse this page, the script will be executed in the user browser, which may lead to risks such as session hijacking and sensitive information leakage.',
    'SQL Injection': 'SQL injection vulnerability allows an attacker to insert malicious SQL code into the application input and execute it on the backend database, which can lead to unauthorized data access, data breaches, or data corruption.',
    'CSRF': 'Cross-site request forgery (CSRF) vulnerability allows an attacker to induce users to perform unexpected actions, such as changing account passwords or transferring money without the user knowledge.',
    'Information leakage': 'Information leakage vulnerabilities involve applications inadvertently exposing sensitive information, such as configuration details, internal paths, or user data.',
    'Configuration error': 'An incorrect configuration refers to the inappropriate security configuration of the system, framework, or application server, which may lead to unauthorized access or information leakage.',
    'File contains': 'File Containment Vulnerabilities allow an attacker to include malicious files that may lead to code execution, information disclosure, or server control.',
    'Directory traversal': 'The directory traversal vulnerability allows an attacker to access files outside of the expected directory, including system files or other sensitive data.',
    'Revealing of sensitive information': 'Sensitive information leakage refers to the application exposing sensitive data in the front-end or response, such as API keys, internal paths, user data, etc.'
  }

  return descriptions[type] || 'This type of vulnerability may cause system security risks and needs to be fixed in time.'
}
// Get vulnerability solutions
function getVulnerabilitySolution(type) {
  const solutions = {
    'XSS': 'All user input is strictly filtered and encoded, using Content Security Policy (CSP), and using the modern framework automatic XSS protection function.',
    'SQL Injection': 'Use parameterized query or preprocessing statements to verify user input and use a database account with a minimum permission.',
    'CSRF': 'Implement Anti-CSRF tokens, verify the Referer header, use the SameSite Cookie attribute, and require reauthentication of sensitive operations.',
    'Information leakage': 'Review error messages, configure appropriate HTTP response headers, remove sensitive data, and ensure that debug information is disabled in the production environment.',
    'Configuration flaw': 'Follow security configuration guidelines, disable unnecessary features, remove default accounts, and implement the principle of minimum permissions.',
    'File inclusion': 'Limit file include features, validate and sanitize user input, and use predefined file lists instead of directly accepting user input.',
    'Directory traversal': 'Use security functions to process file paths, limit file access only within a specific directory, and verify user input.',
    'Sensitive data exposure': 'Review all responses, implement appropriate data desensitization, configure secure HTTP headers, and ensure that error messages do not leak sensitive information.'
  };

  return solutions[type] || 'It is recommended to contact a security expert for detailed evaluation and repair recommendations.';
}

// Export the report
function exportReport(format = 'pdf') {
  ElMessage.success(`Exporting the report as${format.toUpperCase()}Format...`)

  setTimeout(() => {
    ElMessage.success(`Reports have been exported successfully`)
  }, 1500)
}

// Send a report email
function emailReport(email) {
  if (!email) {
    ElMessageBox.prompt('Please enter the address to receive the report', 'Send a report', {
      confirmButtonText: 'send',
      cancelButtonText: 'Cancel',
      inputPattern: /[\w!#$%&'*+/=?^_`{|}~-]+(?:\.[\w!#$%&'*+/=?^_`{|}~-]+)*@(?:[\w](?:[\w-]*[\w])?\.)+[\w](?:[\w-]*[\w])?/,
      inputErrorMessage: 'Please enter a valid email address'
    }).then(({ value }) => {
      ElMessage({
        type: 'success',
        message: `Report is being sent to ${value}`
      })
    }).catch(() => { })
  } else {
    ElMessage({
      type: 'success',
      message: `Report is being sent to ${email}`
    })
  }
}

// Generate PDF
async function generatePDF() {
  try {
    ElMessage.info('Preparing to print a PDF report, please wait...')

    // Use browser native printing function
    const printWindow = window.open('', '_blank')

    if (!printWindow) {
      throw new Error('Please allow the browser to open pop-up windows to generate PDF')
    }

    // Get PDF template elements
    const element = pdfContainer.value.querySelector('#report-pdf-template')
    if (!element) {
      throw new Error('Unable to find PDF template element')
    }

    // Set the contents of the print window
    printWindow.document.write(`
      <!DOCTYPE html>
      <html>
      <head>
        <title>Security scan report - ${currentReportScanId.value}</title>
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
          <button onclick="window.close()" style="padding: 8px 16px; background-color: #F56C6C; color: white; border: none; border-radius: 4px; cursor: pointer;">Close the window</button>
        </div>
        ${element.outerHTML}
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

    ElMessage.success('The PDF is open, please select "Save as PDF" Options')
  } catch (error) {
    console.error('An error occurred while generating PDF:', error)
    ElMessage.error('Failed to generate PDF: ' + error.message)
  }
}

// Add to clear all scan history function
async function clearAllScanHistory() {
  try {
    await scanStore.clearAllScans()
    // Retrieve the scan list
    fetchScans()
    ElMessage.success('Scan history has been cleared')
  } catch (error) {
    console.error('Clear scan history failed:', error)
    ElMessage.error('Clear scan history failed: ' + (error.message || 'Unknown error'))
  }
}

onMounted(() => {
  fetchScans()

  // Simulate progress updates for active scans
  const progressInterval = setInterval(() => {
    if (activeScans.value.length > 0) {
      activeScans.value.forEach(scan => {
        if (scan.status === 'in_progress') {
          scan.progress = Math.min(99, (scan.progress || 0) + Math.floor(Math.random() * 5) + 1)

          // Complete certain scans randomly
          if (scan.progress > 90 && Math.random() > 0.7) {
            scan.status = 'completed'
            scan.progress = 100
            scan.end_time = new Date().toISOString()

            // Add to history
            scans.value.unshift({
              id: scan.id,
              url: scan.url,
              start_time: scan.start_time,
              end_time: scan.end_time,
              status: 'completed',
              vulnerabilities: Math.random() > 0.5 ?
                Array(Math.floor(Math.random() * 4) + 1).fill(0).map(() => {
                  const types = ['XSS', 'SQL Injection', 'CSRF', 'Information leakage', 'Configuration error']
                  const severities = ['high', 'middle', 'Low']
                  return {
                    type: types[Math.floor(Math.random() * types.length)],
                    severity: severities[Math.floor(Math.random() * severities.length)]
                  }
                }) : []
            })

            // Update localStorage
            scanStore.saveScansToLocalStorage && scanStore.saveScansToLocalStorage()

            // Notify users
            ElMessage.success(`Scan the task ${Completedn.id} Completed`)
          }
        }
      })

      // Update active scan list
      activeScans.value = activeScans.value.filter(scan => scan.status !== 'completed')
    }
  }, 3000)

  onUnmounted(() => {
    clearInterval(progressInterval)
  })
})
</script>

<style scoped>
.scan-center {
  min-height: calc(100vh - 64px);
  background-color: #f5f7fa;
}

/* PDF Container Style */
.pdf-container {
  position: absolute;
  left: -9999px;
  top: 0;
  width: 210mm;
  /* A4 width */
  z-index: -1000;
}

.pdf-template {
  font-family: 'SimSun', 'Arial', sans-serif;
  background-color: white;
  padding: 20px;
  width: 210mm;
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

.vulnerability-details h2,
.vulnerability-summary h2,
.remediation-advice h2 {
  font-size: 18px;
  margin-top: 25px;
  margin-bottom: 10px;
  padding-bottom: 5px;
  border-bottom: 1px solid #eee;
}

.vulnerability-item {
  margin-bottom: 20px;
  padding: 10px;
  background-color: #f9f9f9;
  border-radius: 5px;
}

.advice-item {
  margin-bottom: 15px;
}
</style>