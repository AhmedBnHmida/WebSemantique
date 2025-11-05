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

def analyze_rdf_file(file_path):
    """Analyser le fichier RDF avant chargement pour voir ce qui est présent"""
    try:
        print("\n📋 Analyse du fichier RDF avant chargement...")
        g = Graph()
        g.parse(file_path, format="xml")
        print(f"✓ Fichier RDF parsé: {len(g)} triplets trouvés")
        
        # Analyser les types d'entités présents
        ontology_prefix = "http://www.education-intelligente.org/ontologie#"
        entity_types_map = {
            "Personnes": f"{ontology_prefix}Personne",
            "Universites": f"{ontology_prefix}Universite",
            "Specialites": f"{ontology_prefix}Specialite",
            "Cours": f"{ontology_prefix}Cours",
            "Competences": f"{ontology_prefix}Competence",
            "ProjetsAcademiques": f"{ontology_prefix}ProjetAcademique",
            "RessourcesPedagogiques": f"{ontology_prefix}RessourcePedagogique",
            "TechnologiesEducatives": f"{ontology_prefix}TechnologieEducative",
            "Evaluations": f"{ontology_prefix}Evaluation",
            "OrientationsAcademiques": f"{ontology_prefix}OrientationAcademique"
        }
        
        print("\n📊 Entités trouvées dans le fichier RDF:")
        print("-" * 60)
        
        for entity_name, class_uri in entity_types_map.items():
            # Use rdfs:subClassOf* to include all subclasses
            query = f"""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT (COUNT(DISTINCT ?s) as ?count) WHERE {{
                ?s a ?type .
                ?type rdfs:subClassOf* <{class_uri}> .
            }}
            """
            try:
                result = list(g.query(query))
                count = int(result[0][0]) if result else 0
                if count > 0:
                    print(f"  ✓ {entity_name:30s}: {count:3d} entité(s)")
                else:
                    print(f"  ✗ {entity_name:30s}: {count:3d} entité(s)")
            except Exception as e:
                # Fallback: try direct type check
                query = f"""
                SELECT (COUNT(DISTINCT ?s) as ?count) WHERE {{
                    ?s a <{class_uri}> .
                }}
                """
                result = list(g.query(query))
                count = int(result[0][0]) if result else 0
                print(f"  ? {entity_name:30s}: {count:3d} entité(s) (fallback)")
        
        print("-" * 60)
        return g
        
    except Exception as e:
        print(f"✗ Erreur lors de l'analyse: {str(e)}")
        return None

