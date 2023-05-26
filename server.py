import socket
from _thread import *
import random


# loup garou
class Server:

    def __init__(self):
        
        self.ip = str(input("Ip (default: 127.0.0.1): "))
        if self.ip == "":
            self.ip = "127.0.0.1"

        self.port = str(input("Port (default: 5757): "))
        if self.port == "":
            self.port = 5757
        self.port = int(self.port)

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((self.ip, self.port))

        self.playerMax = int(input("How many players? "))
        self.s.listen()
        print(f"Server started at {self.ip}:{self.port}")

        self.playercount = 0 #define nb of players
        self.data = {
            "players": {},
            "chat": [],
            "turn": "lg"
        }
        self.roles = [] #define roles

        self.playerTurn = 0 #player turn
        self.end = False

        self.defineRoles()


    def clientConn(self, conn, addr):
        self.playercount += 1
        playerdata = {
            "playerID": self.playercount,
            "role": random.choice(self.roles),
            "chat": "global",
            "state": "vivant",
            "action": "sleep",
            "msg": ""
        }
        self.data["players"][self.playercount] = playerdata
        self.roles.remove(playerdata["role"])
        conn.send(str.encode(str(playerdata)))
        reply = ''

        while True:
            try:
                recvData = conn.recv(8192).decode() #receive data from client
                if not recvData:
                    print("Client", addr, ": Disconnected")
                else:
                    
                    self.getData(recvData)
                    sendData = str(self.data) #send data to client
                    reply = str.encode(sendData)

                conn.send(reply)
            except:
                print("Client", addr, ": Lost Connection")
                break

        self.playercount -= 1


    def getData(self, data):
        data = eval(data)
        if data["msg"] != "":
            if data["msg"].startswith("/vote"):
                pass
            elif data["msg"].startswith("/tuer"):
                pass
            elif data["msg"].startswith("/sauver"):
                pass
            else:
                self.data["msg"].append([data["chat"], data["msg"]])


    def nextTurn(self):
        pass


    def connPlayer(self):

        while self.playercount < self.playerMax:
            #wait until a connection is etablished
            conn, addr = self.s.accept()
            print("Client Connected:", addr)

            if self.playercount == 0:
                pass

            #start async connection for client
            start_new_thread(self.clientConn, (conn, addr))


    def defineRoles(self): #init

        pNb = self.playerMax

        nbLG = int(pNb/4)
        pNb -= nbLG

        if pNb > 0: nbCupidon = 1; pNb -= 1
        else: nbCupidon = 0
        if pNb > 0: nbVoyante = 1; pNb -= 1
        else: nbVoyante = 0
        if pNb > 0: nbSorciere = 1; pNb -= 1
        else: nbSorciere = 0
        if pNb > 0: nbChasseur = 1; pNb -= 1
        else: nbChasseur = 0
        if pNb > 0: nbSalvateur = 1; pNb -= 1
        else: nbSalvateur = 0
        if pNb > 0: nbPetiteFille = 1; pNb -= 1
        else: nbPetiteFille = 0

        nbVillageois = pNb

        for i in range(nbLG):
            self.roles.append("Loup Garou")
        for i in range(nbVoyante):
            self.roles.append("Voyante")
        for i in range(nbSorciere):
            self.roles.append("Sorciere")
        for i in range(nbChasseur):
            self.roles.append("Chasseur")
        for i in range(nbCupidon):
            self.roles.append("Cupidon")
        for i in range(nbSalvateur):
            self.roles.append("Salvateur")
        #self.roles.append("Voleur")
        for i in range(nbPetiteFille):
            self.roles.append("Petite Fille")
        for i in range(nbVillageois):
            self.roles.append("Villageois")

        print(self.roles)

    
    def runGame(self):
        if self.data["turn"] == "cupidon":
            for element in self.data["players"]:
                pass



server = Server()
server.connPlayer()
