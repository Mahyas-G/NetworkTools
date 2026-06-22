# NetworkTools

in Progress...

## 1) IP_Calculator

An interactive command-line utility for calculating comprehensive IPv4 subnet details. By providing an IP address with its CIDR notation, it quickly generates network boundaries, host ranges, and binary representations.

Features:
- **Network Details:** Automatically calculates Network Address, Broadcast Address, Subnet Mask, and Wildcard Mask.
- **Host Ranges:** Identifies the first and last usable hosts, plus total and usable host counts (with built-in support for `/31` point-to-point and `/32` host routes).
- **IP Classification:** Determines the IP Class (A, B, C, D, E) and flags Private network ranges (RFC 1918).
- **Binary Conversion:** Displays accurate binary representations for the Network, Subnet Mask, and Wildcard Mask.

Usage:

Simply run the script. It will open an interactive prompt where you can enter your IP/CIDR. Type `q` to quit.

```bash
python IP_Calculator.py
```

Example Interaction:

```plaintext
Enter IP/CIDR (or 'q' to quit): 192.168.1.50/24

==================================================
  IP Subnet Calculator
==================================================
  CIDR Notation          192.168.1.0/24
  Network Address        192.168.1.0
  Broadcast Address      192.168.1.255
  Subnet Mask            255.255.255.0
  Wildcard Mask          0.0.0.255
  First Usable Host      192.168.1.1
  Last Usable Host       192.168.1.254
  Total Addresses        256
  Usable Hosts           254
  IP Class               C
  Private Range          Yes (RFC 1918)
--------------------------------------------------
  Binary Representation
  Network                11000000.10101000.00000001.00000000
  Subnet Mask            11111111.11111111.11111111.00000000
  Wildcard Mask          00000000.00000000.00000000.11111111
==================================================
```

## 2) Ping_Monitor

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

Features:
- **Auto-Detection:** Automatically normalizes JSON structures and highlights status fields (`status`, `state`, `health`, etc.).
- **Advanced Filtering:** Chain multiple exact-match conditions using `and` or use free-text search.
- **Export & Formatting:** Output data as plain text tables, Markdown, JSON, or export directly to CSV.
- **Summary Statistics:** Generate visual progress bars and status counts.


Options:

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


Usage:

```bash
python Inventory_Management.py <file.json> [options]
```

Examples:
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
```
```bash
python Inventory_Management.py sample_data/servers.json --json
```
