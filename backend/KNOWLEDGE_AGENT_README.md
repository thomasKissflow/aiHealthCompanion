# Knowledge Specialist Agent

## Overview

The Knowledge Specialist Agent is responsible for retrieving relevant medical information from a knowledge base using ChromaDB for vector storage. It implements cache-first retrieval, semantic search, and logs chunk retrieval counts.

## Features

- **PDF Knowledge Loading**: Automatically loads and processes medical reference PDFs
- **Intelligent Chunking**: Splits documents into ~500 character chunks with 50 character overlap
- **Semantic Search**: Uses sentence-transformers (all-MiniLM-L6-v2) for embedding generation
- **Vector Storage**: ChromaDB for efficient similarity search
- **Cache-First Retrieval**: Checks Response_Cache before generating new responses
- **Comprehensive Logging**: Logs all operations including chunk retrieval counts

## Requirements Implemented

✓ **Requirement 9.1**: Load medical reference PDF files  
✓ **Requirement 9.2**: Split PDF content into chunks of appropriate size  
✓ **Requirement 9.3**: Generate embeddings for each chunk  
✓ **Requirement 9.4**: Store embeddings in ChromaDB vector database  
✓ **Requirement 9.5**: Check Response_Cache for similar queries first  
✓ **Requirement 9.6**: Retrieve relevant context chunks based on user query  
✓ **Requirement 9.7**: Log the number of chunks to terminal  
✓ **Requirement 9.8**: Return retrieved chunks to the Supervisor_Agent  
✓ **Requirement 9.9**: Cache the generated response with the query as key  
✓ **Requirement 9.10**: Retrieve context about migraines when user mentions headache symptoms  

## File Structure

```
backend/
├── knowledge_agent.py              # Main Knowledge Specialist Agent implementation
├── knowledge/                      # Medical knowledge PDFs
│   ├── migraines_and_headaches.pdf
│   └── common_symptoms_guide.pdf
├── create_sample_pdfs.py          # Script to generate sample medical PDFs
├── test_knowledge_agent.py        # Unit tests for the agent
├── test_knowledge_integration.py  # Integration tests with other components
└── test_knowledge_requirements.py # Requirements verification tests
```

## Usage

### Basic Usage

```python
from knowledge_agent import KnowledgeSpecialistAgent
from response_cache import ResponseCache

# Initialize
cache = ResponseCache()
agent = KnowledgeSpecialistAgent(
    response_cache=cache,
    chroma_persist_dir="./chroma_db"
)

# Load knowledge base
await agent.initialize(pdf_directory="backend/knowledge")

# Retrieve context chunks
chunks = await agent.retrieve("What are migraine symptoms?", n_results=3)

# Generate response with LLM
response = await agent.generate_response(query, chunks, llm_client)
```

### Integration with Supervisor Agent

```python
# In Supervisor Agent
if intent in [Intent.SYMPTOM_CHECK, Intent.KNOWLEDGE_QUERY]:
    # Retrieve medical context
    chunks = await knowledge_agent.retrieve(user_query, n_results=3)
    
    # Generate response
    response = await knowledge_agent.generate_response(
        user_query, 
        chunks, 
        llm_client
    )
```

## Sample Medical Knowledge

The system includes two sample medical reference PDFs:

1. **migraines_and_headaches.pdf**: Comprehensive information about:
   - Types of headaches (tension, migraines)
   - Migraine symptoms and characteristics
   - Common triggers
   - When to seek medical attention
   - Management strategies

2. **common_symptoms_guide.pdf**: Information about:
   - Nausea and vomiting
   - Dizziness and vertigo
   - Fatigue and tiredness
   - Fever
   - Cough
   - Chest pain
   - Difficulty breathing

## Testing

Run the test suite to verify all functionality:

```bash
# Unit tests
python test_knowledge_agent.py

# Integration tests
python test_knowledge_integration.py

# Requirements verification
python test_knowledge_requirements.py
```

## Performance

- **Chunk Processing**: 18 chunks from 2 PDFs in ~3 seconds
- **Embedding Generation**: Uses sentence-transformers with MPS acceleration (Mac)
- **Retrieval Speed**: ~50ms for semantic search
- **Cache Hit Rate**: 33-50% in typical usage
- **Total Initialization**: ~5 seconds (one-time cost)

## Logging

The agent logs all operations to help with debugging and monitoring:

```
[Knowledge Agent] Loading embedding model...
[Knowledge Agent] Initialized
[Knowledge Agent] Starting knowledge base initialization...
[Knowledge Agent] Collection 'medical_knowledge' ready
[Knowledge Agent] Found 2 PDF files to process
[Knowledge Agent] Processing common_symptoms_guide.pdf...
[Knowledge Agent] Extracted 11 chunks from common_symptoms_guide.pdf
[Knowledge Agent] Generating embeddings for 18 chunks...
[Knowledge Agent] Successfully loaded 18 chunks into knowledge base
[Knowledge Agent] retrieving medical context
[Knowledge Agent] Retrieved 3 chunks
[Knowledge Agent] Response generated and cached
[Knowledge Agent] Cache hit - returning cached response
```

## Dependencies

- `chromadb==0.4.22`: Vector database
- `pypdf==4.0.1`: PDF processing
- `sentence-transformers==2.3.1`: Embedding generation
- `numpy<2.0`: Required for ChromaDB compatibility

## Future Enhancements

- Add more medical reference PDFs
- Implement metadata filtering (by topic, severity, etc.)
- Add support for multiple languages
- Implement hybrid search (semantic + keyword)
- Add document versioning and updates
- Implement relevance feedback loop
