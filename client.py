import socket
import tkinter as tk

class Network:

    def __init__(self):

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.server = str(input('Server Address : '))
        self.ip = str(self.server.split(":")[0])
        try:
            self.port = int(self.server.split(":")[1])
        except:
            self.port = 5757
        print(self.ip, "/", self.port)
        self.addr = (self.ip, self.port)

        self.player = self.connect()


    def connect(self):
        try:
            self.client.connect(self.addr)
            print("Connected !")
            return self.client.recv(4096).decode()
        except:
            pass


    def send(self, data):
        try:
            self.client.send(str.encode(data))
            return self.client.recv(4096).decode()
        except socket.error as e:
            print(e)


class Interface:

    def __init__(self):

        self.conn = Network()
        self.data = eval(self.conn.player)
        self.playerID = self.data["playerID"]
        self.role = self.data["role"]
        self.chat = self.data["chat"]
        self.receivedChat = []
        self.loggedChat = []
        self.lastMsg = ""
        self.state = self.data["state"]
        self.action = self.data["action"]
        self.msg = ""
        self.lover = self.data["lover"]
        print([self.lover])

        self.roleDict = {
            "Villageois": {
                "chat": "village",
                "def": "Vous devez éliminer les Loups Garou au vote !"
            },
            "Loup Garou": {
                "chat": "lg",
                "def": "Vous devez tuer tous les innocents !"
            },
            "Voyante": {
                "chat": "voyante",
                "def": "Vous pouvez voir le rôle d'un joueur\nchaque nuit !"
            },
            "Sorciere": {
                "chat": "sorciere",
                "def": "Vous pouvez sauver un joueur de la mort\net/ou tuer un joueur chaque nuit !\n(Une seule fois chaque pouvoir)"
            },
            "Chasseur": {
                "chat": "chasseur",
                "def": "Vous pouvez tuer un joueur lorsque vous\nmourrez !"
            },
            "Cupidon": {
                "chat": "cupidon",
                "def": "Vous pouvez lier deux joueurs ensembles !\n(Début de partie)"
            },
            "Petite Fille": {
                "chat": "petite fille",
                "def": "Vous pouvez espionner les Loups Garou chaque\nnuit !"
            },
            "Salvateur": {
                "chat": "salvateur",
                "def": "Vous pouvez protéger un joueur\nde la mort chaque nuit !\n(Pas deux fois de suite la meme personne)"
            }
        }

        self.root = tk.Tk()
        self.root.title("Loup Garou")
        self.root.resizable(False, False)

        self.frame = tk.Frame(self.root)
        self.frame.grid(column=1, row=1, rowspan=2)

        self.infoFrame = tk.Frame(self.frame)
        self.infoFrame.config(width=400, height=600)
        self.infoFrame.grid(column=1, row=1, rowspan=2)
        self.image = tk.PhotoImage(file=rf"img/{self.role}" + ".png") # Image
        self.imagebox = tk.Label(self.infoFrame, image=self.image) # Show Image
        self.imagebox.grid(column=1, row=1)
        self.roletext = tk.Label(self.infoFrame, text="Role : " + self.role) # Role
        self.roletext.grid(column=1, row=2)
        self.statebox = tk.Label(self.infoFrame, text="Vous êtes " + self.state) # State
        self.statebox.grid(column=1, row=3)
        self.roleInfoText = tk.Label(self.infoFrame, text=self.roleDict[self.role]["def"]) # Role info
        self.roleInfoText.grid(column=1, row=4)
        self.playerIDText = tk.Label(self.infoFrame, text="Votre ID est " + str(self.playerID)) # Player ID
        self.playerIDText.grid(column=1, row=5)
        self.loverText = tk.Label(self.infoFrame) # Lover

        self.chatbox = tk.Text(self.frame, height=20, width=50) # Chatbox
        self.chatbox.grid(column=2, row=1, columnspan=2)

        self.chatentry = tk.Entry(self.frame, width=50) # Chat entry
        self.chatentry.grid(column=2, row=2)
        self.chatentry.bind("<Return>", lambda x: self.validateMessage())

        self.chatbutton = tk.Button(self.frame, text="[➜]", command=self.validateMessage) # Chat button
        self.chatbutton.grid(column=3, row=2)


    def send(self):
        data = {
            "playerID": self.playerID,
            "role": self.role,
            "chat": self.chat,
            "state": self.state,
            "action": self.action,
            "msg": self.msg
        }
        self.msg = ""
        data = str(data)
        return self.conn.send(data)


    def validateMessage(self):
        self.msg = self.chatentry.get()
        self.chatentry.delete(0, tk.END)

    
    def updateChat(self):
        self.receivedChat = self.data["chat"]
        if self.loggedChat != []:
            for i in range(len(self.receivedChat)):
                if self.receivedChat[i] == self.loggedChat[-1]:
                    self.receivedChat = self.receivedChat[i+1:]
                    break
        if self.receivedChat != []:
            for msg in self.receivedChat:
                if msg[0] == "global":
                    self.chatbox.insert(tk.END, msg[1] + "\n")
                elif msg[0] == self.roleDict[self.role]["chat"]:
                    self.chatbox.insert(tk.END, msg[1] + "\n")
                elif msg[0] == self.playerID:
                    self.chatbox.insert(tk.END, msg[1] + "\n")
                self.chatbox.see(tk.END)
            self.loggedChat = self.receivedChat


    def update(self):
        self.root.update()
        data = self.send()
        self.data = eval(data)

        # Update data
        self.state = self.data["players"][self.playerID]["state"]
        self.action = self.data["players"][self.playerID]["action"]
        self.lover = self.data["players"][self.playerID]["lover"]

        self.updateChat()
        if self.lover != "" and self.lover.grid_info() == {}:
            self.loverText.config(text="Vous êtes amoureux du joueur " + self.lover)
            self.loverText.grid(column=1, row=6)


app = Interface()
while True:
    app.update()
