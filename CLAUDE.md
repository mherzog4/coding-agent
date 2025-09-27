# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Environment

This is a Python-based coding agent project using UV for dependency management. The project requires Python >=3.13.

### Key Commands

- `uv run python main.py` - Run the interactive coding agent
- `uv sync` - Install/sync dependencies
- `uv add <package>` - Add new dependency
- `uv run ruff check` - Run linting (ruff is included in dependencies)
- `uv run ruff format` - Format code

### Environment Setup

Copy `.env.example` to `.env` and set:
- `ANTHROPIC_API_KEY` - Required for the agent to function

## Architecture

This is a conversational coding agent that interacts with Claude's API to provide file manipulation capabilities through a chat interface.

### Core Components

**Agent Class** (`main.py:178-296`)
- Main conversation loop with tool execution
- Handles continuous chat interaction until Ctrl+C
- Uses Claude Sonnet 3.7 model for inference
- Manages conversation history and tool results

**Tool System** (`main.py:21-176`)
- `ToolDefinition` class wraps tools with schemas
- Three core tools: `read_file`, `list_files`, `edit_file`
- Tools use JSON schemas for input validation
- `edit_file` supports both editing existing files and creating new ones

### Key Behaviors

- Interactive CLI with colored output (blue for user, yellow for Claude, green for tools)
- Tool execution is logged with function name and parameters
- File operations are relative to working directory
- Error handling for file operations and API calls
- Conversation continues until manual interrupt

### Tool Capabilities

- **File Reading**: Read any file in the working directory tree
- **Directory Listing**: Recursive file/directory listing with JSON output
- **File Editing**: String replacement editing, creates files if they don't exist