import requests
import json

BASE_URL = "http://localhost:5000/api"

def test_search(question, endpoint="/search"):
    """Test a search endpoint"""
    try:
        response = requests.post(
            f"{BASE_URL}{endpoint}",
            json={"question": question},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS: {endpoint}")
            print(f"Question: {question}")
            print(f"Search Type: {data.get('search_type', 'N/A')}")
            print(f"Results Count: {data.get('results_count', len(data.get('results', [])))}")
            print(f"SPARQL Query: {data.get('sparql_query', 'N/A')[:100]}...")
            print("---")
        else:
            print(f"❌ ERROR {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Connection error: {e}")

# Test different types of questions
test_questions = [
    "Show me all events",
    "Find locations in Boston", 
    "What campaigns are active?",
    "Show me available locations",
    "Events in New York next week",
    "Educational events about climate change"
]

print("🧪 Testing Semantic Search API...\n")

# Test regular search
print("=== REGULAR SEARCH ===")
for question in test_questions[:3]:
    test_search(question, "/search")

# Test AI search
print("\n=== AI SEARCH ===")
for question in test_questions[3:5]:
    test_search(question, "/search/ai")

# Test hybrid search  
print("\n=== HYBRID SEARCH ===")
for question in test_questions[4:6]:
    test_search(question, "/search/hybrid")