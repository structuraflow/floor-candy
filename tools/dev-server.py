import http.server, socketserver, os, functools
ROOT = "/Users/zachriley1206/Projects/floor-candy"
class H(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        p = path.split('?',1)[0].split('#',1)[0]
        fs = os.path.join(ROOT, p.lstrip('/'))
        if p.endswith('/'):
            return os.path.join(fs, 'index.html')
        if not os.path.splitext(fs)[1] and os.path.isfile(fs + '.html'):
            return fs + '.html'
        return fs
    def log_message(self,*a): pass
socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("127.0.0.1", 8899), H) as s:
    s.serve_forever()
