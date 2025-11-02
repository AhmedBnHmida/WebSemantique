import os
import requests
import json
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

load_dotenv()

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
                "domain": "ecological_events",  # Domain-specific analysis
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
        """Map TALN entity types to our ontology classes"""
        mapping = {
            "PERSON": "webprotege:User",
            "ORGANIZATION": "webprotege:User",  # Organizations can be users
            "LOCATION": "webprotege:Location",
            "GPE": "webprotege:Location",  # Geopolitical entity
            "EVENT": "webprotege:Event",
            "FACILITY": "webprotege:Location",
            "WORK_OF_ART": "webprotege:Event",  # Events can be works of art
            "LAW": "webprotege:Campaign",  # Laws can be campaigns
            "LANGUAGE": "webprotege:Resource",  # Language resources
            "MONEY": "webprotege:Resource",  # Financial resources
            "PERCENT": "webprotege:Resource",  # Percentage resources
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
        
        # Extract entity types based on keywords - CORRECTED FROM RDF ANALYSIS
        entity_keywords = {
            # Events (eco: namespace)
            "eco:Event": ["événement", "event", "évènement", "evenement", "événements", "events", "manifestation", "manifestations"],
            "eco:EducationalEvent": ["atelier", "ateliers", "workshop", "workshops", "formation", "formations", "training", "trainings", "séminaire", "séminaires", "seminar", "seminars", "conférence", "conférences", "conference", "conferences", "cours", "course", "courses", "éducation", "education"],
            "eco:EntertainmentEvent": ["festival", "festivals", "fête", "fêtes", "party", "parties", "concert", "concerts", "spectacle", "spectacles", "show", "shows", "divertissement", "entertainment", "loisir", "loisirs", "leisure"],
            "eco:CompetitiveEvent": ["compétition", "compétitions", "competition", "competitions", "challenge", "challenges", "défi", "défis", "contest", "contests", "tournoi", "tournois", "tournament", "tournaments", "marathon", "marathons"],
            "eco:SocializationEvent": ["socialisation", "socialization", "réseautage", "networking", "rencontre", "meeting", "social"],
            
            # Campaigns (eco: namespace)
            "eco:Campaign": ["campagne", "campaign", "initiative", "initiatives"],
            "eco:AwarenessCampaign": ["campagne", "campaign", "sensibilisation", "awareness", "information", "éducation"],
            "eco:CleanupCampaign": ["nettoyage", "cleanup", "ramassage", "collecte", "déchets", "waste"],
            "eco:FundingCampaign": ["financement", "funding", "don", "donation", "collecte", "fundraising"],
            
            # Locations (eco: namespace)
            "eco:Location": ["location", "lieu", "endroit", "salle", "place", "venue", "local", "site", "adresse", "address"],
            "eco:Indoor": ["intérieur", "indoor", "salle", "hall", "auditorium", "salle de conférence"],
            "eco:Outdoor": ["extérieur", "outdoor", "parc", "park", "jardin", "garden", "plage", "beach"],
            "eco:VirtualPlatform": ["virtuel", "virtual", "en ligne", "online", "webinaire", "webinar"],
            
            # Volunteers (webprotege: namespace)
            "webprotege:RCXXzqv27uFuX5nYU81XUvw": ["volontaire", "volunteer", "bénévole", "benevole", "volontaires", "volunteers"],
            
            # Assignments (webprotege: namespace)
            "webprotege:Rj2A7xNWLfpNcbE4HJMKqN": ["assignement", "assignment", "assignation", "affectation", "assignements", "assignments"],
            
            # Resources (eco: namespace)
            "eco:Resource": ["ressource", "resource", "équipement", "equipment", "matériel", "material"],
            "eco:DigitalResource": ["ressource numérique", "digital resource", "logiciel", "software", "application", "app"],
            "eco:EquipmentResource": ["équipement", "equipment", "outil", "tool", "matériel", "material"],
            "eco:HumanResource": ["ressource humaine", "human resource", "personnel", "staff", "équipe", "team"],
            
            # Reservations (eco: namespace)
            "eco:Reservation": ["réservation", "reservation", "réserver", "booking", "réservations", "reservations"],
            
            # Blogs (eco: namespace)
            "eco:Blog": ["blog", "article", "publication", "post", "blogs", "articles"],
            
            # Certifications (eco: namespace)
            "eco:Certification": ["certification", "certificat", "diplôme", "diploma", "récompense", "reward", "badge"]
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
            # Check for event-related terms
            event_terms = ["événement", "event", "évènement", "evenement", "événements", "events"]
            if any(term in question_lower for term in event_terms):
                entities.append({
                    "text": "événement",
                    "type": "Event",
                    "category": "domain_entity",
                    "confidence": 0.9,
                    "ontology_class": "eco:Event"
                })
                print(f"DEBUG: Found entity 'événement' -> eco:Event")
            
            # Check for volunteer-related terms
            volunteer_terms = ["volontaire", "volunteer", "bénévole", "benevole"]
            if any(term in question_lower for term in volunteer_terms):
                entities.append({
                    "text": "volontaire",
                    "type": "Volunteer",
                    "category": "domain_entity",
                    "confidence": 0.9,
                    "ontology_class": "webprotege:RCXXzqv27uFuX5nYU81XUvw"
                })
                print(f"DEBUG: Found entity 'volontaire' -> webprotege:RCXXzqv27uFuX5nYU81XUvw")
            
            # Check for assignment-related terms
            assignment_terms = ["assignement", "assignment", "assignation", "affectation"]
            if any(term in question_lower for term in assignment_terms):
                entities.append({
                    "text": "assignement",
                    "type": "Assignment",
                    "category": "domain_entity",
                    "confidence": 0.9,
                    "ontology_class": "webprotege:Rj2A7xNWLfpNcbE4HJMKqN"
                })
                print(f"DEBUG: Found entity 'assignement' -> webprotege:Rj2A7xNWLfpNcbE4HJMKqN")
            
            # Check for campaign-related terms
            campaign_terms = ["campagne", "campaign"]
            if any(term in question_lower for term in campaign_terms):
                entities.append({
                    "text": "campagne",
                    "type": "Campaign",
                    "category": "domain_entity",
                    "confidence": 0.9,
                    "ontology_class": "eco:Campaign"
                })
                print(f"DEBUG: Found entity 'campagne' -> eco:Campaign")
            
            # Check for certification-related terms
            cert_terms = ["certification", "certificat", "diplôme", "récompense", "badge"]
            if any(term in question_lower for term in cert_terms):
                entities.append({
                    "text": "certification",
                    "type": "Certification",
                    "category": "domain_entity",
                    "confidence": 0.9,
                    "ontology_class": "eco:Certification"
                })
                print(f"DEBUG: Found entity 'certification' -> eco:Certification")
        
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
