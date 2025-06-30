import json
import random
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs


DATA = {
    "temperature": 0.0,
    "humidity": 0.0,
    "gas_alert": False,
    "pump": False,
}


class SensorReader(threading.Thread):
    def __init__(self, data: dict) -> None:
        super().__init__(daemon=True)
        self.data = data

    def run(self) -> None:
        while True:
            # In a real environment, replace these lines with GPIO sensor reads
            self.data["temperature"] = round(random.uniform(20.0, 30.0), 1)
            self.data["humidity"] = round(random.uniform(40.0, 60.0), 1)
            self.data["gas_alert"] = random.random() < 0.1
            time.sleep(2)


class LabRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path.startswith("/data"):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(DATA).encode())
        else:
            self.send_error(404)

    def do_POST(self) -> None:
        if self.path.startswith("/pump"):
            qs = parse_qs(urlparse(self.path).query)
            state = qs.get("state", [""])[0]
            if state == "on":
                DATA["pump"] = True
            elif state == "off":
                DATA["pump"] = False
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"pump": DATA["pump"]}).encode())
        else:
            self.send_error(404)


def main() -> None:
    SensorReader(DATA).start()
    server = HTTPServer(("0.0.0.0", 8000), LabRequestHandler)
    print("Lab server running on port 8000")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
