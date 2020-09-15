from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import socketserver


class S(BaseHTTPRequestHandler):
    global loop

    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        # status melden

        self._set_response()

        if self.path == '/':
            file_handler = open('index.html', 'rb')
            html_file = file_handler.read()
            file_handler.close()
            self.wfile.write(html_file)

    def do_POST(self):
        # reaktion anfrage status änderung

        self._set_response()

        if self.path == '/garage':
            print("Trigger the relay garage")

        if self.path == '/driveway':
            print("Trigger the relay driveway")


def run(server_class=HTTPServer, handler_class=S, port=50777):
    with socketserver.TCPServer(("", port), S) as httpd:
        print("serving at port", port)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            httpd.server_close()
            socketserver.socket.close()

            pass
        httpd.server_close()


server_thread = threading.Thread(target=run)
server_thread.start()
