import os
import requests
import json
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

load_dotenv()

# Try to import Gemini for NLP analysis
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("WARNING: google-generativeai not installed. Install with: pip install google-generativeai")

class TALNService:
    """
    Service for Text Analysis and Language Processing (TALN) API integration.
    This service extracts entities, relationships, and semantic information from natural language questions.
    """
    
    def __init__(self):
        self.api_key = os.getenv('TALN_API_KEY')
        self.base_url = os.getenv('TALN_API_URL', 'https://api.taln.fr/v1')  # Default TALN API URL
        
        if not self.api_key:
            print("WARNING: TALN_API_KEY not found in environment variables")
            print("Using fallback entity extraction...")
            self.use_fallback = True
        else:
            self.use_fallback = False
            print("SUCCESS: TALN API initialized successfully")
    
    def analyze_question(self, question: str) -> Dict[str, Any]:
        """
        Analyze a natural language question and extract:
        - Entities (Event, Location, User, Campaign, Resource, etc.)
        - Relationships between entities
        - Intent (what the user wants to know)
        - Keywords and semantic information
        
        Args:
            question (str): The natural language question
            
        Returns:
            Dict containing extracted entities, relationships, intent, and metadata
        """
        print(f"DEBUG: Starting TALN analysis for question: '{question}'")
        
        if self.use_fallback:
            print(f"DEBUG: Using fallback analysis (TALN API not configured)")
            result = self._fallback_analysis(question)
            print(f"DEBUG: Fallback analysis completed. Entities: {len(result.get('entities', []))}")
            return result
        
        try:
            print(f"DEBUG: Attempting TALN API call...")
            # Prepare the request payload
            payload = {
                "text": question,
                "language": "fr",  # French language
                "features": {
                    "entities": True,
                    "relationships": True,
                    "intent": True,
                    "keywords": True,
                    "semantic_roles": True,
                    "temporal_expressions": True,
                    "location_expressions": True
                },
                "domain": "education",  # Education domain analysis
                "ontology_mapping": True
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            print(f"DEBUG: Sending request to TALN API...")
            # Make API request
            response = requests.post(
                f"{self.base_url}/analyze",
                json=payload,
                headers=headers,
                timeout=10
            )
            
            print(f"DEBUG: TALN API response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                processed_result = self._process_taln_response(result, question)
                print(f"DEBUG: TALN API analysis completed. Entities: {len(processed_result.get('entities', []))}")
                return processed_result
            else:
                print(f"ERROR: TALN API error: {response.status_code} - {response.text}")
                print(f"DEBUG: Falling back to local analysis")
                return self._fallback_analysis(question)
                
        except Exception as e:
            print(f"ERROR: TALN API request failed: {e}")
            print(f"DEBUG: Falling back to local analysis")
            return self._fallback_analysis(question)
    
    def _process_taln_response(self, taln_result: Dict, original_question: str) -> Dict[str, Any]:
        """
        Process the TALN API response and structure it for Gemini consumption.
        """
        return {
            "original_question": original_question,
            "entities": self._extract_entities(taln_result),
            "relationships": self._extract_relationships(taln_result),
            "intent": self._extract_intent(taln_result),
            "keywords": self._extract_keywords(taln_result),
            "temporal_info": self._extract_temporal_info(taln_result),
            "location_info": self._extract_location_info(taln_result),
            "semantic_roles": self._extract_semantic_roles(taln_result),
            "confidence_scores": self._extract_confidence_scores(taln_result),
            "analysis_metadata": {
                "language": taln_result.get("language", "fr"),
                "processing_time": taln_result.get("processing_time"),
                "api_version": taln_result.get("api_version")
            }
        }
    
    def _extract_entities(self, taln_result: Dict) -> List[Dict]:
        """Extract entities from TALN response"""
        entities = []
        
        # Extract named entities
        for entity in taln_result.get("entities", []):
            entities.append({
                "text": entity.get("text"),
                "type": entity.get("type"),
                "category": entity.get("category"),
                "confidence": entity.get("confidence", 0.0),
                "start_pos": entity.get("start"),
                "end_pos": entity.get("end"),
                "ontology_class": self._map_to_ontology_class(entity.get("type"))
            })
        
        return entities
    
    def _extract_relationships(self, taln_result: Dict) -> List[Dict]:
        """Extract relationships between entities"""
        relationships = []
        
        for rel in taln_result.get("relationships", []):
            relationships.append({
                "subject": rel.get("subject"),
                "predicate": rel.get("predicate"),
                "object": rel.get("object"),
                "confidence": rel.get("confidence", 0.0),
                "relation_type": rel.get("relation_type")
            })
        
        return relationships
    
    def _extract_intent(self, taln_result: Dict) -> Dict:
        """Extract user intent from the question"""
        intent_data = taln_result.get("intent", {})
        return {
            "primary_intent": intent_data.get("primary_intent"),
            "secondary_intents": intent_data.get("secondary_intents", []),
            "action_type": intent_data.get("action_type"),
            "query_type": intent_data.get("query_type"),
            "confidence": intent_data.get("confidence", 0.0)
        }
    
    def _extract_keywords(self, taln_result: Dict) -> List[Dict]:
        """Extract important keywords"""
        keywords = []
        
        for kw in taln_result.get("keywords", []):
            keywords.append({
                "text": kw.get("text"),
                "importance": kw.get("importance", 0.0),
                "category": kw.get("category"),
                "semantic_type": kw.get("semantic_type")
            })
        
        return keywords
    
    def _extract_temporal_info(self, taln_result: Dict) -> Dict:
        """Extract temporal expressions and time-related information"""
        temporal_data = taln_result.get("temporal_expressions", {})
        return {
            "time_expressions": temporal_data.get("expressions", []),
            "relative_time": temporal_data.get("relative_time"),
            "absolute_time": temporal_data.get("absolute_time"),
            "time_period": temporal_data.get("time_period")
        }
    
    def _extract_location_info(self, taln_result: Dict) -> Dict:
        """Extract location-related information"""
        location_data = taln_result.get("location_expressions", {})
        return {
            "locations": location_data.get("locations", []),
            "geographical_entities": location_data.get("geographical_entities", []),
            "spatial_relations": location_data.get("spatial_relations", [])
        }
    
    def _extract_semantic_roles(self, taln_result: Dict) -> List[Dict]:
        """Extract semantic roles (agent, patient, instrument, etc.)"""
        return taln_result.get("semantic_roles", [])
    
    def _extract_confidence_scores(self, taln_result: Dict) -> Dict:
        """Extract confidence scores for different analysis components"""
        return {
            "overall_confidence": taln_result.get("confidence", 0.0),
            "entity_recognition": taln_result.get("entity_confidence", 0.0),
            "relationship_extraction": taln_result.get("relationship_confidence", 0.0),
            "intent_classification": taln_result.get("intent_confidence", 0.0)
        }
    
    def _map_to_ontology_class(self, entity_type: str) -> str:
        """Map TALN entity types to education domain ontology classes"""
        mapping = {
            "PERSON": "edu:Personne",  # People in education context
            "ORGANIZATION": "edu:Universite",  # Organizations in education are universities
            "LOCATION": "location_property",  # Location info stored as properties (ville, pays) on Universite
            "GPE": "location_property",  # Geopolitical entity (country/city) stored as properties
            "EVENT": "edu:Evaluation",  # Events in education context might be evaluations
            "FACILITY": "location_property",  # Facilities stored as location properties
            "WORK_OF_ART": "edu:RessourcePedagogique",  # Educational resources
            "LANGUAGE": "edu:Competence",  # Language as a competency
            "MONEY": "numeric",  # Financial information
            "PERCENT": "numeric",  # Percentage information (grades, etc.)
            "DATE": "temporal",
            "TIME": "temporal",
            "QUANTITY": "numeric",
            "ORDINAL": "numeric",
            "CARDINAL": "numeric"
        }
        
        return mapping.get(entity_type, "unknown")
    
    def _fallback_analysis(self, question: str) -> Dict[str, Any]:
        """
        Fallback analysis when TALN API is not available.
        Uses simple pattern matching and keyword extraction.
        """
        print(f"DEBUG: Starting fallback analysis for: '{question}'")
        question_lower = question.lower()
        
        # Simple entity extraction using keywords
        entities = []
        relationships = []
        keywords = []
        
        # Extract entity types based on keywords - EDUCATION DOMAIN ENTITIES
        entity_keywords = {
            # Education Domain Entities (edu: or ont: namespace)
            # Personnes (People)
            "edu:Personne": ["personne", "person", "personnes", "people", "individu", "individus", "individu", "individual"],
            "edu:Etudiant": ["étudiant", "etudiant", "student", "étudiants", "students", "élève", "eleve", "pupil", "apprenant", "learner"],
            "edu:Enseignant": ["enseignant", "teacher", "professeur", "professor", "prof", "instructeur", "instructor", "formateur", "trainer"],
            "edu:Professeur": ["professeur", "professor", "prof", "professeurs", "professors"],
            "edu:Assistant": ["assistant", "assistants", "aide", "helper"],
            "edu:Encadrant": ["encadrant", "supervisor", "encadrants", "supervisors", "tuteur", "tutor"],
            
            # Universites (Universities)
            "edu:Universite": ["université", "universite", "university", "universités", "universities", "établissement", "etablissement", "institution", "institut", "institute"],
            "edu:UniversitePublique": ["université publique", "public university", "université d'état", "public university"],
            "edu:UniversitePrivee": ["université privée", "private university", "université privée", "private university"],
            
            # Specialites (Specializations)
            "edu:Specialite": ["spécialité", "specialite", "specialization", "spécialisations", "specializations", "domaine", "field", "discipline", "branche", "branch", "majeure", "major"],
            "edu:SpecialiteInformatique": ["informatique", "computer science", "informatique", "computing", "IT", "technologie de l'information"],
            "edu:SpecialiteDataScience": ["data science", "science des données", "data science", "big data", "analytics"],
            "edu:SpecialiteIngenierie": ["ingénierie", "engineering", "génie", "engineer"],
            
            # Cours (Courses)
            "edu:Cours": ["cours", "course", "cours", "courses", "matière", "matiere", "subject", "module", "modules", "cours", "classe", "class"],
            "edu:CoursTheorique": ["cours théorique", "theoretical course", "cours théorique"],
            "edu:CoursPratique": ["cours pratique", "practical course", "cours pratique", "travaux pratiques", "TP"],
            
            # Competences (Competencies/Skills)
            "edu:Competence": ["compétence", "competence", "skill", "skills", "compétences", "competencies", "capacité", "capacity", "aptitude", "aptitude", "savoir-faire", "know-how"],
            
            # ProjetsAcademiques (Academic Projects)
            "edu:ProjetAcademique": ["projet académique", "academic project", "projet", "project", "projets", "projects", "travail", "work", "recherche", "research"],
            
            # RessourcesPedagogiques (Pedagogical Resources)
            "edu:RessourcePedagogique": ["ressource pédagogique", "pedagogical resource", "ressource", "resource", "ressources", "resources", "matériel pédagogique", "educational material", "support de cours", "course material"],
            
            # TechnologiesEducatives (Educational Technologies)
            "edu:TechnologieEducative": ["technologie éducative", "educational technology", "technologie", "technology", "technologies", "tech", "outil pédagogique", "educational tool", "plateforme", "platform"],
            
            # Evaluations (Evaluations/Assessments)
            "edu:Evaluation": ["évaluation", "evaluation", "assessment", "évaluations", "assessments", "examen", "exam", "examens", "exams", "test", "tests", "contrôle", "control", "contrôle continu", "continuous assessment"],
            
            # OrientationsAcademiques (Academic Orientations)
            "edu:OrientationAcademique": ["orientation académique", "academic orientation", "orientation", "orientation", "guidance", "conseil", "counseling", "parcours", "path", "voie", "way"],
            "edu:EntretienConseiller": ["entretien conseiller", "counselor interview", "entretien", "interview"]
        }
        
        # First pass: exact keyword matching
        for entity_type, keywords_list in entity_keywords.items():
            for keyword in keywords_list:
                if keyword in question_lower:
                    entities.append({
                        "text": keyword,
                        "type": entity_type.split(":")[1],
                        "category": "domain_entity",
                        "confidence": 0.8,
                        "ontology_class": entity_type
                    })
                    print(f"DEBUG: Found entity '{keyword}' -> {entity_type}")
        
        # Second pass: flexible pattern matching for common cases
        if not entities:  # Only if no exact matches found
            # Check for education domain entities first
            # Personnes
            personne_terms = ["personne", "person", "personnes", "people"]
            if any(term in question_lower for term in personne_terms):
                entities.append({
                    "text": "personne",
                    "type": "Personne",
                    "category": "domain_entity",
                    "confidence": 0.9,
                    "ontology_class": "edu:Personne"
                })
                print(f"DEBUG: Found entity 'personne' -> edu:Personne")
            
            # Etudiants
            etudiant_terms = ["étudiant", "etudiant", "student", "étudiants", "students"]
            if any(term in question_lower for term in etudiant_terms):
                entities.append({
                    "text": "étudiant",
                    "type": "Etudiant",
                    "category": "domain_entity",
                    "confidence": 0.9,
                    "ontology_class": "edu:Etudiant"
                })
                print(f"DEBUG: Found entity 'étudiant' -> edu:Etudiant")
            
            # Enseignants
            enseignant_terms = ["enseignant", "teacher", "professeur", "professor", "prof"]
            if any(term in question_lower for term in enseignant_terms):
                entities.append({
                    "text": "enseignant",
                    "type": "Enseignant",
                    "category": "domain_entity",
                    "confidence": 0.9,
                    "ontology_class": "edu:Enseignant"
                })
                print(f"DEBUG: Found entity 'enseignant' -> edu:Enseignant")
            
            # Universites
            universite_terms = ["université", "universite", "university", "universités", "universities"]
            if any(term in question_lower for term in universite_terms):
                entities.append({
                    "text": "université",
                    "type": "Universite",
                    "category": "domain_entity",
                    "confidence": 0.9,
                    "ontology_class": "edu:Universite"
                })
                print(f"DEBUG: Found entity 'université' -> edu:Universite")
            
            # Specialites
            specialite_terms = ["spécialité", "specialite", "specialization", "spécialisations", "specializations"]
            if any(term in question_lower for term in specialite_terms):
                entities.append({
                    "text": "spécialité",
                    "type": "Specialite",
                    "category": "domain_entity",
                    "confidence": 0.9,
                    "ontology_class": "edu:Specialite"
                })
                print(f"DEBUG: Found entity 'spécialité' -> edu:Specialite")
            
            # Cours
            cours_terms = ["cours", "course", "cours", "courses", "matière", "matiere", "subject", "module"]
            if any(term in question_lower for term in cours_terms):
                entities.append({
                    "text": "cours",
                    "type": "Cours",
                    "category": "domain_entity",
                    "confidence": 0.9,
                    "ontology_class": "edu:Cours"
                })
                print(f"DEBUG: Found entity 'cours' -> edu:Cours")
            
            # Competences
            competence_terms = ["compétence", "competence", "skill", "skills", "compétences", "competencies"]
            if any(term in question_lower for term in competence_terms):
                entities.append({
                    "text": "compétence",
                    "type": "Competence",
                    "category": "domain_entity",
                    "confidence": 0.9,
                    "ontology_class": "edu:Competence"
                })
                print(f"DEBUG: Found entity 'compétence' -> edu:Competence")
            
            # ProjetsAcademiques
            projet_terms = ["projet", "project", "projets", "projects", "travail", "work"]
            if any(term in question_lower for term in projet_terms):
                entities.append({
                    "text": "projet",
                    "type": "ProjetAcademique",
                    "category": "domain_entity",
                    "confidence": 0.9,
                    "ontology_class": "edu:ProjetAcademique"
                })
                print(f"DEBUG: Found entity 'projet' -> edu:ProjetAcademique")
            
            # RessourcesPedagogiques
            ressource_terms = ["ressource", "resource", "ressources", "resources", "matériel", "material"]
            if any(term in question_lower for term in ressource_terms):
                entities.append({
                    "text": "ressource",
                    "type": "RessourcePedagogique",
                    "category": "domain_entity",
                    "confidence": 0.9,
                    "ontology_class": "edu:RessourcePedagogique"
                })
                print(f"DEBUG: Found entity 'ressource' -> edu:RessourcePedagogique")
            
            # TechnologiesEducatives
            technologie_terms = ["technologie", "technology", "technologies", "tech", "outil", "tool"]
            if any(term in question_lower for term in technologie_terms):
                entities.append({
                    "text": "technologie",
                    "type": "TechnologieEducative",
                    "category": "domain_entity",
                    "confidence": 0.9,
                    "ontology_class": "edu:TechnologieEducative"
                })
                print(f"DEBUG: Found entity 'technologie' -> edu:TechnologieEducative")
            
            # Evaluations
            evaluation_terms = ["évaluation", "evaluation", "assessment", "examen", "exam", "test", "tests"]
            if any(term in question_lower for term in evaluation_terms):
                entities.append({
                    "text": "évaluation",
                    "type": "Evaluation",
                    "category": "domain_entity",
                    "confidence": 0.9,
                    "ontology_class": "edu:Evaluation"
                })
                print(f"DEBUG: Found entity 'évaluation' -> edu:Evaluation")
            
            # OrientationsAcademiques
            orientation_terms = ["orientation", "orientation", "guidance", "conseil", "counseling"]
            if any(term in question_lower for term in orientation_terms):
                entities.append({
                    "text": "orientation",
                    "type": "OrientationAcademique",
                    "category": "domain_entity",
                    "confidence": 0.9,
                    "ontology_class": "edu:OrientationAcademique"
                })
                print(f"DEBUG: Found entity 'orientation' -> edu:OrientationAcademique")
        
        print(f"DEBUG: Total entities found: {len(entities)}")
        
        # Extract temporal information
        temporal_keywords = {
            "future": ["à venir", "futur", "future", "upcoming", "prochain", "demain", "tomorrow"],
            "past": ["passé", "past", "ancien", "previous", "terminé", "hier", "yesterday"],
            "present": ["aujourd'hui", "today", "ce jour", "actuel", "current"],
            "week": ["semaine", "week", "weekend", "week-end"],
            "month": ["mois", "month"],
            "year": ["année", "year", "annuel", "annual"]
        }
        
        temporal_info = {"time_expressions": [], "relative_time": None}
        for time_type, keywords_list in temporal_keywords.items():
            for keyword in keywords_list:
                if keyword in question_lower:
                    temporal_info["time_expressions"].append(keyword)
                    temporal_info["relative_time"] = time_type
                    break
        
        # Extract location information
        location_keywords = ["paris", "london", "new york", "boston", "chicago", "san francisco", "tunis"]
        location_info = {"locations": []}
        for location in location_keywords:
            if location in question_lower:
                location_info["locations"].append(location)
        
        # Extract intent
        intent_patterns = {
            "list": ["quelles", "quels", "montre", "liste", "tous", "all", "every"],
            "count": ["combien", "nombre", "total", "count", "how many"],
            "filter": ["par", "par type", "par catégorie", "par ville", "par date"],
            "search": ["recherche", "trouve", "find", "search", "cherche"],
            "details": ["détails", "informations", "details", "information", "qui", "où", "quand"]
        }
        
        intent = {"primary_intent": "unknown", "query_type": "general"}
        for intent_type, keywords_list in intent_patterns.items():
            for keyword in keywords_list:
                if keyword in question_lower:
                    intent["primary_intent"] = intent_type
                    intent["query_type"] = intent_type
                    break
        
        # Extract important keywords
        important_words = question.split()
        for word in important_words:
            if len(word) > 3 and word.lower() not in ["les", "des", "une", "pour", "avec", "dans", "sur"]:
                keywords.append({
                    "text": word.lower(),
                    "importance": 0.5,
                    "category": "general",
                    "semantic_type": "keyword"
                })
        
        return {
            "original_question": question,
            "entities": entities,
            "relationships": relationships,
            "intent": intent,
            "keywords": keywords,
            "temporal_info": temporal_info,
            "location_info": location_info,
            "semantic_roles": [],
            "confidence_scores": {
                "overall_confidence": 0.6,
                "entity_recognition": 0.7,
                "relationship_extraction": 0.3,
                "intent_classification": 0.8
            },
            "analysis_metadata": {
                "language": "fr",
                "processing_time": 0.1,
                "api_version": "fallback",
                "method": "pattern_matching"
            }
        }
    
    def get_structured_context(self, analysis_result: Dict) -> str:
        """
        Convert the analysis result into a structured context string for Gemini.
        This provides Gemini with clear, structured information about the question.
        """
        context_parts = []
        
        # Original question
        context_parts.append(f"QUESTION: {analysis_result['original_question']}")
        
        # Entities found
        if analysis_result['entities']:
            entities_text = []
            for entity in analysis_result['entities']:
                entities_text.append(f"- {entity['text']} ({entity['ontology_class']})")
            context_parts.append(f"ENTITIES: {', '.join(entities_text)}")
        
        # Intent
        intent = analysis_result['intent']
        context_parts.append(f"INTENT: {intent['primary_intent']} - {intent['query_type']}")
        
        # Temporal information
        temporal = analysis_result['temporal_info']
        if temporal['relative_time']:
            context_parts.append(f"TIME: {temporal['relative_time']}")
        
        # Location information
        location = analysis_result['location_info']
        if location['locations']:
            context_parts.append(f"LOCATIONS: {', '.join(location['locations'])}")
        
        # Keywords
        if analysis_result['keywords']:
            keyword_texts = [kw['text'] for kw in analysis_result['keywords'][:10]]  # Limit to 10
            context_parts.append(f"KEYWORDS: {', '.join(keyword_texts)}")
        
        # Relationships
        if analysis_result['relationships']:
            rel_texts = []
            for rel in analysis_result['relationships']:
                rel_texts.append(f"{rel['subject']} -> {rel['predicate']} -> {rel['object']}")
            context_parts.append(f"RELATIONSHIPS: {'; '.join(rel_texts)}")
        
        return "\n".join(context_parts)


class GeminiTALNService(TALNService):
    """
    TALN Service that uses Gemini API for NLP analysis instead of external TALN API.
    This uses Gemini to extract entities, relationships, and semantic information.
    """
    
    def __init__(self):
        super().__init__()
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        
        if not self.gemini_api_key:
            print("WARNING: GEMINI_API_KEY not found in environment variables")
            print("Falling back to pattern-based entity extraction...")
            self.use_fallback = True
            self.model = None
        elif not GEMINI_AVAILABLE:
            print("WARNING: google-generativeai package not installed")
            print("Install with: pip install google-generativeai")
            print("Falling back to pattern-based entity extraction...")
            self.use_fallback = True
            self.model = None
        else:
            try:
                genai.configure(api_key=self.gemini_api_key)
                # Use a fast model for analysis
                try:
                    self.model = genai.GenerativeModel('models/gemini-2.0-flash-exp')
                except:
                    try:
                        self.model = genai.GenerativeModel('models/gemini-flash-latest')
                    except:
                        self.model = genai.GenerativeModel('models/gemini-pro-latest')
                self.use_fallback = False
                print("SUCCESS: Gemini TALN Service initialized successfully")
            except Exception as e:
                print(f"WARNING: Gemini initialization failed: {e}")
                print("Falling back to pattern-based entity extraction...")
                self.use_fallback = True
                self.model = None
    
    def analyze_question(self, question: str) -> Dict[str, Any]:
        """
        Analyze a natural language question using Gemini API.
        Extracts entities, relationships, intent, and semantic information.
        
        Args:
            question (str): The natural language question
            
        Returns:
            Dict containing extracted entities, relationships, intent, and metadata
        """
        print(f"DEBUG: Starting Gemini NLP analysis for question: '{question}'")
        
        if self.use_fallback or not self.model:
            print(f"DEBUG: Using fallback analysis (Gemini not configured)")
            result = self._fallback_analysis(question)
            print(f"DEBUG: Fallback analysis completed. Entities: {len(result.get('entities', []))}")
            return result
        
        try:
            print(f"DEBUG: Attempting Gemini API call for NLP analysis...")
            
            # Build prompt for Gemini to extract structured information
            prompt = self._build_gemini_analysis_prompt(question)
            
            # Call Gemini for analysis
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.2,  # Lower temperature for more consistent extraction
                    top_p=0.8,
                    top_k=40,
                    max_output_tokens=1500,
                )
            )
            
            print(f"DEBUG: Gemini analysis response received")
            
            # Parse Gemini response into structured format
            analysis_result = self._parse_gemini_analysis_response(response.text, question)
            
            print(f"DEBUG: Gemini analysis completed. Entities: {len(analysis_result.get('entities', []))}")
            return analysis_result
            
        except Exception as e:
            print(f"ERROR: Gemini NLP analysis failed: {e}")
            print(f"DEBUG: Falling back to local analysis")
            return self._fallback_analysis(question)
    
    def _build_gemini_analysis_prompt(self, question: str) -> str:
        """Build prompt for Gemini to extract structured NLP information"""
        return f"""You are an expert NLP analyst for an educational platform. Analyze the following French question and extract structured information in JSON format.

Analyze the question and extract:
1. Entities (Events, Locations, Users, Campaigns, Volunteers, Assignments, Certifications, Reservations, etc.)
2. Intent (what the user wants: list, count, filter, search, details)
3. Temporal information (future, past, present, specific dates)
4. Location information (cities, places mentioned)
5. Keywords and important terms
6. Relationships between entities

Return ONLY a valid JSON object with this exact structure:
{{
  "entities": [
    {{
      "text": "entity text from question",
      "type": "Personne|Etudiant|Enseignant|Universite|Specialite|Cours|Competence|ProjetAcademique|RessourcePedagogique|TechnologieEducative|Evaluation|OrientationAcademique",
      "category": "domain_entity",
      "confidence": 0.9,
      "ontology_class": "edu:Personne|edu:Etudiant|edu:Enseignant|edu:Universite|edu:Specialite|edu:Cours|edu:Competence|edu:ProjetAcademique|edu:RessourcePedagogique|edu:TechnologieEducative|edu:Evaluation|edu:OrientationAcademique"
    }}
  ],
  "intent": {{
    "primary_intent": "list|count|filter|search|details",
    "query_type": "list|count|filter|search|details"
  }},
  "temporal_info": {{
    "relative_time": "future|past|present|null",
    "time_expressions": ["à venir", "futur", etc.]
  }},
  "location_info": {{
    "locations": ["paris", "tunis", etc.]
  }},
  "keywords": [
    {{
      "text": "keyword",
      "importance": 0.8,
      "category": "content_word"
    }}
  ],
  "relationships": []
}}

ONTOLOGY CONTEXT (Education Domain):
- edu:Personne, edu:Etudiant, edu:Enseignant, edu:Professeur, edu:Assistant, edu:Encadrant
- edu:EtudiantLicence, edu:EtudiantMaster, edu:EtudiantDoctorat
- edu:Universite, edu:UniversitePublique, edu:UniversitePrivee
- edu:Specialite, edu:SpecialiteInformatique, edu:SpecialiteDataScience, edu:SpecialiteIngenierie, etc.
- edu:Cours, edu:CoursTheorique, edu:CoursPratique
- edu:Competence
- edu:ProjetAcademique
- edu:RessourcePedagogique
- edu:TechnologieEducative
- edu:Evaluation
- edu:OrientationAcademique, edu:EntretienConseiller

QUESTION: "{question}"

Return ONLY the JSON object, no explanations:"""
    
    def _parse_gemini_analysis_response(self, response_text: str, original_question: str) -> Dict[str, Any]:
        """Parse Gemini's JSON response into structured analysis format"""
        try:
            # Try to extract JSON from response
            # Remove markdown code blocks if present
            text = response_text.strip()
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            
            # Try to parse JSON
            try:
                analysis_data = json.loads(text)
            except json.JSONDecodeError:
                # Try to find JSON object in text
                import re
                json_match = re.search(r'\{.*\}', text, re.DOTALL)
                if json_match:
                    analysis_data = json.loads(json_match.group())
                else:
                    raise ValueError("No JSON found in response")
            
            # Structure the response to match expected format
            result = {
                "original_question": original_question,
                "entities": [],
                "relationships": [],
                "intent": {
                    "primary_intent": analysis_data.get("intent", {}).get("primary_intent", "unknown"),
                    "query_type": analysis_data.get("intent", {}).get("query_type", "general"),
                    "action_type": None,
                    "confidence": 0.8
                },
                "keywords": [],
                "temporal_info": {
                    "time_expressions": analysis_data.get("temporal_info", {}).get("time_expressions", []),
                    "relative_time": analysis_data.get("temporal_info", {}).get("relative_time"),
                    "absolute_time": None,
                    "time_period": None
                },
                "location_info": {
                    "locations": analysis_data.get("location_info", {}).get("locations", []),
                    "geographical_entities": [],
                    "spatial_relations": []
                },
                "semantic_roles": [],
                "confidence_scores": {
                    "overall_confidence": 0.85,
                    "entity_recognition": 0.9,
                    "relationship_extraction": 0.7,
                    "intent_classification": 0.85
                },
                "analysis_metadata": {
                    "language": "fr",
                    "processing_time": 0.5,
                    "api_version": "gemini_nlp",
                    "method": "gemini_analysis"
                }
            }
            
            # Process entities
            for entity in analysis_data.get("entities", []):
                result["entities"].append({
                    "text": entity.get("text", ""),
                    "type": entity.get("type", "unknown"),
                    "category": entity.get("category", "domain_entity"),
                    "confidence": entity.get("confidence", 0.8),
                    "start_pos": None,
                    "end_pos": None,
                    "ontology_class": entity.get("ontology_class", "unknown")
                })
            
            # Process keywords
            for keyword in analysis_data.get("keywords", []):
                result["keywords"].append({
                    "text": keyword.get("text", ""),
                    "importance": keyword.get("importance", 0.7),
                    "category": keyword.get("category", "general"),
                    "semantic_type": keyword.get("semantic_type", "keyword")
                })
            
            # Process relationships
            for rel in analysis_data.get("relationships", []):
                result["relationships"].append({
                    "subject": rel.get("subject", ""),
                    "predicate": rel.get("predicate", ""),
                    "object": rel.get("object", ""),
                    "confidence": rel.get("confidence", 0.7),
                    "relation_type": rel.get("relation_type", "unknown")
                })
            
            return result
            
        except Exception as e:
            print(f"ERROR: Failed to parse Gemini analysis response: {e}")
            print(f"DEBUG: Response text: {response_text[:500]}")
            # Fallback to pattern matching
            return self._fallback_analysis(original_question)
