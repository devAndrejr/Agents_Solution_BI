# scripts/generate_embeddings.py
import json
import os
import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Constants ---
CATALOG_PATH = os.path.join(os.getcwd(), "data", "catalog_focused.json")
VECTOR_STORE_PATH = os.path.join(os.getcwd(), "data", "vector_store.pkl")
MODEL_NAME = 'all-MiniLM-L6-v2' # A good starting model

def generate_embeddings():
    """
    Loads the data catalog, generates embeddings for column descriptions,
    and saves them to a FAISS index and a pickle file.
    """
    logging.info("Starting embedding generation process...")

    # --- 1. Load Data Catalog ---
    try:
        with open(CATALOG_PATH, 'r', encoding='utf-8') as f:
            catalog = json.load(f)
        logging.info(f"Successfully loaded data catalog from {CATALOG_PATH}")
    except FileNotFoundError:
        logging.error(f"Data catalog not found at {CATALOG_PATH}. Aborting.")
        return
    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON from {CATALOG_PATH}. Aborting.")
        return

    # --- 2. Create Descriptive Texts ---
    logging.info("Creating descriptive texts for each column...")
    documents = []
    metadata = []
    for table in catalog:
        table_name = table.get('file_name', 'N/A')
        table_desc = table.get('description', '')
        for col_name, col_desc in table.get('column_descriptions', {}).items():
            # Create a rich description for better embedding quality
            text = f"The column '{col_name}' in the table '{table_name}' contains {col_desc}. The table itself is described as: {table_desc}"
            documents.append(text)
            metadata.append({
                'table_name': table_name,
                'column_name': col_name,
                'column_description': col_desc,
                'table_description': table_desc
            })
    
    if not documents:
        logging.warning("No column descriptions found in the catalog. No embeddings will be generated.")
        return

    logging.info(f"Generated {len(documents)} descriptive documents to be embedded.")

    # --- 3. Generate Embeddings ---
    logging.info(f"Loading SentenceTransformer model: '{MODEL_NAME}'...")
    model = SentenceTransformer(MODEL_NAME)
    logging.info("Model loaded. Generating embeddings...")
    embeddings = model.encode(documents, show_progress_bar=True)
    logging.info(f"Embeddings generated successfully. Shape: {embeddings.shape}")

    # --- 4. Create and Populate FAISS Index ---
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings, dtype=np.float32))
    logging.info(f"FAISS index created and populated with {index.ntotal} vectors.")

    # --- 5. Save to File ---
    vector_store_data = {
        'index': faiss.serialize_index(index),
        'metadata': metadata,
        'documents': documents
    }

    try:
        with open(VECTOR_STORE_PATH, 'wb') as f:
            pickle.dump(vector_store_data, f)
        logging.info(f"Vector store saved successfully to {VECTOR_STORE_PATH}")
    except Exception as e:
        logging.error(f"Failed to save vector store: {e}")

if __name__ == "__main__":
    generate_embeddings()
