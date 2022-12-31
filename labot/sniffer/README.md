## sniffer

**Attention ce sniffer n'est plus maintenu**

Nécessite wdom et scapy (`pip install wdom scapy`).

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