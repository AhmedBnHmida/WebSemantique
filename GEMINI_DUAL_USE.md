# Gemini Dual-Use Pipeline

## Overview

This implementation uses **Gemini API twice** in the pipeline:
1. **First Gemini Call**: NLP Analysis (replaces TALN API)
2. **Second Gemini Call**: SPARQL Generation (from structured analysis)

## Architecture

```
User Question 
    ↓
Gemini API (Call 1) → NLP Analysis (entities, intent, temporal, location)
    ↓
Gemini API (Call 2) → SPARQL Query Generation
    ↓
SPARQL Execution → Results
```

## How It Works

### Step 1: Gemini NLP Analysis

The `GeminiTALNService` class uses Gemini to extract structured information:

```python
from modules.taln_service import GeminiTALNService

# Initialize service (uses GEMINI_API_KEY)
taln_service = GeminiTALNService()

# Analyze question
analysis = taln_service.analyze_question("Quelles sont les campagnes actives ?")
```

**Gemini extracts:**
- Entities (Events, Locations, Campaigns, Volunteers, etc.)
- Intent (list, count, filter, search, details)
- Temporal information (future, past, present)
- Location information (cities, places)
- Keywords and relationships

**Returns structured JSON:**
```json
{
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
    "relative_time": null,
    "time_expressions": []
  },
  "location_info": {
    "locations": []
  }
}
```

### Step 2: Gemini SPARQL Generation

The `GeminiSPARQLTransformer` uses the structured analysis to generate SPARQL:

```python
from modules.gemini_sparql_service import GeminiSPARQLTransformer

gemini_transformer = GeminiSPARQLTransformer()

# Generate SPARQL from analysis
sparql_query = gemini_transformer.transform_taln_analysis_to_sparql(analysis)
```

**Gemini generates precise SPARQL query:**
```sparql
PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
SELECT ?campaignName ?campaignDescription ?campaignStatus
WHERE {
  ?campaign a eco:Campaign .
  ?campaign eco:campaignName ?campaignName .
  ?campaign eco:campaignStatus ?campaignStatus .
  FILTER(LCASE(STR(?campaignStatus)) = "active" || LCASE(STR(?campaignStatus)) = "actif")
  OPTIONAL { ?campaign eco:campaignDescription ?campaignDescription }
}
ORDER BY ?campaignName
LIMIT 50
```

### Step 3: Execute SPARQL

The generated SPARQL query is executed against the Fuseki endpoint:

```python
from sparql_utils import sparql_utils

results = sparql_utils.execute_query(sparql_query)
```

## Configuration

### Environment Variables

You only need **ONE API key**:

```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

### Automatic Selection

The system automatically uses `GeminiTALNService` if `GEMINI_API_KEY` is available:

```python
# In backend/modules/search.py
if gemini_api_key:
    taln_service = GeminiTALNService()  # Uses Gemini for NLP
else:
    taln_service = TALNService()  # Uses pattern-based fallback
```

## Benefits

1. **Single API Key**: Only need Gemini API key (no TALN API needed)
2. **Better Accuracy**: Gemini provides better NLP analysis than pattern matching
3. **Consistent Pipeline**: Both steps use the same AI model
4. **Structured Analysis**: First call extracts structured data, second call uses it
5. **Fallback Support**: Falls back to pattern matching if Gemini fails

## API Endpoint

The `/api/search` endpoint uses this pipeline:

```bash
POST /api/search
Content-Type: application/json

{
  "question": "Quelles sont les campagnes actives ?"
}
```

**Response:**
```json
{
  "results": [...],
  "taln_analysis": {
    "entities": [...],
    "intent": {...}
  },
  "sparql_query": "PREFIX eco: ...",
  "pipeline_info": {
    "method": "gemini_taln",
    "status": "success",
    "results_count": 5
  }
}
```

## Testing

Test the pipeline:

```bash
cd backend
python test_taln_integration.py
```

Or test with curl:

```bash
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{"question": "Quelles sont les campagnes actives ?"}'
```

## Cost Considerations

- **Two Gemini API calls per search**
- First call: NLP analysis (~500-1000 tokens)
- Second call: SPARQL generation (~500-1500 tokens)
- Total: ~1000-2500 tokens per search
- Gemini Flash models are very cost-effective

## Fallback Behavior

If Gemini API fails or is unavailable:
1. Falls back to pattern-based entity extraction
2. Still generates SPARQL using Gemini (or template engine)
3. System continues to work

## Comparison

| Feature | Pattern Matching | Gemini NLP |
|---------|-----------------|------------|
| Accuracy | Medium | High |
| Entity Detection | Keyword-based | Semantic understanding |
| Intent Classification | Pattern-based | Context-aware |
| Cost | Free | API costs |
| Speed | Fast | Slightly slower |
| Setup | None | API key needed |

