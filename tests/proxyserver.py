from __future__ import print_function


import sys

try:    # py2
    import SocketServer as socketserver
    from SimpleHTTPServer import SimpleHTTPRequestHandler
    from urllib import urlopen
except ImportError:     # py3
    import socketserver
    from http.server import SimpleHTTPRequestHandler
    from urllib.request import urlopen

    import shutil
    from io import BytesIO


class Proxy(SimpleHTTPRequestHandler):

    def do_GET(self):
        if (2, 7) <= sys.version_info <= (3, 3):
            self.copyfile(urlopen(self.path), self.wfile)
        else:
            shutil.copyfileobj(urlopen(self.path), self.wfile)


if __name__ == "__main__":
    # https://stackoverflow.com/questions/6380057
    PROXY_PORT = int(sys.argv[1])
    proxy_server = socketserver.ThreadingTCPServer(('', PROXY_PORT), Proxy,
                                                   bind_and_activate=False)
    proxy_server.allow_reuse_address = True
    proxy_server.server_bind()
    proxy_server.server_activate()
    print("proxy server ready at http://localhost:%s/" % PROXY_PORT)
    proxy_server.serve_forever()
