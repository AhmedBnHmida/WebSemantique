# Alternative TALN Service Implementations

## ⚠️ IMPORTANT: TALN API is NOT a Real Service

**TL;DR:** The "TALN API" referenced in the code (`https://api.taln.fr/v1`) is **NOT a real, publicly available service**. There is **NO website** to get an API key from, and **NO API key to obtain**.

### What is TALN?

"TALN" stands for "Text Analysis and Language Processing" - it's a **conceptual placeholder** in the code. The system was designed to potentially integrate with an NLP service, but:

- ❌ **No real TALN API exists** at `api.taln.fr`
- ❌ **No website** to sign up for an API key
- ❌ **No service** to create an account with
- ✅ **The system works perfectly** without it using the built-in fallback

### Current Status

Your system **already works** using a built-in fallback mechanism that:
- ✅ Detects entities using pattern matching
- ✅ Classifies user intent
- ✅ Extracts temporal and location information
- ✅ Requires NO API keys or external services

### Why Alternatives?

If you want **more advanced NLP capabilities** than the fallback provides, you can use one of these **real, available services** instead:

---

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
3. **✅ Completely free, no credit card required**

---

## Option 4: Hugging Face Inference API (FREE - No Credit Card)

**✅ FREE - No credit card required**
- 10,000 free tokens per month
- Access to thousands of pre-trained NLP models
- Simple API calls

```python
# Add this to your taln_service.py

import requests
import os

class HuggingFaceTALNService(TALNService):
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv('HUGGINGFACE_API_KEY')  # Free, no credit card needed
        self.base_url = "https://api-inference.huggingface.co/models"
        
        # Use a French NER model
        self.ner_model = "Jean-Baptiste/camembert-ner"  # French Named Entity Recognition
    
    def analyze_question(self, question: str) -> Dict[str, Any]:
        """Use Hugging Face Inference API for free NLP"""
        if not self.api_key:
            return self._fallback_analysis(question)
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Named Entity Recognition
            ner_response = requests.post(
                f"{self.base_url}/{self.ner_model}",
                headers=headers,
                json={"inputs": question}
            )
            
            if ner_response.status_code == 200:
                entities = ner_response.json()
                return self._process_huggingface_response(entities, question)
            else:
                return self._fallback_analysis(question)
                
        except Exception as e:
            print(f"Hugging Face API error: {e}")
            return self._fallback_analysis(question)
```

**Setup:**
1. Go to [Hugging Face](https://huggingface.co/)
2. Create a free account (no credit card)
3. Go to Settings → Access Tokens
4. Create a new token
5. Set environment variable: `export HUGGINGFACE_API_KEY="your_token"`

---

## Option 5: APILayer NLP API (FREE - No Credit Card)

**✅ FREE - No credit card required**
- 100 requests per month free
- Simple REST API

**Setup:**
1. Go to [APILayer NLP API](https://apilayer.com/marketplace/nlp-api)
2. Sign up for free (no credit card)
3. Get your API key
4. Set environment variable: `export APILAYER_NLP_KEY="your_key"`

---

## Recommendation

### ✅ **Free NLP Options (No Credit Card Required)**

**Best options for FREE NLP without credit card:**

1. **⭐ spaCy (Recommended)**
   - ✅ **100% FREE** - No credit card, no API key
   - ✅ Runs locally on your computer
   - ✅ No usage limits
   - ✅ Good French language support
   - Setup: `pip install spacy && python -m spacy download fr_core_news_sm`

2. **Hugging Face Inference API**
   - ✅ **FREE** - No credit card required
   - ✅ 10,000 tokens per month free
   - ✅ Access to thousands of NLP models
   - Setup: Sign up at [huggingface.co](https://huggingface.co/) → Get free token

3. **APILayer NLP API**
   - ✅ **FREE** - No credit card required
   - ✅ 100 requests per month free
   - Setup: Sign up at [apilayer.com](https://apilayer.com/marketplace/nlp-api)

### ❌ **Paid Services (Require Credit Card)**

- **Google Cloud NLP** - Requires credit card (free tier available)
- **Azure Text Analytics** - Requires credit card (free tier available)

### 🎯 **My Recommendation**

**Start with spaCy** - it's the best free option:
- No signup required
- No API keys needed
- No credit card required
- No usage limits
- Works offline
- Great for French language processing

### How to Get Started

1. **Option 1: Use current fallback** - Already works, no setup needed!
2. **Option 2: Install spaCy** (Best free upgrade):
   ```bash
   pip install spacy
   python -m spacy download fr_core_news_sm
   ```
3. **Option 3: Use Hugging Face** - Free API, 10k tokens/month
4. **Option 4: Use APILayer** - Free API, 100 requests/month

**Bottom line:** You have multiple FREE options without credit card! spaCy is the best choice for local processing. 🎉