def load_ontology_to_fuseki_batch(file_path):
    """Charger l'ontologie en utilisant l'upload direct par fichier"""
    try:
        print("\nChargement du fichier RDF...")
        
        # Charger le fichier RDF
        g = Graph()
        g.parse(file_path, format="xml")
        print(f"✓ Ontologie chargée: {len(g)} triplets trouvés")
        
        # Sauvegarder temporairement le graphe
        temp_file = "temp_ontology.ttl"
        g.serialize(temp_file, format="turtle")
        
        # Vérifier que le fichier temporaire contient bien des données
        import os
        file_size = os.path.getsize(temp_file)
        print(f"✓ Fichier temporaire créé ({file_size:,} bytes)")
        
        if file_size < 1000:
            print("⚠️  ATTENTION: Le fichier temporaire est très petit, il pourrait y avoir un problème de conversion!")
        
        # Upload direct du fichier vers Fuseki
        with open(temp_file, 'rb') as f:
            headers = {'Content-Type': 'text/turtle'}
            print(f"Upload du fichier vers Fuseki ({file_size:,} bytes)...")
            response = requests.post(FUSEKI_DATA, data=f, headers=headers, timeout=120)
            
        if response.status_code in [200, 201, 204]:
            print("✓ Données chargées avec succès via upload direct")
            
            # Attendre un peu pour que Fuseki indexe les données
            print("Attente de l'indexation Fuseki (3 secondes)...")
            time.sleep(3)
            
            # Nettoyer le fichier temporaire
            import os
            if os.path.exists(temp_file):
                os.remove(temp_file)
                print("✓ Fichier temporaire supprimé")
                
            return True
        else:
            print(f"✗ Erreur lors de l'upload: {response.status_code}")
            print(f"  Réponse: {response.text[:500] if response.text else 'Aucune réponse'}")
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
        # Note: Pour de gros fichiers, on doit faire par lots
        print("Conversion en format N-Triples...")
        ntriples_data = g.serialize(format='nt')
        
        # Vérifier la taille des données
        data_size = len(ntriples_data.encode('utf-8'))
        print(f"✓ Données N-Triples: {data_size:,} bytes")
        
        # Si c'est trop gros, on utilise LOAD au lieu de INSERT DATA
        if data_size > 10000000:  # > 10MB
            print("⚠️  Fichier volumineux détecté, utilisation de LOAD...")
            # Sauvegarder en fichier temporaire et utiliser LOAD
            temp_file = "temp_ontology.nt"
            with open(temp_file, 'wb') as f:
                f.write(ntriples_data.encode('utf-8'))
            
            # Upload du fichier d'abord
            with open(temp_file, 'rb') as f:
                headers = {'Content-Type': 'application/n-triples'}
                response = requests.post(FUSEKI_DATA, data=f, headers=headers, timeout=120)
            
            # Nettoyer
            import os
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
            if response.status_code in [200, 201, 204]:
                print("✓ Données chargées avec succès via upload N-Triples")
                time.sleep(3)  # Attendre l'indexation
                return True
            else:
                print(f"✗ Erreur upload N-Triples: {response.status_code}")
                return False
        else:
            # Préparer la requête INSERT
            insert_query = f"""
            INSERT DATA {{
                {ntriples_data}
            }}
            """
            
            headers = {'Content-Type': 'application/sparql-update'}
            print("Envoi de la requête SPARQL INSERT...")
            response = requests.post(FUSEKI_UPDATE, data=insert_query.encode('utf-8'), headers=headers, timeout=180)
            
            if response.status_code in [200, 204]:
                print("✓ Données chargées avec succès via SPARQL INSERT")
                time.sleep(3)  # Attendre l'indexation
                return True
            else:
                print(f"✗ Erreur SPARQL INSERT: {response.status_code}")
                print(f"  Réponse: {response.text[:500] if response.text else 'Aucune réponse'}")
                return False
            
    except Exception as e:
        print(f"✗ Erreur lors du chargement SPARQL: {str(e)}")
        return False

