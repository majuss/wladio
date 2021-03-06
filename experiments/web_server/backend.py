from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import socketserver
import os


DIR_PATH = os.path.dirname(os.path.abspath(__file__))
INDEX_CONTENT = open(DIR_PATH + '/index.html', 'rb').read()


class S(BaseHTTPRequestHandler):

    def do_GET(self):
        # status melden

        self.send_response(200)
        self.send_header('content-type', 'text/html')
        self.end_headers()

        if self.path == '/':
            self.wfile.write(INDEX_CONTENT)

    def do_POST(self):
        # reaktion anfrage status änderung

        self.send_response(204)

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
