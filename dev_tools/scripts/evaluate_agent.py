# scripts/evaluate_agent.py
import sys
import os
import time

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.query_processor import QueryProcessor

queries = [
    "Qual é o preço do produto 369947?",
    "Liste os 10 produtos mais caros da categoria 'BRINQUEDOS'.",
    "gere os dez tecidos mais vendidos."
]

def main():
    query_processor = QueryProcessor()
    for query in queries:
        print(f"--- Running query: {query} ---")
        response = query_processor.process_query(query)
        print(f"Response: {response}")
        print("-------------------------------------\n")
        time.sleep(60) # Add a 60-second delay between queries

if __name__ == "__main__":
    main()
