from rdflib import Graph
import requests
import time
import sys

# Configuration Fuseki
FUSEKI_ENDPOINT = "http://localhost:3030"
FUSEKI_DATASET = "educationInfin"
FUSEKI_DATA = f"{FUSEKI_ENDPOINT}/{FUSEKI_DATASET}/data"
FUSEKI_UPDATE = f"{FUSEKI_ENDPOINT}/{FUSEKI_DATASET}/update"
FUSEKI_QUERY = f"{FUSEKI_ENDPOINT}/{FUSEKI_DATASET}/query"

def test_fuseki_connection():
    """Tester la connexion à Fuseki"""
    try:
        response = requests.get(FUSEKI_ENDPOINT, timeout=10)
        if response.status_code == 200:
            print("✓ Connexion à Fuseki réussie")
            return True
        else:
            print(f"✗ Fuseki ne répond pas: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Impossible de se connecter à Fuseki: {str(e)}")
        return False

def clear_dataset():
    """Vider le dataset avant de charger les nouvelles données"""
    try:
        clear_query = "CLEAR ALL"
        headers = {'Content-Type': 'application/sparql-update'}
        
        response = requests.post(FUSEKI_UPDATE, data=clear_query, headers=headers, timeout=30)
        
        if response.status_code in [200, 204]:
            print("✓ Dataset vidé avec succès")
            return True
        else:
            print(f"✗ Impossible de vider le dataset: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Erreur lors du vidage: {str(e)}")
        return False

def load_ontology_to_fuseki_batch(file_path):
    """Charger l'ontologie en utilisant l'upload direct par fichier"""
    try:
        print("Chargement du fichier RDF...")
        
        # Charger le fichier RDF
        g = Graph()
        g.parse(file_path, format="xml")
        print(f"✓ Ontologie chargée: {len(g)} triplets trouvés")
        
        # Sauvegarder temporairement le graphe
        temp_file = "temp_ontology.ttl"
        g.serialize(temp_file, format="turtle")
        print("✓ Fichier temporaire créé")
        
        # Upload direct du fichier vers Fuseki
        with open(temp_file, 'rb') as f:
            headers = {'Content-Type': 'text/turtle'}
            response = requests.post(FUSEKI_DATA, data=f, headers=headers, timeout=60)
            
        if response.status_code in [200, 201, 204]:
            print("✓ Données chargées avec succès via upload direct")
            
            # Nettoyer le fichier temporaire
            import os
            if os.path.exists(temp_file):
                os.remove(temp_file)
                
            return True
        else:
            print(f"✗ Erreur lors de l'upload: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Erreur lors du chargement: {str(e)}")
        return False

def load_ontology_to_fuseki_sparql(file_path):
    """Charger l'ontologie en utilisant SPARQL INSERT (méthode alternative)"""
    try:
        print("Chargement du fichier RDF pour méthode SPARQL...")
        
        g = Graph()
        g.parse(file_path, format="xml")
        print(f"✓ Ontologie chargée: {len(g)} triplets trouvés")
        
        # Convertir en format N-Triples pour INSERT
        ntriples_data = g.serialize(format='nt')
        
        # Préparer la requête INSERT
        insert_query = f"""
        INSERT DATA {{
            {ntriples_data}
        }}
        """
        
        headers = {'Content-Type': 'application/sparql-update'}
        response = requests.post(FUSEKI_UPDATE, data=insert_query, headers=headers, timeout=120)
        
        if response.status_code in [200, 204]:
            print("✓ Données chargées avec succès via SPARQL INSERT")
            return True
        else:
            print(f"✗ Erreur SPARQL INSERT: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Erreur lors du chargement SPARQL: {str(e)}")
        return False

def verify_data_loaded():
    """Vérifier que les données sont bien chargées"""
    try:
        test_query = """
        SELECT (COUNT(*) as ?count) WHERE { 
            ?s ?p ?o 
        }
        """
        headers = {'Accept': 'application/json'}
        response = requests.get(FUSEKI_QUERY, params={'query': test_query}, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            count = data['results']['bindings'][0]['count']['value']
            print(f"✓ Total des triplets dans Fuseki: {count}")
            
            # Compter quelques entités importantes
            count_students = """
            SELECT (COUNT(DISTINCT ?s) as ?count) WHERE {
                ?s a <http://www.education-intelligente.org/ontologie#Etudiant>
            }
            """
            
            response = requests.get(FUSEKI_QUERY, params={'query': count_students}, headers=headers, timeout=30)
            if response.status_code == 200:
                data = response.json()
                student_count = data['results']['bindings'][0]['count']['value']
                print(f"✓ Nombre d'étudiants: {student_count}")
            
            return True
        else:
            print(f"✗ Impossible de vérifier les données: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Erreur de vérification: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("CHARGEMENT DE L'ONTOLOGIE ÉDUCATION INTELLIGENTE")
    print("=" * 60)
    
    # Vérifier que le fichier existe
    file_path = "../data/educationInfin.rdf"
    import os
    if not os.path.exists(file_path):
        print(f"✗ Fichier non trouvé: {file_path}")
        print("Assurez-vous que le fichier RDF est dans le dossier 'data/'")
        return
    
    if not test_fuseki_connection():
        print("\nVeuillez démarrer Fuseki d'abord:")
        print("./fuseki-server")
        return
    
    # Vider le dataset
    if not clear_dataset():
        print("Échec du vidage du dataset")
        return
    
    # Attendre un peu après le vidage
    time.sleep(2)
    
    # Essayer la méthode d'upload direct d'abord (plus rapide)
    print("\n1. Tentative de chargement par upload direct...")
    if load_ontology_to_fuseki_batch(file_path):
        print("✓ Méthode upload direct réussie!")
    else:
        print("✗ Échec de l'upload direct, tentative avec SPARQL INSERT...")
        if not load_ontology_to_fuseki_sparql(file_path):
            print("✗ Échec de toutes les méthodes de chargement")
            return
    
    # Vérification finale
    print("\n" + "=" * 40)
    print("VÉRIFICATION FINALE")
    print("=" * 40)
    
    if verify_data_loaded():
        print("\n🎉 CHARGEMENT TERMINÉ AVEC SUCCÈS!")
        print(f"URL de l'interface Fuseki: {FUSEKI_ENDPOINT}")
        print(f"Dataset: {FUSEKI_DATASET}")
    else:
        print("\n⚠️  Chargement terminé avec des avertissements")

if __name__ == '__main__':
    main()