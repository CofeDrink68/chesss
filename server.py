import threading # on importe threading, une librairie qui permet du faire du multithread
import socket    # on importe socket, une libraire pour le tcp/ip
import chess     # on importe chess, une librairie moteur d'échec
import json      # on importe json, une librairue pour traiter du json
import random    # on importe random, une librairie pour générer des nombres aléatoires
import time      # on importe time, une librairie de temps
import os        # on importe la librairie système

linux = False

def clear(): # On définit la fonction pour nettoyer le terminal
    os.system("clear" if linux else "cls") # On execute cls sour windows ou clear sous linux

class Game(threading.Thread): # on initialise une nouvelle classe "Game"
    def __init__(self): # Fonction d'initialisation
        threading.Thread.__init__(self)
        self.board = chess.Board() # On initie un plateau
        self.id = (int(time.time()*100) ^ random.randint(1, 1000)) # on génère une clé avec du xor
        # On initialise des variables
        self.isWhiteUsed = None
        self.isBlackUsed = None
        self.tour = 0 # %2==0 is that it's white to play
    
    def run(self):
        while (self.isWhiteUsed is None) or (self.isBlackUsed is None): # On attend que les deux soient connectés
            pass

        self.begin() # On initialise

    def getColor(self, conn): # On définit la fonction qui désigne la couleur 
        if(self.isWhiteUsed is None and self.isBlackUsed is None): # on regarde si ni les blancs ni les noirs sont pris
            x = random.randint(0, 1) # On pioche au hasard
            if x: # Si on a choisi 1 donc noir
                self.isBlackUsed = conn # On affecte la connection à la variable
                return 1 # On renvoie qu'on a choisi noir
            else: # Sinon on a choisi blanc
                self.isWhiteUsed = conn # On affecte la connection à la variable
                return -1 # On renvoie qu'on a choisi blanc
        elif(self.isBlackUsed is None): # Si le noir n'est pas utilisé (et que les blancs sont donc pris)
            self.isBlackUsed = conn # On affecte la connection à la variable
            return 1 # On renvoie que l'utilisateur sera noir
        elif(self.isWhiteUsed is None): # Si le blanc n'est pas utilisé (et que les noirs sont donc pris)
            self.isWhiteUsed = conn # On affecte la connection à la variable
            return -1 # On renvoie que l'utilisateur sera blanc
        else: # C'est que déjà deux joueurs sont présents
            return 0 # On renvoie une erreur
    
    def move(self, color, moveName): # Fonction pour commander une pièce
        if not(self.isWhiteUsed is None) and not(self.isBlackUsed is None): # Est ce que les deux joueurs sont présents  
                if color == (-1 if self.tour%2==0 else 1): # Est ce que c'est à la bonne personne de jouer
                    if not(self.board.is_game_over()):
                        if len(moveName) == 4:
                            if chess.Move.from_uci(moveName) in self.board.legal_moves: # Est ce que le mouvement est possible
                                m = chess.Move.from_uci(moveName) # On inscrit le mouvement
                                self.board.push(m) # On le mets dans le plateau
                                self.tour += 1 # On incrémente le tour

                                if color == -1: # Si couleur blanche
                                    self.isWhiteUsed.send(json.dumps({"error": 0}).encode()) #dire qu'il n'y a pas d'erreur
                                else: # Sinon
                                    self.isBlackUsed.send(json.dumps({"error": 0}).encode()) # dire qu'il n'y a pas d'erreur

                                return 0 # On renvoie que c'est bon
                            else: # Si le mouvement est illégal
                                if not(0 if self.tour%2==0 else 1): # Si c'est aux blancs
                                    self.isWhiteUsed.send(json.dumps({"over": self.board.is_game_over(), "error": 4, "board": self.board.fen(), "is2Play": (-1 if self.tour%2==0 else 1)}).encode()) # On lui envoie une erreur 4
                                else: # Si c'est au noirs
                                    self.isBlackUsed.send(json.dumps({"over": self.board.is_game_over(), "error": 4, "board": self.board.fen(), "is2Play": (-1 if self.tour%2==0 else 1)}).encode()) # On lui envoie une erreur 4
                                return 4 # On return l'error
                        else:
                            if not(0 if self.tour%2==0 else 1): # Si c'est aux blancs
                                self.isWhiteUsed.send(json.dumps({"over": self.board.is_game_over(), "error": 4, "board": self.board.fen(), "is2Play": (-1 if self.tour%2==0 else 1)}).encode()) # On lui envoie une erreur 4
                            else: # Si c'est au noirs
                                self.isBlackUsed.send(json.dumps({"over": self.board.is_game_over(), "error": 4, "board": self.board.fen(), "is2Play": (-1 if self.tour%2==0 else 1)}).encode()) # On lui envoie une erreur 4
                            return 4 # On return l'error
                    else: # Si c'est echec 
                        pass # Ben on s'en fout

                    message = {"board": self.board.fen(), "is2Play": (-1 if self.tour%2==0 else 1)} #  On envoie l'objet du plateau
                    message["over"] = self.board.is_game_over() # On ajoute l'echec et mat

                    self.isBlackUsed.send(json.dumps(message).encode()) # On envoie le message au client noir
                    self.isWhiteUsed.send(json.dumps(message).encode()) # On envoie le message au client blanc
        else: # Si un des utilisateur est pas connecté
            self.isWhiteUsed.send(json.dumps({"over": self.board.is_game_over(), "error": 3, "board": self.board.fen(), "is2Play": (-1 if self.tour%2==0 else 1)}).encode()) # On lui envoie une erreur 3
            self.isBlackUsed.send(json.dumps({"over": self.board.is_game_over(), "error": 3, "board": self.board.fen(), "is2Play": (-1 if self.tour%2==0 else 1)}).encode()) # On lui envoie une erreur 3
            return 3 # Erreur 3 (errors.txt)
    
    def begin(self):
        message = {"board": self.board.fen(), "is2Play": (-1 if self.tour%2==0 else 1)} #  On envoie l'objet du plateau
        self.isBlackUsed.send(json.dumps(message).encode()) # On envoie le message au client noir
        self.isWhiteUsed.send(json.dumps(message).encode()) # On envoie le message au client blanc

