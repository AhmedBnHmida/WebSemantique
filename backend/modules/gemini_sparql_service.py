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
            return self._get_fallback_query("personnes")
    
    def _build_prompt(self, question: str) -> str:
        """Build the prompt for Gemini - Education domain only"""
        return f"""You are a SPARQL query generator for an educational platform. Convert the natural language question to a valid SPARQL query.

ONTOLOGY CONTEXT:
PREFIX edu: <http://www.education-intelligente.org/ontologie#>
PREFIX ont: <http://www.education-intelligente.org/ontologie#>

MAIN CLASSES:
- Personne (Person): Etudiant (Student), Enseignant (Teacher), Professeur (Professor), Assistant, Encadrant (Supervisor)
- Universite (University): UniversitePublique (Public), UniversitePrivee (Private)
- Specialite (Specialization): SpecialiteInformatique, SpecialiteDataScience, SpecialiteIngenierie, etc.
- Cours (Course): CoursTheorique (Theoretical), CoursPratique (Practical)
- Competence (Competency/Skill)
- ProjetAcademique (Academic Project)
- RessourcePedagogique (Pedagogical Resource)
- TechnologieEducative (Educational Technology)
- Evaluation (Assessment/Exam)
- OrientationAcademique (Academic Orientation)

KEY PROPERTIES:
- Personne: nom, prenom, email, telephone, dateNaissance, role
- Etudiant: numeroMatricule, niveauEtude, moyenneGenerale, appartientA, specialiseEn, suitCours
- Enseignant: grade, anciennete, appartientA, enseigne
- Universite: nomUniversite, ville, pays, nombreEtudiants, offre, emploie
- Specialite: nomSpecialite, codeSpecialite, description, estOffertePar, faitPartieDe
- Cours: intitule, codeCours, creditsECTS, semestre, volumeHoraire, langueCours, faitPartieDe, enseignePar
- Competence: nomCompetence, description, niveau
- ProjetAcademique: nomProjet, description, dateDebut, dateFin
- RessourcePedagogique: nomRessource, description, typeRessource
- TechnologieEducative: nomTechnologie, description, typeTechnologie
- Evaluation: typeEvaluation, dateEvaluation, note
- OrientationAcademique: typeOrientation, dateOrientation

IMPORTANT QUERY PATTERNS:
- For Personne queries: Use UNION to include all subclasses (Etudiant, Enseignant, etc.)
- For Cours queries: Use UNION to include CoursTheorique and CoursPratique
- For Universite queries: Use UNION to include UniversitePublique and UniversitePrivee
- For text searches: Use FILTER(CONTAINS(LCASE(STR(?field)), "searchterm"))
- For date filters: Use FILTER(?date >= NOW()) for future, FILTER(?date < NOW()) for past
- For city filters: FILTER(CONTAINS(LCASE(STR(?ville)), "cityname"))

CRITICAL RULES:
1. Always use PREFIX edu: <http://www.education-intelligente.org/ontologie#> or PREFIX ont: <http://www.education-intelligente.org/ontologie#>
2. Use OPTIONAL for properties that might not exist
3. Use ORDER BY when appropriate for sorting
4. Use LIMIT 20-50 to prevent too many results
5. Use UNION for multiple entity types or subclasses
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
        
        return f"""You are an expert SPARQL query generator for an educational platform. Generate a precise SPARQL query based on the structured analysis provided below.

ONTOLOGY CONTEXT:
PREFIX edu: <http://www.education-intelligente.org/ontologie#>
PREFIX ont: <http://www.education-intelligente.org/ontologie#>

MAIN CLASSES AND THEIR PROPERTIES (Education Domain):
- Personne (edu:Personne): nom, prenom, email, telephone, dateNaissance, role
  - Etudiant (edu:Etudiant): nom, prenom, email, telephone, numeroMatricule, niveauEtude, moyenneGenerale, appartientA, specialiseEn, suitCours
  - EtudiantLicence (edu:EtudiantLicence): same as Etudiant
  - EtudiantMaster (edu:EtudiantMaster): same as Etudiant
  - EtudiantDoctorat (edu:EtudiantDoctorat): same as Etudiant
  - Enseignant (edu:Enseignant): nom, prenom, email, telephone, grade, anciennete, appartientA, enseigne
  - Professeur (edu:Professeur): same as Enseignant
  - Assistant (edu:Assistant): same as Enseignant
  - Encadrant (edu:Encadrant): same as Enseignant
