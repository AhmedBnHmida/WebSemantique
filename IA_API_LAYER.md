# Couche IA API - Documentation pour l'Évaluation du Projet

## 📋 Vue d'ensemble

La couche **IA API** (Intelligence Artificielle API) est un composant central de votre architecture qui fait le lien entre les questions en langage naturel des utilisateurs et les requêtes SPARQL structurées nécessaires pour interroger votre ontologie OWL via Fuseki.

## 🎯 Objectif principal

**Transformer les questions utilisateur en requêtes SPARQL** pour permettre la **Recherche sémantique** - l'un des 4 objectifs d'évaluation de votre projet.

## 🔄 Flux de données dans l'architecture

```
Front-end (Question Utilisateur)
    ↓
IA API (TALN + Gemini)
    ↓
Requête SPARQL
    ↓
Fuseki API
    ↓
Back-end (Ontologie OWL)
    ↓
Données (résultats)
    ↓
Front-end (affichage)
```

## 🏗️ Architecture de la couche IA API

Votre implémentation actuelle utilise une **approche en deux étapes** :

### Étape 1 : Analyse TALN (Traitement Automatique du Langage Naturel)

**Fichier :** `backend/modules/taln_service.py`

**Rôle :** Analyser la question utilisateur et extraire :
- **Entités** : Identifie les concepts de votre ontologie (Event, Location, Campaign, Volunteer, etc.)
- **Intentions** : Détecte ce que l'utilisateur veut faire (lister, compter, filtrer, rechercher, obtenir des détails)
- **Informations temporelles** : Extrait les expressions temporelles (futur, passé, présent, dates)
- **Informations spatiales** : Identifie les lieux mentionnés
- **Relations** : Détecte les relations entre entités
- **Mots-clés** : Extrait les termes importants

**Exemple de sortie TALN :**
```json
{
  "original_question": "Quelles sont les campagnes actives ?",
  "entities": [
    {
      "text": "campagnes",
      "type": "Campaign",
      "ontology_class": "eco:Campaign",
      "confidence": 0.9
    }
  ],
  "intent": {
    "primary_intent": "list",
    "query_type": "list"
  },
  "temporal_info": {},
  "location_info": {},
  "keywords": ["campagnes", "actives"],
  "confidence_scores": {
    "overall_confidence": 0.85
  }
}
```

**Fonctionnalités :**
- ✅ **Mode fallback intégré** : Fonctionne sans API externe en utilisant la correspondance de motifs
- ✅ **Mapping vers l'ontologie** : Assigne les entités détectées aux classes OWL appropriées (`eco:`, `webprotege:`)
- ✅ **Classification d'intention** : Identifie automatiquement le type de requête souhaité

### Étape 2 : Génération SPARQL avec Gemini

**Fichier :** `backend/modules/gemini_sparql_service.py`

**Rôle :** Générer une requête SPARQL valide à partir de l'analyse TALN

**Processus :**
1. Reçoit l'analyse TALN structurée
2. Construit un prompt contextuel pour Gemini avec :
   - La question originale
   - Les entités détectées et leurs classes d'ontologie
   - L'intention de l'utilisateur
   - Les informations temporelles/spatiales
   - Les préfixes OWL de votre ontologie
3. Utilise Gemini AI pour générer une requête SPARQL conforme
4. Valide et nettoie la requête générée

**Exemple de prompt Gemini :**
```
Question: "Quelles sont les campagnes actives ?"
Entités détectées: eco:Campaign
Intention: list
Préfixes OWL: PREFIX eco: <...>, PREFIX webprotege: <...>
Génère une requête SPARQL SELECT pour lister les campagnes actives...
```

**Fonctionnalités :**
- ✅ **Génération dynamique** : Crée des requêtes SPARQL adaptées à chaque question
- ✅ **Conformité OWL** : Utilise correctement les préfixes et classes de votre ontologie
- ✅ **Optimisation** : Ajoute des LIMIT, FILTER, OPTIONAL selon le contexte
- ✅ **Fallback** : Utilise un moteur de templates si Gemini échoue

## 📡 Endpoint API

**Fichier :** `backend/modules/search.py`

**Route :** `POST /api/search`

