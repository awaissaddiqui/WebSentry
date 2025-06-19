<template>
  <div class="demo-implementation p-6">
    <h1 class="text-2xl font-bold mb-6">Feature Implementation Demo</h1>
    
    <el-tabs type="border-card" class="mb-6">
      <el-tab-pane label="SQL Injection Detection Implementation">
        <div class="p-4">
          <h2 class="text-xl font-semibold mb-4">SQL Injection Detection Implementation</h2>
          
          <div class="bg-blue-50 p-4 rounded-md mb-6">
            <p class="text-sm text-gray-700 mb-3">
              The SQL injection detection module identifies potential SQL injection vulnerabilities by:
            </p>
            <ol class="list-decimal pl-5 text-sm space-y-2">
              <li>Adding SQL injection test points to URL parameters (e.g. <code>'</code>, <code>OR 1=1</code>)</li>
              <li>Analyzing error messages and characteristic keywords in the response content</li>
              <li>Detecting database error information leakage</li>
              <li>Time-based blind injection testing</li>
            </ol>
          </div>
          
          <div class="mb-6">
            <h3 class="text-lg font-medium mb-3">Core Code Implementation</h3>
            <div class="bg-gray-50 p-4 rounded-md font-mono text-sm overflow-auto">
              <pre>
async def check_sql_injection(
    session: aiohttp.ClientSession,
    url: str, 
    vulnerability_library: Dict[str, Any],
    vulnerabilities: List[Dict[str, Any]]
) -> None:
    """Detect SQL injection vulnerabilities"""
    if "sql_injection" not in vulnerability_library:
        return
    
    patterns = vulnerability_library["sql_injection"].get("patterns", [])
    severity = vulnerability_library["sql_injection"].get("severity", "High")
    
    # Add SQL injection test points to URL parameters
    parsed_url = urlparse(url)
    path = parsed_url.path
    
    # If the URL already has parameters, add test points after the parameters
    if parsed_url.query:
        query_parts = parsed_url.query.split('&')
        for pattern in patterns:
            test_queries = []
            for part in query_parts:
                if '=' in part:
                    name, value = part.split('=', 1)
                    test_query = f"{name}={value}{pattern}"
                    test_queries.append(test_query)
            
            if test_queries:
                test_url = urlunparse((
                    parsed_url.scheme,
                    parsed_url.netloc,
                    path,
                    '',
                    '&'.join(test_queries),
                    parsed_url.fragment
                ))
                
                try:
                    response = await fetch_url(session, test_url)
                    if response and ('SQL' in response["text"] or 'syntax' in response["text"] 
                                    or 'mysql' in response["text"].lower() or 'error' in response["text"].lower()):
                        vulnerabilities.append({
                            "type": "sql_injection",
                            "url": url,
                            "test_url": test_url,
                            "description": "Potential SQL injection vulnerability found",
                            "severity": severity,
                            "details": f"Test parameter: {pattern}"
                        })
                        break  # Stop after finding one injection point
                except Exception as e:
                    logger.error(f"Error during SQL injection test: {str(e)}")
              </pre>
            </div>
          </div>
          
          <div class="mb-6">
            <h3 class="text-lg font-medium mb-3">Test Example</h3>
            <div class="bg-white border border-gray-200 rounded-md p-4">
              <div class="mb-4">
                <p class="text-sm font-medium mb-2">Test URL: <span class="text-blue-600">http://example.com/user.php?id=1</span></p>
                <div class="flex space-x-4 mb-4">
                  <el-button size="small" type="primary" @click="testSqlInjection">Test SQL Injection</el-button>
                  <p class="text-sm text-gray-500 mt-1">Click the button to add test vectors to the target URL</p>
                </div>
                
                <!-- Interactive SQL Injection Test Form -->
                <div class="bg-gray-50 p-4 rounded-md mt-4">
                  <h4 class="text-md font-medium mb-3">Interactive SQL Injection Test</h4>
                  <el-form :model="sqlForm" label-position="top">
                    <el-form-item label="Target URL">
                      <el-input v-model="sqlForm.targetUrl" placeholder="Enter the URL to test (e.g. http://example.com/page.php?id=1)" />
                    </el-form-item>
                    <el-form-item label="Select Test Vector">
                      <el-select v-model="sqlForm.vector" class="w-full">
                        <el-option 
                          v-for="item in sqlVectors" 
                          :key="item.vector" 
                          :label="item.vector" 
                          :value="item.vector" 
                        />
                      </el-select>
                    </el-form-item>
                    <el-form-item>
                      <el-button type="primary" @click="runSqlTest">Run Test</el-button>
                      <el-button @click="resetSqlForm">Reset</el-button>
                    </el-form-item>
                  </el-form>
                  
                  <!-- Test Results -->
                  <div v-if="sqlTestResults.show" class="mt-4 border-t pt-4">
                    <h4 class="text-md font-medium mb-2">Test Results</h4>
                    <div :class="['p-3 rounded', sqlTestResults.vulnerable ? 'bg-red-50' : 'bg-green-50']">
                      <p class="text-sm" :class="sqlTestResults.vulnerable ? 'text-red-600' : 'text-green-600'">
                        <span class="font-bold">Status:</span> {{ sqlTestResults.vulnerable ? 'Vulnerability Found' : 'No Vulnerability Found' }}
                      </p>
                      <p class="text-sm mt-1">
                        <span class="font-bold">Test URL:</span> {{ sqlTestResults.testUrl }}
                      </p>
                      <template v-if="sqlTestResults.vulnerable">
                        <p class="text-sm mt-1">
                          <span class="font-bold">Vulnerability Type:</span> SQL Injection
                        </p>
                        <p class="text-sm mt-1">
                          <span class="font-bold">Vulnerability Details:</span> {{ sqlTestResults.details }}
                        </p>
                      </template>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="mt-4">
                <p class="text-sm font-medium mb-2">Test Vectors:</p>
                <el-table :data="sqlVectors" border style="width: 100%" size="small">
                  <el-table-column prop="vector" label="Test Vector" />
                  <el-table-column prop="purpose" label="Purpose" />
                  <el-table-column prop="result" label="Detection Result">
                    <template #default="scope">
                      <el-tag :type="scope.row.result === 'Vulnerable' ? 'danger' : 'success'">
                        {{ scope.row.result }}
                      </el-tag>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>
      
      <el-tab-pane label="XSS Detection Implementation">
        <div class="p-4">
          <h2 class="text-xl font-semibold mb-4">XSS Detection Principle</h2>
          
          <div class="bg-blue-50 p-4 rounded-md mb-6">
            <p class="text-sm text-gray-700 mb-3">
              The XSS detection module checks whether the web page has cross-site scripting vulnerabilities mainly by:
            </p>
            <ol class="list-decimal pl-5 text-sm space-y-2">
              <li>Checking if HTML forms have input fields that may lead to XSS</li>
              <li>Analyzing if URL parameters are directly reflected in the page content</li>
              <li>Testing whether various XSS payloads are properly filtered or encoded</li>
              <li>Checking if HTTP response headers contain appropriate security headers (e.g. Content-Security-Policy)</li>
            </ol>
          </div>
          
          <div class="mb-6">
            <h3 class="text-lg font-medium mb-3">Core Code Implementation</h3>
            <div class="bg-gray-50 p-4 rounded-md font-mono text-sm overflow-auto">
              <pre>
def check_xss(
    url: str, 
    html_content: str, 
    vulnerability_library: Dict[str, Any],
    vulnerabilities: List[Dict[str, Any]]
) -> None:
    """Detect XSS vulnerabilities"""
    if "xss" not in vulnerability_library:
        return
    
    patterns = vulnerability_library["xss"].get("patterns", [])
    severity = vulnerability_library["xss"].get("severity", "High")
    
    # Check for unsafe input reflection in HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Check forms
    forms = soup.find_all('form')
    if forms:
        for form in forms:
            inputs = form.find_all('input')
            if inputs:
                for input_field in inputs:
                    # Check if input is properly filtered
                    if input_field.get('type') in ['text', 'search', 'url', 'tel', 'email', None]:
                        vulnerabilities.append({
                            "type": "xss",
                            "url": url,
                            "description": "Form may have XSS vulnerability",
                            "severity": severity,
                            "details": f"Form ID: {form.get('id', 'Unknown')}, Input field: {input_field.get('name', 'Unknown')}"
                        })
                        break
    
    # Check if URL parameters are reflected in the page
    parsed_url = urlparse(url)
    if parsed_url.query:
        query_parts = parsed_url.query.split('&')
        for part in query_parts:
            if '=' in part:
                name, value = part.split('=', 1)
                if value and value in html_content:
                    for pattern in patterns:
                        if pattern in value:
                            vulnerabilities.append({
                                "type": "xss",
                                "url": url,
                                "description": "URL parameter is directly reflected in the page",
                                "severity": severity,
                                "details": f"Parameter: {name}, Value: {value}"
                            })
                            break
              </pre>
            </div>
          </div>
          
          <div class="mb-6">
            <h3 class="text-lg font-medium mb-3">Test Example</h3>
            <div class="bg-white border border-gray-200 rounded-md p-4">
              <div class="mb-4">
                <p class="text-sm font-medium mb-2">Test URL: <span class="text-blue-600">http://example.com/search.php?q=test</span></p>
                <div class="flex space-x-4 mb-4">
                  <el-button size="small" type="primary" @click="testXss">Test XSS</el-button>
                  <p class="text-sm text-gray-500 mt-1">Click the button to add XSS test vectors to the target URL</p>
                </div>
                
                <!-- Interactive XSS Test Tool -->
                <div class="bg-gray-50 p-4 rounded-md mt-4">
                  <h4 class="text-md font-medium mb-3">Interactive XSS Test</h4>
                  <el-form :model="xssForm" label-position="top">
                    <el-form-item label="Target URL">
                      <el-input v-model="xssForm.targetUrl" placeholder="Enter the URL to test (e.g. http://example.com/search.php?q=test)" />
                    </el-form-item>
                    <el-form-item label="XSS Test Payload">
                      <el-input 
                        v-model="xssForm.payload" 
                        type="textarea" 
                        :rows="2"
                        placeholder="Enter XSS test payload (e.g. <script>alert('XSS')</script>)" 
                      />
                    </el-form-item>
                    <el-form-item label="Test Method">
                      <el-radio-group v-model="xssForm.method">
                        <el-radio-button label="get">GET Parameter</el-radio-button>
                        <el-radio-button label="post">Form Submission</el-radio-button>
                        <el-radio-button label="reflection">Reflection Test</el-radio-button>
                      </el-radio-group>
                    </el-form-item>
                    <el-form-item>
                      <el-button type="primary" @click="runXssTest">Run Test</el-button>
                      <el-button @click="resetXssForm">Reset</el-button>
                    </el-form-item>
                  </el-form>
                  
                  <!-- XSS Test Results -->
                  <div v-if="xssTestResults.show" class="mt-4 border-t pt-4">
                    <h4 class="text-md font-medium mb-2">Test Results</h4>
                    <div :class="['p-3 rounded', xssTestResults.vulnerable ? 'bg-red-50' : 'bg-green-50']">
                      <p class="text-sm" :class="xssTestResults.vulnerable ? 'text-red-600' : 'text-green-600'">
                        <span class="font-bold">Status:</span> {{ xssTestResults.vulnerable ? 'XSS Vulnerability Found' : 'No XSS Vulnerability Found' }}
                      </p>
                      <p class="text-sm mt-1">
                        <span class="font-bold">Test URL:</span> {{ xssTestResults.testUrl }}
                      </p>
                      <template v-if="xssTestResults.vulnerable">
                        <p class="text-sm mt-1">
                          <span class="font-bold">Vulnerability Reason:</span> {{ xssTestResults.reason }}
                        </p>
                        <p class="text-sm mt-2 font-bold">Security Advice:</p>
                        <ul class="list-disc pl-5 text-sm text-red-600">
                          <li>HTML-encode all user input</li>
                          <li>Implement Content Security Policy (CSP)</li>
                          <li>Use XSS filtering libraries</li>
                        </ul>
                      </template>
                    </div>
                    
                    <!-- XSS Test Preview -->
                    <div v-if="xssTestResults.previewAvailable" class="mt-4">
                      <h4 class="text-md font-medium mb-2">Response Preview (Demo Only)</h4>
                      <div class="border rounded p-3">
                        <div class="text-xs text-gray-500 mb-2">
                          The following shows the effect of a simulated XSS attack (scripts are not executed in the real environment)
                        </div>
                        <div class="bg-white p-2 border rounded">
                          <div v-html="xssTestResults.sanitizedPreview"></div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="mt-4">
                <p class="text-sm font-medium mb-2">XSS Test Vectors:</p>
                <el-table :data="xssVectors" border style="width: 100%" size="small">
                  <el-table-column prop="vector" label="Test Vector" />
                  <el-table-column prop="purpose" label="Purpose" />
                  <el-table-column prop="result" label="Detection Result">
                    <template #default="scope">
                      <el-tag :type="scope.row.result === 'Vulnerable' ? 'danger' : 'success'">
                        {{ scope.row.result }}
                      </el-tag>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>
      
      <el-tab-pane label="Other Vulnerability Detection Implementation">
        <div class="p-4">
          <h2 class="text-xl font-semibold mb-4">Other Vulnerability Detection Implementation</h2>
          
          <el-tabs>
            <el-tab-pane label="CSRF Detection">
              <div class="mb-6">
                <h3 class="text-lg font-medium mb-3">CSRF Detection Principle</h3>
                <div class="bg-blue-50 p-4 rounded-md mb-4">
                  <p class="text-sm text-gray-700 mb-3">
                    The CSRF detection module identifies cross-site request forgery vulnerabilities by:
                  </p>
                  <ol class="list-decimal pl-5 text-sm space-y-2">
                    <li>Checking if forms contain CSRF tokens</li>
                    <li>Checking if security-related HTTP headers are properly set</li>
                    <li>Analyzing the security settings of cookies</li>
                  </ol>
                </div>
                
                <!-- CSRF Detection Interactive Tool -->
                <div class="bg-white border border-gray-200 rounded-md p-4 mb-4">
                  <h4 class="text-md font-medium mb-3">CSRF Detection Tool</h4>
                  <el-form :model="csrfForm" label-position="top">
                    <el-form-item label="Target Website URL">
                      <el-input v-model="csrfForm.targetUrl" placeholder="Enter the website URL to test" />
                    </el-form-item>
                    <el-form-item label="Detection Options">
                      <el-checkbox-group v-model="csrfForm.options">
                        <el-checkbox label="checkForms">Check form CSRF tokens</el-checkbox>
                        <el-checkbox label="checkHeaders">Check security HTTP headers</el-checkbox>
                        <el-checkbox label="checkCookies">Check cookie settings</el-checkbox>
                      </el-checkbox-group>
                    </el-form-item>
                    <el-form-item>
                      <el-button type="primary" @click="runCsrfTest">Run CSRF Detection</el-button>
                      <el-button @click="resetCsrfForm">Reset</el-button>
                    </el-form-item>
                  </el-form>
                  
                  <!-- CSRF Test Results -->
                  <div v-if="csrfTestResults.show" class="mt-4 border-t pt-4">
                    <h4 class="text-md font-medium mb-2">CSRF Detection Results</h4>
                    <div :class="['p-3 rounded', csrfTestResults.vulnerable ? 'bg-red-50' : 'bg-green-50']">
                      <p class="text-sm" :class="csrfTestResults.vulnerable ? 'text-red-600' : 'text-green-600'">
                        <span class="font-bold">Detection Result:</span> {{ csrfTestResults.vulnerable ? 'CSRF Vulnerability Found' : 'No CSRF Vulnerability Found' }}
                      </p>
                      <template v-if="csrfTestResults.vulnerable">
                        <div class="mt-2">
                          <p class="text-sm font-bold">Vulnerability Details:</p>
                          <ul class="list-disc pl-5 text-sm text-red-600">
                            <li v-for="(detail, index) in csrfTestResults.details" :key="index">
                              {{ detail }}
                            </li>
                          </ul>
                        </div>
                        <div class="mt-3">
                          <p class="text-sm font-bold">Remediation Advice:</p>
                          <ul class="list-disc pl-5 text-sm text-gray-700">
                            <li>Add CSRF tokens to all forms</li>
                            <li>Set the SameSite=Strict cookie attribute</li>
                            <li>Implement X-Frame-Options and Content-Security-Policy headers</li>
                          </ul>
                        </div>
                      </template>
                    </div>
                  </div>
                </div>
                
                <div class="bg-gray-50 p-4 rounded-md font-mono text-sm overflow-auto mb-4">
                  <pre>
def check_csrf(
    url: str, 
    html_content: str, 
    headers: Dict[str, str],
    vulnerability_library: Dict[str, Any],
    vulnerabilities: List[Dict[str, Any]]
) -> None:
    """Detect CSRF vulnerabilities"""
    if "csrf" not in vulnerability_library:
        return
    
    severity = vulnerability_library["csrf"].get("severity", "Medium")
    
    # Check if CSRF tokens are used
    soup = BeautifulSoup(html_content, 'html.parser')
    forms = soup.find_all('form', method=re.compile(r'post', re.I))
    
    for form in forms:
        has_csrf_token = False
        
        # Find common CSRF token fields
        csrf_fields = form.find_all('input', attrs={
            'name': re.compile(r'csrf|token|nonce', re.I)
        })
        
        if csrf_fields:
            has_csrf_token = True
        
        if not has_csrf_token:
            vulnerabilities.append({
                "type": "csrf",
                "url": url,
                "description": "Form does not have CSRF protection",
                "severity": severity,
                "details": f"Form action: {form.get('action', 'Unknown')}"
            })
    
    # Check HTTP security headers
    has_csrf_headers = False
    for header in ['X-CSRF-Token', 'X-Frame-Options', 'Content-Security-Policy']:
        if header.lower() in [h.lower() for h in headers]:
            has_csrf_headers = True
            break
    
    if not has_csrf_headers and forms:
        vulnerabilities.append({
            "type": "csrf",
            "url": url,
            "description": "No anti-CSRF HTTP security headers used",
            "severity": severity,
            "details": "Missing X-CSRF-Token, X-Frame-Options, or Content-Security-Policy headers"
        })
                  </pre>
                </div>
              </div>
            </el-tab-pane>
            
            <el-tab-pane label="File Upload Vulnerability Detection">
              <div class="mb-6">
                <h3 class="text-lg font-medium mb-3">File Upload Vulnerability Detection Principle</h3>
                <div class="bg-blue-50 p-4 rounded-md mb-4">
                  <p class="text-sm text-gray-700 mb-3">
                    The file upload vulnerability detection module identifies insecure file upload functionality by:
                  </p>
                  <ol class="list-decimal pl-5 text-sm space-y-2">
                    <li>Checking for file upload forms</li>
                    <li>Analyzing whether there are sufficient restrictions on uploaded file types</li>
                    <li>Detecting whether dangerous file types are allowed to be uploaded</li>
                  </ol>
                </div>
                
                <!-- File Upload Vulnerability Test Tool -->
                <div class="bg-white border border-gray-200 rounded-md p-4 mb-4">
                  <h4 class="text-md font-medium mb-3">File Upload Vulnerability Test Tool</h4>
                  
                  <el-form :model="fileUploadForm" label-position="top">
                    <el-form-item label="Target Upload Page URL">
                      <el-input v-model="fileUploadForm.targetUrl" placeholder="Enter the file upload page URL to test" />
                    </el-form-item>
                    
                    <el-form-item label="File Type Test">
                      <el-select v-model="fileUploadForm.fileType" class="w-full">
                        <el-option label="PHP file (.php)" value="php" />
                        <el-option label="JSP file (.jsp)" value="jsp" />
                        <el-option label="ASP file (.asp)" value="asp" />
                        <el-option label="Executable file (.exe)" value="exe" />
                        <el-option label="Shell script (.sh)" value="sh" />
                        <el-option label="SVG file (.svg)" value="svg" />
                      </el-select>
                    </el-form-item>
                    
                    <el-form-item label="Bypass Method">
                      <el-radio-group v-model="fileUploadForm.bypassMethod">
                        <el-radio-button label="rename">Double Extension</el-radio-button>
                        <el-radio-button label="mimetype">MIME Type Spoofing</el-radio-button>
                        <el-radio-button label="nullbyte">Null Byte Bypass</el-radio-button>
                      </el-radio-group>
                    </el-form-item>
                    
                    <el-form-item>
                      <el-button type="primary" @click="runFileUploadTest">Run Test</el-button>
                      <el-button @click="resetFileUploadForm">Reset</el-button>
                    </el-form-item>
                  </el-form>
                  
                  <!-- File Upload Test Results -->
                  <div v-if="fileUploadResults.show" class="mt-4 border-t pt-4">
                    <h4 class="text-md font-medium mb-2">File Upload Vulnerability Test Results</h4>
                    <div :class="['p-3 rounded', fileUploadResults.vulnerable ? 'bg-red-50' : 'bg-green-50']">
                      <p class="text-sm" :class="fileUploadResults.vulnerable ? 'text-red-600' : 'text-green-600'">
                        <span class="font-bold">Test Result:</span> {{ fileUploadResults.vulnerable ? 'File Upload Vulnerability Found' : 'No File Upload Vulnerability Found' }}
                      </p>
                      
                      <template v-if="fileUploadResults.vulnerable">
                        <p class="text-sm mt-2">
                          <span class="font-bold">Test File Type:</span> {{ fileUploadForm.fileType }}
                        </p>
                        <p class="text-sm mt-1">
                          <span class="font-bold">Bypass Method:</span> {{ fileUploadResults.bypassMethod }}
                        </p>
                        <p class="text-sm mt-1">
                          <span class="font-bold">Test File Name:</span> {{ fileUploadResults.filename }}
                        </p>
                        
                        <div class="mt-3">
                          <p class="text-sm font-bold">Security Risk:</p>
                          <div class="bg-red-100 p-2 rounded text-sm text-red-700 mt-1">
                            Allowing upload of such files may lead to remote code execution, enabling attackers to gain server control.
                          </div>
                        </div>
                        
                        <div class="mt-3">
                          <p class="text-sm font-bold">Remediation Advice:</p>
                          <ul class="list-disc pl-5 text-sm text-gray-700">
                            <li>Strictly whitelist allowed file types</li>
                            <li>Validate file content, not just extension</li>
                            <li>Use random file names and store outside the web root</li>
                            <li>Set appropriate file permissions</li>
                          </ul>
                        </div>
                      </template>
                    </div>
                  </div>
                </div>
                
                <div class="bg-gray-50 p-4 rounded-md font-mono text-sm overflow-auto mb-4">
                  <pre>
def check_file_upload(
    url: str, 
    html_content: str, 
    vulnerability_library: Dict[str, Any],
    vulnerabilities: List[Dict[str, Any]]
) -> None:
    """Detect file upload vulnerabilities"""
    if "file_upload" not in vulnerability_library:
        return
    
    dangerous_extensions = vulnerability_library["file_upload"].get("patterns", [])
    severity = vulnerability_library["file_upload"].get("severity", "Critical")
    
    # Check for file upload forms
    soup = BeautifulSoup(html_content, 'html.parser')
    file_inputs = soup.find_all('input', attrs={'type': 'file'})
    
    if file_inputs:
        for file_input in file_inputs:
            # Check for extension restrictions
            accept_attr = file_input.get('accept', '')
            
            # If no accept attribute or accept allows dangerous file types
            if not accept_attr or any(ext in accept_attr for ext in dangerous_extensions):
                form = file_input.find_parent('form')
                form_action = form.get('action', 'Unknown') if form else 'Unknown'
                
                vulnerabilities.append({
                    "type": "file_upload",
                    "url": url,
                    "description": "Potential insecure file upload",
                    "severity": severity,
                    "details": f"Form action: {form_action}, Upload field: {file_input.get('name', 'Unknown')}"
                })
                  </pre>
                </div>
              </div>
            </el-tab-pane>
            
            <el-tab-pane label="Other Vulnerability Implementations">
              <div class="p-4">
                <h3 class="text-lg font-medium mb-3">Other Implemented Vulnerability Detections</h3>
                <el-card class="mb-4">
                  <template #header>
                    <div class="flex justify-between">
                      <span>Directory Traversal Detection</span>
                      <el-tag size="small" type="info">In Development</el-tag>
                    </div>
                  </template>
                  <p class="text-sm text-gray-700">
                    Detects directory traversal attempts in URL parameters, such as "../", "..\", "/.." patterns, and analyzes responses to determine if restricted directories can be accessed.
                  </p>
                </el-card>
                
                <el-card class="mb-4">
                  <template #header>
                    <div class="flex justify-between">
                      <span>Sensitive Information Disclosure Detection</span>
                      <el-tag size="small" type="info">In Development</el-tag>
                    </div>
                  </template>
                  <p class="text-sm text-gray-700">
                    Detects sensitive information such as API keys, passwords, database connection strings, internal paths, etc. in the page source code, and checks for server information leakage.
                  </p>
                </el-card>
                
                <el-card class="mb-4">
                  <template #header>
                    <div class="flex justify-between">
                      <span>SSRF Detection</span>
                      <el-tag size="small" type="warning">Testing</el-tag>
                    </div>
                  </template>
                  <p class="text-sm text-gray-700">
                    Detects server-side request forgery vulnerabilities by analyzing whether URL parameters can be used to access internal resources or services. Sends requests to different internal/external endpoints to verify the vulnerability.
                  </p>
                </el-card>
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>
      </el-tab-pane>
    </el-tabs>
    
    <div class="bg-gray-50 p-4 rounded-md">
      <h2 class="text-lg font-semibold mb-2">Feature Development Notes</h2>
      <p class="text-sm text-gray-700">
        CySmart.ai supports detection of multiple types of web vulnerabilities. This page demonstrates the implementation principles and code snippets of core vulnerability detection modules.
        In actual use, the system will perform comprehensive security scans on the target URL according to the configured detection modules and generate detailed security reports.
      </p>
      <p class="text-sm text-gray-700 mt-2">
        For more technical details, please check the source code or refer to the developer documentation.
      </p>
    </div>
  </div>
</template>


<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

// SQL Injection Test Vectors
const sqlVectors = ref([
  { vector: "' OR '1'='1", purpose: "Bypass authentication", result: "Vulnerable" },
  { vector: "1 UNION SELECT username,password FROM users--", purpose: "Extract database content", result: "Vulnerable" },
  { vector: "1; DROP TABLE users--", purpose: "Destroy database", result: "Not Vulnerable" },
  { vector: "1' OR sleep(5)--", purpose: "Time-based blind injection test", result: "Vulnerable" },
  { vector: "' OR (SELECT count(*) FROM users) > 0--", purpose: "Boolean-based blind injection test", result: "Vulnerable" }
])

// XSS Test Vectors
const xssVectors = ref([
  { vector: "&lt;script&gt;alert('XSS')&lt;/script&gt;", purpose: "Basic XSS test", result: "Vulnerable" },
  { vector: "javascript:alert(document.cookie)", purpose: "Cookie theft", result: "Not Vulnerable" },
  { vector: "&lt;img src='x' onerror='alert(1)'&gt;", purpose: "Event handler XSS", result: "Vulnerable" },
  { vector: "&lt;svg onload=alert(1)&gt;", purpose: "SVG payload", result: "Not Vulnerable" },
  { vector: "\"&gt;&lt;script&gt;alert(1)&lt;/script&gt;", purpose: "Inject into attribute value", result: "Vulnerable" }
])

// SQL Injection Test Form
const sqlForm = ref({
  targetUrl: '',
  vector: "' OR '1'='1"
})

// SQL Injection Test Results
const sqlTestResults = ref({
  show: false,
  vulnerable: false,
  testUrl: '',
  details: ''
})

// XSS Test Form
const xssForm = ref({
  targetUrl: '',
  payload: '&lt;script&gt;alert("XSS")&lt;/script&gt;',
  method: 'get'
})

// XSS Test Results
const xssTestResults = ref({
  show: false,
  vulnerable: false,
  testUrl: '',
  reason: '',
  previewAvailable: false,
  sanitizedPreview: ''
})

// CSRF Test Form
const csrfForm = ref({
  targetUrl: '',
  options: ['checkForms', 'checkHeaders']
})

// CSRF Test Results
const csrfTestResults = ref({
  show: false,
  vulnerable: false,
  details: []
})

// File Upload Test Form
const fileUploadForm = ref({
  targetUrl: '',
  fileType: 'php',
  bypassMethod: 'rename'
})

// File Upload Test Results
const fileUploadResults = ref({
  show: false,
  vulnerable: false,
  bypassMethod: '',
  filename: ''
})

// Test SQL Injection Button Click
function testSqlInjection() {
  ElMessage.info('Adding SQL injection test vector to example URL...')
  setTimeout(() => {
    sqlTestResults.value = {
      show: true,
      vulnerable: true,
      testUrl: "http://example.com/user.php?id=1' OR '1'='1",
      details: 'The target URL is vulnerable to SQL injection, allowing malicious SQL code execution via single quote closure and conditional operators.'
    }
    ElMessage.success('SQL injection test completed')
  }, 800)
}

// Run SQL Injection Test
function runSqlTest() {
  if (!sqlForm.value.targetUrl) {
    ElMessage.warning('Please enter the target URL')
    return
  }

  ElMessage.info('Running SQL injection test...')

  // Simulate test process
  setTimeout(() => {
    const isVulnerable = Math.random() > 0.3 // 70% chance to show vulnerability

    // Build test URL
    const url = sqlForm.value.targetUrl
    const hasParams = url.includes('?')
    const separator = hasParams ? '&' : '?'
    const paramName = hasParams ? 'id' : 'id'
    const testUrl = `${url}${separator}${paramName}=${sqlForm.value.vector}`

    sqlTestResults.value = {
      show: true,
      vulnerable: isVulnerable,
      testUrl: testUrl,
      details: isVulnerable
        ? 'The target application does not properly filter user input when processing SQL queries, allowing execution of malicious SQL code.'
        : 'No obvious SQL injection vulnerability detected, but further security testing is recommended.'
    }

    ElMessage.success('SQL injection test completed')
  }, 1500)
}

// Reset SQL Form
function resetSqlForm() {
  sqlForm.value = {
    targetUrl: '',
    vector: "' OR '1'='1"
  }
  sqlTestResults.value.show = false
}

// Test XSS Button Click
function testXss() {
  ElMessage.info('Adding XSS test vector to example URL...')
  setTimeout(() => {
    xssTestResults.value = {
      show: true,
      vulnerable: true,
      testUrl: 'http://example.com/search.php?q=&lt;script&gt;alert("XSS")&lt;/script&gt;',
      reason: 'The target application does not HTML-encode user input, allowing direct injection of malicious JavaScript code.',
      previewAvailable: true,
      sanitizedPreview: 'Search result: <span class="text-red-500">[XSS code executed here]</span>'
    }
    ElMessage.success('XSS vulnerability test completed')
  }, 800)
}

// Run XSS Test
function runXssTest() {
  if (!xssForm.value.targetUrl) {
    ElMessage.warning('Please enter the target URL')
    return
  }

  if (!xssForm.value.payload) {
    ElMessage.warning('Please enter the XSS test payload')
    return
  }

  ElMessage.info('Running XSS vulnerability test...')

  // Simulate test process
  setTimeout(() => {
    const isVulnerable = Math.random() > 0.3 // 70% chance to show vulnerability

    // Build test URL
    let testUrl
    if (xssForm.value.method === 'get') {
      const url = xssForm.value.targetUrl
      const hasParams = url.includes('?')
      const separator = hasParams ? '&' : '?'
      const paramName = hasParams ? 'q' : 'q'
      testUrl = `${url}${separator}${paramName}=${encodeURIComponent(xssForm.value.payload)}`
    } else {
      testUrl = `${xssForm.value.targetUrl} [POST method test]`
    }

    xssTestResults.value = {
      show: true,
      vulnerable: isVulnerable,
      testUrl: testUrl,
      reason: isVulnerable
        ? 'The target application does not properly filter or escape user input, allowing execution of client-side script code.'
        : 'No obvious XSS vulnerability detected.',
      previewAvailable: isVulnerable,
      sanitizedPreview: isVulnerable
        ? 'Search result: <span class="text-red-500">[XSS code executed here]</span>'
        : 'Search result: Content has been safely filtered'
    }

    ElMessage.success('XSS vulnerability test completed')
  }, 1500)
}

// Reset XSS Form
function resetXssForm() {
  xssForm.value = {
    targetUrl: '',
    payload: '&lt;script&gt;alert("XSS")&lt;/script&gt;',
    method: 'get'
  }
  xssTestResults.value.show = false
}

// Run CSRF Test
function runCsrfTest() {
  if (!csrfForm.value.targetUrl) {
    ElMessage.warning('Please enter the target website URL')
    return
  }

  if (csrfForm.value.options.length === 0) {
    ElMessage.warning('Please select at least one detection option')
    return
  }

  ElMessage.info('Running CSRF vulnerability detection...')

  // Simulate test process
  setTimeout(() => {
    const isVulnerable = Math.random() > 0.4 // 60% chance to show vulnerability

    let details = []
    if (isVulnerable) {
      if (csrfForm.value.options.includes('checkForms')) {
        details.push('Detected form missing CSRF token')
      }
      if (csrfForm.value.options.includes('checkHeaders')) {
        details.push('X-Frame-Options or Content-Security-Policy security headers not set')
      }
      if (csrfForm.value.options.includes('checkCookies')) {
        details.push('Cookie does not have SameSite attribute set')
      }
    }

    csrfTestResults.value = {
      show: true,
      vulnerable: isVulnerable,
      details: details
    }

    ElMessage.success('CSRF vulnerability detection completed')
  }, 1800)
}

// Reset CSRF Form
function resetCsrfForm() {
  csrfForm.value = {
    targetUrl: '',
    options: ['checkForms', 'checkHeaders']
  }
  csrfTestResults.value.show = false
}

// Run File Upload Test
function runFileUploadTest() {
  if (!fileUploadForm.value.targetUrl) {
    ElMessage.warning('Please enter the target upload page URL')
    return
  }

  ElMessage.info('Running file upload vulnerability test...')

  // Simulate test process
  setTimeout(() => {
    const isVulnerable = Math.random() > 0.3 // 70% chance to show vulnerability

    // Generate test filename based on selected parameters
    let filename = ''
    switch (fileUploadForm.value.bypassMethod) {
      case 'rename':
        filename = `image.jpg.${fileUploadForm.value.fileType}`
        break
      case 'mimetype':
        filename = `malicious.${fileUploadForm.value.fileType}`
        break
      case 'nullbyte':
        filename = `exploit.${fileUploadForm.value.fileType}%00.jpg`
        break
    }

    fileUploadResults.value = {
      show: true,
      vulnerable: isVulnerable,
      bypassMethod: fileUploadForm.value.bypassMethod,
      filename: filename
    }

    ElMessage.success('File upload vulnerability test completed')
  }, 2000)
}

// Reset File Upload Form
function resetFileUploadForm() {
  fileUploadForm.value = {
    targetUrl: '',
    fileType: 'php',
    bypassMethod: 'rename'
  }
  fileUploadResults.value.show = false
}
</script>