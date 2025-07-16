# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

BrightData Pain Extractor is a Python application that integrates BrightData's MCP (Model Context Protocol) server with OpenAI for AI-powered web scraping and data extraction. The project combines async Python backend with Node.js MCP client communication.

## Architecture

The codebase follows a modular architecture with clear separation of concerns:

- **llm/**: OpenAI client wrapper with async support and Pydantic models
- **agent/**: MCP client for communicating with BrightData MCP server via subprocess stdio
- **models/**: Pydantic schemas for tools, agents, and data structures
- **Root files**: Main entry points and demo applications

### Key Components

- `OpenAIClient`: Async wrapper around OpenAI API with streaming support
- `MCPClient`: Manages subprocess communication with BrightData MCP server via JSON over stdio
- `BrightDataTool`: Pydantic model for tool definitions with async executors
- `OpenAIAgent`: Main orchestrator combining OpenAI with BrightData tools

## Running the Application

### Environment Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Node.js MCP package
npm install
```

### Required Environment Variables
Copy and configure environment variables:
- `API_TOKEN`: BrightData API token
- `BROWSER_AUTH`: BrightData browser authentication 
- `WEB_UNLOCKER_ZONE`: BrightData web unlocker zone
- `OPENAI_API_KEY`: OpenAI API key
- `OPENAI_MODEL`: OpenAI model (defaults to gpt-4.1-2025-04-14)

### Entry Points
```bash
# Main demo with MCP integration
python demo_agent.py

# Simple chat interface
python main.py
```

## Development Notes

### MCP Communication
The application communicates with BrightData MCP server through subprocess stdio using JSON messages. The MCP client expects:
- Command: `["npx", "@brightdata/mcp"]`
- Environment variables for BrightData authentication
- JSON request/response over stdin/stdout

### Error Handling
- MCP connection failures are graceful - application continues with native tools only
- 15-second timeout for MCP tool calls with stderr logging
- Environment variable validation with warnings for missing credentials

### Code Patterns
- All async/await throughout the codebase
- Pydantic models for type safety and validation
- Environment variable loading with python-dotenv
- Graceful degradation when external services unavailable