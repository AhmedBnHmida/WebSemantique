# 🌿 Eco Platform - Projet Web Sémantique

Plateforme de gestion des campagnes écologiques utilisant une ontologie OWL.

## Structure du Projet
- `backend/` : API Flask avec RDFLib
- `frontend/` : Application React
- `fuseki/` : Serveur SPARQL Apache Jena

## Installation
1. Backend: `cd backend && pip install -r requirements.txt`
2. Frontend: `cd frontend && npm install`
3. Fuseki: Lancer `java -jar fuseki-server.jar` dans le dossier fuseki
4. Lancer la commande `python load_data.py` dans le dossier scripts

## Lancement
1. Démarrer Fuseki
2. Démarrer le backend: `python app.py`
3. Démarrer le frontend: `npm start`