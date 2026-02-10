# Invoice Parser

A full-stack application for parsing unstructured invoice text to extract structured product information. Includes a React frontend and FastAPI backend.

## Features

### Backend API
- **Multi-format Support**: Parses various invoice formats with 10+ regex patterns
- **Confidence Scoring**: Each extracted item includes a confidence score
- **Unit Normalization**: Standardizes units (kg, g, l, ml, pcs, etc.)
- **Currency Handling**: Supports multiple currencies (₹, $, €, £, etc.)
- **Rate Limiting**: 10 requests per minute per IP
- **Payload Size Limits**: Prevents large request abuse (5MB max)
- **Health Monitoring**: Built-in health check endpoint
- **CORS Support**: Configured for web application access

### Frontend Interface
- **Modern React UI**: Clean, responsive interface
- **Real-time Parsing**: Instant results as you type
- **Confidence Visualization**: Color-coded confidence scores
- **Error Handling**: User-friendly error messages
- **Mobile Responsive**: Works on all device sizes

## Prerequisites

### Backend
- Python 3.8 or higher
- pip (Python package manager)

### Frontend
- Node.js 18 or higher
- npm (comes with Node.js)

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Afeez1131/invoice-parsers.git
cd invoice-parsers
```

## Backend Setup

### 1. Navigate to Backend Directory
```bash
cd backend
```

### 2. Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install fastapi uvicorn pydantic slowapi
```

### 4. Start Backend Server
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Backend will be available at:** http://localhost:8000

## Frontend Setup

### 1. Navigate to Frontend Directory
```bash
cd ../frontend/invoice-parser
```

### 2. Install Dependencies
**Choose ONE of these methods:**

#### **Recommended Method** (if facing peer dependency conflicts):
```bash
npm install --legacy-peer-deps
```

#### **Standard Method** (try this first):
```bash
npm install
```

### 3. Configure Environment
Create a `.env` file in the frontend directory:
```env
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=Invoice Parser
```

### 4. Start Frontend Server
```bash
npm run dev
```

**Frontend will be available at:** http://localhost:5173

## Troubleshooting

### Common Issues & Solutions

#### Backend Issues
```bash
# Port 8000 already in use
# On macOS/Linux:
lsof -ti:8000 | xargs kill -9
# On Windows:
netstat -ano | findstr :8000
# Then use the PID from output:
taskkill /PID <PID> /F

# Python dependencies issues
pip install --upgrade pip
pip install -r requirements.txt  # If you have requirements.txt
```

#### Frontend Issues
```bash
# "npm install" fails with peer dependency conflicts
npm cache clean --force
npm install --legacy-peer-deps

# "npm run dev" not working after install
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps

# Port 5173 already in use
# Change port:
npm run dev -- --port 3000
```

### Complete Clean Install (Frontend)
```bash
# 1. Remove existing dependencies
rm -rf node_modules package-lock.json

# 2. Clear npm cache
npm cache clean --force

# 3. Install with legacy peer deps
npm install --legacy-peer-deps

# 4. Start the dev server
npm run dev
```

## API Usage

### Backend API Endpoints

#### `POST /parse`
Parse unstructured invoice text.

