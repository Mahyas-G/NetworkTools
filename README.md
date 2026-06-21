# NetworkTools

in Progress...

## 3) Port_Scanner

Options:

-s, --start: Start port (default: 1)

-e, --end: End port (default: 1024)

-w, --workers: Maximum concurrent threads (default: 100, max: 1000)

-t, --timeout: Connection timeout in seconds (default: 0.5)

-b, --batch-size: Number of ports to process per batch (default: 2048)

-o, --output: Save open port results to a JSON file


Examples:

```
# Basic scan
python Port_Scanner.py 127.0.0.1

# High-concurrency scan with JSON export
python Port_Scanner.py 192.168.1.1 -s 1 -e 10000 -w 500 -o results.json
```

Logging:

All background execution errors and exceptions are captured in scanner_debug.log to maintain a clean terminal user interface.

---
 ## 4) Inventory_Management (CLI)

A smart, plugin-less command-line utility to view, filter, and manage JSON inventory files. It automatically detects nested structures, flattens arrays, and identifies status fields across different device types (Cisco, MikroTik, Servers, IoT, etc.) without requiring specific plugins.

Features
- **Auto-Detection:** Automatically normalizes JSON structures and highlights status fields (`status`, `state`, `health`, etc.).
- **Advanced Filtering:** Chain multiple exact-match conditions using `and` or use free-text search.
- **Export & Formatting:** Output data as plain text tables, Markdown, JSON, or export directly to CSV.
- **Summary Statistics:** Generate visual progress bars and status counts.


Options

| Flag             | Description |
|------------------|-------------|
| `-c, --columns`  | Show only specific columns (comma-separated). |
| `-e, --export`   | Export filtered results to a CSV file. |
| `-f, --filter`   | Filter rows using exact matches (e.g., `status=up and role=web`). |
| `--json`         | Output filtered results as raw JSON. |
| `--markdown`     | Output filtered results as a Markdown table. |
| `-o, --sort`     | Sort by field. Prefix with `-` for descending (e.g., `-cpu`). |
| `-s, --search`   | Free-text search across all fields. |
| `--stats`        | Show only summary statistics (hides the main table). |

Usage

```bash
python Inventory_Management.py <file.json> [options]
```

Examples
1. Basic View
Load and display an inventory file as a formatted table:

```bash
python Inventory_Management.py sample_data/devices.json
```

3. Search & Sort
Free-text search across all fields and sort descending by a specific column:
```bash
python Inventory_Management.py sample_data/servers.json --search "prod" --sort=-uptime_days
```

4. Summary Statistics
Skip the table and only display record counts and status distribution:
```bash
python Inventory_Management.py sample_data/iot_devices.json --stats
```

5. Markdown & JSON Output
Perfect for documentation or piping into other tools:

```bash
python Inventory_Management.py sample_data/devices.json --markdown
python Inventory_Management.py sample_data/servers.json --json
```
