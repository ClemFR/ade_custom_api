# ADE-API
Système de récupération de données depuis un emploi du temps ADE sans utiliser l'API officielle.

## Installation
Il est nécessaire de générer un fichier 'ressources.txt' contenant toutes les rubriques dans lesquelles les données seront récupérés.

La génération de ce fichier peut se faire en utilisant le script 'recupere_ressource_liste.py' qui prend en paramètre l'URL de l'emploi du temps ADE avec les informations d'identification. 

**Attention** : cet url nécessite d'être sur la version "JSP" de l'emploi du temps !

Une fois le fichier généré et placé dans le dossier "app" de "ade_parser", il est possible de lancer toute l'application avec un "docker compose up -d".

La configuration de l'application est faite dans le fichier "stack.env"