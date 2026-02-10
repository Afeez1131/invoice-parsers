"""
Invoice Parser with improved line handling
"""
import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict, field


@dataclass
class ParsedItem:
    """Represents a parsed invoice item."""
    product_name: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    unit_price: Optional[float] = None
    total_price: Optional[float] = None
    confidence: float = 0.0
    raw_text: str = ""
    errors: List[str] = field(default_factory=list)


class InvoiceParser:
    """
    invoice parser that handles various formats.
    """

    # Unit mappings
    UNIT_MAPPINGS = {
        'kg': 'kg', 'kgs': 'kg', 'kilogram': 'kg', 'kilograms': 'kg', 'kilo': 'kg', 'k': 'kg',
        'g': 'g', 'gm': 'g', 'gram': 'g', 'grams': 'g', 'gr': 'g',
        'l': 'l', 'ltr': 'l', 'litre': 'l', 'litres': 'l', 'liter': 'l', 'lt': 'l',
        'ml': 'ml', 'milliliter': 'ml', 'millilitre': 'ml', 'mil': 'ml',
        'pcs': 'pcs', 'pc': 'pcs', 'piece': 'pcs', 'pieces': 'pcs', 'p': 'pcs',
        'bottle': 'bottles', 'bottles': 'bottles', 'btl': 'bottles', 'bot': 'bottles',
        'packet': 'packets', 'packets': 'packets', 'pack': 'packets', 'pkt': 'packets',
        'box': 'boxes', 'boxes': 'boxes', 'bx': 'boxes',
        'dozen': 'dozen', 'doz': 'dozen', 'dz': 'dozen',
        'unit': 'units', 'units': 'units', 'un': 'units',
        'carton': 'carton', 'ctn': 'carton', 'crt': 'carton',
        'bag': 'bags', 'bags': 'bags', 'sack': 'sacks', 'sacks': 'sacks',
        'can': 'cans', 'cans': 'cans',
        'jar': 'jars', 'jars': 'jars',
        'tin': 'tins', 'tins': 'tins',
        'roll': 'rolls', 'rolls': 'rolls',
        'meter': 'meters', 'meters': 'meters', 'm': 'meters',
        'yard': 'yards', 'yards': 'yards', 'yd': 'yards',
    }

    def __init__(self):
        self.patterns = self._compile_patterns()

    def _compile_patterns(self) -> List[Dict]:
        """Compile regex patterns with comprehensive currency handling."""
        patterns = []

        # Define currency patterns
        currency_symbols = r'(?:Rs\.?|₹|INR|USD|\$|€|£|GBP|EUR|₦|NGN|N|#)'
        optional_currency = rf'(?:{currency_symbols}\s*)?'

        # Pattern 1: "Sugar – Rs. 6,000 (50 kg)" - WITH currency symbol
        patterns.append({
            'regex': re.compile(
                rf'^(?P<product>[^\d:\-–—@()]+?)\s*[\-–—]\s*'
                rf'{optional_currency}\s*(?P<total>[\d,]+(?:\.\d{{1,2}})?)\s*'
                rf'\(\s*(?P<quantity>\d+(?:\.\d+)?)\s*(?P<unit>[a-zA-Z]+)\s*\)',
                re.IGNORECASE
            ),
            'priority': 1,
            'description': 'product - price (quantity unit)'
        })

        # Pattern 1b: "Sugar – 6,000 (50 kg)" - WITHOUT currency symbol
        patterns.append({
            'regex': re.compile(
                rf'^(?P<product>[^\d:\-–—@()]+?)\s*[\-–—]\s*'
                rf'(?P<total>[\d,]+(?:\.\d{{1,2}})?)\s*'
                rf'\(\s*(?P<quantity>\d+(?:\.\d+)?)\s*(?P<unit>[a-zA-Z]+)\s*\)',
                re.IGNORECASE
            ),
            'priority': 1,
            'description': 'product - price (quantity unit) no currency'
        })

        # Pattern 2: "Wheat Flour (10kg @ 950)" or "Wheat Flour (10kg @ Rs. 950)"
        patterns.append({
            'regex': re.compile(
                rf'^(?P<product>[^\d:\-–—@()]+?)\s*'
                rf'\(\s*(?P<quantity>\d+(?:\.\d+)?)\s*(?P<unit>[a-zA-Z]+)\s*'
                rf'@\s*{optional_currency}\s*(?P<unit_price>[\d,]+(?:\.\d{{1,2}})?)\s*\)',
                re.IGNORECASE
            ),
            'priority': 1,
            'description': 'product (quantity unit @ price)'
        })

        # Pattern 3: "Cooking Oil: Qty 5 bottles Price 1200/bottle" or "Price Rs.1200/bottle"
        patterns.append({
            'regex': re.compile(
                rf'^(?P<product>[^\d:\-–—@()]+?)\s*:\s*'
                rf'(?:Qty|Quantity)?\s*(?P<quantity>\d+(?:\.\d+)?)?\s*(?P<unit>[a-zA-Z]+)?\s*'
                rf'(?:Price|Rate|Cost)?\s*{optional_currency}\s*(?P<unit_price>[\d,]+(?:\.\d{{1,2}})?)\s*/',
                re.IGNORECASE
            ),
            'priority': 1,
            'description': 'product: qty unit price/unit'
        })

        # Pattern 4: "Rice 25kg Rs.2500" or "Rice 25kg ₹2500" or "Rice 25kg 2500"
        patterns.append({
            'regex': re.compile(
                rf'^(?P<product>[A-Za-z][A-Za-z\s]+?)\s+'
                rf'(?P<quantity>\d+(?:\.\d+)?)\s*(?P<unit>[a-zA-Z]+)\s+'
                rf'{optional_currency}\s*(?P<total>[\d,]+(?:\.\d{{1,2}})?)$',
                re.IGNORECASE
            ),
            'priority': 2,
            'description': 'product quantity unit price'
        })

        # Pattern 5: "Tomato 10kg @ 45/kg" or "Tomato @ Rs.45/kg" - with optional quantity
        patterns.append({
            'regex': re.compile(
                rf'^(?P<product>[A-Za-z][A-Za-z\s]+?)\s+'
                rf'(?:(?P<quantity>\d+(?:\.\d+)?)\s*(?P<unit>[a-zA-Z]+)\s*)?'
                rf'@\s*{optional_currency}\s*(?P<unit_price>[\d,]+(?:\.\d{{1,2}})?)(?:/\w+)?$',
                re.IGNORECASE
            ),
            'priority': 2,
            'description': 'product quantity unit @ price'
        })

        # Pattern 6: "Oil Rs.300/litre" or "Oil 300/litre"
        patterns.append({
            'regex': re.compile(
                rf'^(?P<product>[A-Za-z][A-Za-z\s]+?)\s+'
                rf'{optional_currency}\s*(?P<unit_price>[\d,]+(?:\.\d{{1,2}})?)\s*/'
                rf'(?P<unit>[a-zA-Z]+)$',
                re.IGNORECASE
            ),
            'priority': 2,
            'description': 'product price/unit'
        })

        # Pattern 7: "Sugar – Rs. 6,000" (no quantity in parentheses)
        patterns.append({
            'regex': re.compile(
                rf'^(?P<product>[A-Za-z][A-Za-z\s]+?)\s*[\-–—]\s*'
                rf'{optional_currency}\s*(?P<total>[\d,]+(?:\.\d{{1,2}})?)$',
                re.IGNORECASE
            ),
            'priority': 3,
            'description': 'product - price only'
        })

        # Pattern 8: "Sugar 50kg" (no price)
        patterns.append({
            'regex': re.compile(
                r'^(?P<product>[A-Za-z][A-Za-z\s]+?)\s+'
                r'(?P<quantity>\d+(?:\.\d+)?)\s*(?P<unit>[a-zA-Z]+)$',
                re.IGNORECASE
            ),
            'priority': 4,
            'description': 'product quantity unit only'
        })

        # Pattern 9: "Sugar Rs.6000 50kg" (reversed order)
        patterns.append({
            'regex': re.compile(
                rf'^(?P<product>[A-Za-z][A-Za-z\s]+?)\s+'
                rf'{optional_currency}\s*(?P<total>[\d,]+(?:\.\d{{1,2}})?)\s+'
                rf'(?P<quantity>\d+(?:\.\d+)?)\s*(?P<unit>[a-zA-Z]+)$',
                re.IGNORECASE
            ),
            'priority': 2,
            'description': 'product price quantity unit'
        })

        # Pattern 10: Multiple items in one line - "Sugar 50kg Rs.6000, Rice 25kg Rs.2500"
        patterns.append({
            'regex': re.compile(
                rf'(?P<product>[A-Za-z][A-Za-z\s]+?)\s+'
                rf'(?P<quantity>\d+(?:\.\d+)?)\s*(?P<unit>[a-zA-Z]+)\s+'
                rf'{optional_currency}\s*(?P<total>[\d,]+(?:\.\d{{1,2}})?)',
                re.IGNORECASE
            ),
            'priority': 1,
            'description': 'multi-item pattern'
        })

        return patterns

    def _clean_number(self, value: str) -> Optional[float]:
        """Convert string number to float with enhanced cleaning."""
        if not value:
            return None

        try:
            # Remove currency symbols, commas, and whitespace
            cleaned = str(value).strip()
            # Remove currency symbols
            cleaned = re.sub(r'^(?:Rs\.?|₹|INR|USD|\$|€|£|GBP|EUR|₦|NGN|N|#)\s*', '', cleaned, flags=re.IGNORECASE)
            # Remove commas (thousands separators)
            cleaned = cleaned.replace(',', '')
            # Remove any remaining non-numeric characters except decimal point
            cleaned = re.sub(r'[^\d\.]', '', cleaned)

            # Handle cases where there might be multiple decimal points
            parts = cleaned.split('.')
            if len(parts) > 2:
                # Keep only first decimal point (e.g., "1.234.56" -> "1234.56")
                cleaned = parts[0] + '.' + ''.join(parts[1:])

            if not cleaned:
                return None

            result = float(cleaned)

            # Additional validation
            if result < 0 or result > 10000000:  # Reasonable bounds for invoice items
                return None

            return result

        except (ValueError, TypeError, AttributeError):
            return None

    def _normalize_unit(self, unit: str) -> str:
        """Normalize unit to standard form."""
        if not unit:
            return ""
        unit_lower = unit.lower().strip()
        return self.UNIT_MAPPINGS.get(unit_lower, unit_lower)

    def _extract_from_line(self, line: str) -> Optional[ParsedItem]:
        """Extract product info from a single line."""
        line = line.strip()
        if not line or len(line) < 3:
            return None

        # Skip obvious noise
        noise_patterns = [
            r'^.*invoice.*#?\d+.*$',
            r'^.*traders?.*$',
            r'^.*thank.*you.*$',
            r'^.*total.*:.*$',
            r'^.*tax.*:.*$',
            r'^\s*\d+\s*$',  # Just numbers
        ]

        for pattern in noise_patterns:
            if re.match(pattern, line, re.IGNORECASE):
                return None

        best_match = None
        best_score = -1

        for pattern_info in self.patterns:
            match = pattern_info['regex'].match(line)
            if not match:
                continue

            groups = match.groupdict()
            item = ParsedItem(raw_text=line)

            # Extract basic fields
            if 'product' in groups and groups['product']:
                item.product_name = groups['product'].strip()

            if 'quantity' in groups and groups['quantity']:
                item.quantity = self._clean_number(groups['quantity'])

            if 'unit' in groups and groups['unit']:
                item.unit = self._normalize_unit(groups['unit'])

            # Extract prices
            if 'unit_price' in groups and groups['unit_price']:
                item.unit_price = self._clean_number(groups['unit_price'])

            if 'total' in groups and groups['total']:
                item.total_price = self._clean_number(groups['total'])

            # Calculate missing values
            self._calculate_missing(item)

            # Calculate confidence
            confidence = self._calculate_confidence(item, pattern_info['priority'])
            item.confidence = confidence

            if confidence > best_score:
                best_score = confidence
                best_match = item

        return best_match

    def _calculate_missing(self, item: ParsedItem) -> None:
        """Calculate missing price values."""
        if item.total_price and item.quantity and item.quantity > 0 and not item.unit_price:
            item.unit_price = round(item.total_price / item.quantity, 2)
        elif item.unit_price and item.quantity and item.quantity > 0 and not item.total_price:
            item.total_price = round(item.unit_price * item.quantity, 2)

    def _calculate_confidence(self, item: ParsedItem, pattern_priority: int) -> float:
        """Calculate confidence score."""
        score = 0.0

        # Base score from pattern
        if pattern_priority == 1:
            score += 0.4
        elif pattern_priority == 2:
            score += 0.3
        else:
            score += 0.2

        # Product name
        if item.product_name and len(item.product_name) > 1:
            score += 0.2

        # Quantity
        if item.quantity is not None and item.quantity > 0:
            score += 0.15

        # Unit
        if item.unit:
            score += 0.1

        # Prices
        if item.unit_price is not None or item.total_price is not None:
            score += 0.15

        return min(score, 1.0)

    def parse(self, text: str) -> List[ParsedItem]:
        """Parse invoice text."""
        if not text:
            return []

        # Normalize line endings
        text = text.replace('\r\n', '\n').replace('\r', '\n')

        # Split into lines and process
        lines = text.split('\n')
        items = []

        for line in lines:
            item = self._extract_from_line(line)
            if item and item.confidence > 0.3:
                items.append(item)

        return items

    def parse_to_dict(self, text: str) -> List[Dict]:
        """Parse and return as dictionary."""
        items = self.parse(text)
        return [asdict(item) for item in items]
