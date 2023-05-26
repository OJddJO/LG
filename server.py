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
            "chat": [["global", "Bienvenue dans le chat ! Tapez /help pour afficher la liste des commandes"]],
            "turn": "cupidon"
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
            "msg": "",
            "lover": ""
        }
        self.data["players"][self.playercount] = playerdata
        self.roles.remove(playerdata["role"])
        conn.send(str.encode(str(playerdata)))
        reply = ''

        while True:
            try:
                recvData = conn.recv(4096).decode() #receive data from client
                if not recvData:
                    print("Client", addr, ": Disconnected")
                else:
                    
                    self.getData(recvData)
                    sendData = str(self.data) #send data to client
                    reply = str.encode(sendData)

                conn.sendall(reply)
            except Exception as e:
                print("Client", addr, ": Lost Connection")
                print(e)
                break

        self.playercount -= 1


    def getData(self, data):
        data = eval(data)
        if data["msg"] != "":
            if data["msg"].startswith("/help"):
                self.data["chat"].append([data["playerID"], "Liste des commandes: /help, /vote [ID joueur], /lgvote [ID joueur], /fleche [ID joueur] [ID joueur], /tuer [ID joueur], /sauver [ID joueur]"])
            elif data["msg"].startswith("/vote"):
                pass
            elif data["msg"].startswith("/lgvote"):
                pass
            elif data["msg"].startswith("/fleche"):
                if self.data["turn"] == "cupidon" and self.data["players"][data["playerID"]]["role"] == "Cupidon":
                    if data["msg"].split(" ")[1] == data["msg"].split(" ")[2]:
                        self.data["chat"].append([data["playerID"], "Vous ne pouvez pas faire cela !"])
                    else:
                        j1 = int(data["msg"].split(" ")[1])
                        j2 = int(data["msg"].split(" ")[2])
                        self.data["chat"].append([j1, f"Vous êtes touché(e) par la flèche Cupidon ! Vous êtes maintenant follement amoureux du Joueur {str(j2)}. Si l'un de vous meurt, l'autre vous suivra dans la mort !"])
                        self.data["chat"].append([j2, f"Vous êtes touché(e) par la flèche Cupidon ! Vous êtes maintenant follement amoureux du Joueur {str(j1)}. Si l'un de vous meurt, l'autre vous suivra dans la mort !"])
                        self.data["players"][j1]["lover"] = j2
                        self.data["players"][j2]["lover"] = j1
                        self.nextTurn()
                elif self.data["players"][data["playerID"]]["role"] != "Cupidon":
                    self.data["chat"].append([data["playerID"], "Vous n'êtes pas Cupidon !"])
                else:
                    self.data["chat"].append([data["playerID"], "Vous ne pouvez pas faire cela !"])
            elif data["msg"].startswith("/tuer"): #sorciere
                pass
            elif data["msg"].startswith("/sauver"): #sorciere
                pass
            else:
                self.data["chat"].append([data["chat"], f"[Player {data['playerID']}] {data['msg']}"])


    def nextTurn(self):
        currentTurn = self.data["turn"]
        if currentTurn == "cupidon":
            self.data["turn"] = "jour"
        elif currentTurn == "jour":
            self.data["turn"] = "voyante"
        elif currentTurn == "voyante":
            self.data["turn"] = "salvateur"
        elif currentTurn == "salvateur":
            self.data["turn"] = "lg"
        elif currentTurn == "lg":
            self.data["turn"] = "sorciere"
        elif currentTurn == "sorciere":
            self.data["turn"] = "jour"


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
        if self.data["turn"] == "cupidon": # if it's cupidon's turn
            for element in self.data["players"]:
                self.data["players"][element]["action"] = "cupidon"
        
        elif self.data["turn"] == "lg": # if it's loup garou's turn
            for element in self.data["players"]:
                self.data["players"][element]["action"] = "lg"
        
        elif self.data["turn"] == "voyante": # if it's voyante's turn
            for element in self.data["players"]:
                self.data["players"][element]["action"] = "voyante"
        
        elif self.data["turn"] == "sorciere": # if it's sorciere's turn
            for element in self.data["players"]:
                self.data["players"][element]["action"] = "sorciere"
        
        elif self.data["turn"] == "chasseur": # if it's chasseur's turn
            for element in self.data["players"]:
                self.data["players"][element]["action"] = "chasseur"
        
        elif self.data["turn"] == "salvateur": # if it's salvateur's turn
            for element in self.data["players"]:
                self.data["players"][element]["action"] = "salvateur"
        
        elif self.data["turn"] == "petite fille": # if it's petite fille's turn
            for element in self.data["players"]:
                self.data["players"][element]["action"] = "petite fille"
        
        if len(self.data["chat"]) > 100: #limit chat size to 100
            self.data["chat"].pop(0)


server = Server()
server.connPlayer()
