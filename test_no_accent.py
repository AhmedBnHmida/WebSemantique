import requests
import time

FUSEKI_UPDATE = "http://localhost:3030/eco-ontology/update"

# Tester avec "approved" (sans accent)
print("Test: INSERT avec 'approved' (sans accent)")
query = '''
INSERT DATA { 
    <http://webprotege.stanford.edu/RNewAssignment1> 
    <http://webprotege.stanford.edu/RDT3XEARggTy1BIBKDXXrmx> 
    "approved" . 
}'''
resp = requests.post(FUSEKI_UPDATE, data=query, headers={'Content-Type': 'application/sparql-update'})
print(f"HTTP: {resp.status_code}")

time.sleep(1)

# Vérifier
check = '''
SELECT ?o WHERE {
    <http://webprotege.stanford.edu/RNewAssignment1> 
    <http://webprotege.stanford.edu/RDT3XEARggTy1BIBKDXXrmx> 
    ?o . 
}'''
resp2 = requests.get("http://localhost:3030/eco-ontology/query", 
                    params={'query': check}, 
                    headers={'Accept': 'application/json'})
data = resp2.json()
print(f"Résultats: {len(data['results']['bindings'])}")
for b in data['results']['bindings']:
    print(f"  Status: {b['o']['value']}")

# Maintenant tester avec accent é
print("\nTest: INSERT avec 'approuvé' (avec accent)")
query2 = '''
INSERT DATA { 
    <http://webprotege.stanford.edu/RNewAssignment1> 
    <http://webprotege.stanford.edu/RDT3XEARggTy1BIBKDXXrmx> 
    "approuvé" . 
}'''
resp3 = requests.post(FUSEKI_UPDATE, data=query2, headers={'Content-Type': 'application/sparql-update'})
print(f"HTTP: {resp3.status_code}")

time.sleep(1)

resp4 = requests.get("http://localhost:3030/eco-ontology/query", 
                    params={'query': check}, 
                    headers={'Accept': 'application/json'})
data2 = resp4.json()
print(f"Résultats: {len(data2['results']['bindings'])}")
for b in data2['results']['bindings']:
    print(f"  Status: {b['o']['value']}")

