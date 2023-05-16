# LaBot : Bot Dofus 2 en Python 3

## Introduction

Un bot nécessite de réaliser plusieurs tâches :
1. initier, détourner ou intercepter la communication entre le client et le serveur
2. interpréter les paquets interceptés
3. gérer une logique de comportement
4. générer des paquets et les envoyer

L'étape 1 est la différence entre différents types de bots : 
- un bot "complet" doit initier la connexion avec le serveur et le client
- un bot "mitm" doit détourner la commmunication entre le client et le serveur et éventuellement y injecter des messages
- un bot "sniffer" doit simplement intercepter la communication entre le client et le serveur


## MITM

LaBot est un bot "mitm" qui utilise le module [fritm](https://github.com/louisabraham/fritm) pour détourner la communication entre le client et le serveur. fritm utilise [frida](https://www.frida.re/) pour intercepter les appels à la fonction [`connect`](http://man7.org/linux/man-pages/man2/connect.2.html) du système d'exploitation et les rediriger vers un proxy HTTP CONNECT.

Une fois que le MITM est lancé, le bot récupère deux sockets, un vers le client et un vers le serveur. Il peut alors lire et écrire sur ces sockets pour communiquer avec le client et le serveur.

Des classes de callback basiques sont disponibles dans `labot/mitm/bridge` pour gérer la communication avec le client et le serveur.

Le point d'entrée est le script `scripts/mitm.py` qui lance le proxy fritm et un bridge.

Il existe également un sniffer dans `labot/sniffer` qui utilise [scapy](https://scapy.net/) pour intercepter les paquets mais il n'est plus maintenu.

## Reader / Writer

Les paquets réseau sont lus à l'aide de classes dans `labot/data`. Ces classes décrivent comment séparer les messages individuels dans un flux continu de données et comment lire les types primitifs de données à partir d'informations binaires.

## Protocole

Le procotole désigne la manière dont le jeu encode des données dans différents types de paquets.

Afin de pouvoir répliquer ce protocole entre différentes versions de Dofus, sa construction est automatisée.

### Décompilation

La première étape est de décompiler le jeu. Pour cela, le script `scripts/decompile.sh` est fourni. Il permet de décompiler certaines parties du client avec [JPEXS FFDec](https://github.com/jindrapetrik/jpexs-decompiler).

Le script actuel utilise les chemins par défaut sous macOS.

### Construction du protocole

Après décompilation, le procole est construit par le script `scripts/build_protocol.py`. Il parse les sources et mémorise le protocole dans `protocol.pk`. Les deux scripts doivent être lancés à chaque nouvelle version de Dofus.

### Utilisation du protocole

Le protocole est utilisé dans `labot/protocol.py` pour transformer les paquets binaires en dictionnaires (json). Les méthodes de `labot/protocol.py` sont appelées directement dans les méthodes `json()` et `from_json()` de la classe `Msg` de `labot/data/msg.py`.


### Decodeur en ligne

Un décodeur en ligne est disponible dans le dossier `docs` et à l'adresse https://louisabraham.github.io/LaBot/decoder.html

Le script `scripts/build_pyodide.py` convertit `protocol.pk` en un fichier `protocol.js` et concatène plusieurs fichiers Python pour être exécutés dans le navigateur par [pyodide](https://pyodide.org/en/stable/).


### API

Il est possible de démarrer un serveur web `webapi/api.py` sur le port 5000 pour effectuer des call REST pour décoder/encoder les paquets.
La connexion est aussi acceptée via websocket.


## Comportement

Un bot doit modifier les classes de `labot/mitm/bridge` pour gérer le comportement.

Quelques classes sont fournies à titre d'exemple et il est possible d'en hériter pour créer un nouveau comportement.

`handle_message` est appelé quand un message est reçu du client ou du serveur. Il est possible de modifier le message avant de le renvoyer.

`send_to_client` permnet d'envoyer un message au client et `send_to_server` d'envoyer un message au serveur.

`send_message` montre un exemple de message qui peut être envoyé au serveur, en l'occurrence un message qui demande d'envoyer un message dans le chat.

## Aide

J'ai assez peu de temps pour répondre aux questions. Je recommande le serveur Discord de Cadernis pour des demandes d'aide: https://discord.gg/UYSFa6TCm3