# Ontology Management Guide

## 📋 Overview

This guide explains how deletions work and how to view/manage your ontology data.

## ❓ Question 1: Does deleting a course remove it from the .rdf file?

**Answer: NO** - Deletions modify the **Fuseki database**, not the original `.rdf` file.

### How it works:

1. **Original RDF file**: `data/educationInfin.rdf` is a **static file** that serves as the initial data source
2. **Fuseki database**: When you start the application, data is loaded from the RDF file into Fuseki (Apache Jena Fuseki server)
3. **All operations** (CREATE, UPDATE, DELETE) are performed on the **Fuseki database**, not the file
4. **The original RDF file remains unchanged**

### Deletion Process:

When you delete a course (or any entity):
- A SPARQL `DELETE` query is executed via `sparql_utils.execute_update()`
- The deletion happens in Fuseki at: `http://localhost:3030/educationInfin/update`
- The course is removed from the **live database**, but the original `.rdf` file stays the same

### To persist changes:

If you want to save the current state (including deletions), you need to **export** the current ontology from Fuseki (see below).

---

## 🔍 Question 2: How to view the current ontology (like phpMyAdmin)?

You have **3 ways** to view your ontology:

### Option 1: Fuseki Web Interface (Recommended - Like phpMyAdmin)

**Access:** http://localhost:3030

This is Fuseki's built-in web interface - similar to phpMyAdmin for databases.

**Features:**
- Browse datasets
- Execute SPARQL queries directly
- View query results in tables
- Export data
- Manage datasets

**Steps:**
1. Make sure Fuseki is running: `cd fuseki/apache-jena-fuseki-5.6.0 && java -jar fuseki-server.jar`
2. Open browser: http://localhost:3030
3. Select your dataset: `educationInfin`
4. Click "Query" tab
5. Write SPARQL queries to browse your data

**Example queries:**

```sparql
# Get all courses
PREFIX ont: <http://www.education-intelligente.org/ontologie#>
SELECT ?cours ?intitule WHERE {
    ?cours a ont:Cours .
    ?cours ont:intitule ?intitule .
}
LIMIT 100
```

```sparql
# Get all triples for a specific course
PREFIX ont: <http://www.education-intelligente.org/ontologie#>
SELECT ?p ?o WHERE {
    <http://www.education-intelligente.org/ontologie#Cours_XXX> ?p ?o .
}
```

```sparql
# Count all entities by type
PREFIX ont: <http://www.education-intelligente.org/ontologie#>
SELECT ?type (COUNT(?s) as ?count) WHERE {
    ?s a ?type .
    FILTER(STRSTARTS(STR(?type), "http://www.education-intelligente.org/ontologie#"))
}
GROUP BY ?type
ORDER BY DESC(?count)
```

---

### Option 2: API Endpoints (New - Just Added!)

I've added three new endpoints to help you browse and manage the ontology:

#### 1. Browse by Entity Type
**GET** `/api/ontology/browse`

Browse entities by type or URI:

```bash
# Get all courses
GET http://localhost:5000/api/ontology/browse?type=Cours&limit=50

# Get all properties of a specific entity
GET http://localhost:5000/api/ontology/browse?uri=http://www.education-intelligente.org/ontologie#Cours_XXX&limit=100

# Get all triples (limited)
GET http://localhost:5000/api/ontology/browse?limit=100
```

**Parameters:**
- `type` (optional): Entity type (e.g., 'Cours', 'Personne', 'Universite')
- `uri` (optional): Specific entity URI
- `limit` (optional, default: 100): Maximum number of results

#### 2. Execute Custom SPARQL Query
**POST** `/api/ontology/query`

Execute any SPARQL query - like the query interface in phpMyAdmin:

```bash
POST http://localhost:5000/api/ontology/query
Content-Type: application/json

{
  "query": "PREFIX ont: <http://www.education-intelligente.org/ontologie#>\nSELECT ?cours ?intitule WHERE {\n    ?cours a ont:Cours .\n    ?cours ont:intitule ?intitule .\n}\nLIMIT 10"
}
```

**Body:**
```json
{
  "query": "YOUR_SPARQL_QUERY_HERE"
}
```

#### 3. Export Current State
**GET** `/api/ontology/export`

Export the **current state** of the ontology from Fuseki (including all deletions and modifications):

```bash
# Export as RDF/XML (default)
GET http://localhost:5000/api/ontology/export

# Export as Turtle
GET http://localhost:5000/api/ontology/export?format=turtle

# Export as N-Triples
GET http://localhost:5000/api/ontology/export?format=ntriples

# Export as JSON-LD
GET http://localhost:5000/api/ontology/export?format=json-ld
```

**Formats:**
- `xml` (default): RDF/XML format
- `turtle`: Turtle format (more readable)
- `ntriples`: N-Triples format
- `json-ld`: JSON-LD format

**Use case:** After making changes (deletions, updates, additions), export to get the current state and save it as a new `.rdf` file.

---

### Option 3: Frontend Components

The frontend already has some ontology viewing capabilities:

- **OntologyStats component**: Shows statistics about your ontology
- **Graph visualization**: Available via `/api/ontology/graph` endpoint

---

## 📊 Summary

| Question | Answer |
|----------|--------|
| **Does deletion modify .rdf file?** | ❌ No - only modifies Fuseki database |
| **Where are deletions stored?** | In Fuseki (in-memory or persisted depending on configuration) |
| **How to view current state?** | 1. Fuseki UI (http://localhost:3030)<br>2. API endpoints (`/api/ontology/browse`, `/api/ontology/query`)<br>3. Export endpoint (`/api/ontology/export`) |
| **How to save current state?** | Use `/api/ontology/export` to download current ontology |

---

## 🔄 Workflow Example

1. **Initial load**: `scripts/load_data.py` loads `data/educationInfin.rdf` into Fuseki
2. **Make changes**: Add/update/delete entities via API
3. **View changes**: Use Fuseki UI or API endpoints
4. **Export if needed**: Use `/api/ontology/export` to save current state
5. **Reload if needed**: Run `scripts/load_data.py` again to reset to original state

---

## 💡 Tips

1. **Fuseki persistence**: By default, Fuseki may use in-memory storage. Check your Fuseki configuration if you want persistent storage
2. **Regular exports**: Export periodically if you want to keep snapshots of your ontology state
3. **Backup original**: Keep the original `educationInfin.rdf` file as a backup
4. **Query testing**: Use Fuseki UI to test SPARQL queries before using them in your application

---

## 🚀 Quick Start

1. **View in Fuseki UI:**
   ```
   http://localhost:3030
   → Select dataset: educationInfin
   → Click "Query" tab
   → Write SPARQL queries
   ```

2. **Browse via API:**
   ```bash
   curl http://localhost:5000/api/ontology/browse?type=Cours
   ```

3. **Export current state:**
   ```bash
   curl http://localhost:5000/api/ontology/export?format=turtle -o current_ontology.ttl
   ```



