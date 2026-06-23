# NetworkTools

in Progress...

---

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

```text
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

---

## 2) Ping_Monitor

A fast, concurrent ping monitoring tool designed to check the availability and latency of multiple IP addresses or domains simultaneously. It provides real-time, color-coded terminal feedback alongside persistent logging.

Features:
- **High Concurrency:** Utilizes thread pooling to ping multiple hosts in parallel, significantly reducing execution time.
- **Smart Latency Tracking:** Extracts response times and color-codes terminal output based on latency health (Green < 50ms, Yellow < 150ms, Red for high latency).
- **Auto-Retry Mechanism:** Automatically retries failed pings to prevent false negatives before marking a host as DOWN.
- **Cross-Platform & Encoding Safe:** Automatically adjusts native ping commands for Windows or Unix-like systems. Reading targets from a JSON configuration file ensures stable character encoding and prevents reading errors across different environments.
- **Logging & Summary:** Generates a statistical summary at the end of the run and logs all status changes to `ping_monitor.log`.

Configuration:

Create a file named `ips.json` in the same directory as the script containing your list of target IPs or domains:

```json
[
    "8.8.8.8",
    "1.1.1.1",
    "github.com",
    "api.github.com",
    "youtube.com",
    "www.youtube.com",
    "telegram.org",
    "web.telegram.org",
    "9.9.9.9",
    "185.60.216.35",
    "185.60.219.35",
    "google.com",
    "cloudflare.com",
    "dns.google"
]
```

Usage:

```bash
python Ping_Monitor.py
```

Example Output (Outside Iran):

```text

  Ping Monitor
  2015-01-15 09:25:32

  14 addresses detected | workers=50 | timeout=2s | retry=2
  1.1.1.1               ▲  UP  (15.2 ms)
  cloudflare.com        ▲  UP  (16.7 ms)
  dns.google            ▲  UP  (21.9 ms)
  9.9.9.9               ▲  UP  (22.8 ms)
  8.8.8.8               ▲  UP  (24.1 ms)
  google.com            ▲  UP  (25.4 ms)
  www.youtube.com       ▲  UP  (30.2 ms)
  youtube.com           ▲  UP  (30.5 ms)
  github.com            ▲  UP  (45.8 ms)
  api.github.com        ▲  UP  (46.1 ms)
  telegram.org          ▲  UP  (65.3 ms)
  web.telegram.org      ▲  UP  (66.0 ms)
  185.60.219.35         ▲  UP  (110.5 ms)
  185.60.216.35         ▼  DOWN  [retry×2]

─────────────────────────────────────────────
  Summary:
  Total:    14
  UP:       13
  DOWN:     1
  Average latency: 40.0 ms
─────────────────────────────────────────────

  Log saved to 'ping_monitor.log'.
```

---

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

## 4) Inventory_Manager (CLI)

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
python Inventory_Manager.py <file.json> [options]
```

Examples:
1. Basic View
Load and display an inventory file as a formatted table:

```bash
python Inventory_Manager.py sample_data/devices.json
```

3. Search & Sort
Free-text search across all fields and sort descending by a specific column:
```bash
python Inventory_Manager.py sample_data/servers.json --search "prod" --sort=-uptime_days
```

4. Summary Statistics
Skip the table and only display record counts and status distribution:
```bash
python Inventory_Manager.py sample_data/iot_devices.json --stats
```

5. Markdown & JSON Output
Perfect for documentation or piping into other tools:

```bash
python Inventory_Manager.py sample_data/devices.json --markdown
```
```bash
python Inventory_Manager.py sample_data/servers.json --json
```

---

## 5) Backup_Config_Generator

