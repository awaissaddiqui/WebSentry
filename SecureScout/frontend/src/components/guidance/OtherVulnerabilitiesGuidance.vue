<template>
  <div class="other-vulnerabilities-guidance">
    <el-tabs>
      <el-tab-pane label="CSRF Vulnerability">
        <div class="mb-4">
          <h4 class="text-lg font-medium mb-2">CSRF (Cross-Site Request Forgery) Vulnerability</h4>
          <p class="text-sm text-gray-700 mb-3">
            Cross-site request forgery (CSRF) attacks exploit a user's existing credentials, causing them to perform unintended actions without their knowledge. Attackers trick users into visiting a page containing malicious requests, causing the browser to automatically send requests to the target site and perform actions.
          </p>
          
          <div class="bg-amber-50 p-3 rounded-md mb-4">
            <h5 class="font-medium mb-2">CSRF Attack Example</h5>
            <p class="text-sm mb-2">Suppose a banking site performs a transfer operation via a GET request:</p>
            <code class="text-red-500 text-sm">https://bank.com/transfer?to=attacker&amount=1000</code>
            <p class="text-sm mt-2">An attacker can create the following HTML page and trick the victim into visiting it:</p>
            <pre class="bg-gray-100 p-2 text-sm mt-1">
&lt;html&gt;
  &lt;body&gt;
    &lt;img src="https://bank.com/transfer?to=attacker&amount=1000" width="0" height="0" /&gt;
    &lt;h1&gt;Congratulations!&lt;/h1&gt;
    &lt;p&gt;You have won a prize!&lt;/p&gt;
  &lt;/body&gt;
&lt;/html&gt;
            </pre>
          </div>
          
          <h5 class="font-medium mb-2">Remediation Solutions</h5>
          <div class="security-solution mb-3">
            <div class="solution-title text-md font-medium text-green-700 mb-1">1. Use CSRF Tokens</div>
            <p class="text-sm text-gray-700 mb-2">
              Embed a randomly generated token in the form. The server verifies the token to ensure the request comes from a legitimate source.
            </p>
            <div class="bg-green-50 p-3 rounded mb-2 font-mono text-sm overflow-auto">
              <p class="text-green-600 mb-2">✅ Example Implementation:</p>
              <pre>
// Server-side (Node.js/Express)
const csrf = require('csurf');
const csrfProtection = csrf({ cookie: true });

app.get('/form', csrfProtection, (req, res) => {
  // Pass CSRF token to the view
  res.render('form', { csrfToken: req.csrfToken() });
});

app.post('/process', csrfProtection, (req, res) => {
  // CSRF token is automatically validated
  // Handle form submission...
});

// Frontend template
&lt;form action="/process" method="post"&gt;
  &lt;input type="hidden" name="_csrf" value="{{ csrfToken }}"&gt;
  &lt;!-- Other form fields --&gt;
  &lt;button type="submit"&gt;Submit&lt;/button&gt;
&lt;/form&gt;
              </pre>
            </div>
          </div>
          
          <div class="security-solution mb-3">
            <div class="solution-title text-md font-medium text-green-700 mb-1">2. Use SameSite Cookie Attribute</div>
            <p class="text-sm text-gray-700 mb-2">
              Setting the SameSite attribute on cookies restricts cookies from being sent in cross-site requests, effectively preventing CSRF attacks.
            </p>
            <div class="bg-green-50 p-3 rounded mb-2 font-mono text-sm overflow-auto">
              <p class="text-green-600 mb-2">✅ Example Implementation:</p>
              <pre>
// Node.js/Express
res.cookie('sessionId', 'abc123', {
  httpOnly: true,
  secure: true,
  sameSite: 'strict' // or 'lax'
});

