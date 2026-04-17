#!/usr/bin/env python3
# BitOS Cloud Dashboard v3 — Serveur HTTP Linux
import argparse, getpass, hashlib, http.server, json, os, platform, secrets
import socket, ssl, subprocess, sys, threading, time
import urllib.parse, urllib.request, urllib.error
from http.cookies import SimpleCookie
from pathlib import Path

DASHBOARD_FILE = 'index.html'
DEFAULT_PORT   = 8765
VERSION = '3.4.0'

PROXY_RULES = {
    '/proxy/hiveos':    'https://api2.hiveos.farm/api/v2',
    '/proxy/coingecko': 'https://api.coingecko.com/api/v3',
    '/proxy/kaspa':     'https://api.kaspa.org',
    '/proxy/xmr-pool':  'https://supportxmr.com/api',
    '/proxy/kas-pool':  'https://api-kas.k1pool.com/api',
    '/proxy/xmrchain':  'https://xmrchain.net/api',
}

BANNER = r"""
  ╔══════════════════════════════════════════════════════════╗
  ║   BitOS Cloud v3 — Dashboard Server                      ║
  ╚══════════════════════════════════════════════════════════╝
"""

START_TIME = time.time()
AUTH_ENABLED = False
AUTH_PASS_HASH = ''
AUTH_TOKENS = set()
AUTH_FAIL_COUNT = {}
AUTH_FAIL_LOCK = 5
AUTH_LOCK_TIME = 300
AUTH_FAIL_TIMES = {}

def hash_password(pwd): return hashlib.sha256(pwd.encode('utf-8')).hexdigest()
def generate_token(): return secrets.token_urlsafe(32)

def is_locked(ip):
    if ip not in AUTH_FAIL_COUNT: return False
    if AUTH_FAIL_COUNT[ip] >= AUTH_FAIL_LOCK:
        first_fail = AUTH_FAIL_TIMES.get(ip, 0)
        if time.time() - first_fail < AUTH_LOCK_TIME: return True
        AUTH_FAIL_COUNT.pop(ip, None); AUTH_FAIL_TIMES.pop(ip, None)
    return False

def record_fail(ip):
    AUTH_FAIL_COUNT[ip] = AUTH_FAIL_COUNT.get(ip, 0) + 1
    if ip not in AUTH_FAIL_TIMES: AUTH_FAIL_TIMES[ip] = time.time()

def reset_fails(ip):
    AUTH_FAIL_COUNT.pop(ip, None); AUTH_FAIL_TIMES.pop(ip, None)

LOGIN_PAGE = '''<!DOCTYPE html>
<html lang="fr"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>BitOS — Connexion</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#080c14;color:#e8f0fe;font-family:system-ui,sans-serif;
  display:flex;align-items:center;justify-content:center;min-height:100vh}
.box{background:#0d1421;border:1px solid #1e2d47;border-radius:16px;
  padding:40px 32px;width:100%;max-width:380px;text-align:center}
.logo{width:56px;height:56px;background:linear-gradient(135deg,#00e5ff,#7c3aed);
  border-radius:14px;display:flex;align-items:center;justify-content:center;
  font-size:24px;font-weight:800;color:#fff;margin:0 auto 20px}
h1{font-size:20px;font-weight:800;margin-bottom:6px}
.sub{color:#5a7090;font-size:12px;margin-bottom:28px}
input{width:100%;background:#111a2e;border:1px solid #1e2d47;border-radius:10px;
  padding:14px 16px;color:#e8f0fe;font-size:16px;outline:none;margin-bottom:16px}
input:focus{border-color:#00e5ff}
button{width:100%;background:#00e5ff;color:#080c14;border:none;border-radius:10px;
  padding:14px;font-size:14px;font-weight:800;cursor:pointer}
.err{color:#ff2d55;font-size:12px;margin-top:12px;min-height:18px}
</style></head><body>
<div class="box"><div class="logo">B</div><h1>BitOS Cloud</h1>
<div class="sub">Authentification requise</div>
<form id="f" onsubmit="return go()">
<input type="password" id="p" placeholder="Mot de passe" autofocus>
<button type="submit">Se connecter</button></form>
<div class="err" id="err"><!--ERR--></div></div>
<script>
async function go(){var p=document.getElementById('p').value;if(!p)return false;
try{var r=await fetch('/api/auth',{method:'POST',headers:{'Content-Type':'application/json'},
body:JSON.stringify({password:p})});var d=await r.json();
if(d.ok){window.location.href=d.redirect||'/';}
else{document.getElementById('err').textContent=d.error||'Mot de passe incorrect';
document.getElementById('p').value='';document.getElementById('p').focus();}}
catch(e){document.getElementById('err').textContent='Erreur reseau';}return false;}
</script></body></html>'''