**Flux complet :**
```python
1. Reçoit {"question": "Quelles sont les campagnes actives ?"}
2. TALN analyse → extraction entités/intentions
3. Gemini génère → requête SPARQL
4. Exécute SPARQL → via sparql_utils.execute_query()
5. Retourne résultats + métadonnées
```

**Réponse JSON :**
```json
{
  "results": [...],
  "taln_analysis": {...},
  "sparql_query": "PREFIX eco: ... SELECT ...",
  "pipeline_info": {
    "method": "gemini_taln",
    "status": "success",
    "results_count": 5
  }
}
```

## 🔧 Composants techniques

### 1. TALN Service (`taln_service.py`)

**Classe principale :** `TALNService`

**Méthode clé :**
```python
def analyze_question(question: str) -> Dict[str, Any]:
    """
    Analyse une question en langage naturel et retourne :
    - Entités détectées avec mapping vers l'ontologie
    - Intentions de l'utilisateur
    - Informations temporelles/spatiales
    - Relations entre entités
    """
```

**Mapping entités → ontologie :**
- `eco:Event`, `eco:EducationalEvent`, `eco:EntertainmentEvent`, etc.
- `eco:Campaign`, `eco:AwarenessCampaign`, `eco:CleanupCampaign`
- `eco:Location`, `eco:Indoor`, `eco:Outdoor`, `eco:VirtualPlatform`
- `webprotege:RCXXzqv27uFuX5nYU81XUvw` (Volunteers)
- `webprotege:Rj2A7xNWLfpNcbE4HJMKqN` (Assignments)
- `eco:Resource`, `eco:Certification`, `eco:Blog`, etc.

### 2. Gemini SPARQL Transformer (`gemini_sparql_service.py`)

**Classe principale :** `GeminiSPARQLTransformer`

**Méthode clé :**
```python
def transform_taln_analysis_to_sparql(taln_analysis: Dict) -> str:
    """
    Transforme l'analyse TALN en requête SPARQL valide
    en utilisant Gemini AI avec le contexte de l'ontologie
    """
```

**Configurations Gemini :**
- Modèle : `gemini-2.0-flash` (avec fallback)
- Temperature : 0.1 (pour des réponses déterministes)
- Max tokens : 1200

### 3. SPARQL Utils (`sparql_utils.py`)

**Classe principale :** `SPARQLUtils`

**Méthode clé :**
```python
def execute_query(query: str) -> List[Dict]:
    """
    Exécute la requête SPARQL sur Fuseki
    et retourne les résultats formatés
    """
```

**Endpoint Fuseki :** `http://localhost:3030/educationInfin/query`

## 📊 Exemples concrets

### Exemple 1 : Question simple

**Question utilisateur :** "Quelles sont les campagnes actives ?"

**TALN Analysis :**
```json
{
  "entities": [{"text": "campagnes", "ontology_class": "eco:Campaign"}],
  "intent": {"primary_intent": "list"},
  "keywords": ["campagnes", "actives"]
}
```

**SPARQL généré :**
```sparql
PREFIX eco: <http://www.semanticweb.org/...>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT ?campaign ?title WHERE {
  ?campaign rdf:type eco:Campaign .
  ?campaign eco:status "active" .
  ?campaign eco:title ?title .
} LIMIT 100
```

### Exemple 2 : Question avec filtre temporel

**Question utilisateur :** "Montre-moi les événements à venir à Paris"

**TALN Analysis :**
```json
{
  "entities": [
    {"text": "événements", "ontology_class": "eco:Event"},
    {"text": "Paris", "ontology_class": "eco:Location"}
  ],
  "intent": {"primary_intent": "list"},
  "temporal_info": {"relative_time": "future"},
  "location_info": {"locations": ["paris"]}
}
```

**SPARQL généré :**
```sparql
PREFIX eco: <...>
SELECT ?event ?title ?date ?location WHERE {
  ?event rdf:type eco:Event .
  ?event eco:title ?title .
  ?event eco:date ?date .
  ?event eco:location ?location .
  ?location eco:city "Paris" .
  FILTER (?date > NOW())
} ORDER BY ?date LIMIT 100
```

### Exemple 3 : Question de comptage

**Question utilisateur :** "Combien de volontaires ont des compétences en environnement ?"

