#!/usr/bin/env python3
"""
Test script for TALN + Gemini SPARQL Integration
This script demonstrates the new pipeline functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.taln_service import TALNService
from modules.gemini_sparql_service import GeminiSPARQLTransformer

def test_taln_analysis():
    """Test TALN analysis functionality"""
    print("🧪 Testing TALN Analysis Service")
    print("=" * 50)
    
    taln_service = TALNService()
    
    test_questions = [
        "Quelles sont les campagnes actives ?",
        "Montre-moi les événements à venir à Paris",
        "Combien de volontaires ont des compétences en environnement ?",
        "Quels sont les assignements approuvés ?",
        "Montre-moi les certifications par points",
        "Quelles réservations sont confirmées ?"
    ]
    
    for question in test_questions:
        print(f"\n📝 Question: {question}")
        print("-" * 30)
        
        try:
            analysis = taln_service.analyze_question(question)
            
            print(f"🔍 Entités détectées: {len(analysis['entities'])}")
            for entity in analysis['entities']:
                print(f"  - {entity['text']} ({entity['ontology_class']}) - Confiance: {entity['confidence']:.2f}")
            
            print(f"🎯 Intention: {analysis['intent']['primary_intent']} ({analysis['intent']['query_type']})")
            
            if analysis['temporal_info']['relative_time']:
                print(f"⏰ Temps: {analysis['temporal_info']['relative_time']}")
            
            if analysis['location_info']['locations']:
                print(f"📍 Lieux: {', '.join(analysis['location_info']['locations'])}")
            
            print(f"📊 Confiance globale: {analysis['confidence_scores']['overall_confidence']:.2f}")
            
        except Exception as e:
            print(f"❌ Erreur: {e}")

def test_gemini_integration():
    """Test Gemini SPARQL generation with TALN analysis"""
    print("\n\n🤖 Testing Gemini SPARQL Generation")
    print("=" * 50)
    
    try:
        gemini_transformer = GeminiSPARQLTransformer()
        
        # Test with a sample TALN analysis
        sample_analysis = {
            "original_question": "Quelles sont les campagnes actives ?",
            "entities": [
                {
                    "text": "campagnes",
                    "type": "Campaign",
                    "ontology_class": "eco:Campaign",
                    "confidence": 0.9
                }
            ],
            "intent": {
                "primary_intent": "list",
                "query_type": "list"
            },
            "temporal_info": {
                "relative_time": None,
                "time_expressions": []
            },
            "location_info": {
                "locations": []
            },
            "keywords": [
                {"text": "campagnes", "importance": 0.8},
                {"text": "actives", "importance": 0.7}
            ],
            "relationships": [],
            "confidence_scores": {
                "overall_confidence": 0.85
            }
        }
        
        print("📝 Sample TALN Analysis:")
        print(f"  Question: {sample_analysis['original_question']}")
        print(f"  Entities: {len(sample_analysis['entities'])}")
        print(f"  Intent: {sample_analysis['intent']['primary_intent']}")
        
        print("\n🔧 Generating SPARQL Query...")
        sparql_query = gemini_transformer.transform_taln_analysis_to_sparql(sample_analysis)
        
        print("\n✅ Generated SPARQL Query:")
        print("-" * 30)
        print(sparql_query)
        
    except Exception as e:
        print(f"❌ Erreur Gemini: {e}")

def test_pipeline():
    """Test the complete pipeline"""
    print("\n\n🔄 Testing Complete Pipeline")
    print("=" * 50)
    
    try:
        taln_service = TALNService()
        gemini_transformer = GeminiSPARQLTransformer()
        
        test_question = "Montre-moi les événements à venir à Paris"
        
        print(f"📝 Question: {test_question}")
        
        # Step 1: TALN Analysis
        print("\n📝 Step 1: TALN Analysis...")
        taln_analysis = taln_service.analyze_question(test_question)
        print(f"✅ Entities: {len(taln_analysis['entities'])}")
        print(f"✅ Intent: {taln_analysis['intent']['primary_intent']}")
        
        # Step 2: Gemini SPARQL Generation
        print("\n🤖 Step 2: Gemini SPARQL Generation...")
        sparql_query = gemini_transformer.transform_taln_analysis_to_sparql(taln_analysis)
        print(f"✅ Query generated: {len(sparql_query)} characters")
        
        print("\n📋 Generated SPARQL Query:")
        print("-" * 30)
        print(sparql_query)
        
    except Exception as e:
        print(f"❌ Pipeline Error: {e}")

if __name__ == "__main__":
    print("🚀 TALN + Gemini SPARQL Integration Test")
    print("=" * 60)
    
    # Test individual components
    test_taln_analysis()
    test_gemini_integration()
    test_pipeline()
    
    print("\n\n✅ All tests completed!")
    print("\n📚 Next steps:")
    print("1. Set up your GEMINI_API_KEY in environment variables")
    print("2. Optionally configure TALN_API_KEY for enhanced analysis")
    print("3. Start the Flask backend: python app.py")
    print("4. Test the frontend at http://localhost:3000")
    print("5. Try the new semantic search with various questions!")
