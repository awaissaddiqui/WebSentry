<template>
  <div class="sql-injection-guidance">
    <div class="mb-4">
      <h4 class="text-lg font-medium mb-2">SQL Injection Vulnerability Explained</h4>
      <p class="text-sm text-gray-700 mb-3">
        SQL injection is a code injection technique where attackers can insert malicious SQL statements into application inputs to affect the execution of database queries. Successful attacks may result in unauthorized access, data leakage, or database destruction.
      </p>
    </div>
    
    <el-collapse accordion class="mb-4">
      <el-collapse-item title="Attack Examples">
        <div class="bg-gray-50 p-3 rounded mb-2 font-mono text-sm overflow-auto">
          <p class="mb-1"># Common SQL injection attack examples:</p>
          <p class="mb-1">1. Basic injection: <code>' OR '1'='1</code></p>
          <p class="mb-1">2. Union query: <code>' UNION SELECT username,password FROM users--</code></p>
          <p class="mb-1">3. Blind injection: <code>' OR (SELECT SUBSTRING(username,1,1) FROM users WHERE id=1)='a</code></p>
          <p class="mb-1">4. Time-based blind injection: <code>' OR IF(SUBSTRING(username,1,1)='a',SLEEP(5),0)--</code></p>
          <p class="mb-1">5. Stacked queries: <code>'; DROP TABLE users; --</code></p>
        </div>
      </el-collapse-item>
      
      <el-collapse-item title="Vulnerable Code Example">
        <div class="bg-gray-50 p-3 rounded mb-2 font-mono text-sm overflow-auto">
          <p class="text-red-500 mb-2">❌ Insecure code:</p>
          <pre>
// PHP Example
$username = $_POST['username'];
$query = "SELECT * FROM users WHERE username = '$username'";
$result = mysqli_query($connection, $query);

// Node.js Example
const username = req.body.username;
const query = `SELECT * FROM users WHERE username = '${username}'`;
db.query(query, (err, result) => {
  // Handle result
});
          </pre>
        </div>
      </el-collapse-item>
    </el-collapse>
    
    <div class="mb-4">
      <h4 class="text-lg font-medium mb-2">Remediation Solutions</h4>
      
      <div class="security-solution mb-3">
        <div class="solution-title text-md font-medium text-green-700 mb-1">1. Use Parameterized Queries (Prepared Statements)</div>
        <p class="text-sm text-gray-700 mb-2">
          Parameterized queries ensure user input is strictly treated as data, not code, and are the most effective way to prevent SQL injection.
        </p>
        <div class="bg-green-50 p-3 rounded mb-2 font-mono text-sm overflow-auto">
          <p class="text-green-600 mb-2">✅ Secure code:</p>
          <pre>
// PHP Example
$stmt = $connection->prepare("SELECT * FROM users WHERE username = ?");
$stmt->bind_param("s", $username);
$stmt->execute();
$result = $stmt->get_result();

// Node.js Example
const query = "SELECT * FROM users WHERE username = ?";
db.query(query, [username], (err, result) => {
  // Handle result
});
          </pre>
        </div>
      </div>
      
      <div class="security-solution mb-3">
        <div class="solution-title text-md font-medium text-green-700 mb-1">2. Use ORM Frameworks</div>
        <p class="text-sm text-gray-700 mb-2">
          ORM frameworks usually have built-in parameterized queries, which can effectively prevent SQL injection.
        </p>
        <div class="bg-green-50 p-3 rounded mb-2 font-mono text-sm overflow-auto">
          <p class="text-green-600 mb-2">✅ Secure code:</p>
          <pre>
// Sequelize (Node.js) Example
User.findOne({
  where: { username: username }
}).then(user => {
  // Handle result
});

// Django (Python) Example
user = User.objects.get(username=username)
          </pre>
        </div>
      </div>
      
      <div class="security-solution mb-3">
        <div class="solution-title text-md font-medium text-green-700 mb-1">3. Input Validation and Sanitization</div>
        <p class="text-sm text-gray-700 mb-2">
          While not the primary defense, input validation can be part of a defense-in-depth strategy.
        </p>
        <div class="bg-green-50 p-3 rounded mb-2 font-mono text-sm overflow-auto">
          <p class="text-green-600 mb-2">✅ Validation example:</p>
          <pre>
// JavaScript validation example
function isValidUsername(username) {
  // Only allow letters and numbers
  return /^[A-Za-z0-9]+$/.test(username);
}

if (!isValidUsername(username)) {
  return res.status(400).json({ error: "Invalid username" });
}
          </pre>
        </div>
      </div>
      
      <div class="security-solution mb-3">
        <div class="solution-title text-md font-medium text-green-700 mb-1">4. Principle of Least Privilege</div>
        <p class="text-sm text-gray-700">
          Restrict database user permissions to ensure the application only has the minimum permissions required. This way, even if SQL injection occurs, attackers cannot perform dangerous operations.
        </p>
      </div>
    </div>
    
    <div class="mb-4">
      <h4 class="text-lg font-medium mb-2">Defense-in-Depth Strategies</h4>
      <ul class="list-disc pl-5 text-sm text-gray-700 space-y-1">
        <li>Implement a Web Application Firewall (WAF) to detect and block SQL injection attempts</li>
        <li>Conduct regular security audits and vulnerability scans</li>
        <li>Handle error messages properly to avoid leaking database structure information</li>
        <li>Use SQL injection detection tools such as SQLMap for regular testing</li>
        <li>Provide security training for developers to raise secure coding awareness</li>
      </ul>
    </div>
    
    <div class="p-3 bg-blue-50 rounded-md text-sm text-blue-800">
      <div class="font-medium mb-1">Real-time Detection Advice:</div>
      <p>
        In addition to the above remediation solutions, it is recommended to implement real-time detection mechanisms in your application to monitor suspicious SQL queries and log potential injection attempts, so you can quickly detect and respond to security incidents.
      </p>
    </div>
  </div>
</template>

<script setup>
// No additional logic required
</script>

<style scoped>
.sql-injection-guidance {
  width: 100%;
}
</style>