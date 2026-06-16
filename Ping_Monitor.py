import subprocess
import platform
import sys
import os
import logging
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from dataclasses import dataclass
from typing import Optional

MAX_WORKERS   = 50     
TIMEOUT_SEC   = 2      
RETRY_COUNT   = 2      
LOG_FILE      = "ping_monitor.log"
SAVE_LOG      = True   

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IP_FILE = os.path.join(BASE_DIR, "ips.json")

class Color:
    GREEN  = "\033[92m"
    RED    = "\033[91m"
    YELLOW = "\033[93m"
    CYAN   = "\033[96m"
    BOLD   = "\033[1m"
    RESET  = "\033[0m"
    GRAY   = "\033[90m"

def _supports_color() -> bool:
    if platform.system() == "Windows":
        try:
            import ctypes
            kernel = ctypes.windll.kernel32
            kernel.SetConsoleMode(kernel.GetStdHandle(-11), 7)
            return True
        except Exception:
            return False
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

USE_COLOR = _supports_color()

def colorize(text: str, color: str) -> str:
    return f"{color}{text}{Color.RESET}" if USE_COLOR else text

@dataclass
class PingResult:
    ip: str
    is_up: bool
    latency_ms: Optional[float] = None
    attempts: int = 1
    error: Optional[str] = None

def _build_ping_cmd(ip: str, timeout: int) -> list[str]:
    system = platform.system()
    if system == "Windows":
        return ["ping", "-n", "1", "-w", str(timeout * 1000), ip]
    else:  
        return ["ping", "-c", "1", "-W", str(timeout), ip]

def _parse_latency(output: str) -> Optional[float]:
    import re
    patterns = [
        r"time[<=]([\d.]+)\s*ms",
        r"Average\s*=\s*([\d.]+)ms",
        r"(\d+)ms$",
    ]
    for pat in patterns:
        m = re.search(pat, output, re.IGNORECASE | re.MULTILINE)
        if m:
            return float(m.group(1))
    return None

def ping_once(ip: str, timeout: int) -> tuple[bool, Optional[float]]:
    cmd = _build_ping_cmd(ip, timeout)
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=timeout + 1,
            text=True,
        )
        if result.returncode == 0:
            return True, _parse_latency(result.stdout)
        return False, None
    except subprocess.TimeoutExpired:
        return False, None
    except FileNotFoundError:
        raise RuntimeError("Couldn't Find Ping Command")

def ping_with_retry(ip: str, timeout: int, retries: int) -> PingResult:
    for attempt in range(1, retries + 1):
        is_up, latency = ping_once(ip, timeout)
        if is_up:
            return PingResult(ip=ip, is_up=True, latency_ms=latency, attempts=attempt)
    return PingResult(ip=ip, is_up=False, attempts=retries)

def setup_logger(log_file: str) -> logging.Logger:
    logger = logging.getLogger("PingMonitor")
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setFormatter(logging.Formatter("%(asctime)s | %(message)s", "%Y-%m-%d %H:%M:%S"))
    logger.addHandler(fh)
    return logger

def _latency_str(latency: Optional[float]) -> str:
    if latency is None:
        return ""
    color = Color.GREEN if latency < 50 else Color.YELLOW if latency < 150 else Color.RED
    return colorize(f"  ({latency:.1f} ms)", color)

def print_result(res: PingResult) -> None:
    ts = colorize(datetime.now().strftime("%H:%M:%S"), Color.GRAY)
    ip = colorize(f"{res.ip:<20}", Color.BOLD)
    if res.is_up:
        status = colorize("▲  UP", Color.GREEN)
    else:
        status = colorize("▼  DOWN", Color.RED)
    retry_note = colorize(f"  [retry×{res.attempts}]", Color.YELLOW) if res.attempts > 1 else ""
    print(f"[{ts}]  {ip}  {status}{_latency_str(res.latency_ms)}{retry_note}")

def print_summary(results: list[PingResult]) -> None:
    total = len(results)
    up    = sum(1 for r in results if r.is_up)
    down  = total - up
    latencies = [r.latency_ms for r in results if r.is_up and r.latency_ms is not None]
    avg_lat   = sum(latencies) / len(latencies) if latencies else None

    print()
    print(colorize("─" * 45, Color.GRAY))
    print(colorize("  Summary:", Color.BOLD))
    print(f"  Total:    {total}")
    print(f"  {colorize(f'UP:       {up}', Color.GREEN)}")
    print(f"  {colorize(f'DOWN:     {down}', Color.RED)}")
    if avg_lat is not None:
        print(f"  Average latency: {avg_lat:.1f} ms")
    print(colorize("─" * 45, Color.GRAY))

def load_ips(filepath: str) -> list[str]:
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File '{filepath}' not found.")
    
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            if not isinstance(data, list):
                raise ValueError("JSON file must contain a list of IPs/domains.")
            
            ips = [str(item).strip() for item in data if str(item).strip()]
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format in '{filepath}': {e}")
            
    if not ips:
        raise ValueError(f"No IPs found in '{filepath}'.")
    return ips

def main(
    ip_file:    str = IP_FILE,
    max_workers: int = MAX_WORKERS,
    timeout:    int = TIMEOUT_SEC,
    retries:    int = RETRY_COUNT,
    save_log:   bool = SAVE_LOG,
) -> None:
    print(colorize("\n  Ping Monitor", Color.BOLD + Color.CYAN))
    print(colorize(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n", Color.GRAY))

    try:
        ips = load_ips(ip_file)
    except (FileNotFoundError, ValueError) as e:
        print(colorize(f"  Error: {e}", Color.RED))
        sys.exit(1)

    print(colorize(f"  {len(ips)} addresses detected | workers={max_workers} | timeout={timeout}s | retry={retries}\n", Color.GRAY))

    logger = setup_logger(LOG_FILE) if save_log else None

    results: list[PingResult] = [None] * len(ips) 
    with ThreadPoolExecutor(max_workers=min(max_workers, len(ips))) as pool:
        future_to_index = {
            pool.submit(ping_with_retry, ip, timeout, retries): i
            for i, ip in enumerate(ips)
        }
        for future in as_completed(future_to_index):
            idx = future_to_index[future]
            try:
                res = future.result()
            except Exception as exc:
                res = PingResult(ip=ips[idx], is_up=False, error=str(exc))
            results[idx] = res
            print_result(res)
            if logger:
                state = "UP" if res.is_up else "DOWN"
                logger.info(f"{res.ip:<20} {state}  latency={res.latency_ms}ms  attempts={res.attempts}")

    print_summary(results)

    if save_log:
        print(colorize(f"\n  Log saved to '{LOG_FILE}'.", Color.GRAY))

if __name__ == "__main__":
    main()
