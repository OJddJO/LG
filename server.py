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
            "turn": "cupidon",
            "gameState": "Démarrage"
        }
        self.roles = [] #define roles

        self.voteStat = {} #vote

        self.playerTurn = 0 #player turn
        self.end = False

        self.defineRoles()


    def clientConn(self, conn, addr):
        playerdata = {
            "playerID": self.playercount,
            "role": random.choice(self.roles),
            "chat": "global",
            "state": "Vivant",
            "msg": "",
            "lover": ""
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
                self.data["chat"].append([data["playerID"], "Liste des commandes: /help, /joueur en vie, /vote [ID joueur], /lgvote [ID joueur], /fleche [ID joueur] [ID joueur], /tuer [ID joueur], /sauver [ID joueur]"])

            elif data["msg"].startswith("/joueurs en vie"):
                alivePlayers = []
                for player in self.data["players"]:
                    if self.data["players"][player]["state"] == "Vivant":
                        alivePlayers.append(player)
                self.data["chat"].append([data["playerID"], f"Joueurs en vie: {alivePlayers}"])

            elif data["msg"].startswith("/vote"): #vote
                if self.data["turn"] == "vote":
                    try:
                        vote = int(data["msg"].split(" ")[1])
                        if vote in self.data["players"]:
                            self.data["players"][data["playerID"]]["state"] = "A voté"
                            self.data["chat"].append([data["playerID"], f"Vous avez voté pour le Joueur {str(vote)}"])
                            if vote not in self.voteStat:
                                self.voteStat[vote] = 1
                            else:
                                self.voteStat[vote] += 1
                            
                            #check if all players voted
                            allVoted = True
                            for player in self.data["players"]:
                                if self.data["players"][player]["state"] == "Vote":
                                    allVoted = False
                            if allVoted:
                                maxVote = max(self.voteStat, key=self.voteStat.get)
                                self.data["chat"].append(["global", f"Le Joueur {str(maxVote)} a été éliminé !"])
                                self.data["players"][maxVote]["state"] = "Mort"
                                self.nextTurn()

                        else:
                            self.data["chat"].append([data["playerID"], "Ce joueur n'existe pas !"])
                    except:
                        self.data["chat"].append([data["playerID"], "Une erreur est survenue ! Veuillez réessayer."])
                else:
                    self.data["chat"].append([data["playerID"], "Vous ne pouvez pas faire cela maintenant !"])

            elif data["msg"].startswith("/lgvote"): #vote loup garou
                pass
            elif data["msg"].startswith("/fleche"): #cupidon
                if self.data["turn"] == "cupidon" and self.data["players"][data["playerID"]]["role"] == "Cupidon":
                    try:
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
                    except:
                        self.data["chat"].append([data["playerID"], "Une erreur est survenue ! Veuillez réessayer."])
                elif self.data["players"][data["playerID"]]["role"] != "Cupidon":
                    self.data["chat"].append([data["playerID"], "Vous n'êtes pas Cupidon !"])
                else:
                    self.data["chat"].append([data["playerID"], "Vous ne pouvez pas faire cela maintenant !"])

            elif data["msg"].startswith("/tuer"): #sorciere
                pass
            elif data["msg"].startswith("/sauver"): #sorciere
                pass
            else: #chat
                self.data["chat"].append([data["chat"], f"[Player {data['playerID']}] {data['msg']}"])


    def nextTurn(self): #change turn
        #check the role that are still alive
        dictRole = {
            "Voyante": False,
            "Salvateur": False,
            "Loup Garou": False,
            "Sorciere": False,
            "Villageois": False,
            "Chasseur": False,
            "Petite Fille": False,
            "Cupidon": False
        }
        for player in self.data["players"]:
            playerRole = self.data["players"][player]["role"]
            if playerRole not in dictRole:
                if self.data["players"][player]["state"] == "Vivant":
                    dictRole[playerRole] = True

        #check if the game is over
        if dictRole["Loup Garou"] == False:
            self.data["gameState"] = "Villageois" #villageois win
            self.data["chat"].append(["global", "Les villageois ont gagné !"])
        elif dictRole["Villageois"] == False and dictRole["Chasseur"] == False and dictRole["Petite Fille"] == False and dictRole["Cupidon"] == False and dictRole["Sorciere"] == False and dictRole["Salvateur"] == False and dictRole["Voyante"] == False:
            self.data["gameState"] = "Loup Garou" #loup garou win
            self.data["chat"].append(["global", "Les loups garous ont gagné !"])
        else:
            turnList = ["vote", "voyante", "salvateur", "lg", "sorciere"]

            #remove the role that are not in the game
            if dictRole["Voyante"] == False:
                turnList.remove("voyante")
            if dictRole["Salvateur"] == False:
                turnList.remove("salvateur")
            if dictRole["Sorciere"] == False:
                turnList.remove("sorciere")

            previousTurn = self.data["turn"]
            #end turn message
            if previousTurn == ["vote"]:
                self.data["chat"].append(["global", "La nuit tombe sur le village..."])
            elif previousTurn == ["voyante"]:
                self.data["chat"].append(["global", "La voyante se rendort..."])
            elif previousTurn == ["salvateur"]:
                self.data["chat"].append(["global", "Le salvateur se rendort..."])
            elif previousTurn == ["lg"]:
                self.data["chat"].append(["global", "Les loups garous se rendorment..."])
            elif previousTurn == ["sorciere"]:
                self.data["chat"].append(["global", "La sorcière se rendort..."])

            #next turn message
            turnIndex = turnList.index(previousTurn) + 1
            if turnIndex == len(turnList):
                turnIndex = 0
            nextTurn = turnList[turnIndex]
            if nextTurn == "vote":
                self.data["chat"].append(["global", "Le jour se lève sur le village..."])
                self.data["chat"].append(["global", "Tout le monde se réveille..."])
                self.data["chat"].append(["global", "Il est temps de voter pour éliminer un joueur !"])
                for player in self.data["players"]:
                    self.data["players"][player]["state"] = "Vote"
            elif nextTurn == "voyante":
                self.data["chat"].append(["global", "La voyante se réveille..."])
                self.data["chat"].append(["global", "Voyante, choisissez un joueur à espionner !"])
            elif nextTurn == "salvateur":
                self.data["chat"].append(["global", "Le salvateur se réveille..."])
                self.data["chat"].append(["global", "Salvateur, choisissez un joueur à protéger !"])
            elif nextTurn == "lg":
                self.data["chat"].append(["global", "Les loups garous se réveillent..."])
                self.data["chat"].append(["global", "Loups Garous, choisissez un joueur à tuer !"])
            elif nextTurn == "sorciere":
                self.data["chat"].append(["global", "La sorcière se réveille..."])
                self.data["chat"].append(["global", "Sorcière, choisissez un joueur à tuer ou à sauver !"])
            self.data["turn"] = nextTurn


    def connPlayer(self):

        while self.playercount != self.playerMax:
            #wait until a connection is etablished
            conn, addr = self.s.accept()
            self.playercount += 1
            print("Client Connected:", addr)

            self.data["chat"].append(["global", f"Player {self.playercount} joined the game !"])

            #start async connection for client
            start_new_thread(self.clientConn, (conn, addr))
        
        self.data["gameState"] = "En jeu"
        self.data["chat"].append(["global", "La partie commence !"])
        self.data["chat"].append(["global", "La nuit tombe sur le village..."])
        self.data["chat"].append(["global", "Cupidon, choisissez deux joueurs à lier avec votre flèche !"])


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
        if len(self.data["chat"]) > 100: #limit chat size to 100
            self.data["chat"].pop(0)


server = Server()
server.connPlayer()
while True:
    server.runGame()
