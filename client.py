import socket
import tkinter as tk

class Network:

    def __init__(self):

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.server = str(input('Server Address : '))
        self.ip = str(self.server.split(":")[0])
        self.port = int(self.server.split(":")[1])
        print(self.ip, "/", self.port)
        self.addr = (self.ip, self.port)

        self.player = self.connect()


    def connect(self):
        try:
            self.client.connect(self.addr)
            print("Connected !")
            return self.client.recv(8192).decode()
        except:
            pass


    def send(self, data):
        try:
            self.client.send(str.encode(data))
            return self.client.recv(8192).decode()
        except socket.error as e:
            print(e)


class Interface:

    def __init__(self):

        self.conn = Network()
        self.data = eval(self.conn.player)
        self.playerID = self.data["playerID"]
        self.role = self.data["role"]
        self.chat = "global"
        self.state = "vivant"
        self.action = "sleep"
        self.msg = ""

        self.roleDict = {
            "Villageois": {
                "chat": "Village",
                "def": "Vous devez éliminer les Loups Garou au vote !"
            },
            "Loup Garou": {
                "chat": "Loup Garou",
                "def": "Vous devez tuer tous les innocents !"
            },
            "Voyante": {
                "chat": "Village",
                "def": "Vous pouvez voir le rôle d'un joueur\nchaque nuit !"
            },
            "Sorciere": {
                "chat": "Village",
                "def": "Vous pouvez sauver un joueur de la mort\net/ou tuer un joueur chaque nuit !\n(Une seule fois chaque pouvoir)"
            },
            "Chasseur": {
                "chat": "Village",
                "def": "Vous pouvez tuer un joueur lorsque vous\nmourrez !"
            },
            "Cupidon": {
                "chat": "Village",
                "def": "Vous pouvez lier deux joueurs ensembles !\n(Début de partie)"
            },
            "Petite Fille": {
                "chat": "Village",
                "def": "Vous pouvez espionner les Loups Garou chaque\nnuit !"
            },
            "Salvateur": {
                "chat": "Village",
                "def": "Vous pouvez protéger un joueur\nde la mort chaque nuit !\n(Pas deux fois de suite la meme personne)"
            }
        }

        self.root = tk.Tk()
        self.root.title("Loup Garou")

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
        return self.conn.send(str(data))


    def validateMessage(self):
        self.msg = self.chatentry.get()
        self.chatentry.delete(0, tk.END)


    def update(self):
        self.root.update()
        self.send()


app = Interface()
while True:
    app.update()
