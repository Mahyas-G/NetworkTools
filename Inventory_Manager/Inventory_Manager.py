import os
import sys
import json
import argparse
from collections import Counter

STATUS_KEYS = {"status", "state", "condition", "health", "active", "enabled", "online"}

ANSI = {
    "reset":  "\033[0m",
    "bold":   "\033[1m",
    "green":  "\033[92m",
    "red":    "\033[91m",
    "yellow": "\033[93m",
    "cyan":   "\033[96m",
    "gray":   "\033[90m",
    "white":  "\033[97m",
}

def c(color: str, text: str) -> str:
    if sys.stdout.isatty():
        return f"{ANSI.get(color, '')}{text}{ANSI['reset']}"
    return text

def flatten(obj: dict, prefix: str = "") -> dict:
    result = {}
    for key, val in obj.items():
        full_key = f"{prefix}.{key}" if prefix else key
        if isinstance(val, dict):
            result.update(flatten(val, full_key))
        elif isinstance(val, list):
            result[full_key] = ", ".join(str(v) for v in val)
        else:
            result[full_key] = val
    return result

def normalize(raw) -> list[dict]:
    if isinstance(raw, list):
        if not raw:
            return []
        if isinstance(raw[0], dict):
            return [flatten(item) for item in raw]
        return [{"value": item} for item in raw]

    if isinstance(raw, dict):
        for val in raw.values():
            if isinstance(val, list) and val and isinstance(val[0], dict):
                return normalize(val)
        return [flatten(raw)]

    return [{"value": raw}]

def get_columns(rows: list[dict]) -> list[str]:
    seen, cols = set(), []
    for row in rows:
        for k in row:
            if k not in seen:
                seen.add(k)
                cols.append(k)
    return cols

def detect_status_field(columns: list[str]) -> str | None:
    for col in columns:
        if col.lower() in STATUS_KEYS or any(sk in col.lower() for sk in STATUS_KEYS):
            return col
    return None

def status_color(value: str) -> str:
    v = str(value).lower()
    if v in {"up", "active", "online", "enabled", "true", "yes", "ok", "running", "good"}:
        return "green"
    if v in {"down", "inactive", "offline", "disabled", "false", "no", "error", "stopped", "failed"}:
        return "red"
    return "yellow"

def print_table(rows: list[dict], columns: list[str], status_col: str | None) -> None:
    if not rows:
        print(c("yellow", "  (no records to display)"))
        return

    widths = {col: len(col) for col in columns}
    for row in rows:
        for col in columns:
            widths[col] = max(widths[col], len(str(row.get(col, ""))))

    sep = "  "

    header = sep.join(c("bold", col.upper().ljust(widths[col])) for col in columns)
    divider = sep.join(c("gray", "─" * widths[col]) for col in columns)
    print(header)
    print(divider)

    for row in rows:
        parts = []
        for col in columns:
            val = str(row.get(col, ""))
            cell = val.ljust(widths[col])
            if col == status_col:
                parts.append(c(status_color(val), cell))
            else:
                parts.append(cell)
        print(sep.join(parts))

def print_summary(rows: list[dict], status_col: str | None) -> None:
    print(c("cyan", f"\n  ● Total records : {len(rows)}"))
    if not status_col or not rows:
        return
    counts = Counter(str(r.get(status_col, "")) for r in rows)
    for val, n in sorted(counts.items(), key=lambda x: -x[1]):
        col = status_color(val)
        bar = "█" * n + "░" * (max(counts.values()) - n)
        print(f"    {c(col, val.ljust(10))}  {c(col, bar)}  {n}")

def print_markdown(rows: list[dict], columns: list[str]) -> None:
    if not rows:
        return
    print("| " + " | ".join(columns) + " |")
    print("|" + "|".join(["---" for _ in columns]) + "|")
    for row in rows:
        print("| " + " | ".join(str(row.get(col, "")) for col in columns) + " |")

