#!/usr/bin/env python3
"""
BitOS Cloud v3 — Serveur optimisé pour Termux (Android)

Usage Termux:
  python bitos-termux.py              # lance sur 0.0.0.0:8765 + ouvre Chrome
  python bitos-termux.py --port 8080  # port custom

Testé sur: TCL60 + Termux + Chrome Android
"""
import argparse, hashlib, http.server, json, os, platform, secrets
import socket, sys, threading, time
import urllib.parse, urllib.request, urllib.error
from http.cookies import SimpleCookie
from pathlib import Path

VERSION = '3.4.3-termux'
DASHBOARD_FILE = 'index.html'
DEFAULT_PORT = 8765
START_TIME = time.time()

# Auth (désactivé par défaut sur Termux — usage local)
AUTH_ENABLED = False
AUTH_PASS_HASH = ''
AUTH_TOKENS = set()

PROXY_RULES = {
    '/proxy/hiveos':    'https://api2.hiveos.farm/api/v2',
    '/proxy/coingecko': 'https://api.coingecko.com/api/v3',
    '/proxy/kaspa':     'https://api.kaspa.org',
    '/proxy/xmr-pool':  'https://supportxmr.com/api',
    '/proxy/kas-pool':  'https://api-kas.k1pool.com/api',
    '/proxy/xmrchain':  'https://xmrchain.net/api',
}

# ── IP detection (Android/Termux compatible) ─────────────────────
def get_device_ip():
    """Get local IP — works on Termux without hostname -I"""
    # Method 1: socket trick (most reliable)
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('8.8.8.8', 80))
            return s.getsockname()[0]
    except Exception:
        pass
    # Method 2: Termux API
    try:
        import subprocess
        r = subprocess.run(['termux-wifi-connectioninfo'], capture_output=True, text=True, timeout=3)
        if r.returncode == 0:
            import json as _j
            info = _j.loads(r.stdout)
            if info.get('ip'): return info['ip']
    except Exception:
        pass
    return '127.0.0.1'