class Supervisor(threading.Thread):
    def __init__(self, parent, parentOfParent):
        threading.Thread.__init__(self)
        self.parent = parentOfParent
        self._self = parent

    def run(self):
        print(self.parent.connections)

        message = self._self.conn.recv(2048) # On prends le message du client qui contient si on ouvre ou on crée une partie
        message = json.loads(message.decode()) # On convertit la chaîne de caractère formatée JSON en tableau
        if message["party"] == "new": # Si on crée une partie
            gInst = Game() # On initialise une nouvelle instance de Game
            gInst.start() # On démarre le thread
            self._self.conn.send(json.dumps({"id": gInst.id}).encode()) # On envoie l'ID
            self._self.parent.games[gInst.id] = gInst # On renseigne le moteur de jeu grace à son id
            self._self.parent.connections[-1].gameObject = gInst # On l'affecte à la connection
            self._self.parent.connections[-1].gameId = gInst.id # Ainsi que l'ID de partie
        elif message["party"] == "join": # Si on joint une partie
            _pass = True # Retour du try:
            link = 0 # POur eviter les problèmes
            try: # On essaye
                link = int(message["link"]) # de transformer en int
            except: # Si qq passe pas bien
                _pass = False # On le sauvegarde
            if link in self.parent.games and _pass: # Si l'id de partie est connue et pas d'erreur
                self._self.conn.send(json.dumps({"error": 0}).encode()) # On renvoie au client qu'il n'y a pas d'erreur
                self._self.parent.connections[-1].gameObject = self._self.parent.games[link] # On l'affecte à la connection
                self._self.parent.connections[-1].gameId = self._self.parent.games[link].id # Ainsi que l'ID de partie
            else: # Sinon
                self._self.conn.send(json.dumps({"error": 5}).encode()) # Erreur (pour changer)

