import requests
import time

FUSEKI_UPDATE = "http://localhost:3030/eco-ontology/update"
FUSEKI_QUERY = "http://localhost:3030/eco-ontology/query"

# Test 1: Ajouter un rdfs:label pour RNewAssignment1
print("Test 1: Ajout d'un nouveau label pour RNewAssignment1")
query1 = """
INSERT DATA {
    <http://webprotege.stanford.edu/RNewAssignment1> 
    <http://www.w3.org/2000/01/rdf-schema#label> 
    "test_insert_label" .
}
"""
resp1 = requests.post(FUSEKI_UPDATE, data=query1, headers={'Content-Type': 'application/sparql-update'})
print(f"  INSERT HTTP: {resp1.status_code}")

time.sleep(1)

# Vérifier
check1 = """
SELECT ?o WHERE {
    <http://webprotege.stanford.edu/RNewAssignment1> 
    <http://www.w3.org/2000/01/rdf-schema#label> 
    ?o .
}
"""
resp_check1 = requests.get(FUSEKI_QUERY, params={'query': check1}, headers={'Accept': 'application/json'})
data1 = resp_check1.json()
print(f"  Labels trouvés: {len(data1['results']['bindings'])}")
for b in data1['results']['bindings']:
    print(f"    Label: {b['o']['value']}")

# Test 2: Ajouter le status
print("\nTest 2: Ajout du status")
query2 = """
INSERT DATA {
    <http://webprotege.stanford.edu/RNewAssignment1> 
    <http://webprotege.stanford.edu/RDT3XEARggTy1BIBKDXXrmx> 
    "approuvé" .
}
"""
resp2 = requests.post(FUSEKI_UPDATE, data=query2, headers={'Content-Type': 'application/sparql-update'})
print(f"  INSERT HTTP: {resp2.status_code}")

time.sleep(1)

# Vérifier
check2 = """
SELECT ?o WHERE {
    <http://webprotege.stanford.edu/RNewAssignment1> 
    <http://webprotege.stanford.edu/RDT3XEARggTy1BIBKDXXrmx> 
    ?o .
}
"""
resp_check2 = requests.get(FUSEKI_QUERY, params={'query': check2}, headers={'Accept': 'application/json'})
data2 = resp_check2.json()
print(f"  Status trouvés: {len(data2['results']['bindings'])}")
for b in data2['results']['bindings']:
    print(f"    Status: {b['o']['value']}")

