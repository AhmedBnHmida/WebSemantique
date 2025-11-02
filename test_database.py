from sparql_utils import SPARQLUtils

sparql_util = SPARQLUtils()

# Check what classes exist
query = """
SELECT DISTINCT ?class WHERE { 
    ?s a ?class . 
    FILTER(STRSTARTS(STR(?class), "http://webprotege.stanford.edu/"))
} 
LIMIT 10
"""

results = sparql_util.execute_query(query)
print("WebProtege classes:")
for r in results:
    class_name = r.get('class', 'Unknown')
    if isinstance(class_name, str):
        print(f"- {class_name.split('/')[-1]}")
    else:
        print(f"- {class_name}")

# Check events specifically
query2 = """
PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
SELECT DISTINCT ?class WHERE { 
    ?s a ?class . 
    ?s eco:eventTitle ?title .
} 
LIMIT 5
"""

results2 = sparql_util.execute_query(query2)
print("\nClasses with eventTitle property:")
for r in results2:
    print(f"- {r.get('class', 'Unknown')}")

# Check actual event data
query3 = """
PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
SELECT ?s ?title WHERE { 
    ?s eco:eventTitle ?title .
} 
LIMIT 5
"""

results3 = sparql_util.execute_query(query3)
print("\nActual events:")
for r in results3:
    print(f"- {r.get('title', 'No title')} (Subject: {r.get('s', 'Unknown')})")