def apply_filters(
    rows: list[dict],
    filter_expr: str | None,
    search: str | None,
) -> list[dict]:
    if filter_expr:
        conditions = [cond.strip() for cond in filter_expr.split(" and ")]
        for cond in conditions:
            if "=" not in cond:
                print(c("red", f"  ✗ Invalid filter '{cond}'. Use field=value."))
            else:
                key, _, val = cond.partition("=")
                key, val = key.strip(), val.strip().lower()
                rows = [r for r in rows if str(r.get(key, "")).lower() == val]

    if search:
        term = search.lower()
        rows = [r for r in rows if any(term in str(v).lower() for v in r.values())]

    return rows

def export_csv(rows: list[dict], columns: list[str], path: str) -> None:
    import csv
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(c("green", f"  ✓ Exported {len(rows)} rows → {path}"))

def load_inventory(path: str) -> list[dict]:
    if not os.path.isfile(path):
        sys.exit(c("red", f"  ✗ File not found: {path}"))
    with open(path, encoding="utf-8") as f:
        try:
            raw = json.load(f)
        except json.JSONDecodeError as e:
            sys.exit(c("red", f"  ✗ Invalid JSON: {e}"))
    return normalize(raw)

def get_sort_value(v):
    try:
        return (0, float(v))
    except (ValueError, TypeError):
        return (1, str(v).lower())

def run(args: argparse.Namespace) -> None:
    rows = load_inventory(args.file)
    if not rows:
        sys.exit(c("yellow", "  ⚠ JSON file is empty or has no records."))

    columns = get_columns(rows)
    status_col = detect_status_field(columns)

    if args.columns:
        requested = [c.strip() for c in args.columns.split(",")]
        missing = [c for c in requested if c not in columns]
        if missing:
            print(c("yellow", f"  ⚠ Unknown columns ignored: {missing}"))
        columns = [c for c in requested if c in columns] or columns

    rows = apply_filters(rows, args.filter, args.search)

    if args.sort:
        reverse = args.sort.startswith("-")
        sort_key = args.sort.lstrip("-")
        if sort_key not in get_columns(rows):
            print(c("yellow", f"  ⚠ Sort column '{sort_key}' not found. Skipping sort."))
        else:
            rows.sort(key=lambda r: get_sort_value(r.get(sort_key, "")), reverse=reverse)

    if args.json:
        print(json.dumps(rows, indent=2, ensure_ascii=False))
        return

    if args.markdown:
        if not rows:
            print(c("yellow", "  No matching records found."))
            return
        print_markdown(rows, columns)
        return

    if args.stats:
        if not rows:
            print(c("yellow", "  No matching records found."))
            return
        print_summary(rows, status_col)
        return

    print()
    print(c("bold", f"  {os.path.basename(args.file).upper()}"))
    print()
    print_table(rows, columns, status_col)
    print_summary(rows, status_col)
    print()

    if args.export:
        export_csv(rows, columns, args.export)

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="inventory_manager",
        description="Smart CLI viewer for any JSON inventory file.",
    )
    parser.add_argument("file", help="Path to the JSON file")
    parser.add_argument("--filter",  "-f", metavar="EXPR",      help="Filter rows, e.g. --filter 'status=up and site=tehran'")
    parser.add_argument("--search",  "-s", metavar="TEXT",      help="Free-text search across all fields")
    parser.add_argument("--sort",    "-o", metavar="FIELD",     help="Sort by field. Prefix with - for descending (e.g. -name)")
    parser.add_argument("--columns", "-c", metavar="C1,C2",     help="Show only specific columns (comma-separated)")
    parser.add_argument("--export",  "-e", metavar="OUT.csv",   help="Export filtered results to CSV")
    parser.add_argument("--stats",         action="store_true", help="Show only summary statistics")
    parser.add_argument("--json",          action="store_true", help="Output filtered results as JSON")
    parser.add_argument("--markdown",      action="store_true", help="Output filtered results as a Markdown table")
    args = parser.parse_args()
    run(args)

if __name__ == "__main__":
    main()
