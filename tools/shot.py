#!/usr/bin/env python3
"""Zero-dependency full-page screenshots over the Chrome DevTools Protocol.

Usage: shot.py <out-dir> <url> <label:width:height> [...]
Chrome is launched headless on a throwaway profile; nothing is installed.
"""
import base64, hashlib, json, os, socket, struct, subprocess, sys, time, urllib.request

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PORT = 9333


class WS:
    def __init__(self, url):
        _, rest = url.split("://", 1)
        hostport, path = rest.split("/", 1)
        host, port = hostport.split(":")
        self.s = socket.create_connection((host, int(port)))
        key = base64.b64encode(os.urandom(16)).decode()
        self.s.sendall((
            f"GET /{path} HTTP/1.1\r\nHost: {hostport}\r\nUpgrade: websocket\r\n"
            f"Connection: Upgrade\r\nSec-WebSocket-Key: {key}\r\n"
            "Sec-WebSocket-Version: 13\r\n\r\n").encode())
        buf = b""
        while b"\r\n\r\n" not in buf:
            buf += self.s.recv(4096)
        self.buf = buf.split(b"\r\n\r\n", 1)[1]
        self.id = 0

    def _recv(self, n):
        while len(self.buf) < n:
            self.buf += self.s.recv(65536)
        out, self.buf = self.buf[:n], self.buf[n:]
        return out

    def send(self, method, params=None):
        self.id += 1
        payload = json.dumps({"id": self.id, "method": method, "params": params or {}}).encode()
        mask = os.urandom(4)
        n = len(payload)
        head = b"\x81"
        if n < 126:
            head += bytes([0x80 | n])
        elif n < 65536:
            head += b"\xfe" + struct.pack(">H", n)
        else:
            head += b"\xff" + struct.pack(">Q", n)
        self.s.sendall(head + mask + bytes(b ^ mask[i % 4] for i, b in enumerate(payload)))
        return self.id

    def frame(self):
        b0, b1 = self._recv(2)
        n = b1 & 0x7F
        if n == 126:
            n = struct.unpack(">H", self._recv(2))[0]
        elif n == 127:
            n = struct.unpack(">Q", self._recv(8))[0]
        return json.loads(self._recv(n))

    def call(self, method, params=None):
        want = self.send(method, params)
        while True:
            msg = self.frame()
            if msg.get("id") == want:
                if "error" in msg:
                    raise RuntimeError(f"{method}: {msg['error']}")
                return msg.get("result", {})


def main():
    out, url, targets = sys.argv[1], sys.argv[2], sys.argv[3:]
    os.makedirs(out, exist_ok=True)
    proc = subprocess.Popen(
        [CHROME, "--headless=new", f"--remote-debugging-port={PORT}",
         "--user-data-dir=/tmp/fc-shot-profile", "--hide-scrollbars",
         "--force-color-profile=srgb", "--disable-gpu", "about:blank"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(60):
            try:
                meta = json.load(urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/version"))
                break
            except Exception:
                time.sleep(.25)
        else:
            raise SystemExit("chrome did not start")

        tabs = json.load(urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/list"))
        page = next(t for t in tabs if t["type"] == "page")
        ws = WS(page["webSocketDebuggerUrl"])
        ws.call("Page.enable")

        for spec in targets:
            label, w, h = spec.split(":")
            w, h = int(w), int(h)
            ws.call("Emulation.setDeviceMetricsOverride", {
                "width": w, "height": h, "deviceScaleFactor": 2,
                "mobile": w < 700, "screenWidth": w, "screenHeight": h})
            ws.call("Page.navigate", {"url": url})
            time.sleep(3.2)
            ws.call("Runtime.evaluate", {"expression":
                "document.querySelectorAll('[data-reveal]').forEach(e=>e.classList.add('is-in'));"
                "window.scrollTo(0,document.body.scrollHeight);"})
            time.sleep(1.4)
            ws.call("Runtime.evaluate", {"expression": "window.scrollTo(0,0)"})
            time.sleep(.8)
            total = ws.call("Runtime.evaluate", {"expression":
                "document.documentElement.scrollHeight", "returnByValue": True})["result"]["value"]
            shots = max(1, min(14, -(-total // h)))
            for i in range(shots):
                y = i * h
                ws.call("Runtime.evaluate", {"expression": f"window.scrollTo(0,{y})"})
                time.sleep(.45)
                res = ws.call("Page.captureScreenshot", {"format": "png"})
                path = os.path.join(out, f"{label}-{i:02d}.png")
                open(path, "wb").write(base64.b64decode(res["data"]))
                print(f"{path}  ({w}x{h} @ y={y})")

    finally:
        proc.terminate()


if __name__ == "__main__":
    main()
