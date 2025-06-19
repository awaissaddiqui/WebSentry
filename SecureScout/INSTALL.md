# CySmart.ai Installation Guide

This document provides detailed instructions for installing and deploying CySmart.ai.

## System Requirements

- Operating System: Windows 10/11, macOS, or Linux
- Python 3.8+
- Node.js 16+
- npm 8+
- At least 2GB available memory
- At least 1GB available disk space

## Installation Steps

### 1. Install Python Dependencies

First, make sure you have Python 3.8 or higher installed. You can check with the following commands:

```bash
python --version
# or
python3 --version
```

Then, install the backend dependencies:

```bash
cd backend
pip install -r requirements.txt
```

### 2. Install Node.js Dependencies

Make sure Node.js 16+ and npm 8+ are installed. You can check with:

```bash
node --version
npm --version
```

Then, install the frontend dependencies:

```bash
cd frontend
npm install
```

## Running the Application

### Windows Users

For Windows users, the easiest way is to double-click the `start.bat` file in the project root directory. This will start both the frontend and backend services.

### macOS/Linux Users

For macOS or Linux users, you need to start the backend and frontend services in two separate terminals.

1. Start the backend service:

```bash
cd backend
python run.py
```

2. Start the frontend service:

```bash
cd frontend
npm run dev
```

### Accessing the Application

Once started successfully, you can access the following addresses in your browser:

- Frontend UI: http://localhost:3000
- Backend API: http://localhost:8000

## Production Deployment

For production environments, we recommend the following adjustments:

### Frontend Deployment

Build the frontend for production:

```bash
cd frontend
npm run build
```

After building, the files in the `dist` directory can be hosted on any static file server (such as Nginx, Apache, etc.).

### Backend Deployment

For the backend, it is recommended to use Gunicorn with Uvicorn as the production server:

1. Install Gunicorn:

```bash
pip install gunicorn
```

2. Start the service:

```bash
cd backend
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
```

### Security Configuration

In production, be sure to make the following security adjustments:

1. In `main.py`, modify the CORS settings to only allow specific domains:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

2. Use a reverse proxy (such as Nginx) and configure HTTPS

## FAQ

### Port Occupied

If a port is already in use, you can modify the port settings in the relevant configuration files:

- Frontend: Change `server.port` in `frontend/vite.config.js`
- Backend: Change the `port` parameter in `backend/run.py`

### Dependency Installation Failure

If you encounter issues during dependency installation:

1. Try using a mirror source:
   - pip: `pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`
   - npm: `npm install --registry=https://registry.npmmirror.com`

2. Make sure your Python and Node.js versions meet the requirements

### Data Storage Path

By default, all data is stored in the `backend/data` directory. If you need to change the storage location, modify the relevant configuration in `backend/app/main.py`.

## Support & Contact

If you encounter any issues during installation or use, please get support via:

- Submit an Issue on the GitHub repository
- Email support@CySmart.ai.example.com (example email, please replace with actual contact)