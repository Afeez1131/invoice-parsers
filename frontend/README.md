# Invoice Parser API - Frontend Setup

This is the frontend interface for the Invoice Parser API, built with React.

## Prerequisites

Before you begin, ensure you have:
- **Node.js** (version 18 or higher recommended)
- **npm** (comes with Node.js) or **yarn**
- Backend API running (see [Backend Setup](#backend-setup))

## Installation Steps

### Step 1: Clone and Navigate
```bash
# Clone the repository (if not already done)
git clone https://github.com/Afeez1131/invoice-parsers.git

cd invoice-parsers/frontend/invoice-parser
```

### Step 2: Install Dependencies
Choose **ONE** of these installation methods:

#### **Recommended Method** (if facing peer dependency conflicts):
```bash
npm install --legacy-peer-deps
```
*Use this if you encounter version conflicts during installation.*

#### **Standard Method** (try this first):
```bash
npm install
```

### Step 3: Start Development Server
```bash
npm run dev
```
The application will start and typically be available at `http://localhost:5173` (or another port if specified).

## Troubleshooting Installation Issues

### Common Issues and Solutions:

1. **"npm install" fails with peer dependency conflicts**
   ```bash
   # Clear npm cache and retry
   npm cache clean --force
   npm install --legacy-peer-deps
   ```

2. **"npm run dev" not working after install**
   ```bash
   # Delete node_modules and package-lock.json, then reinstall
   rm -rf node_modules package-lock.json
   npm install --legacy-peer-deps
   ```

3. **Port already in use**
   ```bash
   # Check what's running on the port
   lsof -i :5173  # macOS/Linux
   # or
   netstat -ano | findstr :5173  # Windows
   
   # Kill the process or use a different port
   npm run dev -- --port 3000
   ```

### Complete Clean Install Process
If you're starting fresh or facing persistent issues:
```bash
# 1. Remove existing dependencies
rm -rf node_modules package-lock.json

# 2. Clear npm cache
npm cache clean --force

# 3. Install with legacy peer deps (most reliable)
npm install --legacy-peer-deps

# 4. Start the dev server
npm run dev
```

## Environment Configuration

Create a `.env` file in the root directory:
```env
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=Invoice Parser
```

**Important**: Ensure the backend API is running at the URL specified in `VITE_API_URL`.

## Connecting to Backend

The frontend expects the Invoice Parser API to be running. To start the backend:

1. **Navigate to backend directory** (if separate):
   ```bash
   cd ../invoice-parser-api
   ```

2. **Start backend server**:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Verify both are running**:
   - Frontend: `http://localhost:5173`
   - Backend: `http://localhost:8000`
   - Backend docs: `http://localhost:8000/docs`

## Notes

- The `--legacy-peer-deps` flag is often needed due to specific dependency requirements in the project
- Always ensure both frontend and backend are running for full functionality
- API calls will fail if backend is not accessible at the configured URL
