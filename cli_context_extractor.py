#!/usr/bin/env python3
"""
CLI Context Extractor - Command Line Interface for RAG Context Extraction

This utility loads the indexed codebase and retrieves relevant code snippets
based on user queries. The output is formatted as a clear prompt suitable
for copying and pasting into GitHub Copilot chat.

Usage:
    python cli_context_extractor.py "your query here"
    python cli_context_extractor.py --query "your query" --top-k 10
    python cli_context_extractor.py --help

Example:
    python cli_context_extractor.py "How does the ResponseCache class work?"
    python cli_context_extractor.py "Find all functions in core/llm_adapter.py"
"""

import argparse
import json
import sys
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import os

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONSTANTS
# ============================================================================

DEFAULT_STORAGE_PATH = Path("./storage")
DEFAULT_SIMILARITY_TOP_K = 5
MAX_SIMILARITY_TOP_K = 20

# ============================================================================
# LLAMAINDEX CONFIGURATION
# ============================================================================

def configure_llamaindex():
    """
    Configure LlamaIndex to use Gemini 2.5 Flash as LLM.
    
    This requires GEMINI_API_KEY to be set in environment.
    """
    try:
        from llama_index.core import Settings
        from llama_index.llms.gemini import Gemini
        from llama_index.embeddings.gemini import GeminiEmbedding
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        # Configure LLM (Gemini 2.5 Flash)
        Settings.llm = Gemini(
            model="gemini-2.5-flash",
            api_key=api_key,
            temperature=0.7,
        )
        
        # Configure Embedding Model (Gemini)
        Settings.embed_model = GeminiEmbedding(
            model_name="models/embedding-001",
            api_key=api_key,
        )
        
        logger.info("✅ LlamaIndex configured with Gemini 2.5 Flash")
        return True
        
    except ImportError as e:
        logger.error(f"Failed to import LlamaIndex: {str(e)}")
        print(
            "❌ Error: LlamaIndex not installed.\n"
            "Install with: pip install llama-index llama-index-llms-gemini llama-index-embeddings-gemini"
        )
        return False
    
    except ValueError as e:
        logger.error(f"Configuration error: {str(e)}")
        print(f"❌ Error: {str(e)}")
        return False
    
    except Exception as e:
        logger.error(f"Unexpected error configuring LlamaIndex: {str(e)}")
        print(f"❌ Error: {str(e)}")
        return False

# ============================================================================
# RAG ENGINE INITIALIZATION
# ============================================================================

def load_rag_engine(storage_path: Path = DEFAULT_STORAGE_PATH) -> Optional[Any]:
    """
    Load the RAG query engine from storage directory.
    
    Args:
        storage_path: Path to storage directory containing FAISS index
        
    Returns:
        Query engine object if successful, None if failed
        
    Raises:
        FileNotFoundError: If storage directory or index files not found
        json.JSONDecodeError: If index files are corrupted
    """
    try:
        logger.info(f"Loading RAG engine from {storage_path.absolute()}")
        
        # Check if storage directory exists
        if not storage_path.exists():
            raise FileNotFoundError(
                f"Storage directory not found: {storage_path.absolute()}\n"
                "Please run 'python index_code.py' to generate the index."
            )
        
        # Import LlamaIndex components
        try:
            from llama_index.core import (
                VectorStoreIndex,
                load_index_from_storage,
            )
            from llama_index.core.storage import StorageContext
            from llama_index.vector_stores.faiss import FaissVectorStore
            import faiss
            
        except ImportError as e:
            raise ImportError(
                f"LlamaIndex components not available: {str(e)}\n"
                "Install with: pip install llama-index llama-index-vector-stores-faiss"
            )
        
        # Check if FAISS index exists
        faiss_index_path = storage_path / "faiss_index.bin"
        if not faiss_index_path.exists():
            raise FileNotFoundError(
                f"FAISS index not found: {faiss_index_path}\n"
                "Please run 'python index_code.py' to generate the index."
            )
        
        # Load FAISS index
        logger.info("Loading FAISS index...")
        faiss_index = faiss.read_index(str(faiss_index_path))
        vector_store = FaissVectorStore(faiss_index)
        
        # Setup storage context
        storage_context = StorageContext.from_defaults(
            vector_store=vector_store,
            persist_dir=str(storage_path),
        )
        
        # Load index from storage
        logger.info("Loading VectorStoreIndex...")
        index = load_index_from_storage(storage_context)
        
        # Create query engine
        query_engine = index.as_query_engine(
            similarity_top_k=DEFAULT_SIMILARITY_TOP_K,
            response_mode="tree_summarize",
        )
        
        logger.info("✅ RAG engine loaded successfully")
        return query_engine
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {str(e)}")
        print(f"❌ Error: {str(e)}")
        return None
    
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in storage: {str(e)}")
        print(f"❌ Error: Invalid index format - {str(e)}")
        return None
    
    except Exception as e:
        logger.error(f"Unexpected error loading RAG engine: {str(e)}")
        print(f"❌ Error: {str(e)}")
        return None

# ============================================================================
# CONTEXT EXTRACTION
# ============================================================================

def extract_context(
    query: str,
    query_engine: Any,
    top_k: int = DEFAULT_SIMILARITY_TOP_K,
) -> Optional[str]:
    """
    Extract context from indexed codebase based on query.
    
    Args:
        query: User query string
        query_engine: LlamaIndex query engine
        top_k: Number of top similar documents to retrieve
        
    Returns:
        Formatted context string suitable for Copilot, or None if error
    """
    try:
        logger.info(f"Extracting context for query: {query}")
        logger.info(f"Top K: {top_k}")
        
        # Query the engine
        response = query_engine.query(query)
        
        # Extract source nodes
        source_nodes = response.source_nodes if hasattr(response, 'source_nodes') else []
        
        logger.info(f"Found {len(source_nodes)} relevant code snippets")
        
        return format_context_for_copilot(query, source_nodes, response)
        
    except Exception as e:
        logger.error(f"Error extracting context: {str(e)}")
        print(f"❌ Error: {str(e)}")
        return None

