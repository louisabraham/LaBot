# LaBot - Tools

## Bases d'un bot Dofus MITM


* Fonctionnalités :
    - Redirection de la connexion de manière transparente, voir simplement le fichier exécutable `core/network/proxychains.py`
    - serveur proxy http (`core/network/proxy.py`)
    - Différentes interfaces de callback (`core/network/bridge`)
    - Démarrage d'un bot, avec possibilité de lancer les callbacks en asynchrone
    - Décodage sommaire des paquets (`core/data/msg.py`)
    - Reader / Writer Python pouvant être utilisés avec un traducteur


* Plates-formes :
Ce code est compatible avec tout système où la commande [proxychains4](https://github.com/rofl0r/proxychains-ng) est installée (OS X, Linux).


* Mode d'emploi :

Remplacer la fonction main dans core/main.py par la fonction main de votre bot.
Elle prend en entrée `coJeu` et `coServ` les deux sockets vers le client et le serveur.
On peut aussi choisir quelle fonction est appelée (pour distinguer les serveurs de connexion et de jeu) dans la méthode `do_CONNECT` de `core/network/proxy.py`.

Si on prend une fonction de type Bridge(coJeu, coServ, BridgeHandler).run(), cela fera transiter indépendament les paquets selon des critères individuels. Il y a différents handlers, PrintingMsgBridgeHandler permet par exemple de distinguer les paquets, d'afficher les ids ainsi que le contenu hexadécimal. On doit alors utiliser run qui est la méthode synchrone (n'utilise pas de Thread). On peut également utiliser ces interfaces en thread dans un bot.

On peut lancer autant de clients qu'on veut sur le même serveur proxy. On n'est pas obligé de les lancer depuis le même programme non plus.