class DashboardHandler(http.server.BaseHTTPRequestHandler):
    log_file = None

    def log_message(self, fmt, *args):
        msg = f"[{self.address_string()}] {fmt % args}"
        if self.log_file:
            with open(self.log_file, 'a') as f: f.write(msg + '\n')
        if '/proxy/' not in (fmt % args):
            print(f"  \033[90m{msg}\033[0m")

    def _check_auth(self):
        if not AUTH_ENABLED: return True
        ip = self.client_address[0]
        if ip in ('127.0.0.1', '::1', 'localhost'): return True
        if is_locked(ip): return False
        ch = self.headers.get('Cookie', '')
        if ch:
            c = SimpleCookie(ch)
            if 'bitosdash_token' in c and c['bitosdash_token'].value in AUTH_TOKENS:
                return True
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)
        if 'token' in qs and qs['token'][0] in AUTH_TOKENS: return True
        return False

    def _send_401(self):
        path = self.path.split('?')[0]
        if path.startswith('/proxy/') or path.startswith('/api/'):
            data = json.dumps({'error':'auth_required','login':'/login'}).encode()
            self.send_response(401)
            self.send_header('Content-Type','application/json')
            self.send_header('Content-Length',len(data))
            self.end_headers(); self.wfile.write(data)
        else:
            self.send_response(302); self.send_header('Location','/login'); self.end_headers()

    def do_OPTIONS(self): self._send_cors(204); self.end_headers()
    def do_GET(self): self._route('GET')
    def do_POST(self): self._route('POST')
    def do_PUT(self): self._route('PUT')
    def do_PATCH(self): self._route('PATCH')
    def do_DELETE(self): self._route('DELETE')

    def _send_cors(self, code):
        self.send_response(code)
        self.send_header('Access-Control-Allow-Origin','*')
        self.send_header('Access-Control-Allow-Methods','GET, POST, PUT, PATCH, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers','Content-Type, Authorization, X-Requested-With')
        self.send_header('Access-Control-Max-Age','86400')

    def _route(self, method):
        path = self.path.split('?')[0]
        if path == '/login': self._serve_login(); return
        if path == '/api/auth' and method == 'POST': self._handle_auth(); return
        if path == '/logout': self._handle_logout(); return
        if path == '/favicon.ico': self.send_error(404); return
        if not self._check_auth(): self._send_401(); return
        self._handle(method)

    def _serve_login(self):
        if not AUTH_ENABLED:
            self.send_response(302); self.send_header('Location','/'); self.end_headers(); return
        ip = self.client_address[0]
        page = LOGIN_PAGE
        if is_locked(ip):
            remain = int(AUTH_LOCK_TIME - (time.time() - AUTH_FAIL_TIMES.get(ip, 0)))
            page = page.replace('<!--ERR-->', f'IP verrouillee — reessayez dans {max(1,remain//60)} min')
        data = page.encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type','text/html; charset=utf-8')
        self.send_header('Content-Length',len(data))
        self.send_header('Cache-Control','no-store')
        self.end_headers(); self.wfile.write(data)

    def _handle_auth(self):
        ip = self.client_address[0]
        if is_locked(ip):
            remain = int(AUTH_LOCK_TIME - (time.time() - AUTH_FAIL_TIMES.get(ip,0)))
            data = json.dumps({'ok':False,'error':f'IP verrouillee — reessayez dans {max(1,remain//60)} min'}).encode()
            self._send_cors(429)
            self.send_header('Content-Type','application/json')
            self.send_header('Content-Length',len(data)); self.end_headers(); self.wfile.write(data); return
        cl = int(self.headers.get('Content-Length',0))
        body = self.rfile.read(cl) if cl > 0 else b'{}'
        try: payload = json.loads(body)
        except Exception: payload = {}
        password = payload.get('password','')
        if hash_password(password) == AUTH_PASS_HASH:
            token = generate_token(); AUTH_TOKENS.add(token); reset_fails(ip)
            data = json.dumps({'ok':True,'redirect':'/'}).encode()
            self._send_cors(200)
            self.send_header('Content-Type','application/json')
            self.send_header('Content-Length',len(data))
            self.send_header('Set-Cookie',f'bitosdash_token={token}; Path=/; HttpOnly; SameSite=Strict; Max-Age=86400')
            self.end_headers(); self.wfile.write(data)
            print(f"  Connexion reussie depuis {ip}")
        else:
            record_fail(ip)
            remaining = AUTH_FAIL_LOCK - AUTH_FAIL_COUNT.get(ip,0)
            if is_locked(ip):
                msg = f'IP verrouillee — {AUTH_FAIL_LOCK} echecs — reessayez dans 5 min'
            else:
                msg = f'Mot de passe incorrect ({remaining} tentative(s) restante(s))'
            data = json.dumps({'ok':False,'error':msg}).encode()
            self._send_cors(401)
            self.send_header('Content-Type','application/json')
            self.send_header('Content-Length',len(data)); self.end_headers(); self.wfile.write(data)

    def _handle_logout(self):
        ch = self.headers.get('Cookie','')
        if ch:
            c = SimpleCookie(ch)
            if 'bitosdash_token' in c: AUTH_TOKENS.discard(c['bitosdash_token'].value)
        self.send_response(302)
        self.send_header('Location','/login')
        self.send_header('Set-Cookie','bitosdash_token=; Path=/; Max-Age=0')
        self.end_headers()

    def _handle(self, method):
        path = self.path.split('?')[0]
        for prefix, target in PROXY_RULES.items():
            if path == prefix or path.startswith(prefix+'/') or path.startswith(prefix+'?'):
                self._proxy(method, prefix, target); return
        if path.startswith('/proxy/asic/'): self._proxy_asic(method, path); return
        if path in ('/status','/api/status'): self._serve_status(); return
        if path == '/api/proxy-test': self._serve_proxy_test(); return
        self._serve_static(path)

    def _proxy(self, method, prefix, target):
        suffix = self.path[len(prefix):]
        if suffix and not suffix.startswith('/') and not suffix.startswith('?'):
            suffix = '/' + suffix
        url = target + suffix
        body = None
        cl = int(self.headers.get('Content-Length',0))
        if cl > 0: body = self.rfile.read(cl)
        req_headers = {'Accept':'application/json','User-Agent':f'BitOS-Cloud-Dashboard/{VERSION}'}
        for k in ('Content-Type','Authorization'):
            v = self.headers.get(k)
            if v: req_headers[k] = v
        try:
            req = urllib.request.Request(url, data=body, headers=req_headers, method=method)
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = resp.read()
                ct = resp.headers.get('Content-Type','application/json')
                status = resp.status
        except urllib.error.HTTPError as e:
            data = e.read() or b'{}'; ct = 'application/json'; status = e.code
        except Exception as e:
            data = json.dumps({'error':str(e),'proxy':True,'url':url}).encode()
            ct = 'application/json'; status = 502
        self._send_cors(status)
        self.send_header('Content-Type',ct)
        self.send_header('Content-Length',len(data))
        self.send_header('X-Proxy-By','BitOS-Server')
        self.end_headers(); self.wfile.write(data)

    def _serve_static(self, path):
        if path in ('/',''): path = '/' + DASHBOARD_FILE
        file_path = (Path('.') / path.lstrip('/')).resolve()
        base_path = Path('.').resolve()
        if not str(file_path).startswith(str(base_path)):
            self.send_error(403,'Acces refuse'); return
        if not file_path.exists() or not file_path.is_file():
            self.send_error(404,f'Non trouve: {path}'); return
        MIME = {'.html':'text/html; charset=utf-8','.js':'application/javascript; charset=utf-8',
            '.css':'text/css; charset=utf-8','.json':'application/json','.png':'image/png',
            '.ico':'image/x-icon','.svg':'image/svg+xml','.woff2':'font/woff2','.woff':'font/woff',
            '.txt':'text/plain; charset=utf-8','.md':'text/markdown; charset=utf-8'}
        ext = file_path.suffix.lower()
        mime = MIME.get(ext,'application/octet-stream')
        data = file_path.read_bytes()
        self._send_cors(200)
        self.send_header('Content-Type',mime)
        self.send_header('Content-Length',len(data))
        cache = 'no-cache' if ext == '.html' else 'max-age=300'
        self.send_header('Cache-Control',cache)
        self.end_headers(); self.wfile.write(data)

    def _serve_status(self):
        data = json.dumps({'status':'ok','version':VERSION,'file':DASHBOARD_FILE,
            'proxies':list(PROXY_RULES.keys()),'uptime':int(time.time()-START_TIME),
            'host':socket.gethostname(),'platform':platform.system(),'lan_ip':get_lan_ip(),
            'cors':'enabled','auth':AUTH_ENABLED,'sessions':len(AUTH_TOKENS)},indent=2).encode()
        self._send_cors(200)
        self.send_header('Content-Type','application/json')
        self.send_header('Content-Length',len(data))
        self.end_headers(); self.wfile.write(data)

    def _proxy_asic(self, method, path):
        parts = path[len('/proxy/asic/'):].split('/',1)
        asic_ip = parts[0]
        rest = '/' + parts[1] if len(parts) > 1 else '/'
        target_url = 'http://' + asic_ip + rest
        body = None
        cl = int(self.headers.get('Content-Length',0))
        if cl > 0: body = self.rfile.read(cl)
        req_headers = {'Accept':'application/json, text/html, */*',
            'User-Agent':f'BitOS-Cloud-Dashboard/{VERSION}',
            'Content-Type':self.headers.get('Content-Type','application/json')}
        auth = self.headers.get('Authorization')
        if auth: req_headers['Authorization'] = auth
        try:
            req = urllib.request.Request(target_url, data=body, headers=req_headers, method=method)
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = resp.read(); ct = resp.headers.get('Content-Type','application/json'); status = resp.status
        except urllib.error.HTTPError as e:
            data = e.read() or b'{}'; ct = 'application/json'; status = e.code
        except Exception as e:
            data = json.dumps({'error':str(e),'asic_ip':asic_ip,'proxy':True}).encode()
            ct = 'application/json'; status = 502
        self._send_cors(status)
        self.send_header('Content-Type',ct)
        self.send_header('Content-Length',len(data))
        self.send_header('X-Proxy-ASIC',asic_ip)
        self.end_headers(); self.wfile.write(data)

    def _serve_proxy_test(self):
        results = {}
        for prefix, target in PROXY_RULES.items():
            try:
                req = urllib.request.Request(target+'/',
                    headers={'User-Agent':f'BitOS-Cloud-Dashboard/{VERSION}'}, method='GET')
                with urllib.request.urlopen(req, timeout=5) as resp:
                    results[prefix] = {'ok':True,'status':resp.status,'target':target}
            except urllib.error.HTTPError as e:
                results[prefix] = {'ok':True,'status':e.code,'target':target}
            except Exception as e:
                results[prefix] = {'ok':False,'error':str(e)[:80],'target':target}
        data = json.dumps({'proxy_tests':results,'timestamp':int(time.time()),
            'total':len(results),'ok':sum(1 for v in results.values() if v.get('ok'))},indent=2).encode()
        self._send_cors(200)
        self.send_header('Content-Type','application/json')
        self.send_header('Content-Length',len(data))
        self.end_headers(); self.wfile.write(data)

