from fastapi import APIRouter, Request, HTTPException
from datetime import datetime

from slowapi import Limiter
from slowapi.util import get_remote_address
import logging
from fastapi import status

from parser import InvoiceParser
import schemas

parser = InvoiceParser()
router = APIRouter()
# Get limiter from app state
limiter = Limiter(key_func=get_remote_address)
logger = logging.getLogger(__name__)


@router.post(
    "/parse",
    summary="Parse invoice",
    status_code=status.HTTP_200_OK,
    response_model=schemas.ParseResponse,
)
@limiter.limit("10/minutes")
async def parse_invoice(request: Request, parse_request: schemas.ParseRequest):
    """
    Parse unstructured invoice text to extract product information.

    Accepts either a single string or an array of strings.
    Returns extracted fields with confidence scores.
    """
    try:
        results = []
        if isinstance(parse_request.data, str):
            # Single text parsing
            parsed_items = parser.parse(parse_request.data)
            results = [
                schemas.ParsedItemResponse(
                    product_name=item.product_name,
                    quantity=item.quantity,
                    unit=item.unit,
                    unit_price=item.unit_price,
                    total_price=item.total_price,
                    confidence=round(item.confidence, 2),
                    raw_text=item.raw_text[
                        :100
                    ],  # Limit raw text length for frontend display
                    errors=item.errors,
                )
                for item in parsed_items
            ]

        elif isinstance(parse_request.data, list):
            # Multiple texts parsing
            for text in parse_request.data:
                if isinstance(text, str):
                    parsed_items = parser.parse(text)
                    for item in parsed_items:
                        results.append(
                            schemas.ParsedItemResponse(
                                product_name=item.product_name,
                                quantity=item.quantity,
                                unit=item.unit,
                                unit_price=item.unit_price,
                                total_price=item.total_price,
                                confidence=round(item.confidence, 2),
                                raw_text=item.raw_text[:100],
                                errors=item.errors,
                            )
                        )
        return schemas.ParseResponse(
            success=True,
            results=results,
            items_processed=len(parse_request.data)
            if isinstance(parse_request.data, list)
            else 1,
            items_extracted=len(results),
            timestamp=datetime.now().isoformat(),
        )

    except Exception as e:
        logger.error(f"Error parsing invoice: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
