"""
compile.py — Convert ATS resume HTML to PDF via headless Chrome DevTools Protocol.

Usage:
    python compile.py <html_path> <pdf_path>

Requires: pip install requests websocket-client
"""

import subprocess, os, sys, time, json, base64, threading, shutil
import requests
import websocket

if len(sys.argv) != 3:
    print("Usage: python compile.py <html_path> <pdf_path>")
    sys.exit(1)

html_path = os.path.abspath(sys.argv[1])
pdf_path  = os.path.abspath(sys.argv[2])
port      = 9222
tmp_dir   = os.path.join(os.environ.get("TEMP", r"C:\Temp"), "chrome_pdf_tmp")

# Find Chrome
CHROME_PATHS = [
    os.path.join(os.environ.get("PROGRAMFILES", ""), "Google", "Chrome", "Application", "chrome.exe"),
    os.path.join(os.environ.get("PROGRAMFILES(X86)", ""), "Google", "Chrome", "Application", "chrome.exe"),
    os.path.join(os.environ.get("LOCALAPPDATA", ""), "Google", "Chrome", "Application", "chrome.exe"),
]
chrome = next((p for p in CHROME_PATHS if os.path.exists(p)), None)

if not os.path.exists(html_path):
    print(f"ERROR: HTML file not found: {html_path}")
    sys.exit(1)

if not chrome:
    print("ERROR: Chrome not found. Install Google Chrome or update CHROME_PATHS.")
    sys.exit(1)

if os.path.exists(pdf_path):
    os.remove(pdf_path)
shutil.rmtree(tmp_dir, ignore_errors=True)
os.makedirs(tmp_dir, exist_ok=True)

proc = subprocess.Popen([
    chrome, "--headless", "--disable-gpu", "--no-sandbox",
    f"--remote-debugging-port={port}", f"--user-data-dir={tmp_dir}",
    "--remote-allow-origins=*",
], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

ws_url = None
for _ in range(30):
    time.sleep(0.5)
    try:
        tabs = requests.get(f"http://localhost:{port}/json/list", timeout=2).json()
        pages = [t for t in tabs if t.get("type") == "page"]
        if pages:
            ws_url = pages[0]["webSocketDebuggerUrl"]
            break
    except Exception:
        continue

if not ws_url:
    proc.terminate()
    shutil.rmtree(tmp_dir, ignore_errors=True)
    print("ERROR: Chrome debug server did not start")
    sys.exit(1)

done  = threading.Event()
error = []

def send(ws, id_, method, params=None):
    ws.send(json.dumps({"id": id_, "method": method, "params": params or {}}))

def on_message(ws, msg):
    data   = json.loads(msg)
    mid    = data.get("id")
    method = data.get("method", "")
    if mid == 1:
        send(ws, 2, "Page.navigate",
             {"url": "file:///" + html_path.replace("\\", "/")})
    elif method == "Page.loadEventFired":
        send(ws, 3, "Page.printToPDF", {
            "displayHeaderFooter": False, "printBackground": True,
            "paperWidth": 8.27, "paperHeight": 11.69,
            "marginTop": 0.5, "marginBottom": 0.5,
            "marginLeft": 0.5, "marginRight": 0.5,
        })
    elif mid == 3:
        if "error" in data:
            error.append(str(data["error"]))
        else:
            with open(pdf_path, "wb") as f:
                f.write(base64.b64decode(data["result"]["data"]))
        done.set()

def on_error(ws, err):
    error.append(str(err))
    done.set()

def on_open(ws):
    send(ws, 1, "Page.enable")

ws_app = websocket.WebSocketApp(ws_url, on_open=on_open,
                                on_message=on_message, on_error=on_error)
t = threading.Thread(target=ws_app.run_forever)
t.daemon = True
t.start()

if not done.wait(timeout=30):
    print("ERROR: Timed out waiting for Chrome")
elif error:
    print(f"ERROR: {error[0]}")
else:
    print(f"SUCCESS: {pdf_path}")

ws_app.close()
proc.terminate()
shutil.rmtree(tmp_dir, ignore_errors=True)
