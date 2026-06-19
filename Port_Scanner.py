import socket
import concurrent.futures
import time
import argparse
import json
import sys
from functools import lru_cache

@lru_cache(maxsize=None)
def get_service_name(port):
    try:
        return socket.getservbyport(port, 'tcp')
    except OSError:
        return "Unknown"

def scan_port(ip, port, timeout=0.5):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            
            if result == 0:
                service = get_service_name(port)
                banner = ""
                
                try:
                    if port in [80, 8080]:
                        sock.sendall(b"HEAD / HTTP/1.0\r\n\r\n")
                    
                    sock.settimeout(max(0.5, timeout))
                    raw_data = sock.recv(1024)
                    banner = raw_data.decode('utf-8', errors='ignore').strip()[:60]
                    banner = banner.replace('\r', '').replace('\n', ' ')
                except Exception:
                    pass
                    
                return (port, True, service, banner)
                
            return (port, False, "", "")
    except Exception:
        return (port, False, "", "")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("target")
    parser.add_argument("-s", "--start", type=int, default=1)
    parser.add_argument("-e", "--end", type=int, default=1024)
    parser.add_argument("-w", "--workers", type=int, default=100)
    parser.add_argument("-t", "--timeout", type=float, default=0.5)
    parser.add_argument("-o", "--output", type=str)
    
    args = parser.parse_args()

    if args.start > args.end:
        print("[-] Error: Start port cannot be greater than end port.")
        sys.exit(1)

    try:
        target_ip = socket.gethostbyname(args.target)
    except socket.gaierror:
        print(f"[-] Error: Could not resolve {args.target}")
        sys.exit(1)

    max_workers = min(args.workers, 1000)
    total_ports = args.end - args.start + 1

    print("-" * 70)
    print(f"[*] Target: {target_ip} | Ports: {args.start}-{args.end} | Threads: {max_workers}")
    print("-" * 70)

    open_ports = []
    start_time = time.time()
    scanned_count = 0

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(scan_port, target_ip, port, args.timeout): port 
                for port in range(args.start, args.end + 1)
            }
            
            for future in concurrent.futures.as_completed(futures):
                scanned_count += 1
                progress_percent = (scanned_count / total_ports) * 100
                sys.stdout.write(f"\r[*] Progress: {scanned_count}/{total_ports} ports scanned ({progress_percent:.1f}%)")
                sys.stdout.flush()
                
                port, is_open, service, banner = future.result()
                if is_open:
                    open_ports.append({
                        "port": port,
                        "service": service,
                        "banner": banner
                    })
    except KeyboardInterrupt:
        print("\n\n[!] Scan interrupted by user (Ctrl+C). Exiting gracefully...")
        sys.exit(0)

    end_time = time.time()
    
    print("\n\n[+] Results:")
    if not open_ports:
        print("    No open ports found.")
    else:
        open_ports.sort(key=lambda x: x["port"])
        print(f"    {'PORT':<8} {'STATE':<8} {'SERVICE':<12} {'BANNER'}")
        print("    " + "-" * 50)
        for item in open_ports:
            print(f"    {item['port']:<8} {'OPEN':<8} {item['service']:<12} {item['banner']}")

    if args.output and open_ports:
        try:
            with open(args.output, 'w') as f:
                json.dump(open_ports, f, indent=4)
            print(f"\n[*] Results saved to {args.output}")
        except Exception as e:
            print(f"\n[-] Error saving JSON: {e}")

    print("-" * 70)
    print(f"[*] Scan completed in {end_time - start_time:.2f} seconds.")

if __name__ == "__main__":
    main()
