from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Union


class ParseRequest(BaseModel):
    data: Union[str, List[str]] = Field(...)

    @field_validator("data")
    @classmethod
    def check_size(cls, v):
        if isinstance(v, str) and len(v) > 10_000:
            raise ValueError("Text exceeds 10KB")

        if isinstance(v, list):
            if len(v) > 100:
                raise ValueError("Max 100 items")
            if sum(len(i) for i in v) > 50_000:
                raise ValueError("Total exceeds 50KB")

        return v


class ParsedItemResponse(BaseModel):
    """Response model for parsed items."""

    product_name: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    unit_price: Optional[float] = None
    total_price: Optional[float] = None
    confidence: float = 0.0
    raw_text: str = ""
    errors: List[str] = []


class ParseResponse(BaseModel):
    """Response model for parse endpoint."""

    success: bool
    results: List[ParsedItemResponse]
    items_processed: int
    items_extracted: int
    timestamp: str
    version: str = "1.0.0"


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str
    detail: Optional[str] = None
    timestamp: str