// PHP
setcookie('sessionId', 'abc123', [
  'httponly' => true,
  'secure' => true,
  'samesite' => 'Strict'
]);
              </pre>
            </div>
          </div>
          
          <div class="security-solution mb-3">
            <div class="solution-title text-md font-medium text-green-700 mb-1">3. Check the Referer Header</div>
            <p class="text-sm text-gray-700 mb-2">
              Validate the Referer header to ensure requests originate from the same site as an auxiliary CSRF protection measure.
            </p>
            <div class="bg-green-50 p-3 rounded mb-2 font-mono text-sm overflow-auto">
              <pre>
// Node.js/Express
app.post('/api/action', (req, res) => {
  const referer = req.headers.referer || req.headers.referrer;
  
  if (!referer || !referer.startsWith('https://yourdomain.com')) {
    return res.status(403).json({ error: 'Possible CSRF attack' });
  }
  
  // Handle request...
});
              </pre>
            </div>
          </div>
          
          <div class="security-solution mb-3">
            <div class="solution-title text-md font-medium text-green-700 mb-1">4. Require Re-authentication for Sensitive Actions</div>
            <p class="text-sm text-gray-700">
              For sensitive actions (such as changing passwords or transferring funds), require the user to provide their current password or another verification method for re-authentication.
            </p>
          </div>
          
          <div class="p-3 bg-blue-50 rounded-md text-sm text-blue-800 mt-4">
            <div class="font-medium mb-1">Best Practices:</div>
            <p>
              Use a multi-layered defense strategy: combine CSRF tokens and the SameSite cookie attribute. Ensure all state-changing operations use POST requests instead of GET, and add extra verification steps for sensitive actions.
            </p>
          </div>
        </div>
      </el-tab-pane>
      
      <el-tab-pane label="File Upload Vulnerability">
        <div class="mb-4">
          <h4 class="text-lg font-medium mb-2">File Upload Vulnerability</h4>
          <p class="text-sm text-gray-700 mb-3">
            File upload vulnerabilities allow attackers to upload malicious files to the server, potentially leading to remote code execution, privilege escalation, or sensitive information leakage. These vulnerabilities occur when applications fail to properly validate and handle uploaded files.
          </p>
          
          <div class="bg-amber-50 p-3 rounded-md mb-4">
            <h5 class="font-medium mb-2">Common Attack Scenarios</h5>
            <ul class="list-disc pl-5 text-sm">
              <li>Uploading executable script files (PHP, JSP, ASP) to execute malicious code</li>
              <li>Uploading Office documents containing malicious macros</li>
              <li>Uploading malformed image files to exploit vulnerabilities in image processing libraries</li>
              <li>Path traversal attacks via file name manipulation</li>
              <li>Uploading oversized files to exhaust server resources</li>
            </ul>
          </div>
          
          <h5 class="font-medium mb-2">Remediation Solutions</h5>
          
          <div class="security-solution mb-3">
            <div class="solution-title text-md font-medium text-green-700 mb-1">1. File Type Validation</div>
            <p class="text-sm text-gray-700 mb-2">
              Validate the file type and content, not just the file extension.
            </p>
            <div class="bg-green-50 p-3 rounded mb-2 font-mono text-sm overflow-auto">
              <p class="text-green-600 mb-2">✅ Example Implementation:</p>
              <pre>
// Node.js using file-type and multer
const multer = require('multer');
const fileType = require('file-type');
const fs = require('fs');

// Set up file upload
const upload = multer({
  dest: 'uploads/',
  limits: { fileSize: 5 * 1024 * 1024 } // 5MB limit
});

app.post('/upload', upload.single('file'), async (req, res) => {
  try {
    // Check MIME type
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif'];
    if (!allowedTypes.includes(req.file.mimetype)) {
      // Delete disallowed file
      fs.unlinkSync(req.file.path);
      return res.status(400).json({ error: 'Unsupported file type' });
    }
    
    // Validate file type by content
    const buffer = fs.readFileSync(req.file.path);
    const fileInfo = await fileType.fromBuffer(buffer);
    
    if (!fileInfo || !allowedTypes.includes(fileInfo.mime)) {
      // Delete mismatched file
      fs.unlinkSync(req.file.path);
      return res.status(400).json({ error: 'File content does not match declared type' });
    }
    
    // Handle valid file...
    
  } catch (error) {
    return res.status(500).json({ error: 'Upload processing failed' });
  }
});
              </pre>
            </div>
          </div>
          
          <div class="security-solution mb-3">
            <div class="solution-title text-md font-medium text-green-700 mb-1">2. Secure File Storage</div>
            <p class="text-sm text-gray-700 mb-2">
              Use secure storage locations and file naming strategies to prevent path traversal and file overwrite attacks.
            </p>
            <div class="bg-green-50 p-3 rounded mb-2 font-mono text-sm overflow-auto">
              <pre>
