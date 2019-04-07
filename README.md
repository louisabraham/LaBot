LaBot : Bot Dofus 2 en Python 3
===============================

data
----

-   Buffer
-   Fonctions pour reader / writer

decompile.sh
------------

Script pour décompiler certaines parties du client avec [JPEXS
FFDec](https://github.com/jindrapetrik/jpexs-decompiler). Si vous n'êtes
pas sous macOS, le chemin de Dofus doit être modifié.

protocolBuilder.py
------------------

Après avoir décompilé, ce script parse les sources et mémorise le
protocole dans `protocol.pk`. Il doit être lancé à chaque nouvelle
version.

protocol.py
-----------

Parse les Msg.

sniffer
-------

Nécessite wdom et scapy (`pip install wdom scapy`).

Lancer avec

    `sudo python -m labot.sniffer.main`

Pour accéder à l'interface graphique, ouvrir <http://localhost:8888>
dans un navigateur.

`sudo` est nécessaire pour sniffer.

Le filtre par défaut est `tcp port 5555`

L'option `-c` ou `--capture` avec comme argument l'adresse d'un fichier permet de lire depuis une capture faite via wireshark ou tcpdump, pratique en phase de test pour ne pas devoir effectuer 100fois les memes actions dans le jeu. Exemple:

`   sudo python -m labot.sniffer.main -c ./captures/macapture.pcap`

L'option `-d` ou `--debug` permet d'afficher (beaucoup) plus d'informations sur ce qui est entrain de se passer.


mitm (en développement)
-----------------------

### Fonctionnalités

-   Redirection de la connexion de manière transparente, voir simplement
    le fichier exécutable `labot/mitm/proxychains.py`
-   Serveur proxy http (`labot/mitm/proxy.py`)
-   Différentes interfaces de callback (`labot/mitm/bridge.py`)
-   Démarrage d'un bot, avec possibilité de lancer les callbacks en
    asynchrone
-   Décodage sommaire des paquets (`labot/data/msg.py`)

### Plates-formes :

Ce code est compatible avec tout système où la commande
[proxychains4](https://github.com/rofl0r/proxychains-ng) est installée
(OS X, Linux). Il faut simplement modifier la commande de lancement de
Dofus dans le fichier `labot/mitm/proxychains.py`.

### Mode d'emploi :

Remplacer la fonction main dans core/main.py par la fonction main de
votre bot. Elle prend en entrée `coJeu` et `coServ` les deux sockets
vers le client et le serveur. On peut aussi choisir quelle fonction est
appelée (pour distinguer les serveurs de connexion et de jeu) dans la
méthode `do_CONNECT` de `labot/mitm/proxy.py`.

Si on prend une fonction main de type Bridge(coJeu, coServ,
BridgeHandler).run(), cela fera transiter indépendament les paquets
selon des critères individuels. Il y a différents handlers,
PrintingMsgBridgeHandler permet par exemple de distinguer les paquets,
d'afficher les ids ainsi que le contenu hexadécimal. On doit alors
utiliser run qui est la méthode synchrone (n'utilise pas de Thread). On
peut également utiliser ces interfaces en thread dans un bot.

On peut lancer autant de clients qu'on veut sur le même serveur proxy.
On n'est pas obligé de les lancer depuis le même programme non plus.
