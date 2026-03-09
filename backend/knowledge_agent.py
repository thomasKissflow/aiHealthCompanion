"""
Knowledge Specialist Agent for AI Health Companion

This agent retrieves relevant medical information from a knowledge base using ChromaDB
for vector storage. It implements cache-first retrieval, semantic search, and logs
chunk retrieval counts.

Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7, 9.8, 9.9, 9.10
"""

import os
import logging
from typing import List, Optional
from pathlib import Path

import chromadb
from chromadb.config import Settings
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

from response_cache import ResponseCache


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KnowledgeSpecialistAgent:
    """
    Agent responsible for retrieving relevant medical information from a knowledge base.
    
    Uses ChromaDB for vector storage and implements cache-first retrieval strategy.
    """
    
    def __init__(self, response_cache: ResponseCache, chroma_persist_dir: str = "./chroma_db"):
        """
        Initialize the Knowledge Specialist Agent.
        
        Args:
            response_cache: Response cache for storing generated responses
            chroma_persist_dir: Directory to persist ChromaDB data
        """
        self.cache = response_cache
        self.chroma_persist_dir = chroma_persist_dir
        
        # Initialize ChromaDB client
        self.chroma_client = chromadb.Client(Settings(
            persist_directory=chroma_persist_dir,
            anonymized_telemetry=False
        ))
        
        # Initialize embedding model
        logger.info("[Knowledge Agent] Loading embedding model...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Collection will be created during initialization
        self.collection = None
        
        logger.info("[Knowledge Agent] Initialized")
    
    async def initialize(self, pdf_directory: str = "backend/knowledge") -> None:
        """
        Load medical reference PDFs, generate embeddings, and store in ChromaDB.
        
        Requirements: 9.1, 9.2, 9.3, 9.4
        
        Args:
            pdf_directory: Directory containing medical reference PDF files
        """
        logger.info("[Knowledge Agent] Starting knowledge base initialization...")
        
        # Create or get collection
        try:
            self.collection = self.chroma_client.get_or_create_collection(
                name="medical_knowledge",
                metadata={"description": "Medical reference knowledge base"}
            )
            logger.info(f"[Knowledge Agent] Collection 'medical_knowledge' ready")
        except Exception as e:
            logger.error(f"[Knowledge Agent] Failed to create collection: {e}")
            raise
        
        # Check if collection already has documents
        existing_count = self.collection.count()
        if existing_count > 0:
            logger.info(f"[Knowledge Agent] Collection already contains {existing_count} documents")
            return
        
        # Load PDFs from directory
        pdf_path = Path(pdf_directory)
        if not pdf_path.exists():
            logger.warning(f"[Knowledge Agent] PDF directory not found: {pdf_directory}")
            return
        
        pdf_files = list(pdf_path.glob("*.pdf"))
        if not pdf_files:
            logger.warning(f"[Knowledge Agent] No PDF files found in {pdf_directory}")
            return
        
        logger.info(f"[Knowledge Agent] Found {len(pdf_files)} PDF files to process")
        
        # Process each PDF
        all_chunks = []
        all_metadatas = []
        all_ids = []
        
        for pdf_file in pdf_files:
            logger.info(f"[Knowledge Agent] Processing {pdf_file.name}...")
            chunks, metadatas, ids = self._process_pdf(pdf_file)
            all_chunks.extend(chunks)
            all_metadatas.extend(metadatas)
            all_ids.extend(ids)
        
        # Generate embeddings and store in ChromaDB
        if all_chunks:
            logger.info(f"[Knowledge Agent] Generating embeddings for {len(all_chunks)} chunks...")
            embeddings = self.embedding_model.encode(all_chunks, show_progress_bar=True)
            
            logger.info(f"[Knowledge Agent] Storing embeddings in ChromaDB...")
            self.collection.add(
                documents=all_chunks,
                embeddings=embeddings.tolist(),
                metadatas=all_metadatas,
                ids=all_ids
            )
            
            logger.info(f"[Knowledge Agent] Successfully loaded {len(all_chunks)} chunks into knowledge base")
        else:
            logger.warning("[Knowledge Agent] No chunks extracted from PDFs")
    
    def _process_pdf(self, pdf_path: Path) -> tuple[List[str], List[dict], List[str]]:
        """
        Process a PDF file: extract text, split into chunks, and prepare metadata.
        
        Requirements: 9.1, 9.2
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Tuple of (chunks, metadatas, ids)
        """
        chunks = []
        metadatas = []
        ids = []
        
        try:
            reader = PdfReader(str(pdf_path))
            
            for page_num, page in enumerate(reader.pages):
                text = page.extract_text()
                
                if not text.strip():
                    continue
                
                # Split page into chunks (approximately 500 characters with overlap)
                page_chunks = self._split_into_chunks(text, chunk_size=500, overlap=50)
                
                for chunk_idx, chunk in enumerate(page_chunks):
                    chunk_id = f"{pdf_path.stem}_page{page_num}_chunk{chunk_idx}"
                    
                    chunks.append(chunk)
                    metadatas.append({
                        "source": pdf_path.name,
                        "page": page_num,
                        "chunk_index": chunk_idx
                    })
                    ids.append(chunk_id)
            
            logger.info(f"[Knowledge Agent] Extracted {len(chunks)} chunks from {pdf_path.name}")
            
        except Exception as e:
            logger.error(f"[Knowledge Agent] Error processing {pdf_path.name}: {e}")
        
        return chunks, metadatas, ids
    
    def _split_into_chunks(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Requirements: 9.2
        
        Args:
            text: Text to split
            chunk_size: Target size of each chunk in characters
            overlap: Number of characters to overlap between chunks
            
        Returns:
            List of text chunks
        """
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence boundary
            if end < text_length:
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                break_point = max(last_period, last_newline)
                
                if break_point > chunk_size * 0.5:  # Only break if we're past halfway
                    chunk = chunk[:break_point + 1]
                    end = start + break_point + 1
            
            chunks.append(chunk.strip())
            start = end - overlap
        
        return [c for c in chunks if c]  # Filter empty chunks
    
    async def retrieve(self, query: str, n_results: int = 3) -> List[str]:
        """
        Retrieve relevant context chunks based on user query.
        
        Implements cache-first retrieval: checks Response_Cache before ChromaDB.
        
        Requirements: 9.5, 9.6, 9.7, 9.10
        
        Args:
            query: User query text
            n_results: Number of chunks to retrieve
            
        Returns:
            List of relevant context chunks
        """
        logger.info("[Knowledge Agent] retrieving medical context")
        
        # Note: Cache is checked in generate_response, not here
        # This method always retrieves fresh chunks from ChromaDB
        
        # Retrieve from ChromaDB
        if not self.collection:
            logger.warning("[Knowledge Agent] Collection not initialized")
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query])[0]
            
            # Search ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=n_results
            )
            
            chunks = results['documents'][0] if results['documents'] else []
            
            # Log chunk retrieval count
            logger.info(f"[Knowledge Agent] Retrieved {len(chunks)} chunks")
            
            return chunks
            
        except Exception as e:
            logger.error(f"[Knowledge Agent] Error retrieving chunks: {e}")
            return []
    
    async def generate_response(self, query: str, context_chunks: List[str], llm_client) -> str:
        """
        Generate response using LLM with retrieved context.
        
        Implements caching of generated responses.
        
        Requirements: 9.8, 9.9
        
        Args:
            query: User query text
            context_chunks: Retrieved context chunks
            llm_client: LLM client for generating responses
            
        Returns:
            Generated response text
        """
        # Check cache first
        cached_response = self.cache.get(query, {"type": "knowledge"})
        
        if cached_response:
            logger.info("[Knowledge Agent] Cache hit - returning cached response")
            return cached_response
        
        # Build prompt with context
        context_text = "\n\n".join(context_chunks)
        prompt = f"""Based on the following medical reference information, answer the user's question.

Medical Reference Context:
{context_text}

User Question: {query}

Provide a helpful, conversational response. Do not diagnose conditions or recommend specific medications. 
If the context doesn't contain relevant information, acknowledge that and provide general guidance."""

        # Generate response using LLM
        try:
            response = await llm_client.generate(
                prompt=prompt,
                system_prompt="You are a helpful health companion. Provide informative responses based on the given context, but never diagnose or prescribe.",
                temperature=0.7
            )
            
            if response:
                # Cache the response
                self.cache.put(query, response, {"type": "knowledge"})
                logger.info("[Knowledge Agent] Response generated and cached")
                return response
            else:
                logger.warning("[Knowledge Agent] LLM returned no response")
                return "I'm having trouble processing that right now. Could you rephrase your question?"
                
        except Exception as e:
            logger.error(f"[Knowledge Agent] Error generating response: {e}")
            return "I'm having trouble accessing medical information right now. Please try again."