- Universite (edu:Universite): nomUniversite, anneeFondation, ville, pays, nombreEtudiants, rangNational, siteWeb, offre, emploie, adopteTechnologie
  - UniversitePublique (edu:UniversitePublique): same as Universite
  - UniversitePrivee (edu:UniversitePrivee): same as Universite
- Specialite (edu:Specialite): nomSpecialite, codeSpecialite, description, dureeFormation, niveauDiplome, nombreModules, estOffertePar, faitPartieDe, formePour
  - SpecialiteInformatique (edu:SpecialiteInformatique): same as Specialite
  - SpecialiteDataScience (edu:SpecialiteDataScience): same as Specialite
  - SpecialiteIngenierie (edu:SpecialiteIngenierie): same as Specialite
  - SpecialiteSciences (edu:SpecialiteSciences): same as Specialite
  - SpecialiteMedecine (edu:SpecialiteMedecine): same as Specialite
  - SpecialiteEconomie (edu:SpecialiteEconomie): same as Specialite
  - SpecialiteDroit (edu:SpecialiteDroit): same as Specialite
  - SpecialiteLettres (edu:SpecialiteLettres): same as Specialite
- Cours (edu:Cours): intitule, codeCours, creditsECTS, semestre, volumeHoraire, langueCours, faitPartieDe, enseignePar
  - CoursTheorique (edu:CoursTheorique): same as Cours
  - CoursPratique (edu:CoursPratique): same as Cours
- Competence (edu:Competence): nomCompetence, description, niveau, estFormeePar
- ProjetAcademique (edu:ProjetAcademique): nomProjet, description, dateDebut, dateFin, typeProjet, estRealisePar, concerne
- RessourcePedagogique (edu:RessourcePedagogique): nomRessource, description, typeRessource, estUtiliseDans
- TechnologieEducative (edu:TechnologieEducative): nomTechnologie, description, typeTechnologie, estUtilisePar
- Evaluation (edu:Evaluation): typeEvaluation, dateEvaluation, note, estRealisePar, concerne
- OrientationAcademique (edu:OrientationAcademique): typeOrientation, dateOrientation, concerne
  - EntretienConseiller (edu:EntretienConseiller): same as OrientationAcademique

ANALYSIS RESULTS:
Original Question: "{original_question}"

{entity_context}

{intent_context}

{temporal_context}

{location_context}

{keyword_context}

{relationship_context}

QUERY GENERATION RULES:
1. Always use PREFIX edu: <http://www.education-intelligente.org/ontologie#> or PREFIX ont: <http://www.education-intelligente.org/ontologie#>
2. For education domain entities, use edu: or ont: prefix (edu:Personne, edu:Universite, edu:Cours, etc.)
3. For education properties, use edu: prefix (edu:nom, edu:prenom, edu:nomUniversite, edu:intitule, etc.)
4. CRITICAL: Always use proper SPARQL syntax: ?entity edu:property ?variable
6. Use OPTIONAL for properties that might not exist
7. Use FILTER with CONTAINS/REGEX for text searches: FILTER(CONTAINS(LCASE(STR(?nom)), "searchterm"))
8. Use FILTER with date comparisons for temporal queries: FILTER(?date >= NOW()) for future
9. Use FILTER with city/location matching for location queries: FILTER(CONTAINS(LCASE(STR(?ville)), "cityname"))
10. Use ORDER BY when appropriate for sorting: ORDER BY ?nom
11. Use LIMIT 20-50 to prevent too many results
12. Use GROUP BY and COUNT for counting queries: SELECT (COUNT(?entity) as ?count)
13. Use UNION for multiple entity types or subclasses
14. For Personne queries, use UNION to include all subclasses (Etudiant, Enseignant, etc.)
15. For Cours queries, use UNION to include all subclasses (CoursTheorique, CoursPratique)
16. Return ONLY the SPARQL query, no explanations
17. Be precise based on the detected entities and intent

