import uvicorn
import os
from pathlib import Path

if __name__ == "__main__":
    # Make sure you are in the correct working directory and run
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    #  Create data directory
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Start the FastAPI application
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 