// Secure file naming
const path = require('path');
const crypto = require('crypto');

function generateSafeFilename(originalName) {
  // Generate random file name
  const randomName = crypto.randomBytes(16).toString('hex');
  // Keep original extension, but ensure it's safe
  const ext = path.extname(originalName).toLowerCase();
  const safeExt = ['.jpg', '.jpeg', '.png', '.gif'].includes(ext) ? ext : '.bin';
  
  return `${randomName}${safeExt}`;
}

// Store outside the web root
const uploadDir = path.join(__dirname, '../secure-uploads');
              </pre>
            </div>
          </div>
          
          <div class="security-solution mb-3">
            <div class="solution-title text-md font-medium text-green-700 mb-1">3. Image Processing and Content Validation</div>
            <p class="text-sm text-gray-700 mb-2">
              Process uploaded images to ensure they are valid image files.
            </p>
            <div class="bg-green-50 p-3 rounded mb-2 font-mono text-sm overflow-auto">
              <pre>
// Node.js using Sharp for image processing
const sharp = require('sharp');

app.post('/upload-image', upload.single('image'), async (req, res) => {
  try {
    // Try to read and process the image - this validates it's a real image
    const image = await sharp(req.file.path)
      .metadata();
    
    // Re-process image to discard any non-image data
    await sharp(req.file.path)
      .resize(800, 600, { fit: 'inside' })
      .jpeg({ quality: 85 })
      .toFile(path.join(uploadDir, `processed-${req.file.filename}.jpg`));
    
    // Delete original upload
    fs.unlinkSync(req.file.path);
    
    // Return success
    return res.json({ success: true });
  } catch (error) {
    // If image processing fails, it's not a valid image
    if (req.file) {
      fs.unlinkSync(req.file.path);
    }
    return res.status(400).json({ error: 'Invalid image file' });
  }
});
              </pre>
            </div>
          </div>
          
          <div class="security-solution mb-3">
            <div class="solution-title text-md font-medium text-green-700 mb-1">4. Serve User Uploads from a Separate Domain</div>
            <p class="text-sm text-gray-700">
              Place user-uploaded content on a separate domain or subdomain to reduce the risk of XSS and other attacks.
            </p>
          </div>
          
          <div class="p-3 bg-blue-50 rounded-md text-sm text-blue-800 mt-4">
            <div class="font-medium mb-1">Security Advice:</div>
            <p>
              Enforce file upload restrictions (type, size, frequency), scan uploaded files with antivirus software, prohibit execution of uploaded files, and regularly audit upload directories. Consider using third-party storage services (such as AWS S3) to handle file uploads and leverage their built-in security features.
            </p>
          </div>
        </div>
      </el-tab-pane>
      
      <el-tab-pane label="Other Common Vulnerabilities">
        <div class="mb-4">
          <h4 class="text-lg font-medium mb-2">Other Common Web Application Vulnerabilities</h4>
          
          <el-collapse accordion>
            <el-collapse-item title="1. Sensitive Data Exposure">
              <div class="p-3">
                <p class="mb-2">Sensitive data exposure occurs when an application fails to properly protect sensitive information (such as passwords, credit card numbers, or personal identity information).</p>
                <h5 class="font-medium mt-3 mb-1">Remediation Solutions:</h5>
                <ul class="list-disc pl-5 text-sm text-gray-700">
                  <li>Use HTTPS to encrypt data in transit</li>
                  <li>Use strong encryption algorithms for sensitive data</li>
                  <li>Implement good key management</li>
                  <li>Disable browser caching of sensitive data</li>
                  <li>Do not store sensitive information in logs</li>
                </ul>
              </div>
            </el-collapse-item>
            
            <el-collapse-item title="2. Security Misconfiguration">
              <div class="p-3">
                <p class="mb-2">Security misconfiguration includes issues such as using default configurations, enabling unnecessary services, and error handling that leaks information.</p>
                <h5 class="font-medium mt-3 mb-1">Remediation Solutions:</h5>
                <ul class="list-disc pl-5 text-sm text-gray-700">
                  <li>Establish and follow security configuration standards</li>
                  <li>Remove or disable unnecessary features and services</li>
                  <li>Regularly update and patch systems</li>
                  <li>Implement security headers and protections</li>
                  <li>Conduct regular security scans and penetration tests</li>
                </ul>
              </div>
            </el-collapse-item>
            
            <el-collapse-item title="3. Insecure Deserialization">
              <div class="p-3">
                <p class="mb-2">Insecure deserialization can lead to remote code execution when an application deserializes untrusted data.</p>
                <h5 class="font-medium mt-3 mb-1">Remediation Solutions:</h5>
                <ul class="list-disc pl-5 text-sm text-gray-700">
                  <li>Do not accept serialized objects from untrusted sources</li>
                  <li>Use integrity checks to ensure data has not been tampered with</li>
                  <li>Monitor deserialization and log exceptions</li>
                  <li>Use simple data formats like JSON instead of complex object serialization</li>
                </ul>
                <div class="bg-green-50 p-3 rounded mt-2 font-mono text-sm overflow-auto">
                  <p class="text-green-600 mb-2">✅ Security Practice:</p>
                  <pre>