# ── Open browser (Termux-compatible) ─────────────────────────────
def open_browser(url):
    """Open Chrome on Android via Termux, fallback to webbrowser"""
    # Method 1: Termux
    try:
        import subprocess
        subprocess.Popen(['termux-open-url', url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        pass
    # Method 2: am start (Android activity manager)
    try:
        import subprocess
        subprocess.Popen(['am', 'start', '-a', 'android.intent.action.VIEW', '-d', url],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        pass
    # Method 3: standard webbrowser
    try:
        import webbrowser
        webbrowser.open(url)
        return True
    except Exception:
        return False

# ── Kill existing process on port ────────────────────────────────
def kill_port(port):
    """Kill process on port — works without lsof"""
    try:
        import subprocess
        # Try fuser first (available on most Linux/Android)
        subprocess.run(['fuser', '-k', f'{port}/tcp'], capture_output=True, timeout=3)
        time.sleep(0.5)
    except Exception:
        pass

# ── Embedded assets ──────────────────────────────────────────────
def load_or_embed(filename):
    """Try to load from disk, return None if not found"""
    p = Path(filename)
    if p.exists() and p.is_file():
        return p.read_text('utf-8')
    return None

class TermuxHandler(http.server.BaseHTTPRequestHandler):
    embedded_assets = {}

    def log_message(self, fmt, *args):
        if '/proxy/' not in (fmt % args):
            print(f"  {fmt % args}")

    def do_OPTIONS(self):
        self._cors(204); self.end_headers()
    def do_GET(self): self._route('GET')
    def do_POST(self): self._route('POST')
    def do_PUT(self): self._route('PUT')
    def do_DELETE(self): self._route('DELETE')

    def _cors(self, code):
        self.send_response(code)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type,Authorization')

    def _route(self, method):
        path = self.path.split('?')[0]
        if path == '/favicon.ico':
            self.send_error(404); return
        # Proxy
        for prefix, target in PROXY_RULES.items():
            if path == prefix or path.startswith(prefix + '/') or path.startswith(prefix + '?'):
                self._proxy(method, prefix, target); return
        if path.startswith('/proxy/asic/'):
            self._proxy_asic(method, path); return
        # Status
        if path in ('/status', '/api/status'):
            self._status(); return
        if path == '/api/proxy-test':
            self._proxy_test(); return
        # Static
        self._static(path)

    def _proxy(self, method, prefix, target):
        suffix = self.path[len(prefix):]
        if suffix and not suffix.startswith('/') and not suffix.startswith('?'):
            suffix = '/' + suffix
        url = target + suffix
        body = None
        cl = int(self.headers.get('Content-Length', 0))
        if cl > 0: body = self.rfile.read(cl)
        hdrs = {'Accept': 'application/json', 'User-Agent': f'BitOS/{VERSION}'}
        for k in ('Content-Type', 'Authorization'):
            v = self.headers.get(k)
            if v: hdrs[k] = v
        try:
            req = urllib.request.Request(url, data=body, headers=hdrs, method=method)
            with urllib.request.urlopen(req, timeout=15) as r:
                data, ct, status = r.read(), r.headers.get('Content-Type', 'application/json'), r.status
        except urllib.error.HTTPError as e:
            data, ct, status = e.read() or b'{}', 'application/json', e.code
        except Exception as e:
            data = json.dumps({'error': str(e), 'proxy': True}).encode()
            ct, status = 'application/json', 502
        self._cors(status)
        self.send_header('Content-Type', ct)
        self.send_header('Content-Length', len(data))
        self.end_headers(); self.wfile.write(data)

    def _proxy_asic(self, method, path):
        parts = path[len('/proxy/asic/'):].split('/', 1)
        ip = parts[0]; rest = '/' + parts[1] if len(parts) > 1 else '/'
        url = 'http://' + ip + rest
        body = None
        cl = int(self.headers.get('Content-Length', 0))
        if cl > 0: body = self.rfile.read(cl)
        hdrs = {'Accept': 'application/json', 'User-Agent': f'BitOS/{VERSION}',
                'Content-Type': self.headers.get('Content-Type', 'application/json')}
        auth = self.headers.get('Authorization')
        if auth: hdrs['Authorization'] = auth
        try:
            req = urllib.request.Request(url, data=body, headers=hdrs, method=method)
            with urllib.request.urlopen(req, timeout=3) as r:
                data, ct, status = r.read(), r.headers.get('Content-Type', 'application/json'), r.status
        except urllib.error.HTTPError as e:
            data, ct, status = e.read() or b'{}', 'application/json', e.code
        except Exception as e:
            data = json.dumps({'error': str(e), 'asic_ip': ip}).encode()
            ct, status = 'application/json', 502
        self._cors(status)
        self.send_header('Content-Type', ct)
        self.send_header('Content-Length', len(data))
        self.end_headers(); self.wfile.write(data)

    def _static(self, path):
        if path in ('/', ''): path = '/' + DASHBOARD_FILE
        name = path.lstrip('/')
        # Embedded assets first
        if name in self.embedded_assets:
            mime, content = self.embedded_assets[name]
            data = content.encode('utf-8')
            self._cors(200)
            self.send_header('Content-Type', mime)
            self.send_header('Content-Length', len(data))
            self.send_header('Cache-Control', 'no-cache' if name.endswith('.html') else 'max-age=300')
            self.end_headers(); self.wfile.write(data)
            return
        # Disk
        fp = (Path('.') / name).resolve()
        bp = Path('.').resolve()
        if not str(fp).startswith(str(bp)):
            self.send_error(403); return
        if not fp.exists() or not fp.is_file():
            self.send_error(404, f'{name}'); return
        MIMES = {'.html': 'text/html; charset=utf-8', '.js': 'application/javascript; charset=utf-8',
                 '.css': 'text/css; charset=utf-8', '.json': 'application/json',
                 '.png': 'image/png', '.svg': 'image/svg+xml', '.ico': 'image/x-icon'}
        ct = MIMES.get(fp.suffix.lower(), 'application/octet-stream')
        data = fp.read_bytes()
        self._cors(200)
        self.send_header('Content-Type', ct)
        self.send_header('Content-Length', len(data))
        self.end_headers(); self.wfile.write(data)

    def _status(self):
        data = json.dumps({
            'status': 'ok', 'version': VERSION, 'uptime': int(time.time() - START_TIME),
            'device': platform.node(), 'platform': f'{platform.system()} {platform.machine()}',
            'ip': get_device_ip(), 'proxies': list(PROXY_RULES.keys()),
        }, indent=2).encode()
        self._cors(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(data))
        self.end_headers(); self.wfile.write(data)

    def _proxy_test(self):
        results = {}
        for prefix, target in PROXY_RULES.items():
            try:
                req = urllib.request.Request(target + '/', headers={'User-Agent': f'BitOS/{VERSION}'})
                with urllib.request.urlopen(req, timeout=5) as r:
                    results[prefix] = {'ok': True, 'status': r.status}
            except urllib.error.HTTPError as e:
                results[prefix] = {'ok': True, 'status': e.code}
            except Exception as e:
                results[prefix] = {'ok': False, 'error': str(e)[:60]}
        data = json.dumps({'tests': results, 'ok': sum(1 for v in results.values() if v.get('ok'))}, indent=2).encode()
        self._cors(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(data))
        self.end_headers(); self.wfile.write(data)


def main():
    p = argparse.ArgumentParser(description='BitOS Cloud v3 — Termux Edition')
    p.add_argument('--port', type=int, default=DEFAULT_PORT)
    p.add_argument('--no-open', action='store_true', help='Ne pas ouvrir Chrome')
    args = p.parse_args()

    script_dir = Path(__file__).parent.resolve()
    os.chdir(script_dir)

    # Load embedded or disk assets
    embedded = {}
    for name, mime in [('index.html', 'text/html; charset=utf-8'),
                        ('manifest.json', 'application/json'),
                        ('sw.js', 'application/javascript; charset=utf-8')]:
        content = load_or_embed(name)
        if content:
            embedded[name] = (mime, content)
    TermuxHandler.embedded_assets = embedded

    # Check app.js exists
    if not Path('app.js').exists():
        print("\n  app.js introuvable.")
        print("  Placez app.js dans le meme dossier que ce script.")
        sys.exit(1)

    ip = get_device_ip()
    port = args.port
    url = f'http://localhost:{port}'
    lan = f'http://{ip}:{port}'

    kill_port(port)

    print(f"""
  ┌─────────────────────────────────────────────────┐
  │  BitOS Cloud v3 — Termux Edition                │
  │  Optimise pour Android / TCL60                   │
  └─────────────────────────────────────────────────┘

  Dossier  : {script_dir}
  Version  : {VERSION}
  Fichiers : {', '.join(f for f in ['index.html','app.js','manifest.json','sw.js'] if Path(f).exists())}

  ┌─────────────────────────────────────────────────┐
  │  URL locale  : {url:<33}│
  │  URL WiFi    : {lan:<33}│
  └─────────────────────────────────────────────────┘

  Ouvre Chrome sur ton telephone et va sur :
  {url}

  Ctrl+C pour arreter le serveur
""")

    try:
        server = http.server.ThreadingHTTPServer(('0.0.0.0', port), TermuxHandler)
        if not args.no_open:
            threading.Timer(1.0, lambda: open_browser(url)).start()
        server.serve_forever()
    except OSError as e:
        if 'Address already in use' in str(e):
            print(f"\n  Port {port} occupe. Essaie: python bitos-termux.py --port {port+1}")
        else:
            print(f"\n  Erreur: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n  Serveur arrete.\n")

if __name__ == '__main__':
    main()
