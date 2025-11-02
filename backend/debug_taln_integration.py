#!/usr/bin/env python3
"""
Debug Test Script for TALN + Gemini Integration
This script will help debug the pipeline issues
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.taln_service import TALNService
from modules.gemini_sparql_service import GeminiSPARQLTransformer

def test_debug_pipeline():
    """Test the complete pipeline with debugging"""
    print("🔍 DEBUGGING TALN + GEMINI PIPELINE")
    print("=" * 60)
    
    # Initialize services
    print("🚀 Initializing services...")
    taln_service = TALNService()
    gemini_transformer = GeminiSPARQLTransformer()
    
    # Test question
    test_question = "Tous les événements"
    print(f"\n📝 Testing with question: '{test_question}'")
    print("-" * 40)
    
    # Step 1: TALN Analysis
    print("\n🔍 STEP 1: TALN Analysis")
    print("-" * 20)
    taln_analysis = taln_service.analyze_question(test_question)
    
    print(f"\n📊 TALN Analysis Results:")
    print(f"  - Original question: {taln_analysis.get('original_question')}")
    print(f"  - Entities found: {len(taln_analysis.get('entities', []))}")
    for entity in taln_analysis.get('entities', []):
        print(f"    * {entity['text']} -> {entity['ontology_class']} (confidence: {entity['confidence']})")
    
    print(f"  - Intent: {taln_analysis.get('intent', {}).get('primary_intent')}")
    print(f"  - Confidence: {taln_analysis.get('confidence_scores', {}).get('overall_confidence')}")
    
    # Step 2: Gemini SPARQL Generation
    print(f"\n🤖 STEP 2: Gemini SPARQL Generation")
    print("-" * 30)
    sparql_query = gemini_transformer.transform_taln_analysis_to_sparql(taln_analysis)
    
    print(f"\n📋 Generated SPARQL Query:")
    print("-" * 25)
    print(sparql_query)
    
    # Analyze the query
    print(f"\n🔍 Query Analysis:")
    print(f"  - Length: {len(sparql_query)} characters")
    print(f"  - Contains webprotege: prefix: {'webprotege:' in sparql_query}")
    print(f"  - Contains eco: prefix: {'eco:' in sparql_query}")
    print(f"  - Contains Event class: {'webprotege:Event' in sparql_query}")
    print(f"  - Contains Volunteer class: {'webprotege:Volunteer' in sparql_query}")
    print(f"  - Contains Assignment class: {'webprotege:Assignment' in sparql_query}")
    
    return sparql_query

def test_specific_questions():
    """Test with specific questions to debug entity detection"""
    print(f"\n\n🧪 TESTING SPECIFIC QUESTIONS")
    print("=" * 50)
    
    taln_service = TALNService()
    
    test_questions = [
        "Tous les événements",
        "Montre-moi les volontaires",
        "Quels sont les assignements ?",
        "Combien de campagnes actives ?",
        "Les certifications par points"
    ]
    
    for question in test_questions:
        print(f"\n📝 Question: '{question}'")
        print("-" * 30)
        
        analysis = taln_service.analyze_question(question)
        
        print(f"🎯 Entities detected:")
        for entity in analysis.get('entities', []):
            print(f"  - {entity['text']} -> {entity['ontology_class']}")
        
        print(f"🧠 Intent: {analysis.get('intent', {}).get('primary_intent')}")
        print(f"📊 Confidence: {analysis.get('confidence_scores', {}).get('overall_confidence')}")

if __name__ == "__main__":
    print("🚀 TALN + Gemini Debug Test")
    print("=" * 40)
    
    # Test the main pipeline
    sparql_query = test_debug_pipeline()
    
    # Test specific questions
    test_specific_questions()
    
    print(f"\n\n✅ Debug test completed!")
    print(f"\n📚 Next steps:")
    print(f"1. Check the console output above for debug information")
    print(f"2. Verify that entities are being detected correctly")
    print(f"3. Check that Gemini is generating proper SPARQL queries")
    print(f"4. Look for any error messages in the debug output")
