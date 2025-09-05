from wsgiref.simple_server import make_server
from app import wsgi_app

if __name__ == "__main__":
    server = make_server("127.0.0.1", 8000, wsgi_app)
    print("SOAP server is running at http://127.0.0.1/?wsdl")
    server.serve_forever()
    