class Connection(threading.Thread): # On crée une classe Multithread qui gère UNE connection via TCP/IP
    def __init__(self, conn, addr, id, parent): # on définit la fonction utilisation
        threading.Thread.__init__(self) # On configure le thread
        # On copie les variables
        self.conn = conn
        self.addr = addr
        self.id = id
        # On initialise les variables
        self.gameId = None
        self.gameObject = None
        self.black_white = None
        self.stop = False # On stop le thread

        self.parent = parent

        self.s = Supervisor(self, self.parent)

    def run(self): # Lancement du thread
        self.s.start()
        self.s.join()

        print("Supervisor finished "+str(self.addr))

        while (self.gameId is None) or (self.gameObject is None): # On attend d'avoir un game ID
            pass
    
        print("GameObject satisfied "+str(self.addr))

        self.black_white = self.gameObject.getColor(self.conn) # On obtient la couleur

        if(self.black_white == 0): # Si la fonction renvoie 0 c'est que le jeu est déja satisfait
            self.conn.send(json.dumps({"error": 1}).encode()) # Donc on envoie le code 1 (errors.txt) au client
        else: # Couleur choisie
            self.conn.send(json.dumps({"error": 0, "color": self.black_white}).encode()) # On envoie au client que c'est bon

        while (self.gameObject.isWhiteUsed is None) or (self.gameObject.isBlackUsed is None): # On attend qu'ils soient connectés
            pass
    
        print("Game satisfied "+str(self.addr))

        while not self.stop: # Tant que ce n'est pas stoppé
            message = self.conn.recv(2048) # On récupère un message du client
            print("163"+message.decode()) # On débug :)
            if message.decode() != "": # Si c'est pas vide
                message = json.loads(message.decode()) # On le décode
                if(message["move"] is not None): # Si on lui demande de bouger quelque chose
                    result = self.gameObject.move(self.black_white, message["move"])#On appelle la fonction move
                    renvoi = {} # On initialise la variable renvoi
                    renvoi["over"] = self.gameObject.board.is_game_over() # On ajoute si mat
                    renvoi["board"] = self.gameObject.board.fen() # On renvoie le plateau
                    renvoi["error"] = result # On renvoie le message d'erreur
                    print("172"+str(renvoi)) # On débug ;)
                    # self.conn.send(json.dumps(renvoi).encode()) # On utilise la connexion du client pour lui envoyer la variable renvoi.
                    self.gameObject.isWhiteUsed.send(json.dumps(renvoi).encode()) # On envoie le message
                    self.gameObject.isBlackUsed.send(json.dumps(renvoi).encode()) # Idem
                    self.gameObject.begin() # On utilise begin() comme il faut pas XD
                else: # Si le message ne contient pas de mouvement
                    self.conn.send(json.dumps({"error": 4}).encode()) # On envoie l'erreur
            else: # Sinon
                message = {"move": None} # On s'en fout et on évite les bugs

class MainThread(threading.Thread): # On crée jne classe multiThread qui est le coeur du système
    def __init__(self, port=554, ip="127.0.0.1"): # On définit la fonction d'initialisation
        threading.Thread.__init__(self) # On définit le thread
        # On copie la variable port mais pas trop globale :)
        self.port = port
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # On initialise le socket
        self.sock.bind((ip, self.port)) # On affecte le port au socket

        # Initialisation des variables
        self.stop = False
        self.accept = True 
        self.games = {}
        self.connections = []

    def run(self): # On définit la fonction principal
        self.sock.listen(1) # On commence écouter
        while not self.stop: # Tant que le thread n'est pas fini
            if self.accept: # Si on accepte :
                try: # Pour eviter les erreures lors d'un arrêt méchant
                    conn, addr = self.sock.accept() # On attends la venu d'une connection et on accepte
                except: # Si ya des erreures    
                    break # On quitte
                print("Nouvelle connection avec "+str(addr)) # On débug
                self.connections.append(Connection(conn, addr, len(self.connections), self)) # On ouvre une nouvelle instance de Connection et  on la mets dans la variable self.connections
                self.connections[-1].start() # On démare l'instance de connection
        
        for conn in self.connections: # Pour toutes les conections
            conn.conn.close() # Auf widersehen
            conn.stop = True # On arrête le thread
            conn.join() # On attend qu'ils s'arrête


if __name__ == "__main__": # Si le code est éxecuté et pas ouvert par un autre programme python
    clear() # On clear le terminal
    port = 80 # On définit le port
    hostname = socket.gethostname() # On récupère le nom du pc
    IPAddr = socket.gethostbyname(hostname) # et son ip
    print("Serveur démaré sur le port "+str(port)) # Quand on a pas envie de lire la doc ;)
    mt = MainThread(port=port, ip=IPAddr) # On ouvre une instance de MainThread sur le port 554
    mt.start() # et on la démarre
    stop = False # On définit la variable du stop
    while not(stop): # tant qu'on s'arrête pas
        m = input("$ ") # On demande une commande

        if "stop" in m: # si on a entré fini
            stop = True # on s'arrête 
            mt.stop = True # On coupe le thread
            mt.sock.close() # On arrete violamanet le serveur grâce à de merveilleuses erreures 
            mt.join() # On attend que le thread soit coupé
    
    print("Stop") # On affiche stop
    exit(1) # On quitte