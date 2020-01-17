# chesss

Un jeu d'echec non raciste en Python :)
Il n'oppose pas les blancs au noirs mais les majuscules aux minuscules : c'est donc un jeu familial

Le serveur est par défaut sur le port 554

Et c'est en DEVELOPPEMENT n'hésitez pas à reporter les bugs <3

## 1. Jeu :

La grille se compose : 

`a8 b8 c8 d8 e8 f8 g8 h8` 
`a7 b7 c7 d7 e7 f7 g7 h7`
`a6 b6 c6 d6 e6 f6 g6 h6`
`a5 b5 c5 d5 e5 f5 g5 h5`
`a4 b4 c4 d4 e4 f4 g4 h4`
`a3 b3 c3 d3 e3 f3 g3 h3`
`a2 b2 c2 d2 e2 f2 g2 h2`
`a1 b1 c1 d1 e1 f1 g1 h1`

Et chaque mouvement est décrit par

PosDébutPosFin

Exemple : 

a2a4 va bouger la pière en a2 pour la mettre en a4

## 2. Installation des dépendances: 

    `pip install python-chess json`

## 3. Lancement du serveur et du client
### A. Le serveur

    `python server.py`

    Le serveur démarre alors avec le port 554 par défaut

### B. Le client

    `python client.py`

    Le client démare et vous demande d'entrer l'adresse ip du serveur. Si le serveur tourne sur la même machine que le client alors entrer :
    `128.0.0.1`
    Puis le client demande le port, par défaut entrer
    `554`

    Puis sois vous voulez créer une partie (taper 1), il va alors vous afficher l'id de la partie.
    Ou alors vous voulez rejoindre une partie (taper 2), il faut alors entrer l'id de la partie.

    Puis appuyez sur entrer pour commencer la partie. Pour savoir comment jouer, se reférer au point 1.