// Use JSON instead of serialized objects
// Insecure
const data = deserialize(userInput);

// More secure
try {
  const data = JSON.parse(userInput);
  // Validate data format
  validateDataSchema(data);
} catch (error) {
  // Handle exception
}
                  </pre>
                </div>
              </div>
            </el-collapse-item>
            
            <el-collapse-item title="4. XML External Entity (XXE) Attack">
              <div class="p-3">
                <p class="mb-2">When an application parses XML input and is misconfigured, attackers can use XML external entity references to access server files or perform server-side request forgery.</p>
                <h5 class="font-medium mt-3 mb-1">Remediation Solutions:</h5>
                <ul class="list-disc pl-5 text-sm text-gray-700">
                  <li>Disable external entities and DTD processing in XML parsers</li>
                  <li>Upgrade XML parsing libraries to the latest version</li>
                  <li>Use simpler data formats like JSON</li>
                  <li>Input validation and filtering</li>
                </ul>
                <div class="bg-green-50 p-3 rounded mt-2 font-mono text-sm overflow-auto">
                  <p class="text-green-600 mb-2">✅ Secure Configuration:</p>
                  <pre>
// Node.js using libxmljs secure configuration
const libxmljs = require('libxmljs');

// Secure configuration
const xmlParseOptions = {
  noent: false,      // Disable external entities
  dtdload: false,    // Do not load external DTD
  dtdvalid: false    // Do not validate DTD
};

try {
  const xmlDoc = libxmljs.parseXml(xmlString, xmlParseOptions);
  // Handle XML...
} catch (error) {
  // Handle exception
}
                  </pre>
                </div>
              </div>
            </el-collapse-item>
          </el-collapse>
          
          <div class="p-3 bg-blue-50 rounded-md text-sm text-blue-800 mt-4">
            <div class="font-medium mb-1">Comprehensive Security Advice:</div>
            <p>
              Establish a secure development lifecycle (SDL), conduct regular security training, implement multi-layered defense strategies, set up appropriate security monitoring and logging, and keep systems and libraries up to date. Remember, security is an ongoing process, not a one-time task.
            </p>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
// No additional logic required
</script>

<style scoped>
.other-vulnerabilities-guidance {
  width: 100%;
}
</style>