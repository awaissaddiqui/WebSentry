from fastapi import APIRouter, HTTPException
from typing import List, Optional
import json
from pathlib import Path
from datetime import datetime, timedelta

router = APIRouter(
    prefix="/report",
    tags=["report"],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
async def get_all_reports():
    """
    Retrieve all scan reports
    """
    results_file = Path("data/scan_results.json")
    if not results_file.exists():
        return []
    
    with open(results_file, "r") as f:
        scan_results = json.load(f)
    
    return scan_results

@router.get("/{scan_id}")
async def get_report(scan_id: str):
    """
    Retrieve a scan report by specific ID
    """
    results_file = Path("data/scan_results.json")
    if not results_file.exists():
        raise HTTPException(status_code=404, detail="Scan record does not exist")
    
    with open(results_file, "r") as f:
        scan_results = json.load(f)
    
    for result in scan_results:
        if result.get("id") == scan_id:
            return result
    
    raise HTTPException(status_code=404, detail="Scan ID does not exist")

@router.get("/summary/recent")
async def get_recent_summary(days: Optional[int] = 7):
    """
    Get scan summary statistics for recent days
    """
    results_file = Path("data/scan_results.json")
    if not results_file.exists():
        return {
            "total_scans": 0,
            "completed": 0,
            "failed": 0,
            "vulnerability_summary": {},
            "severity_counts": {
                "Low": 0,
                "Medium": 0,
                "High": 0,
                "Critical": 0
            }
        }
    
    with open(results_file, "r") as f:
        scan_results = json.load(f)
    
    # Set the time range
    cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
    
    # Filter recent scans
    recent_scans = [
        scan for scan in scan_results 
        if scan.get("start_time", "0") > cutoff_date
    ]
    
    # Initialize statistics
    summary = {
        "total_scans": len(recent_scans),
        "completed": len([s for s in recent_scans if s.get("status") == "completed"]),
        "failed": len([s for s in recent_scans if s.get("status") == "failed"]),
        "vulnerability_summary": {},
        "severity_counts": {
            "Low": 0,
            "Medium": 0,
            "High": 0,
            "Critical": 0
        }
    }
    
    # Count vulnerability types and severity levels
    for scan in recent_scans:
        if scan.get("status") != "completed":
            continue
            
        vulnerabilities = scan.get("vulnerabilities", [])
        for vuln in vulnerabilities:
            vuln_type = vuln.get("type", "Other")
            severity = vuln.get("severity", "Medium")
            
            # Update vulnerability type counts
            if vuln_type in summary["vulnerability_summary"]:
                summary["vulnerability_summary"][vuln_type] += 1
            else:
                summary["vulnerability_summary"][vuln_type] = 1
            
            # Update severity level counts
            if severity in summary["severity_counts"]:
                summary["severity_counts"][severity] += 1
    
    return summary

@router.delete("/{scan_id}")
async def delete_report(scan_id: str):
    """
    Delete a scan report by specific ID
    """
    results_file = Path("data/scan_results.json")
    if not results_file.exists():
        raise HTTPException(status_code=404, detail="Scan record does not exist")
    
    with open(results_file, "r") as f:
        scan_results = json.load(f)
    
    filtered_results = [result for result in scan_results if result.get("id") != scan_id]
    
    if len(filtered_results) == len(scan_results):
        raise HTTPException(status_code=404, detail="Scan ID does not exist")
    
    with open(results_file, "w") as f:
        json.dump(filtered_results, f, indent=2)
    
    return {"message": "Scan report deleted successfully"}

@router.get("/stats/vulnerability_types")
async def get_vulnerability_types_stats():
    """
    Get statistics of vulnerability types
    """
    results_file = Path("data/scan_results.json")
    if not results_file.exists():
        return {}
    
    with open(results_file, "r") as f:
        scan_results = json.load(f)
    
    vulnerability_counts = {}
    
    for scan in scan_results:
        if scan.get("status") != "completed":
            continue
            
        vulnerabilities = scan.get("vulnerabilities", [])
        for vuln in vulnerabilities:
            vuln_type = vuln.get("type", "Other")
            
            if vuln_type in vulnerability_counts:
                vulnerability_counts[vuln_type] += 1
            else:
                vulnerability_counts[vuln_type] = 1
    
    return vulnerability_counts
