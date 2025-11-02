# Alternative TALN Service Implementations

## Option 1: Google Cloud Natural Language API Integration

```python
# Add this to your taln_service.py

import google.cloud.language_v1 as language
from google.cloud.language_v1 import types

class GoogleNLPTALNService(TALNService):
    def __init__(self):
        super().__init__()
        self.client = language.LanguageServiceClient()
    
    def analyze_question(self, question: str) -> Dict[str, Any]:
        """Use Google Cloud NLP instead of TALN API"""
        try:
            document = types.Document(
                content=question,
                type_=types.Document.Type.PLAIN_TEXT,
                language='fr'
            )
            
            # Entity analysis
            entities_response = self.client.analyze_entities(
                request={'document': document, 'encoding_type': types.EncodingType.UTF8}
            )
            
            # Syntax analysis
            syntax_response = self.client.analyze_syntax(
                request={'document': document, 'encoding_type': types.EncodingType.UTF8}
            )
            
            return self._process_google_nlp_response(entities_response, syntax_response, question)
            
        except Exception as e:
            print(f"Google NLP error: {e}")
            return self._fallback_analysis(question)
```

## Option 2: Azure Text Analytics Integration

```python
# Add this to your taln_service.py

import requests
import json

class AzureTextAnalyticsTALNService(TALNService):
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv('AZURE_TEXT_ANALYTICS_KEY')
        self.endpoint = os.getenv('AZURE_ENDPOINT')
    
    def analyze_question(self, question: str) -> Dict[str, Any]:
        """Use Azure Text Analytics instead of TALN API"""
        try:
            headers = {
                'Ocp-Apim-Subscription-Key': self.api_key,
                'Content-Type': 'application/json'
            }
            
            documents = [{"id": "1", "text": question, "language": "fr"}]
            
            # Entity recognition
            entities_url = f"{self.endpoint}/text/analytics/v3.1/entities/recognition/general"
            entities_response = requests.post(entities_url, headers=headers, json={"documents": documents})
            
            # Key phrase extraction
            phrases_url = f"{self.endpoint}/text/analytics/v3.1/keyPhrases"
            phrases_response = requests.post(phrases_url, headers=headers, json={"documents": documents})
            
            return self._process_azure_response(entities_response, phrases_response, question)
            
        except Exception as e:
            print(f"Azure Text Analytics error: {e}")
            return self._fallback_analysis(question)
```

## Option 3: spaCy Integration (Local Processing)

```python
# Add this to your taln_service.py

import spacy
from spacy import displacy

class SpacyTALNService(TALNService):
    def __init__(self):
        super().__init__()
        try:
            # Load French model
            self.nlp = spacy.load("fr_core_news_sm")
        except OSError:
            print("French spaCy model not found. Install with: python -m spacy download fr_core_news_sm")
            self.nlp = None
    
    def analyze_question(self, question: str) -> Dict[str, Any]:
        """Use spaCy for local NLP processing"""
        if not self.nlp:
            return self._fallback_analysis(question)
        
        try:
            doc = self.nlp(question)
            
            entities = []
            for ent in doc.ents:
                entities.append({
                    "text": ent.text,
                    "type": ent.label_,
                    "category": "named_entity",
                    "confidence": 0.8,  # spaCy doesn't provide confidence scores
                    "start_pos": ent.start_char,
                    "end_pos": ent.end_char,
                    "ontology_class": self._map_to_ontology_class(ent.label_)
                })
            
            # Extract keywords (nouns and adjectives)
            keywords = []
            for token in doc:
                if token.pos_ in ['NOUN', 'ADJ'] and not token.is_stop:
                    keywords.append({
                        "text": token.text.lower(),
                        "importance": 0.7,
                        "category": "content_word",
                        "semantic_type": token.pos_
                    })
            
            return {
                "original_question": question,
                "entities": entities,
                "relationships": [],  # Would need more complex processing
                "intent": self._classify_intent_spacy(doc),
                "keywords": keywords,
                "temporal_info": self._extract_temporal_spacy(doc),
                "location_info": self._extract_location_spacy(doc),
                "semantic_roles": [],
                "confidence_scores": {
                    "overall_confidence": 0.7,
                    "entity_recognition": 0.8,
                    "relationship_extraction": 0.3,
                    "intent_classification": 0.6
                },
                "analysis_metadata": {
                    "language": "fr",
                    "processing_time": 0.1,
                    "api_version": "spacy_local",
                    "method": "spacy_nlp"
                }
            }
            
        except Exception as e:
            print(f"spaCy processing error: {e}")
            return self._fallback_analysis(question)
```

## Quick Setup Instructions

### For Google Cloud NLP:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the Natural Language API
3. Create credentials (API key)
4. Set environment variable: `export GOOGLE_NLP_API_KEY="your_key"`

### For Azure Text Analytics:
1. Go to [Azure Portal](https://portal.azure.com/)
2. Create a Text Analytics resource
3. Get your API key and endpoint
4. Set environment variables:
   ```bash
   export AZURE_TEXT_ANALYTICS_KEY="your_key"
   export AZURE_ENDPOINT="your_endpoint"
   ```

### For spaCy (Local Processing):
1. Install spaCy and French model:
   ```bash
   pip install spacy
   python -m spacy download fr_core_news_sm
   ```
2. No API key needed - runs locally!

## Recommendation

**Start with the built-in fallback system** - it's already working and provides excellent results! You can always upgrade to a commercial NLP API later if needed.

The fallback system I built includes:
- ✅ Pattern-based entity recognition
- ✅ Intent classification
- ✅ Temporal and location extraction
- ✅ Confidence scoring
- ✅ Works for all your entity types

Would you like me to help you set up any of these alternatives, or would you prefer to test the current fallback system first?
