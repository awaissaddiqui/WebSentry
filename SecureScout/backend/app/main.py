from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
import json
import os
from pathlib import Path

app = FastAPI(
    title="CySmart API",
    description="Web Security Detection Tool API",
    version="1.0.0"
)

# Create an API router and add the /api prefix
api_router = APIRouter(prefix="/api")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production environments, this should be set to a specific domain name
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize data directory and files
def init_data_files():
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Initialize config file
    config_file = data_dir / "config.json"
    if not config_file.exists():
        default_config = {
            "scan_timeout": 30,
            "concurrent_scans": 5,
            "user_agent": "CySmart/1.0",
            "default_scan_modules": ["sql_injection", "xss", "csrf", "file_upload"]
        }
        with open(config_file, "w") as f:
            json.dump(default_config, f, indent=2)
    
    # Initialize scan results file
    results_file = data_dir / "scan_results.json"
    if not results_file.exists():
        with open(results_file, "w") as f:
            json.dump([], f)
    
    # Initialize vulnerability database file
    vulns_file = data_dir / "vulnerabilities.json"
    if not vulns_file.exists():
        default_vulns = {
            "sql_injection": {
                "patterns": ["'", "OR 1=1", "' OR '1'='1", "--", "/*"],
                "description": "SQL injection vulnerability allows attackers to execute malicious SQL queries",
                "severity": "High"
            },
            "xss": {
                "patterns": ["<script>", "javascript:", "onerror=", "onload="],
                "description": "Cross-site scripting vulnerability allows attackers to inject client-side scripts",
                "severity": "High"
            },
            "csrf": {
                "description": "Cross-site request forgery vulnerability allows attackers to perform actions as the victim",
                "severity": "Medium"
            },
            "file_upload": {
                "patterns": [".php", ".jsp", ".asp", ".exe"],
                "description": "Unsafe file uploads may lead to remote code execution",
                "severity": "Critical"
            }
        }
        with open(vulns_file, "w") as f:
            json.dump(default_vulns, f, indent=2)

# Initialize data files
init_data_files()

# Import and include API routes here
from app.api import scan, report, config

# Mount sub-routers to the API router
api_router.include_router(scan.router)
api_router.include_router(report.router)
api_router.include_router(config.router)

# Mount the API router to the main app
app.include_router(api_router)

@app.get("/")
async def root():
    return {"message": "Welcome to CySmart.ai Web Security Detection Tool"}