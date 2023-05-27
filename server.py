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
        if self.playerMax < 4:
            raise Exception("Not enough players !")
        self.s.listen()
        print(f"Server started at {self.ip}:{self.port}")

        self.playercount = 0 #define nb of players
        self.data = {
            "players": {},
            "chat": [["Global", "Bienvenue dans le chat ! Tapez /help pour afficher la liste des commandes"]],
            "turn": "cupidon",
            "gameState": f"Démarrage ({self.playercount}/{self.playerMax})",
        }
        self.roles = [] #define roles

        self.voteStat = {} #vote
        self.nightEvent = {} #night event
        self.sorcierePot = ['kill', 'save']

        self.lastProtected = 0

        self.defineRoles()


    def clientConn(self, conn, addr):
        playerdata = {
            "playerID": self.playercount,
            "role": random.choice(self.roles),
            "chat": "Global",
            "state": "Vivant",
            "msg": "",
            "lover": "",
            "protected": False
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
                self.data["chat"].append([data["playerID"], "Liste des commandes: /help, /joueurs en vie, /vote [ID joueur]|blanc\n - Loup Garou: /lg, /chat, /lgvote [ID joueur]\n - Cupidon: /amour [ID joueur] [ID joueur]\n - Salvateur: /proteger [ID joueur]\n - Sorciere: /tuer [ID joueur], /sauver, /ne rien faire\n - Voyante: /voyante [ID joueur]\n - Chasseur: /chasseur [ID joueur]"])

            elif data["msg"].startswith("/joueurs en vie"):
                alivePlayers = []
                for player in self.data["players"]:
                    if self.data["players"][player]["state"] == "Vivant":
                        alivePlayers.append(player)
                self.data["chat"].append([data["playerID"], f"Joueurs en vie: {alivePlayers}"])

            elif data["msg"].startswith("/vote"): #vote
                if self.data["turn"] == "vote" and self.data["players"][data["playerID"]]["state"] == "Vote":
                    try:
                        vote = data["msg"].split(" ")[1]
                        if int(vote) in self.data["players"] or vote == "blanc":
                            self.data["players"][data["playerID"]]["state"] = "Vivant"
                            if vote == "blanc":
                                self.data["chat"].append(["Global", f"Le Joueur {str(data['playerID'])} a voté blanc !"])
                                vote = 0
                            else:
                                self.data["chat"].append(["Global", f"Le Joueur {str(data['playerID'])} a voté pour le Joueur {str(vote)}"])
                            vote = int(vote)
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
                                if maxVote == 0:
                                    self.data["chat"].append(["Global", f"Le vote est terminé ! Personne n'a été éliminé !"])
                                else:
                                    self.data["chat"].append(["Global", f"Le vote est terminé ! Le Joueur {str(maxVote)} a été éliminé ! Il était {self.data['players'][maxVote]['role']} !"])
                                    self.data["players"][maxVote]["state"] = "Mort"
                                self.nextTurn()

                        else:
                            self.data["chat"].append([data["playerID"], "Ce joueur n'existe pas !"])
                    except Exception as e:
                        self.data["chat"].append([data["playerID"], "Une erreur est survenue ! Veuillez réessayer."])
                        print(e)
                else:
                    self.data["chat"].append([data["playerID"], "Vous ne pouvez pas faire cela maintenant !"])
            
            elif data["msg"].startswith("/proteger"): #salvateur
                if self.data["turn"] == "salvateur":
                    if data["role"] == "Salvateur":
                        try:
                            protect = int(data["msg"].split(" ")[1])
                            if protect in self.data["players"]:
                                self.data["players"][protect]["protected"] = True
                                self.data["chat"].append([protect, f"Le Salvateur vous a protégé !"])
                                self.nextTurn()
                            else:
                                self.data["chat"].append([data["playerID"], "Ce joueur n'existe pas !"])
                        except Exception as e:
                            self.data["chat"].append([data["playerID"], "Une erreur est survenue ! Veuillez réessayer."])
                            print(e)
                    else:
                        self.data["chat"].append([data["playerID"], "Vous n'êtes pas Salvateur !"])
                else:
                    self.data["chat"].append([data["playerID"], "Vous ne pouvez pas faire cela maintenant !"])

            elif data["msg"].startswith("/voyante"): #voyante
                if self.data["turn"] == "voyante":
                    if data["role"] == "Voyante":
                        try:
                            check = int(data["msg"].split(" ")[1])
                            if check in self.data["players"]:
                                self.data["chat"].append([data["playerID"], f"Le joueur {str(check)} est {self.data['players'][check]['role']} !"])
                                self.nextTurn()
                            else:
                                self.data["chat"].append([data["playerID"], "Ce joueur n'existe pas !"])
                        except Exception as e:
                            self.data["chat"].append([data["playerID"], "Une erreur est survenue ! Veuillez réessayer."])
                            print(e)
                    else:
                        self.data["chat"].append([data["playerID"], "Vous n'êtes pas Voyante !"])
                else:
                    self.data["chat"].append([data["playerID"], "Vous ne pouvez pas faire cela maintenant !"])

            elif data["msg"].startswith("/chat"): #change chat for lg
                if data["role"] == "Loup Garou":
                    if data["chat"] == "Loup Garou":
                        self.data["players"][data["playerID"]]["chat"] = "Global"
                        self.data["chat"].append([data["playerID"], "Vous êtes maintenant dans le chat Global !"])
                    else:
                        self.data["players"][data["playerID"]]["chat"] = "Loup Garou"
                        self.data["chat"].append([data["playerID"], "Vous êtes maintenant dans le chat des Loups Garous !"])
                else:
                    self.data["chat"].append([data["playerID"], "Vous n'êtes pas Loup Garou !"])

            elif data["msg"].startswith("/lgvote"): #vote loup garou
                if self.data["turn"] == "lg":
                    if data["role"] == "Loup Garou":
                        try:
                            vote = int(data["msg"].split(" ")[1])
                            if vote in self.data["players"]:
                                self.data["players"][data["playerID"]]["state"] = "Vivant"
                                self.data["chat"].append(["Loup Garou", f"Le Loup Garou {str(data['playerID'])} a voté pour le Joueur {str(vote)}"])
                                self.data["chat"].append(["Petite Fille", f"Le Loup Garou {str(data['playerID'])} a voté pour le Joueur {str(vote)}"])
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
                                    self.data["chat"].append(["Loup Garou", f"Tous les Loups Garous ont voté !"])
                                    self.data["chat"].append(["Petite Fille", f"Tous les Loups Garous ont voté !"])
                                    maxVote = max(self.voteStat, key=self.voteStat.get)
                                    if not self.data["players"][maxVote]["protected"]:
                                        self.data["players"][maxVote]["state"] = "Mort"
                                        self.nightEvent["lg"] = maxVote
                                    else:
                                        self.nightEvent["lg"] = "none"
                                    self.nextTurn()
                            else:
                                self.data["chat"].append([data["playerID"], "Ce joueur n'existe pas !"])
                        except Exception as e:
                            self.data["chat"].append([data["playerID"], "Une erreur est survenue ! Veuillez réessayer."])
                            print(e)
                    else:
                        self.data["chat"].append([data["playerID"], "Vous n'êtes pas Loup Garou !"])
                else:
                    self.data["chat"].append([data["playerID"], "Vous ne pouvez pas faire cela maintenant !"])

            elif data["msg"].startswith("/amour"): #cupidon
                if self.data["turn"] == "cupidon" and self.data["players"][data["playerID"]]["role"] == "Cupidon":
                    try:
                        if data["msg"].split(" ")[1] == data["msg"].split(" ")[2]:
                            self.data["chat"].append([data["playerID"], "Vous ne pouvez pas faire cela !"])
                        else:
                            j1 = int(data["msg"].split(" ")[1])
                            j2 = int(data["msg"].split(" ")[2])
                            self.data["chat"].append([j1, f"Vous êtes touché(e) par la flèche Cupidon ! Vous êtes maintenant follement amoureux/amoureuse du Joueur {str(j2)}. Si l'un de vous meurt, l'autre vous suivra dans la mort !"])
                            self.data["chat"].append([j2, f"Vous êtes touché(e) par la flèche Cupidon ! Vous êtes maintenant follement amoureux/amoureuse du Joueur {str(j1)}. Si l'un de vous meurt, l'autre vous suivra dans la mort !"])
                            self.data["players"][j1]["lover"] = j2
                            self.data["players"][j2]["lover"] = j1
                            self.nextTurn()
                    except Exception as e:
                        self.data["chat"].append([data["playerID"], "Une erreur est survenue ! Veuillez réessayer."])
                        print(e)
                elif self.data["players"][data["playerID"]]["role"] != "Cupidon":
                    self.data["chat"].append([data["playerID"], "Vous n'êtes pas Cupidon !"])
                else:
                    self.data["chat"].append([data["playerID"], "Vous ne pouvez pas faire cela maintenant !"])

            elif data["msg"].startswith("/tuer"): #sorciere
                if self.data["turn"] == "sorciere" and self.data["players"][data["playerID"]]["role"] == "Sorciere":
                    if "kill" in self.sorcierePot:
                        try:
                            j = int(data["msg"].split(" ")[1])
                            if self.data["players"][j]["state"] == "Mort":
                                self.data["chat"].append([data["playerID"], "Ce joueur est déjà mort !"])
                            else:
                                #check if player is protected
                                if not self.data["players"][j]["protected"]:
                                    self.data["players"][j]["state"] = "Mort"
                                    self.data["chat"].append([data["playerID"], f"Vous avez tué le joueur {j} !"])
                                    self.nightEvent["sorciere"] = ["kill", j]
                                    self.sorcierePot.remove("kill")
                                else:
                                    self.data["chat"].append([data["playerID"], "Ce joueur était protégé !"])

                                self.nextTurn()
                        except:
                            self.data["chat"].append([data["playerID"], "Une erreur est survenue ! Veuillez réessayer."])
                    else:
                        self.data["chat"].append([data["playerID"], "Vous avez déjà utilisé ce pouvoir !"])
                elif self.data["players"][data["playerID"]]["role"] != "Sorciere":
                    self.data["chat"].append([data["playerID"], "Vous n'êtes pas Sorcière !"])
                else:
                    self.data["chat"].append([data["playerID"], "Vous ne pouvez pas faire cela maintenant !"])

            elif data["msg"].startswith("/sauver"): #sorciere
                if self.data["turn"] == "sorciere" and self.data["players"][data["playerID"]]["role"] == "Sorciere":
                    if "save" in self.sorcierePot:
                        try:
                            j = self.nightEvent["lg"]
                            if self.data["players"][j]["state"] == "Mort":
                                self.data["players"][j]["state"] = "Vivant"
                                self.data["chat"].append([data["playerID"], f"Vous avez sauvé le joueur {j} !"])
                                self.nightEvent["sorciere"] = ["save", j]
                                self.sorcierePot.remove("save")
                                self.nextTurn()
                            else:
                                self.data["chat"].append([data["playerID"], "Ce joueur n'est pas mort !"])
                        except Exception as e:
                            self.data["chat"].append([data["playerID"], "Une erreur est survenue ! Veuillez réessayer."])
                            print(e)
                    else:
                        self.data["chat"].append([data["playerID"], "Vous avez déjà utilisé ce pouvoir !"])
                elif self.data["players"][data["playerID"]]["role"] != "Sorciere":
                    self.data["chat"].append([data["playerID"], "Vous n'êtes pas Sorcière !"])
                else:
                    self.data["chat"].append([data["playerID"], "Vous ne pouvez pas faire cela maintenant !"])

            elif data["msg"].startswith("/ne rien faire"): #sorciere
                if self.data["turn"] == "sorciere":
                    if self.data["players"][data["playerID"]]["role"] == "Sorciere":
                        self.nightEvent["sorciere"] = ["nothing", 0]
                        self.nextTurn()
                    else:
                        self.data["chat"].append([data["playerID"], "Vous n'êtes pas Sorcière !"])
                else:
                    self.data["chat"].append([data["playerID"], "Vous ne pouvez pas faire cela maintenant !"])

            elif data["msg"].startswith("/lg"): #show the list of loup garou only if you are a loup garou
                if data["role"] == "Loup Garou":
                    lgList = []
                    for player in self.data["players"]:
                        if self.data["players"][player]["role"] == "Loup Garou":
                            lgList.append(player)
                    self.data["chat"].append([data["playerID"], f"Liste des Loups Garous: {lgList}"])
                else:
                    self.data["chat"].append([data["playerID"], "Vous n'êtes pas Loup Garou !"])

            elif data["msg"].startswith("/chasseur"): #chasseur
                if self.data["turn"] == "chasseur":
                    if data["role"] == "Chasseur":
                        try:
                            kill = int(data["msg"].split(" ")[1])
                            if kill in self.data["players"] and self.data["players"][kill]["state"] == "Vivant":
                                self.data["players"][kill]["state"] = "Mort"
                                self.data["chat"].append(["Globzl", f"Le Chasseur a tué le joueur {kill} ! Il était {self.data['players'][kill]['role']} !"])
                                self.nextTurn()
                            else:
                                self.data["chat"].append([data["playerID"], "Ce joueur n'existe pas !"])
                        except Exception as e:
                            self.data["chat"].append([data["playerID"], "Une erreur est survenue ! Veuillez réessayer."])
                            print(e)
                    else:
                        self.data["chat"].append([data["playerID"], "Vous n'êtes pas Chasseur !"])
                else:
                    self.data["chat"].append([data["playerID"], "Vous ne pouvez pas faire cela maintenant !"])

            elif data["msg"].startswith("/"): #unknown command
                self.data["chat"].append([data["playerID"], "Cette commande n'existe pas !"])
                self.data["chat"].append([data["playerID"], "Liste des commandes: /help, /joueurs en vie, /vote [ID joueur]|blanc\n - Loup Garou: /lg, /chat, /lgvote [ID joueur]\n - Cupidon: /amour [ID joueur] [ID joueur]\n - Salvateur: /proteger [ID joueur]\n - Sorciere: /tuer [ID joueur], /sauver, /ne rien faire\n - Voyante: /voyante [ID joueur]\n - Chasseur: /chasseur [ID joueur]"])
            else: #chat
                self.data["chat"].append([data["chat"], f"[{data['chat']}] [Joueur {data['playerID']}] {data['msg']}"])


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
            if self.data["players"][player]["state"] == "Vivant":
                dictRole[playerRole] = True

        turnList = ["jour", "vote", "voyante", "salvateur", "lg", "sorciere"]

        #remove the role that are not in the game
        if dictRole["Voyante"] == False:
            turnList.remove("voyante")
        if dictRole["Salvateur"] == False:
            turnList.remove("salvateur")
        if dictRole["Sorciere"] == False or self.sorcierePot == []:
            turnList.remove("sorciere")

        previousTurn = self.data["turn"]
        #end turn message
        if previousTurn == "vote":
            #check if the game is over
            if dictRole["Loup Garou"] == False:
                self.data["gameState"] = "Victoire des Villageois" #villageois win
                self.data["chat"].append(["Global", "Les villageois ont gagné !"])
                return
            elif dictRole["Villageois"] == False and dictRole["Chasseur"] == False and dictRole["Petite Fille"] == False and dictRole["Cupidon"] == False and dictRole["Sorciere"] == False and dictRole["Salvateur"] == False and dictRole["Voyante"] == False:
                self.data["gameState"] = "Victoire des Loups Garous" #loup garou win
                self.data["chat"].append(["Global", "Les loups garous ont gagné !"])
                return
            self.data["chat"].append(["Global", "La nuit tombe sur le village..."])
            self.data["chat"].append(["Global", "Tout le monde se rendort...\n"])
            self.nightEvent = {}
        elif previousTurn == "voyante":
            self.data["chat"].append(["Global", "La voyante se rendort...\n"])
        elif previousTurn == "salvateur":
            self.data["chat"].append(["Global", "Le salvateur se rendort...\n"])
        elif previousTurn == "lg":
            self.data["chat"].append(["Global", "Les loups garous se rendorment...\n"])
            for player in self.data["players"]:
                if self.data["players"][player]["protected"] == True:
                    self.data["players"][player]["protected"] = False
                    self.data["chat"].append([player, f"Le joueur {player} a été protégé !\n"])
        elif previousTurn == "sorciere":
            self.data["chat"].append(["Global", "La sorcière se rendort...\n"])
        elif previousTurn == "cupidon":
            self.data["chat"].append(["Global", "Cupidon se rendort...\n"])

        #next turn message
        if previousTurn == "cupidon":
            turnIndex = 2
        elif previousTurn == "chasseur":
            turnIndex = 1
        else:
            turnIndex = turnList.index(previousTurn) + 1
        if turnIndex == len(turnList):
            turnIndex = 0
        nextTurn = turnList[turnIndex]
        if nextTurn == "jour":
            self.data["chat"].append(["Global", "Le jour se lève sur le village..."])
            self.data["chat"].append(["Global", "Tout le monde se réveille..."])

            #night recap
            try:
                if self.nightEvent["lg"] != ["none"]:
                    self.data["chat"].append(["Global", f"Le joueur {str(self.nightEvent['lg'])} a été tué par les loups garous ! Il était {self.data['players'][self.nightEvent['lg']]['role']} !"])
                else:
                    self.data["chat"].append(["Global", "Les loups garous n'ont tué personne !"])
            except:
                pass
            try:
                if self.nightEvent["sorciere"][0] == "kill":
                    self.data["chat"].append(["Global", f"Le joueur {str(self.nightEvent['sorciere'][1])} a été tué par la sorcière ! Il était {self.data['players'][self.nightEvent['sorciere'][1]]['role']} !"])
                elif self.nightEvent["sorciere"][0] == "save":
                    self.data["chat"].append(["Global", f"Cependant, le joueur {str(self.nightEvent['sorciere'][1])} a été sauvé par la sorcière !"])
            except:
                pass

            #check if player is in love
            try:
                if self.data["players"][self.nightEvent['lg']]["lover"] != "none" and self.data["players"][self.nightEvent['lg']]["state"] == "Mort":
                    self.data["players"][self.data["players"][self.nightEvent['lg']]["lover"]]["state"] = "Mort"
                    self.data["chat"].append(["Global", f"Le joueur {self.data['players'][self.nightEvent['lg']]['lover']} s'est suicidé par amour !"])
            except:
                pass
            try:
                if self.data["players"][self.nightEvent['sorciere'][1]]["lover"] != "none" and self.data["players"][self.nightEvent['sorciere'][1]]["state"] == "Mort":
                    self.data["players"][self.data["players"][self.nightEvent['sorciere'][1]]["lover"]]["state"] = "Mort"
                    self.data["chat"].append(["Global", f"Le joueur {self.data['players'][self.nightEvent['sorciere'][1]]['lover']} s'est suicidé par amour !"])
            except:
                pass

            #check if the game is over
            if dictRole["Loup Garou"] == False:
                self.data["gameState"] = "Victoire des Villageois" #villageois win
                self.data["chat"].append(["Global", "Les villageois ont gagné !"])
                return
            elif dictRole["Villageois"] == False and dictRole["Chasseur"] == False and dictRole["Petite Fille"] == False and dictRole["Cupidon"] == False and dictRole["Sorciere"] == False and dictRole["Salvateur"] == False and dictRole["Voyante"] == False:
                self.data["gameState"] = "Victoire des Loups Garous" #loup garou win
                self.data["chat"].append(["Global", "Les loups garous ont gagné !"])
                return
            
            #check if the chasseur is dead
            try:
                if self.nightEvent["lg"] != "none":
                    if self.data["players"][self.nightEvent["lg"]]["role"] == "Chasseur":
                        self.data["chat"].append(["Global", "Le Chasseur juste avant de mourir tire sa dernière balle..."])
                        self.data["chat"].append(["Global", "Chasseur, choisissez un joueur à tuer !"])
                        self.data["turn"] = "chasseur"
                        return
                    else:
                        self.nextTurn()
                else:
                    self.nextTurn()
            except:
                self.nextTurn()

        elif nextTurn == "vote":
            #check if the game is over
            if dictRole["Loup Garou"] == False:
                self.data["gameState"] = "Victoire des Villageois" #villageois win
                self.data["chat"].append(["Global", "Les villageois ont gagné !"])
                return
            elif dictRole["Villageois"] == False and dictRole["Chasseur"] == False and dictRole["Petite Fille"] == False and dictRole["Cupidon"] == False and dictRole["Sorciere"] == False and dictRole["Salvateur"] == False and dictRole["Voyante"] == False:
                self.data["gameState"] = "Victoire des Loups Garous" #loup garou win
                self.data["chat"].append(["Global", "Les loups garous ont gagné !"])
                return

            self.data["chat"].append(["Global", "Il est temps de voter pour éliminer un joueur !"])
            for player in self.data["players"]:
                if self.data["players"][player]["state"] == "Vivant":
                    self.data["players"][player]["state"] = "Vote"
        elif nextTurn == "voyante":
            self.data["chat"].append(["Global", "La voyante se réveille..."])
            self.data["chat"].append(["Global", "Voyante, choisissez un joueur à espionner !"])
        elif nextTurn == "salvateur":
            self.data["chat"].append(["Global", "Le salvateur se réveille..."])
            self.data["chat"].append(["Global", "Salvateur, choisissez un joueur à protéger !"])
        elif nextTurn == "lg":
            self.data["chat"].append(["Global", "Les loups garous se réveillent..."])
            self.data["chat"].append(["Global", "Loups Garous, votez un joueur à tuer !"])
            for player in self.data["players"]:
                if self.data["players"][player]["role"] == "Loup Garou":
                    self.data["players"][player]["state"] = "Vote"
                    self.data["players"][player]["chat"] = "Loup Garou"
                    self.data["chat"].append([player, "Vous êtes maintenant dans le chat des Loups Garous !"])
        elif nextTurn == "sorciere":
            self.data["chat"].append(["Global", "La sorcière se réveille..."])
            #get sorciere player
            for player in self.data["players"]:
                if self.data["players"][player]["role"] == "Sorciere":
                    sorciere = player
            if self.nightEvent["lg"] == "none":
                self.data["chat"].append([sorciere, "Personne n'a été tué cette nuit !"])
            else:
                self.data["chat"].append([sorciere, f"Le joueur {self.nightEvent['lg']} a été tué cette nuit !"])
            self.data["chat"].append(["Global", "Sorcière, voulez-vous tuer un joueur, sauver la victime des loups ou ne rien faire ?"])
        self.data["turn"] = nextTurn


    def connPlayer(self):

        while self.playercount != self.playerMax:
            #wait until a connection is etablished
            conn, addr = self.s.accept()
            self.playercount += 1
            print("Client Connected:", addr)

            self.data["gameState"] = f"Démarrage ({self.playercount}/{self.playerMax})"
            self.data["chat"].append(["Global", f"Le joueur {self.playercount} a rejoint la partie !"])

            #start async connection for client
            start_new_thread(self.clientConn, (conn, addr))

        self.data["gameState"] = "En jeu"
        self.data["chat"].append(["Global", "La partie commence !\n"])
        self.data["chat"].append(["Global", "La nuit tombe sur le village..."])
        self.data["chat"].append(["Global", "Cupidon, choisissez deux joueurs à lier avec votre flèche !"])


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
        for i in range(nbPetiteFille):
            self.roles.append("Petite Fille")
        for i in range(nbVillageois):
            self.roles.append("Villageois")

        print(self.roles)

    
    def runGame(self):
        if len(self.data["chat"]) > 10: #limit chat size to 10 messages
            self.data["chat"] = self.data["chat"][-10:]
            print(self.data["chat"])


server = Server()
server.connPlayer()
while True:
    server.runGame()
