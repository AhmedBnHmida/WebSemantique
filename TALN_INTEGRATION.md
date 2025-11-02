# TALN + Gemini SPARQL Integration

## Overview

This implementation integrates a TALN (Text Analysis and Language Processing) API with Google's Gemini AI to create a dynamic SPARQL query generation system. Instead of using predefined queries, the system now:

1. **TALN Analysis**: Extracts entities, relationships, intent, and semantic information from natural language questions
2. **Gemini Generation**: Uses the structured TALN analysis to generate precise SPARQL queries
3. **Dynamic Queries**: Creates queries tailored to the specific question and detected entities

## Architecture

```
User Question → TALN Service → Gemini AI → SPARQL Query → Fuseki → Results
```

### Components

1. **TALN Service** (`backend/modules/taln_service.py`)
   - Analyzes natural language questions
   - Extracts entities, relationships, intent, temporal info, location info
   - Maps entities to ontology classes
   - Provides fallback analysis when TALN API is unavailable

2. **Gemini SPARQL Transformer** (`backend/modules/gemini_sparql_service.py`)
   - Enhanced to work with TALN analysis results
   - Generates SPARQL queries based on structured analysis
   - Maintains backward compatibility with direct question processing

3. **Search Endpoints** (`backend/modules/search.py`)
   - `/api/search` - Main TALN → Gemini → SPARQL pipeline
   - `/api/search/ai` - Direct Gemini processing (fallback)
   - `/api/search/hybrid` - Combines both approaches with automatic fallback

## Features

### TALN Analysis Capabilities
- **Entity Recognition**: Detects Event, Location, User, Campaign, Resource, Volunteer, Assignment, Certification, Reservation, Blog entities
- **Intent Classification**: Identifies user intent (list, count, filter, search, details)
- **Temporal Analysis**: Extracts time expressions and relative time information
- **Location Analysis**: Identifies geographical entities and spatial relations
- **Relationship Extraction**: Finds relationships between entities
- **Confidence Scoring**: Provides confidence levels for analysis components

### Gemini SPARQL Generation
- **Structured Prompts**: Uses TALN analysis to create precise prompts
- **Ontology-Aware**: Generates queries using proper ontology classes and properties
- **Dynamic Filtering**: Creates appropriate FILTER clauses based on detected entities
- **Optimized Queries**: Includes LIMIT, ORDER BY, and OPTIONAL clauses as needed

### Frontend Enhancements
- **TALN Analysis Display**: Shows detected entities, intent, and confidence scores
- **Pipeline Information**: Displays processing statistics and method used
- **Enhanced Results**: Better visualization of query results and analysis

## Configuration

### Environment Variables

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional (will use fallback if not provided)
TALN_API_KEY=your_taln_api_key_here
TALN_API_URL=https://api.taln.fr/v1
```

### Fallback Behavior

If TALN API is not available or configured, the system automatically falls back to:
1. Pattern-based entity extraction
2. Keyword-based intent classification
3. Simple temporal and location detection
4. Direct Gemini processing

## Usage Examples

### Entity Detection
**Question**: "Quelles sont les campagnes actives ?"
**TALN Analysis**:
- Entities: [{"text": "campagnes", "type": "Campaign", "ontology_class": "eco:Campaign"}]
- Intent: {"primary_intent": "list", "query_type": "list"}
- Keywords: ["campagnes", "actives"]

### Temporal Queries
**Question**: "Montre-moi les événements à venir à Paris"
**TALN Analysis**:
- Entities: [{"text": "événements", "type": "Event"}, {"text": "Paris", "type": "Location"}]
- Intent: {"primary_intent": "list", "query_type": "list"}
- Temporal: {"relative_time": "future"}
- Location: {"locations": ["paris"]}

### Complex Queries
**Question**: "Combien de volontaires ont des compétences en environnement ?"
**TALN Analysis**:
- Entities: [{"text": "volontaires", "type": "Volunteer"}, {"text": "compétences", "type": "Skill"}]
- Intent: {"primary_intent": "count", "query_type": "count"}
- Keywords: ["volontaires", "compétences", "environnement"]

## Benefits

1. **Dynamic Query Generation**: No more predefined queries - every question gets a tailored SPARQL query
2. **Better Entity Recognition**: TALN provides more accurate entity detection than simple keyword matching
3. **Intent Understanding**: System understands what the user wants to do (list, count, filter, etc.)
4. **Semantic Analysis**: Extracts relationships and semantic roles for more precise queries
5. **Confidence Scoring**: Provides transparency about analysis quality
6. **Fallback Support**: Graceful degradation when TALN API is unavailable
7. **Extensible**: Easy to add new entity types and analysis capabilities

## Testing

The system includes three search endpoints for testing different approaches:

1. **Main Pipeline**: `/api/search` - Full TALN → Gemini → SPARQL
2. **Direct AI**: `/api/search/ai` - Direct Gemini processing
3. **Hybrid**: `/api/search/hybrid` - Automatic fallback between methods

## Future Enhancements

- Integration with additional NLP services
- Machine learning-based query optimization
- Multi-language support
- Query caching and optimization
- Advanced relationship extraction
- Custom entity training for domain-specific entities
