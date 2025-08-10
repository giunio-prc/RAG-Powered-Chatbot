# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a RAG (Retrieval-Augmented Generation) powered chatbot built with FastAPI that provides AI-driven customer support. The application follows hexagonal architecture principles with clear separation between interfaces, implementations, and API layers.

## Development Commands

### Environment Setup
```bash
# Install dependencies
uv install

# Install pre-commit hooks (run once after cloning)
uv run pre-commit install

# Create .env file from template
cp .env.example .env
# Edit .env with your COHERE_API_KEY and optional Chroma server settings
```

### Running the Application
```bash
# Development mode with auto-reload
uv run fastapi dev

# Production mode
uv run fastapi run
```

### Development Tools
```bash
# Run linting with auto-fix
uv run ruff check --fix

# Run type checking (currently commented out in pre-commit)
uv run mypy

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov

# Run pre-commit hooks manually
uv run pre-commit run
```

### Chroma Database Server
```bash
# Run Chroma server locally (if using external server)
uv run chroma run --path ./db_chroma --port <PORT>
```

## Architecture

### Hexagonal Architecture Structure
- **Interfaces** (`app/interfaces/`): Abstract base classes defining contracts
  - `AIAgentInterface`: Contract for AI agents (query_with_context, get_stream_response)
  - `DatabaseManagerInterface`: Contract for vector databases (add_text_to_db, get_context, etc.)

- **Implementations**:
  - **Agents** (`app/agents/`): AI agent implementations
    - `CohereAgent`: Uses Cohere's Command-R-Plus model via LangChain
    - `FakeAgent`: Mock implementation for testing
  - **Databases** (`app/databases/`): Vector database implementations
    - `ChromaDatabase`: Production implementation using ChromaDB with Cohere embeddings
    - `FakeDatabase`: Mock implementation for testing

- **Controller** (`app/controller/controller.py`): Business logic orchestration
  - `add_content_into_db()`: Adds text content to vector database
  - `query_agent()`: Queries agent with retrieved context
  - `query_agent_with_stream_response()`: Streaming version of queries

- **API Layer** (`app/api/`): FastAPI routers and HTTP handling
  - `database.py`: Document upload and vector database stats endpoints
  - `prompting.py`: Chat query endpoints (regular and streaming)

### Key Components
- **Vector Database**: ChromaDB for similarity search and document retrieval
- **AI Agent**: Cohere Command-R-Plus for natural language generation
- **Text Processing**: LangChain's CharacterTextSplitter (200 char chunks, no overlap)
- **Frontend**: Simple HTML templates with JavaScript for chat and document management

### Configuration
- Environment variables via `.env` file:
  - `COHERE_API_KEY`: Required for AI agent and embeddings
  - `CHROMA_SERVER_HOST`, `CHROMA_SERVER_PORT`: Optional external Chroma server (defaults to in-memory)

### Testing Strategy
- Unit tests in `tests/` directory mirror the `app/` structure
- Test implementations use fake/mock agents and databases
- Tests use pytest with asyncio support
- Test data in `tests/data/`

## Key Dependencies
- **FastAPI**: Web framework with async support
- **LangChain**: AI framework for prompt templates and model integration
- **ChromaDB**: Vector database for similarity search
- **Cohere**: AI models for embeddings and text generation
- **Ruff**: Code formatting and linting
- **pytest**: Testing framework
- **uv**: Python package manager and virtual environment