**Request:**
```json
{
  "data": "Sugar – Rs. 6,000 (50 kg)\nRice 25kg Rs.2500"
}
```

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "product_name": "Sugar",
      "quantity": 50.0,
      "unit": "kg",
      "unit_price": 120.0,
      "total_price": 6000.0,
      "confidence": 0.9,
      "raw_text": "Sugar – Rs. 6,000 (50 kg)",
      "errors": []
    }
  ],
  "items_processed": 1,
  "items_extracted": 1,
  "timestamp": "2024-01-15T10:30:00.000Z",
  "version": "1.0.0"
}
```

#### `GET /health`
Check API health status.
```bash
curl http://localhost:8000/health
```

#### `GET /`
Get API information.
```bash
curl http://localhost:8000/
```

### Frontend Interface
Access the web interface at: http://localhost:5173

Features:
- Paste or type invoice text
- Real-time parsing
- Visual confidence indicators
- Copy results to clipboard
- Clear formatting options

## Supported Invoice Patterns

The parser recognizes these formats (and variations):

| Pattern | Example |
|---------|---------|
| Product - Price (Quantity Unit) | `"Sugar – Rs. 6,000 (50 kg)"` |
| Product (Quantity Unit @ Price) | `"Wheat Flour (10kg @ 950)"` |
| Product: Quantity Unit Price/Unit | `"Cooking Oil: Qty 5 bottles Price 1200/bottle"` |
| Product Quantity Unit Price | `"Rice 25kg Rs.2500"` |
| Product @ Price/Unit | `"Tomato 10kg @ Rs.45/kg"` |
| Product Price/Unit | `"Oil Rs.300/litre"` |
| Product - Price Only | `"Sugar – Rs. 6,000"` |
| Product Quantity Unit Only | `"Sugar 50kg"` |
| Multi-item Lines | `"Sugar 50kg Rs.6000, Rice 25kg Rs.2500"` |

##️ Project Structure

```
invoice-parsers/
├── backend/                    # FastAPI Backend (Python)
│   ├──  main.py                # FastAPI application entry point
│   ├──  parser.py              # Invoice parsing logic and patterns
│   ├──  schemas.py             # Pydantic data models and validation
│   ├──  router.py              # API route definitions and endpoints
│   ├──  middleware.py          # Custom middleware (rate limiting, CORS, etc.)
│   └──  requirements.txt       # Python dependencies list
│
└──  frontend/                  # React Frontend
    ├── public/                # Static assets served directly
    │   ├──  favicon.ico        # Browser tab icon
    │   ├──  placeholder.svg    # Default placeholder image
    │   └──  robots.txt         # Search engine crawler instructions
    │
    ├── src/                   # Source code directory
    │   ├── components/        # Reusable UI components
    │   │   ├── ui/            # ShadCN UI component library
    │   │   │   ├──  accordion.tsx
    │   │   │   ├──  alert.tsx
    │   │   │   ├──  button.tsx
    │   │   │   ├──  card.tsx
    │   │   │   ├──  dialog.tsx
    │   │   │   ├──  form.tsx
    │   │   │   ├──  input.tsx
    │   │   │   ├──  table.tsx
    │   │   │   ├──  textarea.tsx
    │   │   │   ├──  toast.tsx
    │   │   │   └── ...           # UI components
    │   │   │
    │   │   └──  NavLink.tsx    # Custom navigation link component
    │   │
    │   ├──  hooks/             # Custom React hooks
    │   │   ├──  use-mobile.tsx # Mobile device detection hook
    │   │   └──  use-toast.ts   # Toast notification hook
    │   │
    │   ├──  lib/               # Utility functions and services
    │   │   ├──  api.ts         # API client and service layer
    │   │   └──  utils.ts       # Helper and utility functions
    │   │
    │   ├──  pages/             # Application page components
    │   │   ├──  Index.tsx      # Main invoice parsing interface
    │   │   └──  NotFound.tsx   # 404 error page
    │   │
    │   ├──  App.css            # Global CSS styles
    │   ├──  App.tsx            # Root application component
    │   ├──  index.css          # Main CSS entry point
    │   ├──  main.tsx           # Application entry point
    │   └──  vite-env.d.ts      # Vite environment type declarations
    │
    ├──  .gitignore             # Git ignore rules
    ├──  bun.lockb              # Bun package manager lock file
    ├──  components.json        # ShadCN UI component configuration
    ├──  eslint.config.js       # ESLint configuration
    ├──  index.html             # HTML entry point
    ├──  package-lock.json      # npm package lock file
    ├──  package.json           # Project dependencies and scripts
    ├──  postcss.config.js      # PostCSS configuration
    ├──  tailwind.config.ts     # Tailwind CSS configuration
    ├──  tsconfig.app.json      # TypeScript app configuration
    ├──  tsconfig.json          # TypeScript root configuration
    ├──  tsconfig.node.json     # TypeScript Node.js configuration
    ├──  vite.config.ts         # Vite build tool configuration
    └──  vitest.config.ts       # Vitest testing framework configuration
```

## Configuration

### Backend Configuration
- **MAX_PAYLOAD_SIZE**: 5 MB (request body limit)
- **RATE_LIMIT**: 10 requests per minute per IP
- **CORS Origins**: http://localhost:5173 (frontend URL)

### Frontend Configuration
- **VITE_API_URL**: http://localhost:8000 (backend URL)
- **VITE_APP_NAME**: Invoice Parser

## Error Handling

### Backend Error Responses
```json
{
  "error": "Rate limit exceeded",
  "detail": "Rate limit exceeded. Please wait for few minutes then try again.",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

**Common HTTP Status Codes:**
- `200`: Success
- `400`: Bad request (invalid input)
- `413`: Payload too large (>5MB)
- `429`: Rate limit exceeded
- `500`: Internal server error

### Frontend Error Handling
- Network errors displayed to user
- Validation errors for input
- Graceful degradation when backend is unavailable

## Testing

### Backend Testing with curl
```bash
# Parse invoice text
curl -X POST "http://localhost:8000/parse" \
  -H "Content-Type: application/json" \
  -d '{"data": "Sugar – Rs. 6,000 (50 kg)\nRice 25kg Rs.2500"}'

# Health check
curl "http://localhost:8000/health"
```

### Frontend Testing
- Open browser at http://localhost:5173
- Enter sample invoice text
- Verify parsed results appear

##  Usage Examples

### Sample Invoice Text
```
Invoice #12345
Sugar – Rs. 6,000 (50 kg)
Rice 25kg Rs.2500
Cooking Oil: Qty 5 bottles Price 1200/bottle
Wheat Flour (10kg @ 950)
Total: Rs. 12,750
Thank you for your business!
```

### Expected Output
- 4 parsed items with confidence scores
- Calculated unit prices
- Normalized units
- Raw text reference

## Limitations

1. **Text-based Only**: Currently only parses text input
2. **Pattern Dependency**: Relies on regex patterns for extraction
3. **Language Support**: Primarily English invoice formats
4. **Confidence Threshold**: Items with confidence < 0.3 are filtered out
5. **Image Processing**: Does not support image or PDF invoices (text extraction only)

## Getting Help

If you encounter issues:

1. **Backend not responding?**
   ```bash
   # Check if backend is running
   curl http://localhost:8000/health
   ```

2. **Frontend not connecting?**
   - Check `.env` file has correct API URL
   - Verify backend is running on port 8000
   - Check browser console for errors (F12)

3. **Parsing not working?**
   - Try different invoice formats from supported patterns
   - Check if text contains special characters
   - Verify currency symbols are supported

4. **Installation problems?**
   - Use `--legacy-peer-deps` flag for npm install
   - Ensure correct Python/Node.js versions
   - Try clean install process