def print_qr(url):
    try:
        import qrcode
        qr = qrcode.QRCode(border=1); qr.add_data(url); qr.make(fit=True)
        print(); qr.print_ascii(invert=True)
    except ImportError:
        print(f"\n  Acces mobile : {url}")

def watchdog(interval=2):
    last_mtime = 0
    while True:
        try:
            mtime = Path(DASHBOARD_FILE).stat().st_mtime
            if last_mtime and mtime != last_mtime:
                print(f"\n  {DASHBOARD_FILE} modifie — rafraichissez le navigateur")
            last_mtime = mtime
        except FileNotFoundError: pass
        time.sleep(interval)

def create_ssl_context():
    cert = Path('/tmp/bitosdash_cert.pem'); key = Path('/tmp/bitosdash_key.pem')
    if not cert.exists():
        try:
            subprocess.run(['openssl','req','-x509','-newkey','rsa:2048',
                '-keyout',str(key),'-out',str(cert),'-days','365','-nodes',
                '-subj','/CN=localhost/O=BitOS/C=FR'], check=True, capture_output=True)
            print("  Certificat auto-signe genere")
        except Exception as e:
            print(f"  HTTPS impossible: {e}"); return None
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(str(cert), str(key))
    return ctx

def get_lan_ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('8.8.8.8', 80)); return s.getsockname()[0]
    except Exception: return '127.0.0.1'

