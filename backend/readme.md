# Invoice Parser API

A FastAPI-based REST API for parsing unstructured invoice text to extract structured product information with intelligent pattern matching.

## Features

- **Multi-format Support**: Parses various invoice formats with 10+ regex patterns
- **Confidence Scoring**: Each extracted item includes a confidence score
- **Unit Normalization**: Standardizes units (kg, g, l, ml, pcs, etc.)
- **Currency Handling**: Supports multiple currencies (₹, $, €, £, etc.)
- **Error Handling**: Comprehensive error responses with details
- **Rate Limiting**: Protection against excessive requests
- **Payload Size Limits**: Prevents large request abuse
- **Health Monitoring**: Built-in health check endpoint
- **CORS Support**: Configured for web application access

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/Afeez1131/invoice-parsers.git
   cd invoice-parsers/backend
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python3 -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install fastapi uvicorn pydantic slowapi
   ```

## Quick Start

1. **Start the server**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Access the API**
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health
   - Root Endpoint: http://localhost:8000/

## API Endpoints

### `POST /parse`
Parse unstructured invoice text.

**Request:**
```json
{
  "data": "Sugar – Rs. 6,000 (50 kg)\nRice 25kg Rs.2500"
}
```

or multiple texts:
```json
{
  "data": ["Sugar – Rs. 6,000 (50 kg)", "Rice 25kg Rs.2500"]
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
    },
    {
      "product_name": "Rice",
      "quantity": 25.0,
      "unit": "kg",
      "unit_price": 100.0,
      "total_price": 2500.0,
      "confidence": 0.85,
      "raw_text": "Rice 25kg Rs.2500",
      "errors": []
    }
  ],
  "items_processed": 1,
  "items_extracted": 2,
  "timestamp": "2024-01-15T10:30:00.000Z",
  "version": "1.0.0"
}
```

### `GET /health`
Check API health status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "service": "invoice-parser"
}
```

### `GET /`
Get API information.

**Response:**
```json
{
  "name": "Invoice Parser API",
  "version": "1.0.0",
  "endpoints": {
    "/parse": "POST - Parse invoice text",
    "/parse/raw": "POST - Parse with raw JSON input",
    "/health": "GET - Health check",
    "/docs": "API documentation"
  }
}
```

## Supported Invoice Patterns

The parser recognizes these formats (and variations):

1. **Product - Price (Quantity Unit)**  
   `"Sugar – Rs. 6,000 (50 kg)"`

2. **Product (Quantity Unit @ Price)**  
   `"Wheat Flour (10kg @ 950)"`

3. **Product: Quantity Unit Price/Unit**  
   `"Cooking Oil: Qty 5 bottles Price 1200/bottle"`

4. **Product Quantity Unit Price**  
   `"Rice 25kg Rs.2500"`

5. **Product @ Price/Unit**  
   `"Tomato @ Rs.45/kg"`

6. **Product Price/Unit**  
   `"Oil Rs.300/litre"`

7. **Product - Price Only**  
   `"Sugar – Rs. 6,000"`

8. **Product Quantity Unit Only**  
   `"Sugar 50kg"`

9. **Multi-item Lines**  
   `"Sugar 50kg Rs.6000, Rice 25kg Rs.2500"`


## Configuration

### Environment Variables
Currently configured with defaults:
- `MAX_PAYLOAD_SIZE`: 5 MB (request body limit)
- `RATE_LIMIT`: 10 requests per minute

### CORS Configuration
Configured to allow:
- Origins: http://localhost:8081 # frontend URL
- Methods: All (`*`)
- Headers: All (`*`)

## Rate Limiting
- **Limit**: 10 requests per minute per IP
- **Exceeded Response**: 429 status code with message
- **Custom Handler**: User-friendly error messages

## Error Handling

The API provides structured error responses:

```json
{
  "error": "Rate limit exceeded",
  "detail": "Rate limit exceeded. Please wait for few minutes then try again.",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

Common HTTP status codes:
- `200`: Success
- `400`: Bad request (invalid input)
- `413`: Payload too large (>5MB)
- `429`: Rate limit exceeded
- `500`: Internal server error

## Development

### Project Structure
```
invoice-parser-api/
├── main.py             # FastAPI application
├── parser.py           # Invoice parsing logic
├── schemas.py          # Pydantic models
├── router.py           # API routes
├── middleware.py       # Custom middleware for checking content size
└── requirements.txt    # Dependencies
```

## Testing

### Using curl
```bash
# Parse invoice text
curl -X POST "http://localhost:8000/parse" \
  -H "Content-Type: application/json" \
  -d '{"data": "Sugar – Rs. 6,000 (50 kg)\nRice 25kg Rs.2500"}'

# Health check
curl "http://localhost:8000/health"

# API info
curl "http://localhost:8000/"
```

### Using Python Requests
```python
import requests

response = requests.post(
    "http://localhost:8000/parse",
    json={"data": "Sugar – Rs. 6,000 (50 kg)"}
)
print(response.json())
```


## Limitations

1. **Text-based Only**: Currently only parses text input
2. **Pattern Dependency**: Relies on regex patterns for extraction
3. **Language Support**: Primarily English invoice formats
4. **Confidence Threshold**: Items with confidence < 0.3 are filtered out