# ============================================================================
# CONTEXT FORMATTING
# ============================================================================

def format_context_for_copilot(
    query: str,
    source_nodes: List[Any],
    response: Any,
) -> str:
    """
    Format extracted context as a clear prompt for GitHub Copilot.
    
    Args:
        query: Original user query
        source_nodes: List of relevant code snippets
        response: Response object from query engine
        
    Returns:
        Formatted prompt string
    """
    lines = []
    
    # Header
    lines.append("=" * 80)
    lines.append("RAG CONTEXT EXTRACTION - CODE ANALYSIS PROMPT")
    lines.append("=" * 80)
    lines.append("")
    
    # Timestamp
    lines.append(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    
    # Query Information
    lines.append("🔍 ORIGINAL QUERY:")
    lines.append("-" * 80)
    lines.append(f"  {query}")
    lines.append("")
    
    # Response Summary
    lines.append("📝 RESPONSE SUMMARY:")
    lines.append("-" * 80)
    response_text = str(response)
    if response_text:
        # Limit response to first 500 characters
        summary = response_text[:500] + "..." if len(response_text) > 500 else response_text
        lines.append(summary)
    lines.append("")
    
    # Source Code Snippets
    if source_nodes:
        lines.append("💻 RELEVANT CODE SNIPPETS (Top 5):")
        lines.append("-" * 80)
        lines.append("")
        
        for idx, node in enumerate(source_nodes[:5], 1):
            # Node metadata
            metadata = node.metadata if hasattr(node, 'metadata') else {}
            file_path = metadata.get('file_path', 'Unknown')
            
            # Node content
            content = node.get_content() if hasattr(node, 'get_content') else str(node.text)
            
            # Relevance score
            score = node.score if hasattr(node, 'score') else 'N/A'
            
            # Format snippet
            lines.append(f"📌 Snippet {idx}:")
            lines.append(f"   File: {file_path}")
            lines.append(f"   Relevance: {score}")
            lines.append("")
            lines.append("   ```python")
            # Limit content to first 300 characters per snippet
            snippet_content = content[:300] + "..." if len(content) > 300 else content
            for code_line in snippet_content.split('\n'):
                lines.append(f"   {code_line}")
            lines.append("   ```")
            lines.append("")
    
    # Instructions for Copilot
    lines.append("📋 INSTRUCTIONS FOR GITHUB COPILOT:")
    lines.append("-" * 80)
    lines.append("""
1. Copy the entire section above (including code snippets)
2. Paste it into GitHub Copilot chat as context
3. Ask your follow-up question with full context about the codebase
4. Copilot will understand the code structure and dependencies

Example follow-up question:
"Based on these code snippets, how should I refactor this function to improve performance?"
""")
    
    # Footer
    lines.append("=" * 80)
    lines.append("End of RAG Context")
    lines.append("=" * 80)
    
    return "\n".join(lines)

# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Extract relevant code context using RAG (Retrieval-Augmented Generation)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli_context_extractor.py "How does the ResponseCache work?"
  python cli_context_extractor.py --query "Find all functions in core/llm_adapter.py" --top-k 10
  python cli_context_extractor.py --storage /path/to/storage --query "your query"
        """,
    )
    
    # Positional argument for query
    parser.add_argument(
        "query",
        nargs="?",
        help="Query string to search the codebase",
    )
    
    # Optional arguments
    parser.add_argument(
        "-q", "--query",
        dest="query_arg",
        help="Query string (alternative to positional argument)",
    )
    
    parser.add_argument(
        "-k", "--top-k",
        type=int,
        default=DEFAULT_SIMILARITY_TOP_K,
        help=f"Number of top results to retrieve (default: {DEFAULT_SIMILARITY_TOP_K}, max: {MAX_SIMILARITY_TOP_K})",
    )
    
    parser.add_argument(
        "-s", "--storage",
        type=Path,
        default=DEFAULT_STORAGE_PATH,
        help=f"Path to storage directory (default: {DEFAULT_STORAGE_PATH})",
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose mode enabled")
    
    # Determine query
    query = args.query_arg or args.query
    
    if not query:
        parser.print_help()
        print("\n❌ Error: Query is required")
        return 1
    
    # Validate top-k
    if args.top_k > MAX_SIMILARITY_TOP_K:
        print(f"⚠️  Warning: top-k {args.top_k} exceeds maximum {MAX_SIMILARITY_TOP_K}, using {MAX_SIMILARITY_TOP_K}")
        args.top_k = MAX_SIMILARITY_TOP_K
    
    # Configure LlamaIndex
    if not configure_llamaindex():
        return 1
    
    # Load RAG engine
    query_engine = load_rag_engine(args.storage)
    if query_engine is None:
        return 1
    
    # Extract context
    context = extract_context(query, query_engine, args.top_k)
    if context is None:
        return 1
    
    # Print context
    print("\n")
    print(context)
    print("\n")
    
    # Success message
    logger.info("✅ Context extraction completed successfully")
    print("✅ Context extracted successfully!")
    print("📋 Copy the above text to paste into GitHub Copilot chat")
    
    return 0

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    sys.exit(main())