def main():
    global AUTH_ENABLED, AUTH_PASS_HASH
    parser = argparse.ArgumentParser(description='BitOS Cloud Dashboard v3')
    parser.add_argument('--port', type=int, default=DEFAULT_PORT)
    parser.add_argument('--host', type=str, default='')
    parser.add_argument('--lan', action='store_true')
    parser.add_argument('--qr', action='store_true')
    parser.add_argument('--https', action='store_true')
    parser.add_argument('--open', action='store_true')
    parser.add_argument('--log', type=str, default='')
    parser.add_argument('--no-watch', action='store_true')
    parser.add_argument('--password', type=str, default='')
    parser.add_argument('--no-auth', action='store_true')
    args = parser.parse_args()

    script_dir = Path(__file__).parent.resolve()
    os.chdir(script_dir)
    if not Path(DASHBOARD_FILE).exists():
        print(f"\n  '{DASHBOARD_FILE}' introuvable dans {script_dir}"); sys.exit(1)

    if args.lan and not args.no_auth:
        AUTH_ENABLED = True
        if args.password: pwd = args.password
        else:
            print("\n  Mode LAN — mot de passe requis\n")
            pwd = getpass.getpass("  Mot de passe BitOS : ")
            if not pwd: print("  Mot de passe vide — abandon."); sys.exit(1)
            pwd2 = getpass.getpass("  Confirmer :          ")
            if pwd != pwd2: print("  Les mots de passe ne correspondent pas."); sys.exit(1)
        AUTH_PASS_HASH = hash_password(pwd); pwd = '***'

    host = args.host or ('0.0.0.0' if args.lan else '127.0.0.1')
    port = args.port
    proto = 'https' if args.https else 'http'
    lan_ip = get_lan_ip()
    local_url = f"{proto}://localhost:{port}"
    lan_url = f"{proto}://{lan_ip}:{port}"

    if args.log: DashboardHandler.log_file = args.log

    print(BANNER)
    print(f"  Repertoire : {script_dir}")
    print(f"  Dashboard  : {DASHBOARD_FILE}")
    print(f"  Auth       : {'activee' if AUTH_ENABLED else 'desactivee'}")
    print(f"  Local      : {local_url}")
    if args.lan: print(f"  LAN        : {lan_url}")

    if args.qr: print_qr(lan_url if args.lan else local_url)

    if not args.no_watch:
        threading.Thread(target=watchdog, daemon=True).start()

    try:
        server = http.server.ThreadingHTTPServer((host, port), DashboardHandler)
        if args.https:
            ctx = create_ssl_context()
            if ctx:
                server.socket = ctx.wrap_socket(server.socket, server_side=True)
                print(f"\n  HTTPS active")
        print(f"\n  Serveur demarre — Ctrl+C pour arreter\n")
        if args.open:
            import webbrowser
            threading.Timer(0.8, lambda: webbrowser.open(local_url)).start()
        server.serve_forever()
    except PermissionError:
        print(f"\n  Port {port} refuse"); sys.exit(1)
    except OSError as e:
        if 'Address already in use' in str(e):
            print(f"\n  Port {port} deja utilise")
        else: print(f"\n  Erreur reseau: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n  Serveur arrete\n")

if __name__ == '__main__':
    main()
