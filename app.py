from spyne import Application
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from services.hello import HelloService
from services.auth import AuthService
from services.account import AccountService

application = Application(
    [HelloService, AuthService, AccountService],
    tns='urn:mini.soap',
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11()
)

wsgi_app = WsgiApplication(application)