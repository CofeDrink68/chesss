import socket # On importe socket, une librairie pour le tcp/ip
import time # On importe time, une librairie de temps
import os # On importe os, la librairie système
import chess # On importe chess, une librairie d'échec
import json # On importe json, une librairie pour traiter du json

linux = False # Est ce que nous sommes sous linux ?

def clear(): # On définit la fonction pour nettoyer le terminal
    os.system("clear" if linux else "cls") # On execute cls sour windows ou clear sous linux

def standard():
    print("*************************************") 
    print(" ****  ****  *  *  ****  ****  /****/")
    print(" **   *      ****  **   *     /****\\")  
    print(" ****  ****  *  *  ****  ****   \***\\") 
    print("*************************************") 


clear()
standard()

ip = input("\nAdresse IP du serveur : ") # On demande l'IP du serveur
port = input("Le port du serveur : ") # On demande le port du serveur

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # On initialise un socket
    s.connect((ip, int(port))) # On essaye de se connecter
except:
    print("Une erreur s'est produite ...") # Une erreur s'est produire lors de la connection au serveur
    exit(1) # On quitte

clear() # On appelle le fonction clear qui nettoie le terminal 
print("Connecté au serveur\n") # On affiche que l'on est connecté au serveur
input("Appuyez sur entrée pour continuer") # On demande au client d'appuyer sur entrée afin de pouvoir jouer

choix = -1 # Choix impossible
while choix == -1: # Tant que rien n'est choisi
    clear() # On appelle encore la fonction clear toujours pour nettoyer le terminal
    standard() # On affiche "Echecs"
    print() # On saute une ligne parce-que flemme de \n
    print("[1] Créer une nouvelle partie") # On affiche que l'on crée une nouvelle partie 
    print("[2] Rejoindre") # On affiche l'option rejoindre 
    print() # On saute une ligne parce-que flemme de \n
    choix = input("$ ") # On lit la réponse de l'utilisateur
    try: # On essaye
        choix = int(choix) # On essaye de transformer <str>choix en <int>choix
        if(choix == 1 or choix == 2): # On teste que c'est bien 1 ou 2
            pass # On passe
        else: # Sinon
            int("quarante-deux") # On génère une erreur ;)
    except:
        print("Une erreur est survenue ...") # On affiche qu'il y a eu une erreur 
        choix = -1 # Toujours pas choisi

if choix == 2: # Si on rejoint une partie
    print() # Nouvelle ligne
    _id = input("ID de la partie : ") # On importe l'ID de la partie 
    s.send(json.dumps({"party": ("new" if choix == 1 else "join"), "link": _id}).encode()) # Si le choix = 1 on envoie new au client sinon on envoie join
    # Est-ce qu'il y a une erreur ?
    message = s.recv(2048) # On prend le premier messgae qui est en attente
    message = json.loads(message.decode()) # On décode le message
    if message["error"] == 0: # Si il n'y a pas d'erreur
        print("\nLien valide") # On affiche que le lien est valide
        # On continue
    else: # Si il y a eu une erreur
        print("Une erreur est apparue, code {}".format(message["error"])) # Pour être explicite
        exit(1) # On quitte
    input("Appuyez sur entrée pour continuer") # On demande au client d'appuyer sur entrée afin de pouvoir jouer
else: # Si on crée une partie
    s.send(json.dumps({"party": ("new" if choix == 1 else "join")}).encode()) # On envoire qu'on veut créer une partie
    m = s.recv(4096) # On reçoit la réponse
    m = json.loads(m.decode()) # On la décode
    print("Id de partie : "+str(m["id"])) # On affiche l'ID de la partie
    # On continue
    input("Appuyez sur entrée pour continuer") # On demande au client d'appuyer sur entrée afin de pouvoir jouer

m__ = s.recv(2048).decode().split("}") # Deux json en un, pour les sepparer
m = json.loads(m__[0]+"}") # On prend le premier 

color = m # On récupère le type de joueur

party = {"stop": False} # POur eviter les erreures :)

first = True # Pour savoir si on doit attendre le serveur ou si on doit prendre la deuxième partie du message ligne 74

while party["stop"] == False: # Tant que pas échech
    if first: # Si c'est la première fois
        m = m__[1]+"}" # On formatte
        m = json.loads(m) # On importe
        first = False # On evite de repasser là la prochaine fois
    else: # Si c'est une fois déjà experimentée 
        m = s.recv(2048) # On attends pour un message
        m = json.loads(m.decode()) # On le décode

    if m["is2Play"] == color["color"]: # Si c'est à noud de jouer
        error = True # Pour entrer dans la boucle
        while error: # Tant que le serveur renvoie qu'il y a une erreur
            clear() # On clear
            standard() # On affiche "echecs"
            print() # On saute une ligne
            print(chess.Board(m["board"])) # On affiche le plateau imbuvable
            print() # On saute une ligne
            print("Quel mouvement voulez-vous effectuer ?") # On demande pour un mouvement
            move = input("$ ") # On prend le mouvement
            s.send(json.dumps({"move": move}).encode()) # Et on l'envoie

            m_ = s.recv(2048) # On attend la réponse du serveur (est-ce qu'il y a un mouvement illégal)
            m_ = json.loads(m_.decode()) # On décode le message

            if m_["error"] == 0: # Si ya pas d'erreur
                error = False # Ben y'a pas d'erreur (sortie de la boucle)
            else: # Si il y a un mouvement illégal
                print("Une erreur est survenue de type "+str(m_["error"])) # On affichie qu'il y a une erreur
                input("Appuyez sur entrée pour continuer") # On demande au client d'appuyer sur entrée afin de pouvoir jouer
        m_ = s.recv(2048) # On attend le message du serveur pour le prochain tour
        m_ = json.loads(m_.decode()) # Et on le décode
    else: # Si c'est pas a nous de jouer
        clear() # On clear
        standard() # On affiche echecs
        print() # On saute une ligne
        print(chess.Board(m["board"])) # On affiche le plateau
        print() # On saute une ligne
        print("En attente de l'autre joueur") # ...  je psense que c'est assez explixite
        m_ = s.recv(2048) # On attend la réponse du serveur pour le prochain tour
        m_ = json.loads(m_.decode()) # On le décode
    
    # print(m_)
    party["stop"] = m_["over"] # On regarde si c'est echec et mat

clear() # Partie finie, on clear
standard() # On affiche echecs
print("\nPartie finie") # ... evident
print("\n"+chess.Board(m["board"])) # On affiche le plateau (notez que j'ai eu la foi de faire un vrai saut de ligne ;) )
input("\nAppuyez sur entrée pour continuer") # On demande au client d'appuyer sur entrée afin de pouvoir jouer
s.close() # On ferme la connectiobn sans aucun scrupule
clear() # On clear le terminal