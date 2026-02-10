const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export interface ParsedItemResponse {
    product_name: string | null;
    quantity: number | null;
    unit: string | null;
    unit_price: number | null;
    total_price: number | null;
    confidence: number;
    raw_text: string;
    errors: string[];
}

export interface ParseResponse {
    success: boolean;
    results: ParsedItemResponse[];
    items_processed: number;
    items_extracted: number;
    timestamp: string;
    version: string;
}

export interface ErrorResponse {
    error: string;
    detail?: string;
    timestamp: string;
}

export async function parseInvoice(
    text: string,
    encodeBase64: boolean
): Promise<ParseResponse> {
    const data = encodeBase64 ? btoa(unescape(encodeURIComponent(text))) : text;

    const response = await fetch(`${API_BASE_URL}/parse`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({data, is_base64: encodeBase64}),
    });

    if (!response.ok) {
        let errorMessage = `Request failed (${response.status})`;

        try {
            const errorData = await response.json();

            // Handle FastAPI validation error structure
            if (errorData.detail) {
                if (Array.isArray(errorData.detail)) {
                    // ValidationError with multiple details
                    errorMessage = errorData.detail
                        .map((err: any) => {
                            if (err.loc && err.msg) {
                                return `${err.loc.join('.')}: ${err.msg}`;
                            }
                            return err.msg || JSON.stringify(err);
                        })
                        .join('; ');
                } else if (typeof errorData.detail === 'string') {
                    // Simple string detail
                    errorMessage = errorData.detail;
                } else if (errorData.detail.message) {
                    // Object with message field
                    errorMessage = errorData.detail.message;
                } else {
                    // Fallback to stringify
                    errorMessage = JSON.stringify(errorData.detail);
                }
            }
            // Handle other common error field names
            else if (errorData.error) {
                errorMessage = errorData.error;
            } else if (errorData.message) {
                errorMessage = errorData.message;
            }
        } catch (parseError) {
            // If JSON parsing fails, try to get text response
            try {
                const text = await response.text();
                if (text) errorMessage = text;
            } catch {
                // Keep the default error message
            }
        }

        throw new Error(errorMessage);
    }

    return response.json();
}
