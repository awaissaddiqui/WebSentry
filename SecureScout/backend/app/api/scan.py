from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
import json
import uuid
from datetime import datetime
from pathlib import Path
import asyncio
import aiohttp
import re
from app.core.scanner import scan_url_for_vulnerabilities

router = APIRouter(
    prefix="/scan",
    tags=["scan"],
    responses={404: {"description": "Not found"}},
)

class ScanRequest(BaseModel):
    url: HttpUrl
    modules: Optional[List[str]] = None
    depth: Optional[int] = 1
    headers: Optional[dict] = None

class BatchScanRequest(BaseModel):
    urls: List[HttpUrl]
    modules: Optional[List[str]] = None
    depth: Optional[int] = 1
    headers: Optional[dict] = None

class ScanResponse(BaseModel):
    scan_id: str
    status: str
    message: str

# Dictionary to keep track of all active scans
active_scans = {}

@router.post("/start", response_model=ScanResponse)
async def start_scan(scan_request: ScanRequest, background_tasks: BackgroundTasks):
    """
    Start a security scan for a single URL
    """
    # Generate a unique scan ID
    scan_id = str(uuid.uuid4())

    # Initialize scan status
    scan_status = {
        "id": scan_id,
        "url": str(scan_request.url),
        "status": "pending",
        "start_time": datetime.now().isoformat(),
        "end_time": None,
        "vulnerabilities": [],
        "modules": scan_request.modules
    }

    # Save to active scans
    active_scans[scan_id] = scan_status

    # Run scan in background
    background_tasks.add_task(
        run_scan, 
        scan_id=scan_id,
        url=str(scan_request.url),
        modules=scan_request.modules,
        depth=scan_request.depth,
        headers=scan_request.headers
    )

    return ScanResponse(
        scan_id=scan_id,
        status="started",
        message="Scan has started"
    )

@router.post("/batch", response_model=List[ScanResponse])
async def batch_scan(batch_request: BatchScanRequest, background_tasks: BackgroundTasks):
    """
    Start security scans for multiple URLs in batch
    """
    responses = []

    for url in batch_request.urls:
        scan_id = str(uuid.uuid4())

        scan_status = {
            "id": scan_id,
            "url": str(url),
            "status": "pending",
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "vulnerabilities": [],
            "modules": batch_request.modules
        }

        active_scans[scan_id] = scan_status

        background_tasks.add_task(
            run_scan, 
            scan_id=scan_id,
            url=str(url),
            modules=batch_request.modules,
            depth=batch_request.depth,
            headers=batch_request.headers
        )

        responses.append(
            ScanResponse(
                scan_id=scan_id,
                status="started",
                message="Scan has started"
            )
        )

    return responses

@router.get("/status/{scan_id}")
async def get_scan_status(scan_id: str):
    """
    Get the current status of a scan by ID
    """
    if scan_id in active_scans:
        return active_scans[scan_id]

    # If not in active scans, check completed scans
    results_file = Path("data/scan_results.json")
    if results_file.exists():
        with open(results_file, "r") as f:
            scan_results = json.load(f)
            for result in scan_results:
                if result.get("id") == scan_id:
                    return result

    raise HTTPException(status_code=404, detail="Scan ID not found")

@router.get("/active")
async def list_active_scans():
    """
    List all currently active scans
    """
    return list(active_scans.values())

async def run_scan(scan_id: str, url: str, modules: Optional[List[str]], depth: int, headers: Optional[dict]):
    """
    Asynchronously execute the scan process
    """
    # Update status to in progress
    active_scans[scan_id]["status"] = "in_progress"

    try:
        # Perform the actual scan
        vulnerabilities = await scan_url_for_vulnerabilities(url, modules, depth, headers)

        # Update scan result
        active_scans[scan_id]["vulnerabilities"] = vulnerabilities
        active_scans[scan_id]["status"] = "completed"
        active_scans[scan_id]["end_time"] = datetime.now().isoformat()

        # Save to history
        save_scan_result(active_scans[scan_id])

    except Exception as e:
        active_scans[scan_id]["status"] = "failed"
        active_scans[scan_id]["error"] = str(e)
        active_scans[scan_id]["end_time"] = datetime.now().isoformat()
        save_scan_result(active_scans[scan_id])

    # Remove from active scans
    active_scans.pop(scan_id, None)

def save_scan_result(scan_result):
    """
    Save scan result to JSON file
    """
    results_file = Path("data/scan_results.json")

    try:
        with open(results_file, "r") as f:
            scan_results = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        scan_results = []

    scan_results.append(scan_result)

    with open(results_file, "w") as f:
        json.dump(scan_results, f, indent=2)
