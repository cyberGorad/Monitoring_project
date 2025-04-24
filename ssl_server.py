import os
import ssl
from django.core.servers.basehttp import WSGIServer, WSGIRequestHandler, get_internal_wsgi_application

# Indique à Django où est ton settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'port_monitor.settings')  # ✅ Ton projet s'appelle bien port_monitor

# SSL
cert_file = "cert.pem"
key_file = "key.pem"
port = 8443

# Contexte SSL
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile=cert_file, keyfile=key_file)

# Lancement serveur
application = get_internal_wsgi_application()
server_address = ('0.0.0.0', port)

httpd = WSGIServer(server_address, WSGIRequestHandler)
httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
httpd.set_app(application)

print(f"🚀 Serveur Django sécurisé lancé sur https://localhost:{port}")
httpd.serve_forever()
