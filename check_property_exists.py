import requests

FUSEKI_QUERY = "http://localhost:3030/eco-ontology/query"

# Vérifier si la propriété existe dans le schéma
print("Vérification si la propriété RDT3XEARggTy1BIBKDXXrmx existe...")

query1 = """
PREFIX webprotege: <http://webprotege.stanford.edu/>
SELECT ?prop WHERE {
    ?prop a owl:DatatypeProperty .
    FILTER(STRSTARTS(STR(?prop), "http://webprotege.stanford.edu/"))
}
LIMIT 20
"""
resp1 = requests.get(FUSEKI_QUERY, params={'query': query1}, headers={'Accept': 'application/json'})
data1 = resp1.json()
print(f"Propriétés DatatypeProperty trouvées: {len(data1['results']['bindings'])}")
for b in data1['results']['bindings'][:5]:
    print(f"  {b['prop']['value']}")

# Chercher spécifiquement RDT3XEARggTy1BIBKDXXrmx
print("\nRecherche spécifique de RDT3XEARggTy1BIBKDXXrmx...")
query2 = """
SELECT ?s ?p ?o WHERE {
    ?s <http://webprotege.stanford.edu/RDT3XEARggTy1BIBKDXXrmx> ?o .
}
LIMIT 10
"""
resp2 = requests.get(FUSEKI_QUERY, params={'query': query2}, headers={'Accept': 'application/json'})
data2 = resp2.json()
print(f"Triplets avec RDT3XEARggTy1BIBKDXXrmx: {len(data2['results']['bindings'])}")

# Chercher la définition de la propriété
print("\nRecherche de la définition de la propriété...")
query3 = """
SELECT ?s ?p ?o WHERE {
    <http://webprotege.stanford.edu/RDT3XEARggTy1BIBKDXXrmx> ?p ?o .
}
"""
resp3 = requests.get(FUSEKI_QUERY, params={'query': query3}, headers={'Accept': 'application/json'})
data3 = resp3.json()
print(f"Triplets pour la définition: {len(data3['results']['bindings'])}")
for b in data3['results']['bindings']:
    print(f"  {b['p']['value'].split('/')[-1]}: {b['o'].get('value', 'N/A')}")