def verify_data_loaded():
    """Vérifier que les données sont bien chargées - Vérifie TOUS les types d'entités"""
    try:
        headers = {'Accept': 'application/json'}
        ontology_prefix = "http://www.education-intelligente.org/ontologie#"
        
        # 1. Compter le total des triplets
        test_query = """
        PREFIX ont: <http://www.education-intelligente.org/ontologie#>
        SELECT (COUNT(*) as ?count) WHERE { 
            ?s ?p ?o 
        }
        """
        response = requests.get(FUSEKI_QUERY, params={'query': test_query}, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            count = data['results']['bindings'][0]['count']['value']
            print(f"✓ Total des triplets dans Fuseki: {count}")
        else:
            print(f"✗ Impossible de compter les triplets: {response.status_code}")
            return False
        
        # 2. Vérifier tous les types d'entités
        entity_types = {
            "Personnes": [
                "ont:Personne", "ont:Etudiant", "ont:Enseignant", "ont:Professeur",
                "ont:Assistant", "ont:Encadrant", "ont:EtudiantLicence",
                "ont:EtudiantMaster", "ont:EtudiantDoctorat"
            ],
            "Universites": ["ont:Universite", "ont:UniversitePublique", "ont:UniversitePrivee"],
            "Specialites": ["ont:Specialite", "ont:SpecialiteInformatique", "ont:SpecialiteEconomie",
                           "ont:SpecialiteDroit", "ont:SpecialiteLettres", "ont:SpecialiteSciences",
                           "ont:SpecialiteMedecine", "ont:SpecialiteIngenierie"],
            "Cours": ["ont:Cours", "ont:CoursTheorique", "ont:CoursPratique", "ont:CoursDirige",
                     "ont:CoursEnLigne", "ont:CoursObligatoire", "ont:CoursOptionnel"],
            "Competences": ["ont:Competence", "ont:CompetenceTechnique", "ont:CompetenceLinguistique",
                           "ont:CompetenceMethodologique", "ont:CompetenceRecherche",
                           "ont:CompetenceTransversale"],
            "ProjetsAcademiques": ["ont:ProjetAcademique", "ont:ProjetDeFinDEtudes", "ont:MemoireDeMaster",
                                   "ont:ProjetDeRecherche", "ont:ProjetCollaboratif", "ont:TheseDoctorale"],
            "RessourcesPedagogiques": ["ont:RessourcePedagogique", "ont:ArticleScientifique", "ont:Livre",
                                      "ont:VideoCours", "ont:SupportCours", "ont:PlateformeEnLigne",
                                      "ont:OutilInteractif"],
            "TechnologiesEducatives": ["ont:TechnologieEducative", "ont:PlateformeLMS", "ont:MOOCPlatform",
                                      "ont:ApplicationMobileEducative", "ont:OutilIAEducatif",
                                      "ont:SeriousGame", "ont:RealiteVirtuelleEducative"],
            "Evaluations": ["ont:Evaluation", "ont:ControleContinu", "ont:ExamenFinal", "ont:QuizEnLigne",
                           "ont:RapportDeStage", "ont:Soutenance", "ont:ProjetEvalue"],
            "OrientationsAcademiques": ["ont:OrientationAcademique", "ont:ConseilOrientation",
                                        "ont:EntretienConseiller", "ont:PlanDeCarriere",
                                        "ont:SalonEtudiant", "ont:StageOrientation", "ont:TestPsychometrique"]
        }
        
        print("\n📊 Vérification des entités par type:")
        print("-" * 60)
        
        all_loaded = True
        total_entities = 0
        
        for entity_type_name, ontology_classes in entity_types.items():
            # Try using rdfs:subClassOf* first (more efficient and includes all subclasses)
            base_class = ontology_classes[0] if ontology_classes else None
            if base_class:
                # Extract base class name (remove "ont:" prefix)
                base_class_name = base_class.replace("ont:", "")
                base_class_uri = f"{ontology_prefix.replace('#', '')}#{base_class_name}"
                
                count_query = f"""
                PREFIX ont: <{ontology_prefix.replace('#', '')}#>
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                SELECT (COUNT(DISTINCT ?s) as ?count) WHERE {{
                    ?s a ?type .
                    ?type rdfs:subClassOf* <{base_class_uri}> .
                }}
                """
            else:
                # Fallback: Créer une requête UNION pour compter toutes les sous-classes
                union_parts = " UNION ".join([f"{{ ?s a {cls} }}" for cls in ontology_classes])
                
                count_query = f"""
                PREFIX ont: <{ontology_prefix.replace('#', '')}#>
                SELECT (COUNT(DISTINCT ?s) as ?count) WHERE {{
                    {union_parts}
                }}
                """
            
            try:
                response = requests.get(FUSEKI_QUERY, params={'query': count_query}, headers=headers, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    entity_count = int(data['results']['bindings'][0]['count']['value'])
                    total_entities += entity_count
                    
                    if entity_count > 0:
                        print(f"✓ {entity_type_name:30s}: {entity_count:3d} entité(s)")
                    else:
                        print(f"✗ {entity_type_name:30s}: {entity_count:3d} entité(s) - MANQUANT!")
                        all_loaded = False
                else:
                    print(f"✗ {entity_type_name:30s}: Erreur de requête ({response.status_code})")
                    all_loaded = False
            except Exception as e:
                print(f"✗ {entity_type_name:30s}: Erreur - {str(e)}")
                all_loaded = False
        
        print("-" * 60)
        print(f"📈 Total des entités chargées: {total_entities}")
        
        # Vérifier quelques entités spécifiques pour debug
        print("\n🔍 Vérification de quelques entités spécifiques:")
        specific_checks = [
            ("Cours (IntroductionIA)", "Cours", "IntroductionIA"),
            ("Competence (Python)", "Competence", "Competence_Python"),
            ("Projet (PFE)", "ProjetAcademique", "Projet_PFE"),
            ("Ressource (Livre)", "RessourcePedagogique", "Livre"),
            ("Technologie (Moodle)", "TechnologieEducative", "Moodle"),
            ("Evaluation (Controle)", "Evaluation", "Controle"),
            ("Orientation (Conseil)", "OrientationAcademique", "Conseil")
        ]
        
        for check_name, class_type, search_term in specific_checks:
            # Use subClassOf* to include all subclasses
            class_uri = f"{ontology_prefix.replace('#', '')}#{class_type}"
            check_query = f"""
            PREFIX ont: <{ontology_prefix.replace('#', '')}#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT ?s WHERE {{
                ?s a ?type .
                ?type rdfs:subClassOf* <{class_uri}> .
                FILTER(CONTAINS(STR(?s), "{search_term}"))
            }}
            LIMIT 1
            """
            
            try:
                response = requests.get(FUSEKI_QUERY, params={'query': check_query}, headers=headers, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    if len(data['results']['bindings']) > 0:
                        print(f"  ✓ {check_name} trouvé")
                    else:
                        print(f"  ✗ {check_name} non trouvé")
            except Exception as e:
                print(f"  ✗ {check_name} erreur: {str(e)}")
        
        # Additional check: Count all NamedIndividuals
        print("\n🔍 Vérification des NamedIndividuals (toutes les instances):")
        named_individuals_query = """
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdf: <http://www.w3.org/1999/02/22/rdf-syntax-ns#>
        SELECT (COUNT(DISTINCT ?s) as ?count) WHERE {
            ?s a owl:NamedIndividual .
        }
        """
        try:
            response = requests.get(FUSEKI_QUERY, params={'query': named_individuals_query}, headers=headers, timeout=30)
            if response.status_code == 200:
                data = response.json()
                ni_count = int(data['results']['bindings'][0]['count']['value'])
                print(f"  Total NamedIndividuals: {ni_count}")
                if ni_count < 100:
                    print(f"  ⚠️  ATTENTION: Moins de 100 entités trouvées! (Attendu: ~141)")
        except Exception as e:
            print(f"  ✗ Erreur comptage NamedIndividuals: {str(e)}")
        
        return all_loaded
            
    except Exception as e:
        print(f"✗ Erreur de vérification: {str(e)}")
        import traceback
        traceback.print_exc()
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
    
    # Analyser le fichier RDF avant chargement
    rdf_graph = analyze_rdf_file(file_path)
    if rdf_graph is None:
        print("✗ Impossible d'analyser le fichier RDF")
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
    print("\n" + "=" * 60)
    print("VÉRIFICATION FINALE - TOUS LES TYPES D'ENTITÉS")
    print("=" * 60)
    
    if verify_data_loaded():
        print("\n🎉 CHARGEMENT TERMINÉ AVEC SUCCÈS!")
        print(f"\nURL de l'interface Fuseki: {FUSEKI_ENDPOINT}")
        print(f"Dataset: {FUSEKI_DATASET}")
        print(f"Interface de requête: {FUSEKI_QUERY}")
    else:
        print("\n⚠️  Chargement terminé avec des avertissements")
        print("Certaines entités peuvent être manquantes.")
        print("Vérifiez les logs ci-dessus pour plus de détails.")

if __name__ == '__main__':
    main()