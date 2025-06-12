# MCP Customer Service Assistant: Building AI Integrations with the Model Context Protocol

This project contains working examples for building AI integrations using the Model Context Protocol (MCP).

## Overview

Learn how to build standardized AI integrations that work across multiple platforms using MCP.

- Build MCP servers with FastMCP framework
- Create resources, tools, and prompts for AI models
- Integrate with Claude Desktop, OpenAI, Anthropic, LangChain, DSPy, and LiteLLM
- Implement async operations for high performance
- Use Pydantic for data validation and type safety

## Prerequisites

- Python 3.12.9 (managed via pyenv)
- Poetry for dependency management
- Go Task for build automation
- API key for OpenAI or Anthropic (Claude) OR Ollama installed locally

## Setup

1. Clone this repository
2. Copy `.env.example` to `.env` and configure your LLM provider:
    
    ```bash
    cp .env.example .env
    ```
    
3. Edit `.env` to select your provider and model:
    - For OpenAI: Set `LLM_PROVIDER=openai` and add your API key
    - For Claude: Set `LLM_PROVIDER=anthropic` and add your API key
    - For Ollama: Set `LLM_PROVIDER=ollama` (install Ollama and pull phi3 model first)
4. Run the setup task:
    
    ```bash
    task setup
    ```

## Supported LLM Providers

### OpenAI

- Model: gpt-4.1-2025-04-14
- Requires: OpenAI API key

### Anthropic (Claude)

- Model: claude-sonnet-4-20250514
- Requires: Anthropic API key

### Ollama (Local)