SPARQL SYNTAX EXAMPLES (Education Domain):
- Correct: ?personne a edu:Personne . ?personne edu:nom ?nom . ?personne edu:prenom ?prenom .
- Correct: ?etudiant a edu:Etudiant . ?etudiant edu:nom ?nom . ?etudiant edu:numeroMatricule ?matricule .
- Correct: ?universite a edu:Universite . ?universite edu:nomUniversite ?nom .
- Correct: ?cours a edu:Cours . ?cours edu:intitule ?intitule . ?cours edu:codeCours ?code .
- Correct: ?specialite a edu:Specialite . ?specialite edu:nomSpecialite ?nom .
- Correct: ?competence a edu:Competence . ?competence edu:nomCompetence ?nom .
- Incorrect: edu:nom ?nom (missing subject)
- Incorrect: ?personne edu:nom (missing object)

IMPORTANT: For education domain entities, use UNION to include all subclasses:

For Personnes (People):
{{
  ?personne a edu:Personne .
  ?personne edu:nom ?nom .
}}
UNION
{{
  ?personne a edu:Etudiant .
  ?personne edu:nom ?nom .
}}
UNION
{{
  ?personne a edu:Enseignant .
  ?personne edu:nom ?nom .
}}

For Cours (Courses):
{{
  ?cours a edu:Cours .
  ?cours edu:intitule ?intitule .
}}
UNION
{{
  ?cours a edu:CoursTheorique .
  ?cours edu:intitule ?intitule .
}}
UNION
{{
  ?cours a edu:CoursPratique .
  ?cours edu:intitule ?intitule .
}}

For Universites (Universities):
{{
  ?universite a edu:Universite .
  ?universite edu:nomUniversite ?nom .
}}
UNION
{{
  ?universite a edu:UniversitePublique .
  ?universite edu:nomUniversite ?nom .
}}
UNION
{{
  ?universite a edu:UniversitePrivee .
  ?universite edu:nomUniversite ?nom .
}}

For Specialites (Specializations):
{{
  ?specialite a edu:Specialite .
  ?specialite edu:nomSpecialite ?nom .
}}
UNION
{{
  ?specialite a edu:SpecialiteInformatique .
  ?specialite edu:nomSpecialite ?nom .
}}
UNION
{{
  ?specialite a edu:SpecialiteDataScience .
  ?specialite edu:nomSpecialite ?nom .
}}

For Evaluations (Assessments):
{{
  ?evaluation a edu:Evaluation .
  ?evaluation edu:typeEvaluation ?type .
}}

For ProjetsAcademiques (Academic Projects):
{{
  ?projet a edu:ProjetAcademique .
  ?projet edu:nomProjet ?nom .
}}

For RessourcesPedagogiques (Pedagogical Resources):
{{
  ?ressource a edu:RessourcePedagogique .
  ?ressource edu:nomRessource ?nom .
}}

For TechnologiesEducatives (Educational Technologies):
{{
  ?technologie a edu:TechnologieEducative .
  ?technologie edu:nomTechnologie ?nom .
}}

