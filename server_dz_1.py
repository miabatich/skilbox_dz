from twisted.internet import reactor
from twisted.internet.protocol import ServerFactory, connectionDone
from twisted.protocols.basic import LineOnlyReceiver


class ServerProtocol(LineOnlyReceiver):
    factory: 'Server'
    login: str = None

    def connectionMade(self):
        # Потенциальный баг для внимательных =)
        self.factory.clients.append(self)

    def connectionLost(self, reason=connectionDone):
        self.factory.clients.remove(self)

    def lineReceived(self, line: bytes):
        content = line.decode()

        if self.login is not None:
            content = f"Message from {self.login}: {content}"

            for user in self.factory.clients:
                if user is not self:
                    user.sendLine(content.encode())
        else:

            if content.startswith("login:"):
                login = content.replace("login:", "")
                logins = [i.login for i in self.factory.clients]
                if login in logins:
                    error = f"{login} already exists!"
                    self.sendLine(error.encode())
                    login = None
                else:
                    self.login = login
                    self.sendLine("Welcome!".encode())
            else:
                self.sendLine("Invalid login".encode())


class Server(ServerFactory):
    protocol = ServerProtocol
    clients: list

    def startFactory(self):
        self.clients = []
        print("Server started")

    def stopFactory(self):
        print("Server closed")


reactor.listenTCP(1234, Server())
reactor.run()