- Model: gemma3:27b
- Requires: Ollama installed and gemma3:27b model pulled
- Install: `brew install ollama` (macOS) or see [ollama.ai](https://ollama.ai/)
- Pull model: `ollama pull gemma3:27b`

## Project Structure

```
.
├── src/
│   ├── __init__.py
│   ├── config.py                 # LLM configuration
│   ├── main.py                   # MCP server implementation
│   ├── openai_integration.py     # OpenAI MCP integration
│   ├── anthropic_integration.py  # Anthropic MCP integration
│   ├── langchain_integration.py  # LangChain MCP integration
│   ├── dspy_integration.py       # DSPy MCP integration
│   └── litellm_integration.py    # LiteLLM MCP integration
├── tests/
│   └── test_mcp_server.py        # Unit tests
├── .env.example                  # Environment template
├── Taskfile.yml                  # Task automation
├── server_config.json            # MCP server configuration
└── pyproject.toml                # Poetry configuration
```

## Key Concepts Demonstrated

1. **MCP Architecture**: Three-layer system with hosts, clients, and servers
2. **Resources**: Standardized data access through custom URI schemes
3. **Tools**: AI-executable functions for performing actions
4. **Prompts**: Structured templates for consistent AI behavior
5. **FastMCP Framework**: Simplified MCP server development with FastAPI
6. **Multi-Platform Integration**: Connect once, use everywhere

## Running Examples

Run the MCP server:

```bash
task run
```

Or run individual integration examples:

```bash
task run-openai          # OpenAI integration
task run-anthropic       # Anthropic integration
task run-langchain       # LangChain integration
task run-dspy           # DSPy integration
task run-litellm        # LiteLLM integration
```

Direct Python execution:

```bash
poetry run python src/main.py
poetry run python src/openai_integration.py
poetry run python src/anthropic_integration.py
```

## Available Tasks

- `task setup` - Set up Python environment and install dependencies
- `task run` - Run the MCP server
- `task test` - Run unit tests
- `task format` - Format code with Black and Ruff
- `task clean` - Clean up generated files
- `task build` - Build the package for distribution
- `task install-global` - Install the package globally for use with uvx
- `task install-claude` - Install and show Claude Desktop configuration

## Installation for Claude Desktop

### Quick Setup

1. **Clone and setup the project**:
   ```bash
   git clone <repository-url>
   cd mcp_article1
   task setup  # or: poetry install
   ```

2. **Get Claude Desktop configuration**:
   ```bash
   task install-claude
   ```

3. **Add the configuration to Claude Desktop**:
   
   The configuration will use a shell script wrapper:
   ```json
   {
     "mcpServers": {
       "customer-service": {
         "command": "/path/to/mcp_article1/run-mcp-server.sh"
       }
     }
   }
   ```

4. **Restart Claude Desktop** to load the MCP server

### Why the Shell Script?

The `run-mcp-server.sh` script ensures:
- The correct working directory is set
- The virtual environment is activated
- All dependencies are available
- The server runs in the proper context

### Troubleshooting Claude Desktop Integration

If the server doesn't appear in Claude Desktop:

1. **Check the logs**: Look for errors in Claude Desktop's developer console
2. **Test the script manually**: 
   ```bash
   ./run-mcp-server.sh
   ```
3. **Verify the path**: Make sure the command path in the config is absolute
4. **Check permissions**: Ensure the script is executable (`chmod +x run-mcp-server.sh`)

## Virtual Environment Setup Instructions

### Prerequisites

1. Install pyenv (if not already installed):
    
    ```bash
    # macOS
    brew install pyenv
    
    # Linux
    curl https://pyenv.run | bash
    ```
    
2. Add pyenv to your shell:
    
    ```bash
    # Add to ~/.zshrc or ~/.bashrc
    echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
    echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
    echo 'eval "$(pyenv init -)"' >> ~/.zshrc
    
    # Reload shell
    source ~/.zshrc
    ```

### Setup Steps

1. **Install Python 3.12.9**:
    
    ```bash
    pyenv install 3.12.9
    ```
    
2. **Navigate to your project directory**:
    
    ```bash
    cd /path/to/mcp-customer-service
    ```
    
3. **Set local Python version**:
    
    ```bash
    pyenv local 3.12.9
    ```
    
4. **Install Poetry** (if not installed):
    
    ```bash
    curl -sSL https://install.python-poetry.org | python3 -
    ```
    
5. **Install project dependencies**:
    
    ```bash
    poetry install
    ```
    
6. **Activate the virtual environment**:
    
    ```bash
    poetry config virtualenvs.in-project true
    source .venv/bin/activate
    ```

### Alternative: If you have Go Task installed

Simply run:

```bash
brew install go-task
task setup
```

### Configure your LLM provider

1. **Copy the example env file**:
    
    ```bash
    cp .env.example .env
    ```
    
2. **Edit .env and set your provider**:
    
    ```bash
    # For OpenAI
    LLM_PROVIDER=openai
    OPENAI_API_KEY=your-key-here
    OPENAI_MODEL=gpt-4.1-2025-04-14
    
    # For Anthropic/Claude
    LLM_PROVIDER=anthropic
    ANTHROPIC_API_KEY=your-key-here
    ANTHROPIC_MODEL=claude-sonnet-4-20250514
    
    # For Ollama (local)
    LLM_PROVIDER=ollama
    OLLAMA_MODEL=gemma3:27b
    # Make sure Ollama is running: ollama serve
    # Pull the model: ollama pull gemma3:27b
    ```

### Verify setup

```bash
# Check Python version
python --version  # Should show 3.12.9

# Test imports
python -c "import fastmcp; print('MCP tools installed successfully')"
```

### Run the example

```bash
poetry run python src/main.py
```

Note: The main.py runs the MCP server, while integration examples demonstrate different client implementations.

## Example Output

The examples demonstrate:

1. Creating an MCP server with customer service resources and tools
2. Integrating with multiple AI platforms using the same server
3. Handling async operations for better performance
4. Using Pydantic for data validation
5. Implementing structured prompts for consistent AI responses

## Troubleshooting

- **Ollama connection error**: Make sure Ollama is running (`ollama serve`)
- **API key errors**: Check your `.env` file has the correct keys
- **Model not found**: For Ollama, ensure you've pulled the model (`ollama pull gemma3:27b`)
- **MCP server not starting**: Check the logs for port conflicts or missing dependencies

## Learn More

- [Model Context Protocol Documentation](https://modelcontextprotocol.io)
- [FastMCP Framework](https://github.com/modelcontextprotocol/fastmcp)
- [MCP: Building AI Integrations Article](https://example.com/mcp-article)
