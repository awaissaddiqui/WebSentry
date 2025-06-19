# Configure logging
import logging # ← This is the missing import
from typing import Optional, List, Dict, Any
import aiohttp

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def scan_url_for_vulnerabilities(
    url: str, 
    modules: Optional[List[str]] = None,
    depth: int = 1,
    headers: Optional[Dict[str, str]] = None
) -> List[Dict[str, Any]]:
    """
    Perform a security scan on the URL to detect possible vulnerabilities
    """
    # Load default modules if not specified
    if not modules:
        config_file = Path("data/config.json")
        if config_file.exists():
            with open(config_file, "r") as f:
                config = json.load(f)
                modules = config.get("default_scan_modules", ["sql_injection", "xss", "csrf", "file_upload"])
        else:
            modules = ["sql_injection", "xss", "csrf", "file_upload"]
    
    # Load vulnerability definitions
    vulns_file = Path("data/vulnerabilities.json")
    if vulns_file.exists():
        with open(vulns_file, "r") as f:
            vulnerability_library = json.load(f)
    else:
        vulnerability_library = {}
    
    # Create request headers
    if not headers:
        headers = {
            "User-Agent": "CySmart/1.0 Security Scanner"
        }
    
    # Store scan results
    vulnerabilities = []
    
    try:
        # Use aiohttp to create a session
        async with aiohttp.ClientSession(headers=headers) as session:
            # Get initial response
            response_data = await fetch_url(session, url)
            
            if not response_data:
                return [{"type": "error", "url": url, "description": "Unable to access target URL", "severity": "medium"}]
            
            # Get all site links (for crawling)
            links = extract_links(url, response_data["text"])
            
            # Detect vulnerabilities on main page
            await detect_vulnerabilities(
                session=session,
                url=url,
                response_data=response_data,
                modules=modules,
                vulnerability_library=vulnerability_library,
                vulnerabilities=vulnerabilities
            )
            
            # If depth > 1, continue scanning linked pages
            if depth > 1 and links:
                visited = {url}
                for link in links[:min(10, len(links))]:  # Limit number of scanned links
                    if link in visited:
                        continue
                    
                    visited.add(link)
                    
                    logger.info(f"Scanning link: {link}")
                    link_response = await fetch_url(session, link)
                    
                    if link_response:
                        await detect_vulnerabilities(
                            session=session,
                            url=link,
                            response_data=link_response,
                            modules=modules,
                            vulnerability_library=vulnerability_library,
                            vulnerabilities=vulnerabilities
                        )
    
    except Exception as e:
        logger.error(f"Error during scan: {str(e)}")
        vulnerabilities.append({
            "type": "error",
            "url": url,
            "description": f"Error during scan: {str(e)}",
            "severity": "medium"
        })
    
    return vulnerabilities

async def fetch_url(session: aiohttp.ClientSession, url: str) -> Optional[Dict[str, Any]]:
    """Fetch response from a URL"""
    try:
        async with session.get(url, timeout=30) as response:
            status = response.status
            text = await response.text()
            headers = dict(response.headers)
            
            return {
                "status": status,
                "text": text,
                "headers": headers,
                "url": str(response.url)
            }
    except Exception as e:
        logger.error(f"Error fetching URL {url}: {str(e)}")
        return None

def extract_links(base_url: str, html_content: str) -> List[str]:
    """Extract links from HTML content"""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        parsed_base = urlparse(base_url)
        base_domain = parsed_base.netloc
        
        links = []
        
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            
            # Handle relative URLs
            if href.startswith('/'):
                link = urlunparse((
                    parsed_base.scheme,
                    parsed_base.netloc,
                    href,
                    '',
                    '',
                    ''
                ))
            elif href.startswith('http'):
                # Keep same-domain links only
                parsed_href = urlparse(href)
                if parsed_href.netloc != base_domain:
                    continue
                link = href
            else:
                # Handle relative paths
                link = urljoin(base_url, href)
            
            if link not in links:
                links.append(link)
        
        return links
    except Exception as e:
        logger.error(f"Error extracting links: {str(e)}")
        return []

async def detect_vulnerabilities(
    session: aiohttp.ClientSession,
    url: str,
    response_data: Dict[str, Any],
    modules: List[str],
    vulnerability_library: Dict[str, Any],
    vulnerabilities: List[Dict[str, Any]]
) -> None:
    """Detect vulnerabilities for a specific URL"""
    html_content = response_data["text"]
    headers = response_data["headers"]
    
    # Run detection logic for each module
    for module in modules:
        if module == "sql_injection":
            await check_sql_injection(session, url, vulnerability_library, vulnerabilities)
        
        elif module == "xss":
            check_xss(url, html_content, vulnerability_library, vulnerabilities)
        
        elif module == "csrf":
            check_csrf(url, html_content, headers, vulnerability_library, vulnerabilities)
        
        elif module == "file_upload":
            check_file_upload(url, html_content, vulnerability_library, vulnerabilities)

