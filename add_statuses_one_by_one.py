import requests
import time

FUSEKI_UPDATE = "http://localhost:3030/eco-ontology/update"

# D'abord supprimer TEST
print("Suppression de TEST...")
delete_query = """
DELETE WHERE {
    <http://webprotege.stanford.edu/RNewAssignment1> 
    <http://webprotege.stanford.edu/RDT3XEARggTy1BIBKDXXrmx> 
    "TEST" .
}
"""
requests.post(FUSEKI_UPDATE, data=delete_query, headers={'Content-Type': 'application/sparql-update'})

# Assignements et leurs statuts
assignments = [
    ("http://webprotege.stanford.edu/RNewAssignment1", "approuvé"),
    ("http://webprotege.stanford.edu/RNewAssignment2", "rejeté"),
    ("http://webprotege.stanford.edu/RAssignment3", "approuvé"),
    ("http://webprotege.stanford.edu/RAssignment4", "approuvé"),
    ("http://webprotege.stanford.edu/RAssignment5", "rejeté"),
    ("http://webprotege.stanford.edu/RAssignment6", "rejeté"),
    ("http://webprotege.stanford.edu/RAssignment7", "approuvé"),
]

predicate = "http://webprotege.stanford.edu/RDT3XEARggTy1BIBKDXXrmx"

print("\nAjout des statuts un par un...")
for assignment, status in assignments:
    query = f'''
INSERT DATA {{
    <{assignment}> 
    <{predicate}> 
    "{status}" .
}}'''
    
    headers = {'Content-Type': 'application/sparql-update'}
    response = requests.post(FUSEKI_UPDATE, data=query, headers=headers)
    
    if response.status_code in [200, 204]:
        assignment_name = assignment.split('/')[-1]
        print(f"✅ {assignment_name}: {status}")
    else:
        print(f"❌ Erreur: HTTP {response.status_code}")

# Vérifier
print("\nVérification finale...")
time.sleep(2)  # Attendre un peu pour que Fuseki synchronise

verify_query = """
PREFIX webprotege: <http://webprotege.stanford.edu/>
SELECT ?assignment ?status WHERE {
    ?assignment a webprotege:Rj2A7xNWLfpNcbE4HJMKqN .
    ?assignment webprotege:RDT3XEARggTy1BIBKDXXrmx ?status .
}
"""

verify_headers = {'Accept': 'application/json'}
verify_response = requests.get("http://localhost:3030/eco-ontology/query", 
                              params={'query': verify_query}, 
                              headers=verify_headers)

if verify_response.status_code == 200:
    data = verify_response.json()
    print(f"✅ {len(data['results']['bindings'])} statuts trouvés:")
    for binding in data['results']['bindings']:
        assignment = binding['assignment']['value'].split('/')[-1]
        status = binding['status']['value']
        print(f"  - {assignment}: {status}")
    
    if len(data['results']['bindings']) == 7:
        print("\n🎉 Tous les statuts ont été ajoutés avec succès!")
    else:
        print(f"\n⚠️ Seulement {len(data['results']['bindings'])}/7 statuts trouvés")

