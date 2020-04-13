# LaBot : Bot Dofus 2 en Python 3

## data

  - Buffer
  - Fonctions pour reader / writer

## decompile.sh

Script pour décompiler certaines parties du client avec [JPEXS
FFDec](https://github.com/jindrapetrik/jpexs-decompiler). Si vous n'êtes
pas sous macOS, le chemin de Dofus doit être modifié.

## protocolBuilder.py

Après avoir décompilé, ce script parse les sources et mémorise le
protocole dans `protocol.pk`. Il doit être lancé à chaque nouvelle
version.

## protocol.py

Parse les Msg.

## sniffer

Nécessite wdom et scapy (`pip install wdom scapy==2.4.2`).

Lancer avec

    `sudo python -m labot.sniffer.main`

Pour accéder à l'interface graphique, ouvrir <http://localhost:8888>
dans un navigateur.

`sudo` est nécessaire pour sniffer.

Le filtre par défaut est `tcp port 5555`

L'option `-c` ou `--capture` avec comme argument l'adresse d'un fichier
permet de lire depuis une capture faite via wireshark ou tcpdump,
pratique en phase de test pour ne pas devoir effectuer 100fois les memes
actions dans le jeu. Exemple:

`sudo python -m labot.sniffer.main -c ./captures/macapture.pcap`

L'option `-d` ou `--debug` permet d'afficher (beaucoup) plus
d'informations sur ce qui est entrain de se passer.

## mitm (en développement)

### Fonctionnalités

  - Redirection de la connexion de manière transparente, voir simplement
    le fichier exécutable `labot/mitm/proxychains.py`
  - Serveur proxy http (`labot/mitm/proxy.py`)
  - Différentes interfaces de callback (`labot/mitm/bridge`)
  - Démarrage d'un bot, avec possibilité de lancer les callbacks en
    asynchrone
  - Décodage sommaire des paquets (`labot/data/msg.py`)

### Plates-formes :

Ce code est compatible avec tout système où la commande
[proxychains4](https://github.com/rofl0r/proxychains-ng) est installée
(OS X, Linux). Il faut simplement modifier la commande de lancement de
Dofus dans le fichier `labot/mitm/proxychains.py`.

### Mode d'emploi :

Lancer `labot.mitm.proxy.startProxyServer` avec en argument la fonction
de votre choix qui prend en entrée `coJeu` et `coServ`, les deux sockets
vers le client et le serveur. Cette fonction fonction est appelée dans
la méthode `do_CONNECT` du proxy HTTP quand le client ouvre une
connexion.

Les classes de `labot.mitm.bridge` implémentent des exemples de
fonctions dans `proxy_callback`. Il y a plusieurs exemples,
`PrintingMsgBridgeHandler.proxy_callback` permet par exemple de
distinguer les paquets, d'afficher les ids ainsi que le contenu
hexadécimal.

On peut lancer autant de clients qu'on veut sur le même serveur proxy
car il utilise 1 thread différent pour chaque connexion.

`labot/mitm/proxychains.py` permet de directement lancer le jeu avec les
paramètres du proxy. Il est aussi possible de lancer le jeu à la "main"
en ayant configuré leur proxy HTTP dans les options du jeu pour qu'il
pointe vers le serveur de `labot.mitm.proxy` (par défaut
`localhost:8000`).
