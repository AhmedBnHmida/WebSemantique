from flask import Blueprint, jsonify, request
from sparql_utils import sparql_utils
from modules.taln_service import TALNService, GeminiTALNService
from modules.gemini_sparql_service import GeminiSPARQLTransformer
from modules.search_templates import template_engine
from modules.dbpedia_service import dbpedia_service
import os

search_bp = Blueprint('search', __name__)

# Initialize services
# Use GeminiTALNService if GEMINI_API_KEY is available, otherwise fallback to TALNService
gemini_api_key = os.getenv('GEMINI_API_KEY')
if gemini_api_key:
    print("✅ Using GeminiTALNService for NLP analysis (using Gemini API)")
    taln_service = GeminiTALNService()
else:
    print("⚠️ Using TALNService with pattern-based fallback (no Gemini API key)")
    taln_service = TALNService()

gemini_transformer = GeminiSPARQLTransformer()

@search_bp.route('/dbpedia/search', methods=['POST'])
def dbpedia_search():
    """Simple DBpedia search endpoint that returns a list of references"""
    try:
        data = request.get_json(force=True)
        search_text = data.get('text', '').strip()
        
        if not search_text:
            return jsonify({"error": "Search text is required"}), 400
        
        print(f"🔍 DBpedia search for: {search_text}")
        
        # Use the simplified DBpedia service
        results = dbpedia_service.search_entities(search_text)
        
        return jsonify(results)
        
    except Exception as e:
        print(f"Error in DBpedia search: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"DBpedia search failed: {str(e)}"}), 500

@search_bp.route('/search', methods=['POST'])
def semantic_search():
    """Recherche sémantique - TALN → Gemini → SPARQL pipeline"""
    try:
        data = request.get_json(force=True)
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({"error": "Question vide"}), 400
        
        print(f"🔍 Processing question: {question}")
        
        # Step 1: TALN Analysis - Extract entities, relationships, intent
        print("📝 Step 1: TALN Analysis...")
        taln_analysis = taln_service.analyze_question(question)
        print(f"✅ TALN Analysis completed. Entities: {len(taln_analysis.get('entities', []))}")
        
        # Step 2: Gemini SPARQL Generation - Generate query from TALN analysis
        print("🤖 Step 2: Gemini SPARQL Generation...")
        sparql_query = None
        method_used = "unknown"
        
        try:
            sparql_query = gemini_transformer.transform_taln_analysis_to_sparql(taln_analysis)
            method_used = "gemini_taln"
            print(f"✅ SPARQL Query generated via Gemini: {len(sparql_query)} characters")
        except Exception as e:
            print(f"⚠️ Gemini generation failed: {e}, falling back to template engine")
            sparql_query = template_engine.generate_query(question)
            method_used = "template_fallback"
            if sparql_query:
                print(f"✅ SPARQL Query generated via template: {len(sparql_query)} characters")
        
        if not sparql_query:
            return jsonify({
                "error": "Impossible de générer une requête SPARQL",
                "taln_analysis": taln_analysis,
                "pipeline_info": {
                    "method": method_used,
                    "status": "failed"
                }
            }), 500
        
        # Step 3: Execute SPARQL query
        print("⚡ Step 3: Executing SPARQL query...")
        try:
            query_results = sparql_utils.execute_query(sparql_query)
            print(f"✅ Query executed. Results: {len(query_results)}")
            
            return jsonify({
                "results": query_results,
                "taln_analysis": taln_analysis,
                "sparql_query": sparql_query,
                "pipeline_info": {
                    "method": method_used,
                    "status": "success",
                    "results_count": len(query_results)
                }
            })
        except Exception as e:
            print(f"❌ SPARQL execution failed: {str(e)}")
            return jsonify({
                "error": f"Erreur lors de l'exécution de la requête SPARQL: {str(e)}",
                "taln_analysis": taln_analysis,
                "sparql_query": sparql_query,
                "pipeline_info": {
                    "method": method_used,
                    "status": "sparql_error"
                }
            }), 500
            
    except Exception as e:
        print(f"Error in semantic search: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Erreur dans la recherche sémantique: {str(e)}"}), 500

def ai_search():
    """Recherche IA - Utilise Gemini pour générer directement une requête SPARQL"""
    try:
        data = request.get_json(force=True)
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({"error": "Question vide"}), 400
        
        # Use Gemini to generate SPARQL directly
        sparql_query = gemini_transformer.generate_sparql_from_question(question)
        
        if not sparql_query:
            return jsonify({"error": "Impossible de générer une requête SPARQL"}), 500
        
        # Execute the query
        query_results = sparql_utils.execute_query(sparql_query)
        
        return jsonify({
            "results": query_results,
            "sparql_query": sparql_query,
            "method": "direct_gemini"
        })
        
    except Exception as e:
        return jsonify({"error": f"Erreur dans la recherche IA: {str(e)}"}), 500

def hybrid_search():
    """Recherche hybride - Combine plusieurs méthodes"""
    # Implementation for future enhancement
    pass