**TALN Analysis :**
```json
{
  "entities": [
    {"text": "volontaires", "ontology_class": "webprotege:RCXXzqv27uFuX5nYU81XUvw"},
    {"text": "compétences", "ontology_class": "eco:Competence"}
  ],
  "intent": {"primary_intent": "count"},
  "keywords": ["volontaires", "compétences", "environnement"]
}
```

**SPARQL généré :**
```sparql
PREFIX eco: <...>
PREFIX webprotege: <...>
SELECT (COUNT(DISTINCT ?volunteer) AS ?count) WHERE {
  ?volunteer rdf:type webprotege:RCXXzqv27uFuX5nYU81XUvw .
  ?volunteer eco:hasCompetence ?competence .
  ?competence eco:name ?competenceName .
  FILTER (CONTAINS(LCASE(?competenceName), "environnement"))
}
```

## ✅ Critères d'évaluation couverts

### Objectif 4 : Recherche sémantique ✅

La couche IA API implémente directement l'objectif de **Recherche sémantique** :

1. ✅ **Requêtes complexes** : Les utilisateurs peuvent poser des questions en langage naturel
2. ✅ **Sémantique des données** : Le système utilise la structure de l'ontologie OWL
3. ✅ **Trouver des informations pertinentes** : Les requêtes SPARQL générées sont adaptées à l'intention
4. ✅ **Interaction intuitive** : Les utilisateurs n'ont pas besoin de connaître SPARQL

## 🎓 Points techniques à mettre en avant

### 1. Traitement du Langage Naturel (TALN)
- Extraction d'entités nommées
- Classification d'intentions
- Analyse sémantique (relations, rôles)
- Mapping automatique vers l'ontologie

### 2. Intelligence Artificielle (Gemini)
- Génération de code SPARQL
- Compréhension du contexte ontologique
- Adaptation aux variations de formulation
- Validation et correction automatique

### 3. Intégration sémantique
- Utilisation correcte des préfixes OWL
- Respect de la hiérarchie des classes
- Gestion des relations entre entités
- Optimisation des requêtes

### 4. Robustesse
- Système de fallback (template engine)
- Gestion d'erreurs
- Validation des requêtes
- Logging et débogage

## 📝 Fichiers clés de l'implémentation

| Fichier | Rôle | Lignes |
|---------|------|--------|
| `backend/modules/taln_service.py` | Analyse TALN | 486 |
| `backend/modules/gemini_sparql_service.py` | Génération SPARQL | ~300 |
| `backend/modules/search.py` | Endpoint API | 145 |
| `backend/sparql_utils.py` | Exécution SPARQL | 81 |

## 🚀 Pour la démonstration

### Scénarios à présenter :

1. **Question simple :** "Liste les événements"
2. **Question avec filtre :** "Quelles sont les campagnes actives ?"
3. **Question complexe :** "Combien de volontaires à Paris ont des compétences en environnement ?"
4. **Question temporelle :** "Montre-moi les événements à venir"
5. **Question de détails :** "Quels sont les détails de l'événement X ?"

### Points à démontrer :

1. ✅ Transformation automatique question → SPARQL
2. ✅ Extraction d'entités et mapping vers l'ontologie
3. ✅ Génération de requêtes adaptées à l'intention
4. ✅ Résultats pertinents retournés
5. ✅ Interface utilisateur conviviale (Front-end)

## 📚 Documentation complémentaire

- `TALN_INTEGRATION.md` - Documentation technique de l'intégration
- `TALN_API_ALTERNATIVES.md` - Alternatives à l'API TALN (fallback)
- `backend/test_taln_integration.py` - Tests de l'intégration

## 🎯 Résumé pour l'évaluation

**La couche IA API est le cœur de votre système de recherche sémantique.**

Elle permet de :
- ✅ Recevoir des questions en langage naturel depuis le Front-end
- ✅ Analyser sémantiquement ces questions (TALN)
- ✅ Générer des requêtes SPARQL adaptées (Gemini)
- ✅ Exécuter ces requêtes sur votre ontologie via Fuseki
- ✅ Retourner des résultats pertinents aux utilisateurs

**Cette implémentation démontre parfaitement l'objectif de "Recherche sémantique"** en permettant aux utilisateurs de poser des requêtes complexes et de trouver des informations pertinentes en utilisant la sémantique des données, sans avoir besoin de connaître SPARQL ou la structure de l'ontologie.

