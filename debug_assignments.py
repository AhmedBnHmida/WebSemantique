import requests

FUSEKI_ENDPOINT = "http://localhost:3030/eco-ontology"

# Vérifier tous les triplets pour RNewAssignment1
print("=== Tous les triplets pour RNewAssignment1 ===")
query1 = """
SELECT ?p ?o WHERE {
    <http://webprotege.stanford.edu/RNewAssignment1> ?p ?o .
}
"""
response1 = requests.get(f"{FUSEKI_ENDPOINT}/query", 
                         params={'query': query1}, 
                         headers={'Accept': 'application/json'})
data1 = response1.json()
for binding in data1['results']['bindings']:
    prop = binding['p']['value'].split('/')[-1]
    val = binding['o'].get('value', binding['o'])
    print(f"  {prop}: {val}")

print("\n=== Vérification si status existe ===")
query2 = """
SELECT ?o WHERE {
    <http://webprotege.stanford.edu/RNewAssignment1> 
    <http://webprotege.stanford.edu/RDT3XEARggTy1BIBKDXXrmx> 
    ?o .
}
"""
response2 = requests.get(f"{FUSEKI_ENDPOINT}/query", 
                         params={'query': query2}, 
                         headers={'Accept': 'application/json'})
data2 = response2.json()
print(f"Résultats: {len(data2['results']['bindings'])}")
if data2['results']['bindings']:
    for binding in data2['results']['bindings']:
        print(f"  Status: {binding['o']}")

print("\n=== Test INSERT simple ===")
# Tester un INSERT très simple
FUSEKI_UPDATE = "http://localhost:3030/eco-ontology/update"
insert_simple = """
INSERT DATA {
    <http://webprotege.stanford.edu/RNewAssignment1> 
    <http://webprotege.stanford.edu/RDT3XEARggTy1BIBKDXXrmx> 
    "TEST" .
}
"""

resp_insert = requests.post(FUSEKI_UPDATE, 
                           data=insert_simple, 
                           headers={'Content-Type': 'application/sparql-update'})
print(f"HTTP Status: {resp_insert.status_code}")

# Re-vérifier immédiatement
import time
time.sleep(1)
response3 = requests.get(f"{FUSEKI_ENDPOINT}/query", 
                         params={'query': query2}, 
                         headers={'Accept': 'application/json'})
data3 = response3.json()
print(f"Après INSERT: {len(data3['results']['bindings'])} résultats")
if data3['results']['bindings']:
    for binding in data3['results']['bindings']:
        print(f"  Status: {binding['o']}")
else:
    print("  Aucun résultat trouvé")

