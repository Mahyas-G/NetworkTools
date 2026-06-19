# NetworkTools

## Port_Scanner

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