For OrientationsAcademiques (Academic Orientations):
{{
  ?orientation a edu:OrientationAcademique .
  ?orientation edu:typeOrientation ?type .
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
        
        # Ensure PREFIX is included - education domain only
        if 'edu:' in query or 'ont:' in query:
            if 'PREFIX edu:' not in query and 'PREFIX ont:' not in query:
                query = f"PREFIX edu: <http://www.education-intelligente.org/ontologie#>\n{query}"
        elif 'PREFIX edu:' not in query:
            # Default to education domain
            query = f"PREFIX edu: <http://www.education-intelligente.org/ontologie#>\n{query}"
            
        return query
    
    def _validate_and_clean_query(self, query: str) -> str:
        """Validate and clean the SPARQL query"""
        # Basic validation
        if not query or 'SELECT' not in query:
            return self._get_fallback_query("personnes")
        
        # Fix common SPARQL syntax errors
        lines = query.split('\n')
        fixed_lines = []
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('PREFIX') or line.startswith('SELECT') or line.startswith('WHERE') or line.startswith('LIMIT') or line.startswith('ORDER'):
                fixed_lines.append(line)
                continue
            
            # Fix missing subject in property statements
            if (line.startswith('edu:') or line.startswith('ont:')) and not (line.startswith('edu: ') or line.startswith('ont: ')):
                # This is a property without a subject, skip it
                print(f"DEBUG: Skipping malformed line: {line}")
                continue
            
            # Fix incomplete triple patterns
            if (line.endswith('edu:') or line.endswith('ont:')) and not (line.endswith('edu: .') or line.endswith('ont: .')):
                # This is an incomplete triple, skip it
                print(f"DEBUG: Skipping incomplete triple: {line}")
                continue
            
            fixed_lines.append(line)
        
        query = '\n'.join(fixed_lines)
        
        # Ensure LIMIT is reasonable
        if 'LIMIT' not in query:
            query += '\nLIMIT 50'

        return query
    
    def _get_fallback_query(self, question: str) -> str:
        """Simple fallback for emergency cases only - Education domain"""
        question_lower = question.lower()
        
        # Specific handling for Personne queries
        if 'personne' in question_lower or 'person' in question_lower or 'personnes' in question_lower or 'people' in question_lower:
                return """
        PREFIX edu: <http://www.education-intelligente.org/ontologie#>
        SELECT ?personne ?nom ?prenom ?email ?telephone ?role
        WHERE {
            {
                ?personne a edu:Personne .
            }
            UNION
            {
                ?personne a edu:Etudiant .
            }
            UNION
            {
                ?personne a edu:Enseignant .
            }
            OPTIONAL { ?personne edu:nom ?nom }
            OPTIONAL { ?personne edu:prenom ?prenom }
            OPTIONAL { ?personne edu:email ?email }
            OPTIONAL { ?personne edu:telephone ?telephone }
            OPTIONAL { ?personne edu:role ?role }
        }
        ORDER BY ?nom
        LIMIT 50
        """
        
        # Specific handling for Etudiant queries
        if 'étudiant' in question_lower or 'etudiant' in question_lower or 'student' in question_lower:
                return """
        PREFIX edu: <http://www.education-intelligente.org/ontologie#>
        SELECT ?etudiant ?nom ?prenom ?email ?numeroMatricule ?niveauEtude ?moyenneGenerale
        WHERE {
            {
                ?etudiant a edu:Etudiant .
            }
            UNION
            {
                ?etudiant a edu:EtudiantLicence .
            }
            UNION
            {
                ?etudiant a edu:EtudiantMaster .
            }
            UNION
            {
                ?etudiant a edu:EtudiantDoctorat .
            }
            OPTIONAL { ?etudiant edu:nom ?nom }
            OPTIONAL { ?etudiant edu:prenom ?prenom }
            OPTIONAL { ?etudiant edu:email ?email }
            OPTIONAL { ?etudiant edu:numeroMatricule ?numeroMatricule }
            OPTIONAL { ?etudiant edu:niveauEtude ?niveauEtude }
            OPTIONAL { ?etudiant edu:moyenneGenerale ?moyenneGenerale }
        }
        ORDER BY ?nom
        LIMIT 50
        """
        
        # Specific handling for Enseignant queries
        if 'enseignant' in question_lower or 'teacher' in question_lower or 'professeur' in question_lower or 'professor' in question_lower:
                return """
        PREFIX edu: <http://www.education-intelligente.org/ontologie#>
        SELECT ?enseignant ?nom ?prenom ?email ?grade ?anciennete
        WHERE {
            {
                ?enseignant a edu:Enseignant .
            }
            UNION
            {
                ?enseignant a edu:Professeur .
            }
            UNION
            {
                ?enseignant a edu:Assistant .
            }
            UNION
            {
                ?enseignant a edu:Encadrant .
            }
            OPTIONAL { ?enseignant edu:nom ?nom }
            OPTIONAL { ?enseignant edu:prenom ?prenom }
            OPTIONAL { ?enseignant edu:email ?email }
            OPTIONAL { ?enseignant edu:grade ?grade }
            OPTIONAL { ?enseignant edu:anciennete ?anciennete }
        }
        ORDER BY ?nom
        LIMIT 50
        """
        
        # Specific handling for Universite queries
        if 'université' in question_lower or 'universite' in question_lower or 'university' in question_lower:
                return """
        PREFIX edu: <http://www.education-intelligente.org/ontologie#>
        SELECT ?universite ?nomUniversite ?ville ?pays ?nombreEtudiants
        WHERE {
            {
                ?universite a edu:Universite .
            }
            UNION
            {
                ?universite a edu:UniversitePublique .
            }
            UNION
            {
                ?universite a edu:UniversitePrivee .
            }
            OPTIONAL { ?universite edu:nomUniversite ?nomUniversite }
            OPTIONAL { ?universite edu:ville ?ville }
            OPTIONAL { ?universite edu:pays ?pays }
            OPTIONAL { ?universite edu:nombreEtudiants ?nombreEtudiants }
        }
        ORDER BY ?nomUniversite
        LIMIT 50
        """
        
        # Specific handling for Specialite queries
        if 'spécialité' in question_lower or 'specialite' in question_lower or 'specialization' in question_lower:
                return """
        PREFIX edu: <http://www.education-intelligente.org/ontologie#>
        SELECT ?specialite ?nomSpecialite ?codeSpecialite ?description
        WHERE {
            ?specialite a edu:Specialite .
            OPTIONAL { ?specialite edu:nomSpecialite ?nomSpecialite }
            OPTIONAL { ?specialite edu:codeSpecialite ?codeSpecialite }
            OPTIONAL { ?specialite edu:description ?description }
        }
        ORDER BY ?nomSpecialite
        LIMIT 50
        """
        
        # Specific handling for Cours queries
        if 'cours' in question_lower or 'course' in question_lower:
                return """
        PREFIX edu: <http://www.education-intelligente.org/ontologie#>
        SELECT ?cours ?intitule ?codeCours ?creditsECTS ?semestre
        WHERE {
            {
                ?cours a edu:Cours .
            }
            UNION
            {
                ?cours a edu:CoursTheorique .
            }
            UNION
            {
                ?cours a edu:CoursPratique .
            }
            OPTIONAL { ?cours edu:intitule ?intitule }
            OPTIONAL { ?cours edu:codeCours ?codeCours }
            OPTIONAL { ?cours edu:creditsECTS ?creditsECTS }
            OPTIONAL { ?cours edu:semestre ?semestre }
        }
        ORDER BY ?intitule
        LIMIT 50
        """
        
        # Specific handling for Competence queries
        if 'compétence' in question_lower or 'competence' in question_lower or 'skill' in question_lower:
                return """
        PREFIX edu: <http://www.education-intelligente.org/ontologie#>
        SELECT ?competence ?nomCompetence ?description ?niveau
        WHERE {
            ?competence a edu:Competence .
            OPTIONAL { ?competence edu:nomCompetence ?nomCompetence }
            OPTIONAL { ?competence edu:description ?description }
            OPTIONAL { ?competence edu:niveau ?niveau }
        }
        ORDER BY ?nomCompetence
        LIMIT 50
        """
        
        # Specific handling for ProjetAcademique queries
        if 'projet' in question_lower or 'project' in question_lower:
                return """
        PREFIX edu: <http://www.education-intelligente.org/ontologie#>
        SELECT ?projet ?nomProjet ?description ?dateDebut ?dateFin
        WHERE {
            ?projet a edu:ProjetAcademique .
            OPTIONAL { ?projet edu:nomProjet ?nomProjet }
            OPTIONAL { ?projet edu:description ?description }
            OPTIONAL { ?projet edu:dateDebut ?dateDebut }
            OPTIONAL { ?projet edu:dateFin ?dateFin }
        }
        ORDER BY ?nomProjet
        LIMIT 50
        """
        
        # Specific handling for RessourcePedagogique queries
        if 'ressource' in question_lower or 'resource' in question_lower:
                return """
        PREFIX edu: <http://www.education-intelligente.org/ontologie#>
        SELECT ?ressource ?nomRessource ?description ?typeRessource
        WHERE {
            ?ressource a edu:RessourcePedagogique .
            OPTIONAL { ?ressource edu:nomRessource ?nomRessource }
            OPTIONAL { ?ressource edu:description ?description }
            OPTIONAL { ?ressource edu:typeRessource ?typeRessource }
        }
        ORDER BY ?nomRessource
        LIMIT 50
        """
        
        # Specific handling for TechnologieEducative queries
        if 'technologie' in question_lower or 'technology' in question_lower:
                return """
        PREFIX edu: <http://www.education-intelligente.org/ontologie#>
        SELECT ?technologie ?nomTechnologie ?description ?typeTechnologie
        WHERE {
            ?technologie a edu:TechnologieEducative .
            OPTIONAL { ?technologie edu:nomTechnologie ?nomTechnologie }
            OPTIONAL { ?technologie edu:description ?description }
            OPTIONAL { ?technologie edu:typeTechnologie ?typeTechnologie }
        }
        ORDER BY ?nomTechnologie
        LIMIT 50
        """
        
        # Specific handling for Evaluation queries
        if 'évaluation' in question_lower or 'evaluation' in question_lower or 'examen' in question_lower or 'exam' in question_lower:
                return """
        PREFIX edu: <http://www.education-intelligente.org/ontologie#>
        SELECT ?evaluation ?typeEvaluation ?dateEvaluation ?note
        WHERE {
            ?evaluation a edu:Evaluation .
            OPTIONAL { ?evaluation edu:typeEvaluation ?typeEvaluation }
            OPTIONAL { ?evaluation edu:dateEvaluation ?dateEvaluation }
            OPTIONAL { ?evaluation edu:note ?note }
        }
        ORDER BY ?dateEvaluation
        LIMIT 50
        """
        
        # Specific handling for OrientationAcademique queries
        if 'orientation' in question_lower or 'orientation' in question_lower:
                return """
        PREFIX edu: <http://www.education-intelligente.org/ontologie#>
        SELECT ?orientation ?typeOrientation ?dateOrientation
        WHERE {
            {
                ?orientation a edu:OrientationAcademique .
            }
            UNION
            {
                ?orientation a edu:EntretienConseiller .
            }
            OPTIONAL { ?orientation edu:typeOrientation ?typeOrientation }
            OPTIONAL { ?orientation edu:dateOrientation ?dateOrientation }
        }
        ORDER BY ?dateOrientation
        LIMIT 50
        """
        
        # Default fallback query for education domain
        return """
        PREFIX edu: <http://www.education-intelligente.org/ontologie#>
        SELECT ?item ?name ?type
        WHERE {
            {
                ?item a edu:Personne .
                OPTIONAL { ?item edu:nom ?nom1 . ?item edu:prenom ?prenom1 . }
                BIND(CONCAT(COALESCE(?nom1, ""), " ", COALESCE(?prenom1, "")) as ?name)
                BIND("Personne" as ?type)
            }
            UNION
            {
                ?item a edu:Universite .
                ?item edu:nomUniversite ?name .
                BIND("Universite" as ?type)
            }
            UNION
            {
                ?item a edu:Specialite .
                ?item edu:nomSpecialite ?name .
                BIND("Specialite" as ?type)
            }
            UNION
            {
                ?item a edu:Cours .
                ?item edu:intitule ?name .
                BIND("Cours" as ?type)
            }
            UNION
            {
                ?item a edu:Competence .
                ?item edu:nomCompetence ?name .
                BIND("Competence" as ?type)
            }
            UNION
            {
                ?item a edu:ProjetAcademique .
                ?item edu:nomProjet ?name .
                BIND("ProjetAcademique" as ?type)
            }
            UNION
            {
                ?item a edu:RessourcePedagogique .
                ?item edu:nomRessource ?name .
                BIND("RessourcePedagogique" as ?type)
            }
            UNION
            {
                ?item a edu:TechnologieEducative .
                ?item edu:nomTechnologie ?name .
                BIND("TechnologieEducative" as ?type)
            }
            UNION
            {
                ?item a edu:Evaluation .
                ?item edu:typeEvaluation ?name .
                BIND("Evaluation" as ?type)
            }
            UNION
            {
                ?item a edu:OrientationAcademique .
                ?item edu:typeOrientation ?name .
                BIND("OrientationAcademique" as ?type)
            }
        }
        ORDER BY ?type ?name
        LIMIT 50
        """