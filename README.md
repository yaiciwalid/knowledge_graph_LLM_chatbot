## Description du projet
Le projet consiste à créer un chatbot pouvant répondre à des question sur le thème des films, en utilisant des documents extrait de Wikipedia.
Pour celà deux bases de données ont été créer pour aider le Chatbot à répondre aux questions.

## Installation des dependancies

Un fichier requirement.txt est à votre disposition, tout ce que vous avez à faire est de lancer la commande: 
```pip install requirement.txt```


## Le Chatbot Final: 
L'application du chatbot final se trouve dans le dossier Chatbot, à fin de pouvoir lancer l'application, il vous faut certaines clés (pour la bases de données, et openai).
Pour celà suivez les étapes qui suivent.

## Base de données
Pour pouvoir directement tester le chatbot final sans avoir à reconstruire les Bases de données à travers les notebooks, les fichiers dumb vous sont fournit dans le dossier Neo4j_bdd_dumps.
Il est donc possible de directement les charger dans Neo4J (En local ou dans AuraDB) pour ensuite les utiliser.

Après celà, remplacer dans les emplacement indiqués dans le fichier chatbot.py vos coordonnées Neo4J à fin de les connecter aux Bases de données. 

## Clé Openai
Vous avez aussi besoin d'une clé Openai pour lancer l'application, pour celà, il faut la remplacer dans le fichier chatbot.py.

## Lancement du chatbot
Pour lancer l'application, il vous suffit de lancer la commande :
```streamlit run chatbot.py```

## Notebook Graph_structure
Ce notebook est celui utilisé pour construire la base de données Structure utilisé, pour reconstruire cette Base de donnée, il suffit de mettre vos coordonnées Neo4J dans l'emplacement dédié à celà, et d'exécuter les cellules.

## Notebook Graph_contenu
Pour commencer, il est nécessaire de télécharger le module en_core_web_lg avec la commande :
```python -m spacy download en_core_web_lg```
Pour construire la base de données contenu, il vous suffit de mettre vos coordonnées Neo4J dans l'emplacement convenu du notebook "graph_contenu_creation.ipynb", et d'éxecuter toutes les cellules du notebook.

## Notebook Q&A
Les trois notebook Q&A peuvent etre utilisé pour tester chaque partie du requetages indépendamment.
Q&A_Contenu: pour le graphe Contenu
Q&A_STRUCTURE: pour le graphe structure
Q&A: pour les 2 graphe rassemblé (méme résultats que l'application final)

## Contact 
Si vous avez des question, hésitez pas à nous contacter via nos adresse mail 
M.Yassine : yassine.maziz@ens.uvsq.fr / mazizyassine25@gmail.com
Y.Walid: hw_yaici@esi.dz





