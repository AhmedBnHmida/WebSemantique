import os
import google.generativeai as genai
from dotenv import load_dotenv
import re
from typing import Dict, Any

load_dotenv()

class GeminiSPARQLTransformer:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=self.api_key)
        

        try:
            self.model = genai.GenerativeModel('models/gemini-2.0-flash')
            print("Gemini initialized successfully with models/gemini-2.0-flash")
        except Exception as e:
            print(f"Error with models/gemini-2.0-flash: {e}")
            # Fallback to other models
            try:
                self.model = genai.GenerativeModel('models/gemini-flash-latest')
                print("Gemini initialized successfully with models/gemini-flash-latest")
            except Exception as e2:
                print(f"Error with models/gemini-flash-latest: {e2}")
                try:
                    self.model = genai.GenerativeModel('models/gemini-pro-latest')
                    print("Gemini initialized successfully with models/gemini-pro-latest")
                except Exception as e3:
                    print(f"All model attempts failed: {e3}")
                    raise
        
    def transform_question_to_sparql(self, question: str) -> str:
        """Transform natural language question to SPARQL using Gemini ONLY"""
        try:
            prompt = self._build_prompt(question)
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,
                    top_p=0.8,
                    top_k=40,
                    max_output_tokens=1000,
                )
            )
            
            sparql_query = self._extract_sparql_query(response.text)
            return self._validate_and_clean_query(sparql_query)
            
        except Exception as e:
            print(f"Gemini API error: {e}")
            return self._get_fallback_query(question)
    
    def transform_taln_analysis_to_sparql(self, taln_analysis: Dict[str, Any]) -> str:
        """
        Transform TALN analysis result to SPARQL using Gemini.
        This is the new method that works with TALN extracted data.
        
        Args:
            taln_analysis: Dictionary containing TALN analysis results
            
        Returns:
            Generated SPARQL query string
        """
        try:
            print(f"DEBUG: Starting Gemini SPARQL generation")
            print(f"DEBUG: TALN Analysis keys: {list(taln_analysis.keys())}")
            print(f"DEBUG: Entities detected: {len(taln_analysis.get('entities', []))}")
            print(f"DEBUG: Intent: {taln_analysis.get('intent', {}).get('primary_intent', 'unknown')}")
            
            prompt = self._build_taln_prompt(taln_analysis)
            print(f"DEBUG: Prompt length: {len(prompt)} characters")
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,
                    top_p=0.8,
                    top_k=40,
                    max_output_tokens=1200,
                )
            )
            
            print(f"DEBUG: Gemini response received: {len(response.text)} characters")
            sparql_query = self._extract_sparql_query(response.text)
            print(f"DEBUG: Extracted SPARQL query: {len(sparql_query)} characters")
            print(f"DEBUG: Query preview: {sparql_query[:200]}...")
            
            validated_query = self._validate_and_clean_query(sparql_query)
            print(f"DEBUG: Final validated query: {len(validated_query)} characters")
            
            return validated_query
            
        except Exception as e:
            print(f"ERROR: Gemini API error with TALN analysis: {e}")
            print(f"DEBUG: Falling back to original question method")
            # Fallback to original question if available
            original_question = taln_analysis.get('original_question', '')
            if original_question:
                return self.transform_question_to_sparql(original_question)
            return self._get_fallback_query("events")
    
    def _build_prompt(self, question: str) -> str:
        """Build the prompt for Gemini - FOCUS ON DYNAMIC GENERATION"""
        return f"""You are a SPARQL query generator for an ecological events platform. Convert the natural language question to a valid SPARQL query.

ONTOLOGY CONTEXT:
Prefix: eco: <http://www.semanticweb.org/eco-ontology#>

MAIN CLASSES:
- Event, Location, User, Campaign, Resource, Reservation, Certification, Sponsor, Donation

EVENT PROPERTIES:
- eventTitle, eventDate, eventDescription, maxParticipants, isLocatedAt, isOrganizedBy, eventStatus, duration, eventImages, eventType

LOCATION PROPERTIES:
- locationName, address, city, country, capacity, price, reserved, inRepair, locationDescription, latitude, longitude, locationImages, locationType

USER PROPERTIES:
- firstName, lastName, email, role, phone, registrationDate

RESERVATION PROPERTIES:
- belongsToUser, confirmedBy, numberOfTickets, reservationStatus, reservationDate

CERTIFICATION PROPERTIES:
- awardedTo, issuedBy, certificateCode, pointsEarned, certificationType

SPONSOR PROPERTIES:
- companyName, industry, contactEmail, phoneNumber, website

DONATION PROPERTIES:
- donationAmount (or amount for FinancialDonation), currency, dateDonated, description, estimatedValue, hoursDonated, fundsEvent

IMPORTANT QUERY PATTERNS:
- For event type questions: Use FILTER with CONTAINS/REGEX on eventTitle, eventDescription, or eventType
- For location type questions: Use FILTER with CONTAINS/REGEX on locationName, locationType, or address
- For date filters: Use FILTER(?date >= NOW()) for future, FILTER(?date < NOW()) for past
- For city filters: FILTER(CONTAINS(LCASE(STR(?city)), "cityname"))
- For text searches: Use FILTER(CONTAINS(LCASE(STR(?field)), "searchterm"))
- For available locations: FILTER(!BOUND(?reserved) || ?reserved = false) && FILTER(!BOUND(?inRepair) || ?inRepair = false)

CRITICAL RULES:
1. Always use PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
2. Use OPTIONAL for properties that might not exist
3. Use ORDER BY when appropriate for sorting
4. Use LIMIT 20-50 to prevent too many results
5. Make location properties OPTIONAL (locationName, city, etc.)
6. Return ONLY the SPARQL query, no explanations
7. Be creative and adapt to the specific question

QUESTION: "{question}"

SPARQL QUERY:"""
    
    def _build_taln_prompt(self, taln_analysis: Dict[str, Any]) -> str:
        """
        Build the prompt for Gemini using TALN analysis results.
        This provides much more structured and accurate information to Gemini.
        """
        original_question = taln_analysis.get('original_question', '')
        entities = taln_analysis.get('entities', [])
        intent = taln_analysis.get('intent', {})
        temporal_info = taln_analysis.get('temporal_info', {})
        location_info = taln_analysis.get('location_info', {})
        keywords = taln_analysis.get('keywords', [])
        relationships = taln_analysis.get('relationships', [])
        
        # Build entity context
        entity_context = ""
        if entities:
            entity_list = []
            for entity in entities:
                entity_list.append(f"- {entity['text']} ({entity['ontology_class']})")
            entity_context = f"ENTITIES DETECTED:\n" + "\n".join(entity_list)
        
        # Build intent context
        intent_context = ""
        if intent:
            primary_intent = intent.get('primary_intent', 'unknown')
            query_type = intent.get('query_type', 'general')
            intent_context = f"USER INTENT: {primary_intent} (Query Type: {query_type})"
        
        # Build temporal context
        temporal_context = ""
        if temporal_info.get('relative_time'):
            temporal_context = f"TEMPORAL INFO: {temporal_info['relative_time']}"
            if temporal_info.get('time_expressions'):
                temporal_context += f" (Expressions: {', '.join(temporal_info['time_expressions'])})"
        
        # Build location context
        location_context = ""
        if location_info.get('locations'):
            locations = location_info['locations']
            location_context = f"LOCATIONS MENTIONED: {', '.join(locations)}"
        
        # Build keyword context
        keyword_context = ""
        if keywords:
            keyword_texts = [kw['text'] for kw in keywords[:10]]  # Limit to 10 most important
            keyword_context = f"IMPORTANT KEYWORDS: {', '.join(keyword_texts)}"
        
        # Build relationship context
        relationship_context = ""
        if relationships:
            rel_texts = []
            for rel in relationships:
                rel_texts.append(f"{rel['subject']} -> {rel['predicate']} -> {rel['object']}")
            relationship_context = f"RELATIONSHIPS: {'; '.join(rel_texts)}"
        
        return f"""You are an expert SPARQL query generator for an ecological events platform. Generate a precise SPARQL query based on the structured analysis provided below.

ONTOLOGY CONTEXT:
PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
PREFIX webprotege: <http://webprotege.stanford.edu/>

MAIN CLASSES AND THEIR PROPERTIES:
- Event (eco:Event): eventTitle, eventDate, eventDescription, maxParticipants, isLocatedAt, isOrganizedBy, eventStatus, duration, eventImages, eventType
- EducationalEvent (eco:EducationalEvent): eventTitle, eventDate, eventDescription, maxParticipants, isLocatedAt, isOrganizedBy, eventStatus, duration, eventImages, eventType
- EntertainmentEvent (eco:EntertainmentEvent): eventTitle, eventDate, eventDescription, maxParticipants, isLocatedAt, isOrganizedBy, eventStatus, duration, eventImages, eventType
- CompetitiveEvent (eco:CompetitiveEvent): eventTitle, eventDate, eventDescription, maxParticipants, isLocatedAt, isOrganizedBy, eventStatus, duration, eventImages, eventType
- SocializationEvent (eco:SocializationEvent): eventTitle, eventDate, eventDescription, maxParticipants, isLocatedAt, isOrganizedBy, eventStatus, duration, eventImages, eventType
- Location (eco:Location): locationName, address, city, country, capacity, price, reserved, inRepair, locationDescription, latitude, longitude, locationImages, locationType
- Indoor (eco:Indoor): locationName, address, city, country, capacity, price, reserved, inRepair, locationDescription, latitude, longitude, locationImages, locationType
- Outdoor (eco:Outdoor): locationName, address, city, country, capacity, price, reserved, inRepair, locationDescription, latitude, longitude, locationImages, locationType
- VirtualPlatform (eco:VirtualPlatform): locationName, address, city, country, capacity, price, reserved, inRepair, locationDescription, latitude, longitude, locationImages, locationType
- Campaign (eco:Campaign): campaignName, campaignDescription, campaignStatus, startDate, endDate, goal, targetAmount, fundsRaised
- AwarenessCampaign (eco:AwarenessCampaign): campaignName, campaignDescription, campaignStatus, startDate, endDate, goal
- CleanupCampaign (eco:CleanupCampaign): campaignName, campaignDescription, campaignStatus, startDate, endDate, goal
- EventCampaign (eco:EventCampaign): campaignName, campaignDescription, campaignStatus, startDate, endDate, goal, targetParticipants
- FundingCampaign (eco:FundingCampaign): campaignName, campaignDescription, campaignStatus, startDate, endDate, goal, targetAmount, fundsRaised
- Resource (eco:Resource): resourceName, resourceDescription, resourceCategory, quantityAvailable, unitCost, resourceType
- DigitalResource (eco:DigitalResource): resourceName, resourceDescription, resourceCategory, quantityAvailable, unitCost, resourceType
- EquipmentResource (eco:EquipmentResource): resourceName, resourceDescription, resourceCategory, quantityAvailable, unitCost, equipmentType
- FinancialResource (eco:FinancialResource): resourceName, resourceDescription, resourceCategory, quantityAvailable, unitCost, currency
- HumanResource (eco:HumanResource): resourceName, resourceDescription, resourceCategory, quantityAvailable, unitCost, skillLevel
- MaterialResource (eco:MaterialResource): resourceName, resourceDescription, resourceCategory, quantityAvailable, unitCost, materialType
- Volunteer (webprotege:RCXXzqv27uFuX5nYU81XUvw): phone (webprotege:R8BxRbqkCT2nIQCr5UoVlXD), healthIssues (webprotege:R9F95BAS8WtbTv8ZGBaPe42), motivation (webprotege:R9PW79FzwQKWuQYdTdYlHzN), experience (webprotege:R9tdW5crNU837y5TemwdNfR), skills (webprotege:RBqpxvMVBnwM1Wb6OhzTpHf)
- Assignment (webprotege:Rj2A7xNWLfpNcbE4HJMKqN): startDate (webprotege:RD3Wor03BEPInfzUaMNVPC7), status (webprotege:RDT3XEARggTy1BIBKDXXrmx), rating (webprotege:RRatingAssignment)
- Certification (eco:Certification): certificateCode, pointsEarned, certificationType, awardedTo, issuedBy
- Reservation (eco:Reservation): seatNumber, status, belongsToUser, confirmedBy, numberOfTickets, reservationDate
- Blog (eco:Blog): blogTitle, blogContent, category, publicationDate
- Sponsor (eco:Sponsor): companyName, industry, contactEmail, phoneNumber, website, hasSponsorshipLevel, makesDonation
- SponsorshipLevel (eco:SponsorshipLevel): levelName, minAmount, benefits
- BronzeSponsor (eco:BronzeSponsor): levelName, minAmount, benefits
- SilverSponsor (eco:SilverSponsor): levelName, minAmount, benefits
- GoldSponsor (eco:GoldSponsor): levelName, minAmount, benefits
- PlatinumSponsor (eco:PlatinumSponsor): levelName, minAmount, benefits
- Donation (eco:Donation): dateDonated, note, donationType, fundsEvent
- FinancialDonation (eco:FinancialDonation): dateDonated, note, donationType, amount, currency, paymentMethod
- MaterialDonation (eco:MaterialDonation): dateDonated, note, donationType, itemDescription, estimatedValue, quantity
- ServiceDonation (eco:ServiceDonation): dateDonated, note, donationType, serviceDescription, hoursDonated

ANALYSIS RESULTS:
Original Question: "{original_question}"

{entity_context}

{intent_context}

{temporal_context}

{location_context}

{keyword_context}

{relationship_context}

QUERY GENERATION RULES:
1. Always use PREFIX eco: <http://www.semanticweb.org/eco-ontology#> and PREFIX webprotege: <http://webprotege.stanford.edu/>
2. Use webprotege: classes for main entities (webprotege:Event, webprotege:Location, etc.)
3. Use eco: properties for entity attributes (eco:eventTitle, eco:locationName, etc.)
4. CRITICAL: Always use proper SPARQL syntax: ?entity eco:property ?variable
5. Use OPTIONAL for properties that might not exist
6. Use FILTER with CONTAINS/REGEX for text searches
7. Use FILTER with date comparisons for temporal queries
8. Use FILTER with city/location matching for location queries
9. Use ORDER BY when appropriate for sorting
10. Use LIMIT 20-50 to prevent too many results
11. Use GROUP BY and COUNT for counting queries
12. Use UNION for multiple entity types
13. Make location properties OPTIONAL (locationName, city, etc.)
14. Return ONLY the SPARQL query, no explanations
15. Be precise based on the detected entities and intent

SPARQL SYNTAX EXAMPLES:
- Correct: ?event a eco:Event . ?event eco:eventTitle ?title .
- Correct: ?event a eco:EducationalEvent . ?event eco:eventTitle ?title .
- Correct: ?campaign a eco:Campaign . ?campaign eco:campaignName ?name .
- Correct: ?volunteer a webprotege:RCXXzqv27uFuX5nYU81XUvw . ?volunteer webprotege:R8BxRbqkCT2nIQCr5UoVlXD ?phone .
- Correct: ?assignment a webprotege:Rj2A7xNWLfpNcbE4HJMKqN . ?assignment webprotege:RDT3XEARggTy1BIBKDXXrmx ?status .
- Incorrect: eco:eventTitle ?title (missing subject)
- Incorrect: ?event eco:eventTitle (missing object)

IMPORTANT: For events, use UNION to include all event types:
{{
  ?event a eco:Event .
  ?event eco:eventTitle ?title .
}}
UNION
{{
  ?event a eco:EducationalEvent .
  ?event eco:eventTitle ?title .
}}
UNION
{{
  ?event a eco:EntertainmentEvent .
  ?event eco:eventTitle ?title .
}}
UNION
{{
  ?event a eco:CompetitiveEvent .
  ?event eco:eventTitle ?title .
}}
UNION
{{
  ?event a eco:SocializationEvent .
  ?event eco:eventTitle ?title .
}}

Generate a SPARQL query that accurately addresses the user's intent using the detected entities and relationships:

SPARQL QUERY:"""
    
    def _extract_sparql_query(self, text: str) -> str:
        """Extract clean SPARQL query from Gemini response"""
        # Remove markdown code blocks
        text = re.sub(r'```.*?\n', '', text)
        text = re.sub(r'```', '', text)
        
        # Find the SPARQL query
        lines = text.split('\n')
        query_lines = []
        in_query = False
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith(('PREFIX', 'SELECT', 'CONSTRUCT', 'ASK', 'DESCRIBE')):
                in_query = True
            if in_query:
                if stripped and not stripped.startswith('QUESTION:'):
                    query_lines.append(line)
        
        query = '\n'.join(query_lines).strip()
        
        # Ensure PREFIX is included
        if 'PREFIX eco:' not in query:
            query = f"PREFIX eco: <http://www.semanticweb.org/eco-ontology#>\n{query}"
            
        return query
    
    def _validate_and_clean_query(self, query: str) -> str:
        """Validate and clean the SPARQL query"""
        # Basic validation
        if not query or 'SELECT' not in query:
            return self._get_fallback_query("events")
        
        # Fix common SPARQL syntax errors
        lines = query.split('\n')
        fixed_lines = []
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('PREFIX') or line.startswith('SELECT') or line.startswith('WHERE') or line.startswith('LIMIT') or line.startswith('ORDER'):
                fixed_lines.append(line)
                continue
            
            # Fix missing subject in property statements
            if line.startswith('eco:') and not line.startswith('eco: '):
                # This is a property without a subject, skip it
                print(f"DEBUG: Skipping malformed line: {line}")
                continue
            
            # Fix incomplete triple patterns
            if line.endswith('eco:') and not line.endswith('eco: .'):
                # This is an incomplete triple, skip it
                print(f"DEBUG: Skipping incomplete triple: {line}")
                continue
            
            fixed_lines.append(line)
        
        query = '\n'.join(fixed_lines)
        
        # Ensure location properties are optional
        if '?location eco:locationName ?locationName' in query and 'OPTIONAL' not in query:
            query = query.replace(
                '?location eco:locationName ?locationName .',
                'OPTIONAL { ?location eco:locationName ?locationName . }'
            )
        
        if '?location eco:city ?city' in query and 'OPTIONAL' not in query:
            query = query.replace(
                '?location eco:city ?city .',
                'OPTIONAL { ?location eco:city ?city . }'
            )
        
        # Ensure LIMIT is reasonable
        if 'LIMIT' not in query:
            query += '\nLIMIT 50'

        # Defensive fix: some generated queries expect a property eco:donationType
        # to be present on donation instances, but in the ontology we model
        # type via rdf:type (e.g. eco:FinancialDonation) and many individuals
        # don't have eco:donationType. Make such patterns optional so queries
        # still return donation rows when donationType is absent.
        try:
            # Replace required donationType triples with OPTIONAL blocks
            query = re.sub(r"\?donation\s+eco:donationType\s+\?donationType\s*\.", \
                           "OPTIONAL { ?donation eco:donationType ?donationType . }", query)
        except Exception as e:
            print(f"DEBUG: failed to apply donationType defensive fix: {e}")

        # Defensive fix: queries that require '?donation a eco:Donation .' or that
        # ask for a specific donation subclass (e.g. eco:ServiceDonation) can miss
        # individuals typed in related subclasses. Replace any direct type check
        # on ?donation for a class whose name ends with 'Donation' with a UNION
        # covering the known donation classes so instances typed with subclasses
        # are still matched.
        try:
            def _donation_union_replacer(m):
                cls = m.group(1)
                # Only apply when the matched class name ends with 'Donation'
                if not cls or not cls.endswith('Donation'):
                    return m.group(0)
                unions = [
                    "{ ?donation a eco:Donation . }",
                    "{ ?donation a eco:FinancialDonation . }",
                    "{ ?donation a eco:MaterialDonation . }",
                    "{ ?donation a eco:ServiceDonation . }"
                ]
                return " UNION ".join(unions)

            query = re.sub(r"\?donation\s+a\s+eco:([A-Za-z0-9_]+)\s*\.", _donation_union_replacer, query)
        except Exception as e:
            print(f"DEBUG: failed to apply donation subclass union fix: {e}")

        # If the result set includes donations coming from UNIONs, the same
        # donation node can be matched multiple times (once per matching union
        # branch). Ensure a DISTINCT select for donation queries to remove
        # duplicate rows.
        try:
            if '?donation' in query and 'SELECT DISTINCT' not in query:
                # Replace the first occurrence of SELECT with SELECT DISTINCT
                query = re.sub(r"SELECT\s", "SELECT DISTINCT ", query, count=1)
        except Exception as e:
            print(f"DEBUG: failed to enforce DISTINCT on donation queries: {e}")

        return query
    
    def _get_fallback_query(self, question: str) -> str:
        """Simple fallback for emergency cases only"""
        question_lower = question.lower()
        
        # Specific handling for volunteer queries
        if 'volontaire' in question_lower or 'volunteer' in question_lower:
            # "compétences" or "skills"
            if 'compétence' in question_lower or 'skill' in question_lower or 'compétences' in question_lower:
                return """
        PREFIX webprotege: <http://webprotege.stanford.edu/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?label ?skills ?activityLevel
        WHERE {
            ?volunteer a webprotege:RCXXzqv27uFuX5nYU81XUvw .
            ?volunteer webprotege:RBqpxvMVBnwM1Wb6OhzTpHf ?skills .
            OPTIONAL { ?volunteer rdfs:label ?label }
            OPTIONAL { ?volunteer webprotege:RCHqvY6cUdoI8XfAt441VX0 ?activityLevel }
        }
        ORDER BY ?label
        LIMIT 50
        """
            # "expérience" or "experience"
            elif 'expérience' in question_lower or 'experience' in question_lower:
                return """
        PREFIX webprotege: <http://webprotege.stanford.edu/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?label ?experience ?activityLevel ?skills
        WHERE {
            ?volunteer a webprotege:RCXXzqv27uFuX5nYU81XUvw .
            ?volunteer webprotege:R9tdW5crNU837y5TemwdNfR ?experience .
            OPTIONAL { ?volunteer rdfs:label ?label }
            OPTIONAL { ?volunteer webprotege:RCHqvY6cUdoI8XfAt441VX0 ?activityLevel }
            OPTIONAL { ?volunteer webprotege:RBqpxvMVBnwM1Wb6OhzTpHf ?skills }
        }
        ORDER BY ?label
        LIMIT 50
        """
            # "contacts" or "contact"
            elif 'contact' in question_lower:
                return """
        PREFIX webprotege: <http://webprotege.stanford.edu/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?label ?phone ?email
        WHERE {
            ?volunteer a webprotege:RCXXzqv27uFuX5nYU81XUvw .
            OPTIONAL { ?volunteer rdfs:label ?label }
            OPTIONAL { ?volunteer webprotege:R8BxRbqkCT2nIQCr5UoVlXD ?phone }
            OPTIONAL { 
                ?volunteer webprotege:RBNk0vvVsRh8FjaWPGT0XCO ?user .
                ?user rdfs:comment ?email
            }
        }
        ORDER BY ?label
        LIMIT 50
        """
            # Default: all volunteers
            else:
                return """
        PREFIX webprotege: <http://webprotege.stanford.edu/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?volunteer ?label ?phone ?activityLevel ?skills ?experience
        WHERE {
            ?volunteer a webprotege:RCXXzqv27uFuX5nYU81XUvw .
            OPTIONAL { ?volunteer rdfs:label ?label }
            OPTIONAL { ?volunteer webprotege:R8BxRbqkCT2nIQCr5UoVlXD ?phone }
            OPTIONAL { ?volunteer webprotege:RCHqvY6cUdoI8XfAt441VX0 ?activityLevel }
            OPTIONAL { ?volunteer webprotege:RBqpxvMVBnwM1Wb6OhzTpHf ?skills }
            OPTIONAL { ?volunteer webprotege:R9tdW5crNU837y5TemwdNfR ?experience }
        }
        ORDER BY ?label
        LIMIT 50
        """
        
        # Specific handling for assignment queries
        if 'assignement' in question_lower or 'assignment' in question_lower:
            # "approuvés" or "approved"
            if 'approuvé' in question_lower or 'approuvés' in question_lower or 'approved' in question_lower:
                return """
        PREFIX webprotege: <http://webprotege.stanford.edu/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?assignment ?label ?status ?rating ?startDate
        WHERE {
            ?assignment a webprotege:Rj2A7xNWLfpNcbE4HJMKqN .
            ?assignment webprotege:RDT3XEARggTy1BIBKDXXrmx ?status .
            FILTER(CONTAINS(LCASE(STR(?status)), "approuv") || CONTAINS(LCASE(STR(?status)), "approved") || LCASE(STR(?status)) = "approved")
            OPTIONAL { ?assignment rdfs:label ?label }
            OPTIONAL { ?assignment webprotege:RRatingAssignment ?rating }
            OPTIONAL { ?assignment webprotege:RD3Wor03BEPInfzUaMNVPC7 ?startDate }
        }
        ORDER BY ?assignment
        LIMIT 50
        """
            # "rejetés" or "rejected"
            elif 'rejeté' in question_lower or 'rejetés' in question_lower or 'rejected' in question_lower:
                return """
        PREFIX webprotege: <http://webprotege.stanford.edu/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?assignment ?label ?status ?rating ?startDate
        WHERE {
            ?assignment a webprotege:Rj2A7xNWLfpNcbE4HJMKqN .
            ?assignment webprotege:RDT3XEARggTy1BIBKDXXrmx ?status .
            FILTER(CONTAINS(LCASE(STR(?status)), "rejet") || CONTAINS(LCASE(STR(?status)), "rejected") || LCASE(STR(?status)) = "rejected")
            OPTIONAL { ?assignment rdfs:label ?label }
            OPTIONAL { ?assignment webprotege:RRatingAssignment ?rating }
            OPTIONAL { ?assignment webprotege:RD3Wor03BEPInfzUaMNVPC7 ?startDate }
        }
        ORDER BY ?assignment
        LIMIT 50
        """
            # "statistiques" or "statistics"
            elif 'statistique' in question_lower or 'statistics' in question_lower:
                return """
        PREFIX webprotege: <http://webprotege.stanford.edu/>
        SELECT (COUNT(?assignment) as ?totalAssignments) 
               (COUNT(?approved) as ?approvedCount)
               (COUNT(?rejected) as ?rejectedCount)
               (COUNT(?pending) as ?pendingCount)
               (AVG(?rating) as ?averageRating)
        WHERE {
            ?assignment a webprotege:Rj2A7xNWLfpNcbE4HJMKqN .
            OPTIONAL { 
                ?assignment webprotege:RDT3XEARggTy1BIBKDXXrmx ?status .
                FILTER(CONTAINS(LCASE(STR(?status)), "approuv") || CONTAINS(LCASE(STR(?status)), "approved") || LCASE(STR(?status)) = "approved")
                BIND(?assignment as ?approved)
            }
            OPTIONAL { 
                ?assignment webprotege:RDT3XEARggTy1BIBKDXXrmx ?status .
                FILTER(CONTAINS(LCASE(STR(?status)), "rejet") || CONTAINS(LCASE(STR(?status)), "rejected") || LCASE(STR(?status)) = "rejected")
                BIND(?assignment as ?rejected)
            }
            OPTIONAL { 
                ?assignment webprotege:RDT3XEARggTy1BIBKDXXrmx ?status .
                FILTER(LCASE(STR(?status)) = "pending" || LCASE(STR(?status)) = "en attente")
                BIND(?assignment as ?pending)
            }
            OPTIONAL { ?assignment webprotege:RRatingAssignment ?rating }
        }
        """
            # "notes" or "ratings"
            elif 'note' in question_lower or 'rating' in question_lower:
                return """
        PREFIX webprotege: <http://webprotege.stanford.edu/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?assignment ?label ?rating ?status
        WHERE {
            ?assignment a webprotege:Rj2A7xNWLfpNcbE4HJMKqN .
            ?assignment webprotege:RRatingAssignment ?rating .
            OPTIONAL { ?assignment rdfs:label ?label }
            OPTIONAL { ?assignment webprotege:RDT3XEARggTy1BIBKDXXrmx ?status }
        }
        ORDER BY DESC(?rating)
        LIMIT 50
        """
            # Default: all assignments
            else:
                return """
        PREFIX webprotege: <http://webprotege.stanford.edu/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?assignment ?label ?status ?rating ?startDate
        WHERE {
            ?assignment a webprotege:Rj2A7xNWLfpNcbE4HJMKqN .
            OPTIONAL { ?assignment rdfs:label ?label }
            OPTIONAL { ?assignment webprotege:RDT3XEARggTy1BIBKDXXrmx ?status }
            OPTIONAL { ?assignment webprotege:RRatingAssignment ?rating }
            OPTIONAL { ?assignment webprotege:RD3Wor03BEPInfzUaMNVPC7 ?startDate }
        }
        ORDER BY ?assignment
        LIMIT 50
        """
        
        # Specific handling for reservation queries
        if 'réservation' in question_lower or 'reservation' in question_lower or 'reserve' in question_lower:
            # "par événement" or "by event" means group by event with count
            if 'par événement' in question_lower or 'by event' in question_lower or 'par event' in question_lower:
                return """
        PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
        PREFIX webprotege: <http://webprotege.stanford.edu/>
        SELECT ?eventTitle (COUNT(?reservation) as ?reservationCount)
        WHERE {
            ?reservation a eco:Reservation .
            OPTIONAL {
                ?reservation webprotege:R8r5yxVXnZfa0TwP5biVHiL ?event .
                ?event eco:eventTitle ?eventTitle .
            }
        }
        GROUP BY ?eventTitle
        ORDER BY ?eventTitle
        LIMIT 50
        """
            elif 'confirmée' in question_lower or 'confirmed' in question_lower or 'confirme' in question_lower:
                return """
        PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
        PREFIX webprotege: <http://webprotege.stanford.edu/>
        SELECT ?reservation ?seatNumber ?status ?eventTitle ?userName ?userLastName ?userEmail
        WHERE {
            ?reservation a eco:Reservation .
            ?reservation webprotege:R9wdyKGFoajnFCFN4oqnwHr ?status .
            FILTER(LCASE(STR(?status)) = "confirmed" || LCASE(STR(?status)) = "confirmée" || LCASE(STR(?status)) = "confirme")
            OPTIONAL { ?reservation webprotege:R7QgAmvOpBSpwRmRrDZL8VE ?seatNumber }
            OPTIONAL {
                ?reservation webprotege:R8r5yxVXnZfa0TwP5biVHiL ?event .
                ?event eco:eventTitle ?eventTitle .
            }
            OPTIONAL {
                ?reservation eco:belongsToUser ?user .
                ?user eco:firstName ?userName .
                OPTIONAL { ?user eco:lastName ?userLastName }
                OPTIONAL { ?user eco:email ?userEmail }
            }
        }
        ORDER BY ?reservation
        LIMIT 50
        """
            elif 'en attente' in question_lower or 'pending' in question_lower or 'attente' in question_lower:
                return """
        PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
        PREFIX webprotege: <http://webprotege.stanford.edu/>
        SELECT ?reservation ?seatNumber ?status ?eventTitle ?userName ?userLastName ?userEmail
        WHERE {
            ?reservation a eco:Reservation .
            ?reservation webprotege:R9wdyKGFoajnFCFN4oqnwHr ?status .
            FILTER(LCASE(STR(?status)) = "pending" || LCASE(STR(?status)) = "attente" || LCASE(STR(?status)) = "en attente")
            OPTIONAL { ?reservation webprotege:R7QgAmvOpBSpwRmRrDZL8VE ?seatNumber }
            OPTIONAL {
                ?reservation webprotege:R8r5yxVXnZfa0TwP5biVHiL ?event .
                ?event eco:eventTitle ?eventTitle .
            }
            OPTIONAL {
                ?reservation eco:belongsToUser ?user .
                ?user eco:firstName ?userName .
                OPTIONAL { ?user eco:lastName ?userLastName }
                OPTIONAL { ?user eco:email ?userEmail }
            }
        }
        ORDER BY ?reservation
        LIMIT 50
        """
            else:
                return """
        PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
        PREFIX webprotege: <http://webprotege.stanford.edu/>
        SELECT ?reservation ?seatNumber ?status ?eventTitle ?userName ?userLastName ?userEmail
        WHERE {
            ?reservation a eco:Reservation .
            OPTIONAL { ?reservation webprotege:R7QgAmvOpBSpwRmRrDZL8VE ?seatNumber }
            OPTIONAL { ?reservation webprotege:R9wdyKGFoajnFCFN4oqnwHr ?status }
            OPTIONAL {
                ?reservation webprotege:R8r5yxVXnZfa0TwP5biVHiL ?event .
                ?event eco:eventTitle ?eventTitle .
            }
            OPTIONAL {
                ?reservation eco:belongsToUser ?user .
                ?user eco:firstName ?userName .
                OPTIONAL { ?user eco:lastName ?userLastName }
                OPTIONAL { ?user eco:email ?userEmail }
            }
        }
        ORDER BY ?reservation
        LIMIT 50
        """
        
        # Specific handling for certification queries
        if 'certification' in question_lower or 'certificat' in question_lower:
            # "qui a reçu" or "who received" - show recipients
            if 'qui a reçu' in question_lower or 'who received' in question_lower or 'qui a reçu' in question_lower:
                return """
        PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
        PREFIX webprotege: <http://webprotege.stanford.edu/>
        SELECT ?awardedToName ?awardedToEmail (COUNT(?certification) as ?certificationCount) (SUM(?pointsEarned) as ?totalPoints)
        WHERE {
            ?certification a eco:Certification .
            ?certification eco:awardedTo ?recipient .
            ?recipient eco:firstName ?awardedToName .
            OPTIONAL { ?recipient eco:email ?awardedToEmail }
            OPTIONAL { ?certification webprotege:R9gsGMKtVBKEAd4d8I75UkC ?pointsEarned }
        }
        GROUP BY ?awardedToName ?awardedToEmail
        ORDER BY DESC(?certificationCount)
        LIMIT 50
        """
            # "qui émet" or "who issues" - show issuers
            elif 'qui émet' in question_lower or 'who issues' in question_lower or 'who issues' in question_lower or 'émet' in question_lower:
                return """
        PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
        PREFIX webprotege: <http://webprotege.stanford.edu/>
        SELECT ?issuerName ?issuerEmail (COUNT(?certification) as ?issuedCount)
        WHERE {
            ?certification a eco:Certification .
            ?certification eco:issuedBy ?issuer .
            ?issuer eco:firstName ?issuerName .
            OPTIONAL { ?issuer eco:email ?issuerEmail }
        }
        GROUP BY ?issuerName ?issuerEmail
        ORDER BY DESC(?issuedCount)
        LIMIT 50
        """
            # "quels types" or "what types" - show certification types
            elif 'quels types' in question_lower or 'what types' in question_lower or 'type' in question_lower:
                return """
        PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
        PREFIX webprotege: <http://webprotege.stanford.edu/>
        SELECT ?type (COUNT(?certification) as ?certificationCount)
        WHERE {
            ?certification a eco:Certification .
            ?certification webprotege:RBPJvon09P5n1GLdLbu2esV ?type .
        }
        GROUP BY ?type
        ORDER BY DESC(?certificationCount)
        LIMIT 50
        """
            # "par points" or "by points" means order by points
            elif 'par points' in question_lower or 'by points' in question_lower:
                return """
        PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
        PREFIX webprotege: <http://webprotege.stanford.edu/>
        SELECT ?certification ?certificateCode ?pointsEarned ?type ?issuerName ?awardedToName ?eventTitle
        WHERE {
            ?certification a eco:Certification .
            OPTIONAL { ?certification webprotege:R9QGoktbkOBbsLkvgjicNA8 ?certificateCode }
            OPTIONAL { ?certification webprotege:R9gsGMKtVBKEAd4d8I75UkC ?pointsEarned }
            OPTIONAL { ?certification webprotege:RBPJvon09P5n1GLdLbu2esV ?type }
            OPTIONAL {
                ?certification eco:issuedBy ?issuer .
                ?issuer eco:firstName ?issuerName .
            }
            OPTIONAL {
                ?certification eco:awardedTo ?recipient .
                ?recipient eco:firstName ?awardedToName .
            }
            OPTIONAL {
                ?reservation a eco:Reservation .
                ?reservation eco:belongsToUser ?recipient .
                ?reservation webprotege:R8r5yxVXnZfa0TwP5biVHiL ?event .
                ?event eco:eventTitle ?eventTitle .
            }
        }
        ORDER BY DESC(?pointsEarned)
        LIMIT 50
        """
            # "émise" or "issued" - show all issued certifications with details
            elif 'émis' in question_lower or 'issued' in question_lower or 'émises' in question_lower:
                return """
        PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
        PREFIX webprotege: <http://webprotege.stanford.edu/>
        SELECT ?certification ?certificateCode ?pointsEarned ?type ?issuerName ?awardedToName ?eventTitle
        WHERE {
            ?certification a eco:Certification .
            OPTIONAL { ?certification webprotege:R9QGoktbkOBbsLkvgjicNA8 ?certificateCode }
            OPTIONAL { ?certification webprotege:R9gsGMKtVBKEAd4d8I75UkC ?pointsEarned }
            OPTIONAL { ?certification webprotege:RBPJvon09P5n1GLdLbu2esV ?type }
            OPTIONAL {
                ?certification eco:issuedBy ?issuer .
                ?issuer eco:firstName ?issuerName .
            }
            OPTIONAL {
                ?certification eco:awardedTo ?recipient .
                ?recipient eco:firstName ?awardedToName .
            }
            OPTIONAL {
                ?reservation a eco:Reservation .
                ?reservation eco:belongsToUser ?recipient .
                ?reservation webprotege:R8r5yxVXnZfa0TwP5biVHiL ?event .
                ?event eco:eventTitle ?eventTitle .
            }
        }
        ORDER BY ?certification
        LIMIT 50
        """
            else:
                return """
        PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
        PREFIX webprotege: <http://webprotege.stanford.edu/>
        SELECT ?certification ?certificateCode ?pointsEarned ?type ?issuerName ?awardedToName ?eventTitle
        WHERE {
            ?certification a eco:Certification .
            OPTIONAL { ?certification webprotege:R9QGoktbkOBbsLkvgjicNA8 ?certificateCode }
            OPTIONAL { ?certification webprotege:R9gsGMKtVBKEAd4d8I75UkC ?pointsEarned }
            OPTIONAL { ?certification webprotege:RBPJvon09P5n1GLdLbu2esV ?type }
            OPTIONAL {
                ?certification eco:issuedBy ?issuer .
                ?issuer eco:firstName ?issuerName .
            }
            OPTIONAL {
                ?certification eco:awardedTo ?recipient .
                ?recipient eco:firstName ?awardedToName .
            }
            OPTIONAL {
                ?reservation a eco:Reservation .
                ?reservation eco:belongsToUser ?recipient .
                ?reservation webprotege:R8r5yxVXnZfa0TwP5biVHiL ?event .
                ?event eco:eventTitle ?eventTitle .
            }
        }
        ORDER BY ?certification
        LIMIT 50
        """
        
        # Specific handling for campaign queries
        if 'campagne' in question_lower or 'campaign' in question_lower:
            if 'active' in question_lower or 'actif' in question_lower:
                return """
        PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
        SELECT ?campaignName ?campaignDescription ?campaignStatus ?startDate ?endDate ?goal
        WHERE {
            {
                ?campaign a eco:Campaign .
                ?campaign eco:campaignName ?campaignName .
                ?campaign eco:campaignStatus ?campaignStatus .
                FILTER(LCASE(STR(?campaignStatus)) = "active" || LCASE(STR(?campaignStatus)) = "actif")
            }
            UNION
            {
                ?campaign a eco:CleanupCampaign .
                ?campaign eco:campaignName ?campaignName .
                ?campaign eco:campaignStatus ?campaignStatus .
                FILTER(LCASE(STR(?campaignStatus)) = "active" || LCASE(STR(?campaignStatus)) = "actif")
            }
            UNION
            {
                ?campaign a eco:AwarenessCampaign .
                ?campaign eco:campaignName ?campaignName .
                ?campaign eco:campaignStatus ?campaignStatus .
                FILTER(LCASE(STR(?campaignStatus)) = "active" || LCASE(STR(?campaignStatus)) = "actif")
            }
            UNION
            {
                ?campaign a eco:FundingCampaign .
                ?campaign eco:campaignName ?campaignName .
                ?campaign eco:campaignStatus ?campaignStatus .
                FILTER(LCASE(STR(?campaignStatus)) = "active" || LCASE(STR(?campaignStatus)) = "actif")
            }
            UNION
            {
                ?campaign a eco:EventCampaign .
                ?campaign eco:campaignName ?campaignName .
                ?campaign eco:campaignStatus ?campaignStatus .
                FILTER(LCASE(STR(?campaignStatus)) = "active" || LCASE(STR(?campaignStatus)) = "actif")
            }
            OPTIONAL { ?campaign eco:campaignDescription ?campaignDescription }
            OPTIONAL { ?campaign eco:startDate ?startDate }
            OPTIONAL { ?campaign eco:endDate ?endDate }
            OPTIONAL { ?campaign eco:goal ?goal }
        }
        ORDER BY ?campaignName
        LIMIT 50
        """
            else:
                return """
        PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
        SELECT ?campaignName ?campaignDescription ?campaignStatus ?startDate ?endDate ?goal
        WHERE {
            ?campaign a eco:Campaign .
            ?campaign eco:campaignName ?campaignName .
            OPTIONAL { ?campaign eco:campaignDescription ?campaignDescription }
            OPTIONAL { ?campaign eco:campaignStatus ?campaignStatus }
            OPTIONAL { ?campaign eco:startDate ?startDate }
            OPTIONAL { ?campaign eco:endDate ?endDate }
            OPTIONAL { ?campaign eco:goal ?goal }
        }
        ORDER BY ?campaignName
        LIMIT 50
        """
        
        return """
        PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
        PREFIX webprotege: <http://webprotege.stanford.edu/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?item ?name ?type
        WHERE {
            {
                ?item a eco:Event ;
                     eco:eventTitle ?name .
                BIND("Event" as ?type)
            }
            UNION
            {
                ?item a eco:EducationalEvent ;
                     eco:eventTitle ?name .
                BIND("EducationalEvent" as ?type)
            }
            UNION
            {
                ?item a eco:EntertainmentEvent ;
                     eco:eventTitle ?name .
                BIND("EntertainmentEvent" as ?type)
            }
            UNION
            {
                ?item a eco:CompetitiveEvent ;
                     eco:eventTitle ?name .
                BIND("CompetitiveEvent" as ?type)
            }
            UNION
            {
                ?item a eco:Location ;
                     eco:locationName ?name .
                BIND("Location" as ?type)
            }
            UNION
            {
                ?item a webprotege:RCXXzqv27uFuX5nYU81XUvw ;
                     rdfs:label ?name .
                BIND("Volunteer" as ?type)
            }
            UNION
            {
                ?item a webprotege:Rj2A7xNWLfpNcbE4HJMKqN ;
                     rdfs:label ?name .
                BIND("Assignment" as ?type)
            }
            UNION
            {
                ?item a eco:Campaign ;
                     eco:campaignName ?name .
                BIND("Campaign" as ?type)
            }
            UNION
            {
                ?item a eco:Sponsor ;
                     eco:companyName ?name .
                BIND("Sponsor" as ?type)
            }
            UNION
            {
                ?item a eco:Donation ;
                     eco:dateDonated ?name .
                BIND("Donation" as ?type)
            }
        }
        ORDER BY ?type ?name
        LIMIT 20
        """