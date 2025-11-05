"""
Deterministic SPARQL Template Engine for Semantic Search Fallback
Maps keywords to SPARQL query templates when AI pipeline fails
"""
import re

class SearchTemplateEngine:
    """Template-based SPARQL query generator for education domain"""
    
    PREFIX = "http://www.education-intelligente.org/ontologie#"
    
    # Entity patterns
    ENTITY_PATTERNS = {
        'universite': r'(universit[ée]|univ|facult[ée])',
        'specialite': r'(sp[ée]cialit[ée]|formation|programme|domaine)',
        'cours': r'(cours|matière|module|enseignement)',
        'competence': r'(comp[ée]tence|skill|savoir-faire)',
        'projet': r'(projet|stage|travail)',
        'personne': r'(personne|étudiant|enseignant|professeur)',
        'evaluation': r'(évaluation|examen|note|contrôle)',
        'orientation': r'(orientation|conseil|guidance)',
        'ressource': r'(ressource|matériel|support)',
        'technologie': r'(technologie|outil|logiciel|plateforme)'
    }
    
    # Intent patterns
    INTENT_PATTERNS = {
        'list': r'(liste|tous|toutes|montrer|afficher|quels|quelles)',
        'count': r'(combien|nombre|total|statistique)',
        'filter': r'(par|selon|filtrer|où|qui|avec)',
        'search': r'(rechercher|trouver|chercher)',
        'top': r'(meilleur|top|premier|classement|rang)'
    }
    
    def match_intent(self, question):
        """Detect intent from question"""
        q_lower = question.lower()
        for intent, pattern in self.INTENT_PATTERNS.items():
            if re.search(pattern, q_lower):
                return intent
        return 'list'
    
    def match_entities(self, question):
        """Detect entities from question"""
        q_lower = question.lower()
        entities = []
        for entity, pattern in self.ENTITY_PATTERNS.items():
            if re.search(pattern, q_lower):
                entities.append(entity)
        return entities
    
    def generate_query(self, question):
        """Generate SPARQL query from template based on question"""
        entities = self.match_entities(question)
        intent = self.match_intent(question)
        
        if not entities:
            return None
        
        # Primary entity
        primary_entity = entities[0]
        
        # Generate query based on entity and intent
        if primary_entity == 'universite':
            if intent == 'list':
                return self._query_universities_list()
            elif intent == 'count':
                return self._query_universities_count()
            elif intent == 'top':
                return self._query_universities_top_rated()
            else:
                return self._query_universities_list()
        
        elif primary_entity == 'specialite':
            if intent == 'list':
                return self._query_specialites_list()
            elif intent == 'count':
                return self._query_specialites_count()
            else:
                return self._query_specialites_list()
        
        elif primary_entity == 'cours':
            return self._query_cours_list()
        
        elif primary_entity == 'personne':
            return self._query_personnes_list()
        
        elif primary_entity == 'projet':
            return self._query_projets_list()
        
        # Default fallback
        return self._query_universities_list()
    
    def _query_universities_list(self):
        return f"""
        PREFIX ont: <{self.PREFIX}>
        SELECT ?universite ?nomUniversite ?ville ?pays ?rangNational ?nombreEtudiants
        WHERE {{
            ?universite a ont:Universite .
            OPTIONAL {{ ?universite ont:nomUniversite ?nomUniversite . }}
            OPTIONAL {{ ?universite ont:ville ?ville . }}
            OPTIONAL {{ ?universite ont:pays ?pays . }}
            OPTIONAL {{ ?universite ont:rangNational ?rangNational . }}
            OPTIONAL {{ ?universite ont:nombreEtudiants ?nombreEtudiants . }}
        }}
        ORDER BY ?nomUniversite
        LIMIT 50
        """
    
    def _query_universities_count(self):
        return f"""
        PREFIX ont: <{self.PREFIX}>
        SELECT (COUNT(DISTINCT ?universite) as ?total)
        WHERE {{
            ?universite a ont:Universite .
        }}
        """
    
    def _query_universities_top_rated(self):
        return f"""
        PREFIX ont: <{self.PREFIX}>
        SELECT ?universite ?nomUniversite ?ville ?pays ?rangNational
        WHERE {{
            ?universite a ont:Universite .
            ?universite ont:nomUniversite ?nomUniversite .
            ?universite ont:rangNational ?rangNational .
            FILTER(xsd:integer(?rangNational) <= 5)
            OPTIONAL {{ ?universite ont:ville ?ville . }}
            OPTIONAL {{ ?universite ont:pays ?pays . }}
        }}
        ORDER BY xsd:integer(?rangNational)
        LIMIT 10
        """
    
    def _query_specialites_list(self):
        return f"""
        PREFIX ont: <{self.PREFIX}>
        SELECT ?specialite ?nomSpecialite ?codeSpecialite ?niveauDiplome ?universite ?nomUniversite
        WHERE {{
            ?specialite a ont:Specialite .
            OPTIONAL {{ ?specialite ont:nomSpecialite ?nomSpecialite . }}
            OPTIONAL {{ ?specialite ont:codeSpecialite ?codeSpecialite . }}
            OPTIONAL {{ ?specialite ont:niveauDiplome ?niveauDiplome . }}
            OPTIONAL {{
                ?specialite ont:estOffertePar ?universite .
                ?universite ont:nomUniversite ?nomUniversite .
            }}
        }}
        ORDER BY ?nomSpecialite
        LIMIT 50
        """
    
    def _query_specialites_count(self):
        return f"""
        PREFIX ont: <{self.PREFIX}>
        SELECT (COUNT(DISTINCT ?specialite) as ?total)
        WHERE {{
            ?specialite a ont:Specialite .
        }}
        """
    
    def _query_cours_list(self):
        return f"""
        PREFIX ont: <{self.PREFIX}>
        SELECT ?cours ?intitule ?codeCours ?creditsECTS ?semestre
        WHERE {{
            ?cours a ont:Cours .
            OPTIONAL {{ ?cours ont:intitule ?intitule . }}
            OPTIONAL {{ ?cours ont:codeCours ?codeCours . }}
            OPTIONAL {{ ?cours ont:creditsECTS ?creditsECTS . }}
            OPTIONAL {{ ?cours ont:semestre ?semestre . }}
        }}
        ORDER BY ?intitule
        LIMIT 50
        """
    
    def _query_personnes_list(self):
        return f"""
        PREFIX ont: <{self.PREFIX}>
        SELECT ?personne ?nom ?prenom ?type ?email
        WHERE {{
            ?personne a ?type .
            FILTER(?type IN (ont:Personne, ont:Etudiant, ont:Enseignant, ont:Administrateur))
            OPTIONAL {{ ?personne ont:nom ?nom . }}
            OPTIONAL {{ ?personne ont:prenom ?prenom . }}
            OPTIONAL {{ ?personne ont:email ?email . }}
        }}
        ORDER BY ?nom ?prenom
        LIMIT 50
        """
    
    def _query_projets_list(self):
        return f"""
        PREFIX ont: <{self.PREFIX}>
        SELECT ?projet ?titreProjet ?typeProjet ?anneeRealisation ?universite ?nomUniversite
        WHERE {{
            ?projet a ont:ProjetAcademique .
            OPTIONAL {{ ?projet ont:titreProjet ?titreProjet . }}
            OPTIONAL {{ ?projet ont:typeProjet ?typeProjet . }}
            OPTIONAL {{ ?projet ont:anneeRealisation ?anneeRealisation . }}
            OPTIONAL {{
                ?projet ont:estOrganisePar ?universite .
                ?universite ont:nomUniversite ?nomUniversite .
            }}
        }}
        ORDER BY DESC(?anneeRealisation)
        LIMIT 50
        """

# Global instance
template_engine = SearchTemplateEngine()




