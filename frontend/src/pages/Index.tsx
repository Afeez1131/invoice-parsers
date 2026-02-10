import {useState} from "react";
import {Textarea} from "@/components/ui/textarea";
import {Button} from "@/components/ui/button";
import {Checkbox} from "@/components/ui/checkbox";
import {Badge} from "@/components/ui/badge";
import {
    Table,
    TableHeader,
    TableBody,
    TableHead,
    TableRow,
    TableCell,
} from "@/components/ui/table";
import {
    Tooltip,
    TooltipContent,
    TooltipTrigger,
} from "@/components/ui/tooltip";
import {Card, CardContent} from "@/components/ui/card";
import {Loader2, FileText, CheckCircle2, XCircle, Download} from "lucide-react";
import {toast} from "@/hooks/use-toast";
import {parseInvoice, type ParseResponse, type ParsedItemResponse} from "@/lib/api";

const MAX_SIZE = 10_000;

function confidenceBadge(confidence: number) {
    if (confidence >= 0.8)
        return <Badge
            className="bg-success hover:bg-success/90 text-success-foreground">{(confidence * 100).toFixed(0)}%</Badge>;
    if (confidence >= 0.5)
        return <Badge
            className="bg-warning hover:bg-warning/90 text-warning-foreground">{(confidence * 100).toFixed(0)}%</Badge>;
    return <Badge variant="destructive">{(confidence * 100).toFixed(0)}%</Badge>;
}

const EditableCell = ({
                          value,
                          onChange,
                          type = "text",
                          align = "left",
                      }: {
    value: string | number | null;
    onChange: (val: string) => void;
    type?: "text" | "number";
    align?: "left" | "right";
}) => {
    const [editing, setEditing] = useState(false);
    const [draft, setDraft] = useState(String(value ?? ""));

    const commit = () => {
        setEditing(false);
        onChange(draft);
    };

    if (editing) {
        return (
            <input
                autoFocus
                type={type}
                step={type === "number" ? "any" : undefined}
                className={`w-full bg-transparent border-b border-primary outline-none text-sm py-0.5 ${align === "right" ? "text-right" : ""}`}
                value={draft}
                onChange={(e) => setDraft(e.target.value)}
                onBlur={commit}
                onKeyDown={(e) => {
                    if (e.key === "Enter") commit();
                    if (e.key === "Escape") setEditing(false);
                }}
            />
        );
    }

    return (
        <span
            className={`cursor-pointer hover:bg-muted/60 rounded px-1 -mx-1 py-0.5 transition-colors ${align === "right" ? "text-right block" : ""}`}
            onClick={() => {
                setDraft(String(value ?? ""));
                setEditing(true);
            }}
            title="Click to edit"
        >
      {value != null && value !== ""
          ? type === "number"
              ? Number(value).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})
              : String(value)
          : "—"}
    </span>
    );
};

