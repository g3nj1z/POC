import http.server, socketserver, urllib.parse

PORT = 8003
COOKIE_NAME = "sid"
COOKIE_VAL  = "admin"

def alias_for(variant: str) -> str:
    if variant == "zpad":
        return "127.000.000.001"
    if variant == "octal":
        return "0177.0.0.1"
    if variant == "hex":
        return "0x7f000001"
    if variant == "dword":
        return "2130706433"
    return "127.0.0.1"

class H(http.server.BaseHTTPRequestHandler):
    server_version = "BaseHTTP/0.6"
    sys_version = "Python"

    def _write(self, s: str):
        self.wfile.write(s.encode("utf-8"))

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        path = u.path
        qs = urllib.parse.parse_qs(u.query)
        host = self.headers.get("Host","")
        cookie = self.headers.get("Cookie","")

        if path == "/login":
            body = "login ok\n"
            self.send_response(200)
            self.send_header("Set-Cookie", f"{COOKIE_NAME}={COOKIE_VAL}; Path=/")
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self._write(body)
            return

        if path == "/redir":
            variant = (qs.get("variant") or ["zpad"])[0]
            alias = alias_for(variant)
            loc = f"http://{alias}:{PORT}/admin/do"
            self.send_response(302)
            self.send_header("Location", loc)
            self.end_headers()
            return

        if path == "/admin/do":
            lines = [
                "[echo] Path: /admin/do",
                f"[echo] Host: {host}",
                f"[echo] Cookie: {cookie}" if cookie else "[echo] Cookie: (none)",
            ]
            if COOKIE_NAME + "=" + COOKIE_VAL in (cookie or ""):
                lines.append("[ADMIN ACTION EXECUTED]")
            else:
                lines.append("[denied]")
            body = "\n".join(lines) + "\n"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self._write(body)
            return

        self.send_response(404)
        self.end_headers()

    def log_message(self, fmt, *args): pass

if __name__ == "__main__":
    with socketserver.TCPServer(("127.0.0.1", PORT), H) as httpd:
        print(f"[+] admin_server listening on 127.0.0.1:{PORT}")
        httpd.serve_forever()
