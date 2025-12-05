#!/usr/bin/env python
"""
Generate FAISS vector index for RAG from codebase.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import List

# Configure logging with proper encoding
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_environment():
    """Setup environment for LlamaIndex."""
    os.environ['TOKENIZERS_PARALLELISM'] = 'false'
    
    # Load .env
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        logger.error("GEMINI_API_KEY not found in environment")
        sys.exit(1)
    return api_key

def configure_llamaindex():
    """Configure LlamaIndex with Gemini."""
    try:
        from llama_index.core import Settings
        from llama_index.llms.gemini import Gemini
        from llama_index.embeddings.gemini import GeminiEmbedding
        
        # Configure LLM
        Settings.llm = Gemini(
            model="gemini-2.5-flash",
            temperature=0.3,
            max_tokens=2048
        )
        
        # Configure Embeddings
        Settings.embed_model = GeminiEmbedding(
            model_name="models/embedding-001"
        )
        
        logger.info("✅ LlamaIndex configured with Gemini 2.5 Flash")
        return True
    except Exception as e:
        logger.error(f"Failed to configure LlamaIndex: {e}")
        return False

def load_code_files(root_dir: str = ".") -> List[dict]:
    """Load Python files from codebase."""
    logger.info(f"📂 Loading Python files from {root_dir}...")
    
    code_files = []
    root_path = Path(root_dir)
    
    # Skip directories
    skip_dirs = {'.venv', '__pycache__', '.git', 'node_modules', '.pytest_cache', 'storage'}
    
    for py_file in root_path.rglob('*.py'):
        # Skip files in unwanted directories
        if any(skip_dir in py_file.parts for skip_dir in skip_dirs):
            continue
        
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            code_files.append({
                'path': str(py_file.relative_to(root_path)),
                'content': content
            })
        except Exception as e:
            logger.warning(f"Failed to read {py_file}: {e}")
    
    logger.info(f"📄 Loaded {len(code_files)} Python files")
    return code_files

def create_rag_documents(code_files: List[dict]):
    """Create LlamaIndex documents from code files."""
    from llama_index.core.schema import Document
    
    documents = []
    for idx, file_info in enumerate(code_files, 1):
        # Create document with metadata
        doc = Document(
            text=file_info['content'],
            metadata={
                'file_path': file_info['path'],
                'file_name': Path(file_info['path']).name,
            }
        )
        documents.append(doc)
        
        if idx % 50 == 0:
            logger.info(f"  Processed {idx}/{len(code_files)} files...")
    
    logger.info(f"✅ Created {len(documents)} documents")
    return documents

def generate_faiss_index(documents, storage_path: str = "./storage"):
    """Generate FAISS vector store index."""
    try:
        from llama_index.core import VectorStoreIndex
        from llama_index.vector_stores.faiss import FaissVectorStore
        import faiss
        
        logger.info("🔄 Building FAISS index (this may take a few minutes)...")
        
        # Create storage directory
        storage_dir = Path(storage_path)
        storage_dir.mkdir(exist_ok=True)
        
        # Create FAISS index
        dimension = 768  # Gemini embedding dimension
        faiss_index = faiss.IndexFlatL2(dimension)
        
        # Create vector store
        vector_store = FaissVectorStore(faiss_index)
        
        # Create index from documents
        index = VectorStoreIndex.from_documents(
            documents,
            vector_store=vector_store,
            show_progress=True
        )
        
        # Persist index
        index.vector_store.persist(str(storage_dir / "faiss_index"))
        
        logger.info(f"✅ FAISS index generated at {storage_dir}/faiss_index")
        return True
    except Exception as e:
        logger.error(f"Failed to generate FAISS index: {e}")
        return False

def main():
    """Main function."""
    logger.info("=" * 80)
    logger.info("[RAG INDEX GENERATION] Starting...")
    logger.info("=" * 80)
    
    # Setup
    setup_environment()
    
    # Configure LlamaIndex
    if not configure_llamaindex():
        sys.exit(1)
    
    # Load code files
    code_files = load_code_files()
    if not code_files:
        logger.error("No Python files found!")
        sys.exit(1)
    
    # Create documents
    documents = create_rag_documents(code_files)
    
    # Generate FAISS index
    if not generate_faiss_index(documents):
        sys.exit(1)
    
    logger.info("=" * 80)
    logger.info("[RAG INDEX GENERATION] Complete!")
    logger.info("=" * 80)
    logger.info("You can now use:")
    logger.info("  - Streamlit: streamlit run streamlit_app.py")
    logger.info("  - CLI: python cli_context_extractor.py 'your query'")

if __name__ == "__main__":
    main()