const Index = () => {
    const [text, setText] = useState("");
    const [encodeBase64, setEncodeBase64] = useState(false);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<ParseResponse | null>(null);

    const byteLength = new TextEncoder().encode(text).length;
    const overLimit = byteLength > MAX_SIZE;

    const handleParse = async () => {
        if (!text.trim()) {
            toast({title: "Empty input", description: "Please paste some invoice text.", variant: "destructive"});
            return;
        }
        if (overLimit) {
            toast({title: "Input too large", description: "Text exceeds 10 KB limit.", variant: "destructive"});
            return;
        }

        setLoading(true);
        try {
            const res = await parseInvoice(text, encodeBase64);
            setResult(res);
        } catch (err: any) {
            toast({title: "Parse failed", description: err.message || "Network error", variant: "destructive"});
        } finally {
            setLoading(false);
        }
    };

    const recalculateTotal = (item: ParsedItemResponse): ParsedItemResponse => {
        // Only calculate if we have both quantity and unit_price
        const quantity = item.quantity;
        const unitPrice = item.unit_price;

        // Check if both are valid numbers
        if (
            quantity != null &&
            unitPrice != null &&
            !isNaN(quantity) &&
            !isNaN(unitPrice) &&
            typeof quantity === 'number' &&
            typeof unitPrice === 'number'
        ) {
            const calculated = quantity * unitPrice;
            // Round to 2 decimal places to avoid floating point issues
            const roundedTotal = Math.round(calculated * 100) / 100;
            return {...item, total_price: roundedTotal};
        }

        // If we're missing either quantity or unit_price, set total_price to null
        if (item.total_price != null && (quantity == null || unitPrice == null)) {
            return {...item, total_price: null};
        }

        return item;
    };

    const updateItem = (index: number, field: keyof ParsedItemResponse, value: string) => {
        if (!result) return;

        setResult((prev) => {
            if (!prev) return prev;

            const newResults = prev.results.map((item, i) => {
                if (i !== index) return item;

                const numFields: (keyof ParsedItemResponse)[] = ["quantity", "unit_price", "total_price"];

                let newValue: string | number | null =
                    numFields.includes(field)
                        ? value === "" || value === "-" ? null : Number(value)
                        : value === "" ? null : value;

                // Special handling for total_price - we should NOT recalculate if user manually edits it
                if (field === "total_price") {
                    return {...item, [field]: newValue};
                }

                const updatedItem = {...item, [field]: newValue};

                // Always recalculate total when quantity or unit_price changes
                return recalculateTotal(updatedItem);
            });

            return {...prev, results: newResults};
        });
    };

    const exportToCSV = () => {
        if (!result?.results?.length) {
            toast({title: "Nothing to export", variant: "destructive"});
            return;
        }

        const headers = ["Product Name", "Quantity", "Unit", "Unit Price", "Total Price", "Confidence", "Raw Text", "Errors"];

        const rows = result.results.map((item) => [
            `"${(item.product_name || "").replace(/"/g, '""')}"`,
            item.quantity ?? "",
            item.unit ?? "",
            item.unit_price != null ? item.unit_price.toFixed(2) : "",
            item.total_price != null ? item.total_price.toFixed(2) : "",
            (item.confidence * 100).toFixed(0) + "%",
            `"${(item.raw_text || "").replace(/"/g, '""')}"`,
            item.errors.join("; "),
        ]);

        const csv = [headers.join(","), ...rows.map((r) => r.join(","))].join("\n");

        const blob = new Blob([csv], {type: "text/csv;charset=utf-8;"});
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = "invoice_items.csv";
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);

        toast({title: "Exported", description: "CSV downloaded"});
    };

    const addNewRow = () => {
        if (!result) return;
        setResult({
            ...result,
            results: [
                ...result.results,
                {
                    product_name: null,
                    quantity: null,
                    unit: null,
                    unit_price: null,
                    total_price: null,
                    confidence: 1,
                    raw_text: "",
                    errors: [],
                },
            ],
        });
    };

    return (
        <main className="min-h-screen bg-background px-4 py-10 md:px-0">
            <div className="mx-auto max-w-4xl space-y-8">
                <div>
                    <h1 className="text-2xl font-semibold tracking-tight">Invoice Parser</h1>
                    <p className="text-sm text-muted-foreground mt-1">Paste invoice text below to extract product
                        data.</p>
                </div>

                <section className="space-y-3">
                    <Textarea
                        placeholder="Paste your invoice text here…"
                        className="min-h-[180px] font-mono text-sm"
                        value={text}
                        onChange={(e) => setText(e.target.value)}
                    />


                    <Button onClick={handleParse} disabled={loading || overLimit || !text.trim()}
                            className="w-full sm:w-auto">
                        {loading ? <Loader2 className="animate-spin mr-2 h-4 w-4"/> :
                            <FileText className="mr-2 h-4 w-4"/>}
                        {loading ? "Parsing…" : "Parse Invoice"}
                    </Button>
                </section>

                {result && (
                    <section className="space-y-4">
                        <Card>
                            <CardContent className="flex flex-wrap items-center gap-4 py-3 px-4 text-sm">
                                {result.success ? (
                                    <span className="flex items-center gap-1 text-success"><CheckCircle2
                                        className="h-4 w-4"/> Success</span>
                                ) : (
                                    <span className="flex items-center gap-1 text-destructive"><XCircle
                                        className="h-4 w-4"/> Failed</span>
                                )}
                                <span className="text-muted-foreground">
                  Processed: <strong className="text-foreground">{result.items_processed}</strong>
                </span>
                                <span className="text-muted-foreground">
                  Extracted: <strong className="text-foreground">{result.items_extracted}</strong>
                </span>
                                <div className="ml-auto flex items-center gap-3">
                                    <Button variant="outline" size="sm" onClick={exportToCSV}
                                            disabled={!result.results.length}>
                                        <Download className="h-4 w-4 mr-2"/>
                                        Export CSV
                                    </Button>
                                    <span
                                        className="text-xs text-muted-foreground">{new Date(result.timestamp).toLocaleString()}</span>
                                </div>
                            </CardContent>
                        </Card>

                        {result.results.length > 0 ? (
                            <div className="rounded-lg border">
                                <Table>
                                    <TableHeader>
                                        <TableRow>
                                            <TableHead>Product</TableHead>
                                            <TableHead className="text-right">Qty</TableHead>
                                            <TableHead>Unit</TableHead>
                                            <TableHead className="text-right">Unit Price</TableHead>
                                            <TableHead className="text-right">Total</TableHead>
                                            <TableHead className="text-center">Confidence</TableHead>
                                            <TableHead>Raw Text</TableHead>
                                            <TableHead>Errors</TableHead>
                                        </TableRow>
                                    </TableHeader>
                                    <TableBody>
                                        {result.results.map((item: ParsedItemResponse, i: number) => {
                                            const isAutoCalculated = (
                                                item.quantity != null &&
                                                item.unit_price != null &&
                                                !isNaN(item.quantity) &&
                                                !isNaN(item.unit_price) &&
                                                item.total_price != null &&
                                                Math.abs(item.total_price - (item.quantity * item.unit_price)) < 0.01
                                            );

                                            return (
                                                <TableRow key={i}>
                                                    <TableCell className="font-medium">
                                                        <EditableCell value={item.product_name}
                                                                      onChange={(v) => updateItem(i, "product_name", v)}/>
                                                    </TableCell>
                                                    <TableCell className="text-right">
                                                        <EditableCell
                                                            value={item.quantity}
                                                            onChange={(v) => updateItem(i, "quantity", v)}
                                                            type="number"
                                                            align="right"
                                                        />
                                                    </TableCell>
                                                    <TableCell>
                                                        <EditableCell value={item.unit}
                                                                      onChange={(v) => updateItem(i, "unit", v)}/>
                                                    </TableCell>
                                                    <TableCell className="text-right">
                                                        <EditableCell
                                                            value={item.unit_price}
                                                            onChange={(v) => updateItem(i, "unit_price", v)}
                                                            type="number"
                                                            align="right"
                                                        />
                                                    </TableCell>
                                                    <TableCell className="text-right">
                                                        <div className="relative group">
                                                            <EditableCell
                                                                value={item.total_price}
                                                                onChange={(v) => updateItem(i, "total_price", v)}
                                                                type="number"
                                                                align="right"
                                                            />
                                                            {isAutoCalculated && (
                                                                <Tooltip>
                                                                    <TooltipTrigger asChild>
                                                                        <span
                                                                            className="absolute -right-2 top-1/2 transform -translate-y-1/2 text-xs text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity cursor-help">
                                                                            ⚡
                                                                        </span>
                                                                    </TooltipTrigger>
                                                                    <TooltipContent>
                                                                        Auto-calculated from quantity × unit price
                                                                    </TooltipContent>
                                                                </Tooltip>
                                                            )}
                                                        </div>
                                                    </TableCell>
                                                    <TableCell
                                                        className="text-center">{confidenceBadge(item.confidence)}</TableCell>
                                                    <TableCell className="max-w-[150px]">
                                                        <Tooltip>
                                                            <TooltipTrigger asChild>
                                                                <span
                                                                    className="block truncate text-xs text-muted-foreground cursor-default">
                                                                    {item.raw_text || "—"}
                                                                </span>
                                                            </TooltipTrigger>
                                                            <TooltipContent side="bottom"
                                                                            className="max-w-sm whitespace-pre-wrap text-xs">
                                                                {item.raw_text}
                                                            </TooltipContent>
                                                        </Tooltip>
                                                    </TableCell>
                                                    <TableCell>
                                                        {item.errors.length > 0 ? (
                                                            <span
                                                                className="text-xs text-destructive">{item.errors.join(", ")}</span>
                                                        ) : (
                                                            <span className="text-xs text-muted-foreground">—</span>
                                                        )}
                                                    </TableCell>
                                                </TableRow>
                                            );
                                        })}
                                    </TableBody>
                                </Table>
                            </div>
                        ) : (
                            <p className="text-sm text-muted-foreground text-center py-8">No items extracted.</p>
                        )}

                        <Button variant="outline" size="sm" onClick={addNewRow}>
                            + Add Row
                        </Button>
                    </section>
                )}

                {!result && !loading && (
                    <div className="text-center py-16 text-muted-foreground">
                        <FileText className="mx-auto h-10 w-10 mb-3 opacity-40"/>
                        <p className="text-sm">Paste invoice text above and click "Parse Invoice" to get started.</p>
                    </div>
                )}
            </div>
        </main>
    );
};

export default Index;