async def check_sql_injection(
    session: aiohttp.ClientSession,
    url: str, 
    vulnerability_library: Dict[str, Any],
    vulnerabilities: List[Dict[str, Any]]
) -> None:
    """Check for SQL Injection vulnerabilities"""
    if "sql_injection" not in vulnerability_library:
        return
    
    patterns = vulnerability_library["sql_injection"].get("patterns", [])
    severity = vulnerability_library["sql_injection"].get("severity", "high")
    
    parsed_url = urlparse(url)
    path = parsed_url.path
    
    # If URL already has parameters, inject test payloads
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
                            "description": "Possible SQL injection vulnerability found",
                            "severity": severity,
                            "details": f"Test pattern: {pattern}"
                        })
                        break  # Stop on first match
                except Exception as e:
                    logger.error(f"Error during SQL injection test: {str(e)}")

def check_xss(
    url: str, 
    html_content: str, 
    vulnerability_library: Dict[str, Any],
    vulnerabilities: List[Dict[str, Any]]
) -> None:
    """Check for XSS (Cross-Site Scripting) vulnerabilities"""
    if "xss" not in vulnerability_library:
        return
    
    patterns = vulnerability_library["xss"].get("patterns", [])
    severity = vulnerability_library["xss"].get("severity", "high")
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Check forms for unsafe inputs
    forms = soup.find_all('form')
    if forms:
        for form in forms:
            inputs = form.find_all('input')
            if inputs:
                for input_field in inputs:
                    if input_field.get('type') in ['text', 'search', 'url', 'tel', 'email', None]:
                        vulnerabilities.append({
                            "type": "xss",
                            "url": url,
                            "description": "Possible XSS vulnerability in form",
                            "severity": severity,
                            "details": f"Form ID: {form.get('id', 'unknown')}, Field: {input_field.get('name', 'unknown')}"
                        })
                        break
    
    # Check if URL parameters are reflected on page
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
                                "description": "URL parameter reflected on page",
                                "severity": severity,
                                "details": f"Parameter: {name}, Value: {value}"
                            })
                            break

def check_csrf(
    url: str, 
    html_content: str, 
    headers: Dict[str, str],
    vulnerability_library: Dict[str, Any],
    vulnerabilities: List[Dict[str, Any]]
) -> None:
    """Check for CSRF (Cross-Site Request Forgery) vulnerabilities"""
    if "csrf" not in vulnerability_library:
        return
    
    severity = vulnerability_library["csrf"].get("severity", "medium")
    
    soup = BeautifulSoup(html_content, 'html.parser')
    forms = soup.find_all('form', method=re.compile(r'post', re.I))
    
    for form in forms:
        has_csrf_token = False
        
        # Look for common CSRF token fields
        csrf_fields = form.find_all('input', attrs={
            'name': re.compile(r'csrf|token|nonce', re.I)
        })
        
        if csrf_fields:
            has_csrf_token = True
        
        if not has_csrf_token:
            vulnerabilities.append({
                "type": "csrf",
                "url": url,
                "description": "Form lacks CSRF protection",
                "severity": severity,
                "details": f"Form action: {form.get('action', 'unknown')}"
            })
    
    # Check for CSRF-related security headers
    has_csrf_headers = False
    for header in ['X-CSRF-Token', 'X-Frame-Options', 'Content-Security-Policy']:
        if header.lower() in [h.lower() for h in headers]:
            has_csrf_headers = True
            break
    
    if not has_csrf_headers and forms:
        vulnerabilities.append({
            "type": "csrf",
            "url": url,
            "description": "Missing HTTP security headers for CSRF protection",
            "severity": severity,
            "details": "Missing X-CSRF-Token, X-Frame-Options, or Content-Security-Policy headers"
        })

def check_file_upload(
    url: str, 
    html_content: str, 
    vulnerability_library: Dict[str, Any],
    vulnerabilities: List[Dict[str, Any]]
) -> None:
    """Check for insecure file upload vulnerabilities"""
    if "file_upload" not in vulnerability_library:
        return
    
    dangerous_extensions = vulnerability_library["file_upload"].get("patterns", [])
    severity = vulnerability_library["file_upload"].get("severity", "critical")
    
    soup = BeautifulSoup(html_content, 'html.parser')
    file_inputs = soup.find_all('input', attrs={'type': 'file'})
    
    if file_inputs:
        for file_input in file_inputs:
            accept_attr = file_input.get('accept', '')
            
            if not accept_attr or any(ext in accept_attr for ext in dangerous_extensions):
                form = file_input.find_parent('form')
                form_action = form.get('action', 'unknown') if form else 'unknown'
                
                vulnerabilities.append({
                    "type": "file_upload",
                    "url": url,
                    "description": "Potentially unsafe file upload",
                    "severity": severity,
                    "details": f"Form action: {form_action}, Field: {file_input.get('name', 'unknown')}"
                })
