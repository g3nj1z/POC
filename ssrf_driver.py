import http.server, socketserver, subprocess, urllib.parse, shlex

PORT = 8010
JAR = "/tmp/ssrf.jar"

class H(http.server.BaseHTTPRequestHandler):
    def _ok(self, body: bytes):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        if u.path == "/prime":
            cmd = ["curl","-sS","-c",JAR,"http://127.0.0.1:8003/login"]
            out = subprocess.run(cmd, capture_output=True)
            body = b"".join([
                b"== cmd ==\n", " ".join(shlex.quote(c) for c in cmd).encode(),
                b"\n== stdout ==\n",out.stdout,b"\n== stderr ==\n",out.stderr
            ])
            return self._ok(body)

        if u.path == "/fetch":
            qs = urllib.parse.parse_qs(u.query)
            variant = (qs.get("variant") or ["zpad"])[0]
            url = f"http://127.0.0.1:8003/redir?variant={variant}"
            cmd = ["curl","-L","-v","-b",JAR,"-c",JAR,url]
            out = subprocess.run(cmd, capture_output=True)
            body = b"".join([
                b"== cmd ==\n", " ".join(shlex.quote(c) for c in cmd).encode(),
                b"\n== stdout ==\n",out.stdout,b"\n== stderr ==\n",out.stderr
            ])
            return self._ok(body)

        self.send_response(404); self.end_headers()

    def log_message(self, fmt, *args): pass

if __name__ == "__main__":
    with socketserver.TCPServer(("127.0.0.1", PORT), H) as httpd:
        print(f"[+] ssrf_driver listening on 127.0.0.1:{PORT}")
        httpd.serve_forever()
