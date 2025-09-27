# Code-Editing Agent (Python Implementation)

A minimal Python implementation of a code-editing AI agent, ported from Thorsten Ball's Go tutorial "How to Build an Agent" [https://ampcode.com/how-to-build-an-agent]

## Overview

This project proves that building an impressive AI agent doesn't require complex frameworks or thousands of lines of code. It's fundamentally an LLM, a loop, and enough tokens - everything else is engineering polish.

The agent provides Claude AI with three essential tools:
- **read_file**: Read the contents of any file
- **list_files**: List files and directories
- **edit_file**: Edit files using string replacement

## Features

- Terminal-based chat interface with Claude AI
- File system access for Claude through tools
- Conversation history maintained across interactions
- Tool execution with visual feedback
- Error handling and graceful degradation
- Support for creating new files and editing existing ones

## Prerequisites

- Python 3.13+ (as specified in pyproject.toml)
- UV package manager (recommended) or pip
- Anthropic API key

## Installation

1. Clone or download this repository

2. Install dependencies using UV:
```bash
uv sync
```

Or install manually with pip:
```bash
pip install anthropic python-dotenv
```

3. Set up your environment variables:
```bash
# Create a .env file
echo "ANTHROPIC_API_KEY=your_api_key_here" > .env
```

Or export directly:
```bash
export ANTHROPIC_API_KEY="your_api_key_here"
```

## Usage

Run the agent:
```bash
python main.py
```

You'll see a prompt like:
```
Chat with Claude (use 'ctrl-c' to quit)
You:
```

### Example Interactions

**Explore the current directory:**
```
You: What files do you see in this directory?
Claude: I'll help you see what's in the current directory. Let me list the files and directories for you.
tool: list_files({})
Claude: I can see several files and directories in the current directory:
[... detailed file listing ...]
```

**Read a file:**
```
You: What's in main.py?
Claude: I'll check the main.py file to see what's in it.
tool: read_file({"path":"main.py"})
Claude: Based on my review, main.py implements a Claude AI assistant agent...
```

**Create a new file:**
```
You: Create a hello world script in Python
Claude: I'll create a hello world script in Python for you.
tool: edit_file({"path":"hello.py","old_str":"","new_str":"print(\"Hello, World!\")"})
Claude: I've created a simple hello.py script that prints "Hello, World!" to the console.
```

**Edit an existing file:**
```
You: Change the hello world script to say "Hello, Claude!"
Claude: I'll modify the hello.py script to say "Hello, Claude!" instead.
tool: read_file({"path":"hello.py"})
tool: edit_file({"path":"hello.py","old_str":"print(\"Hello, World!\")","new_str":"print(\"Hello, Claude!\")"})
Claude: I've successfully updated the hello.py script...
```

## Architecture

### Core Components

**Agent Class**: The main orchestrator that manages the conversation loop and tool execution.

**ToolDefinition Class**: Defines the structure for tools with name, description, input schema, and execution function.

**Tool Functions**:
- `read_file()`: Reads file contents with error handling
- `list_files()`: Recursively lists files and directories
- `edit_file()`: Performs string replacement edits or creates new files

### Conversation Flow

1. User inputs message
2. Agent sends conversation history + available tools to Claude
3. Claude responds with either text or tool use requests
4. If tools are requested, agent executes them and sends results back
5. Claude provides final response incorporating tool results
6. Loop continues

### Tool Execution

When Claude wants to use a tool, it responds with structured data like:
```json
{
  "type": "tool_use",
  "id": "tool_123",
  "name": "read_file",
  "input": {"path": "example.txt"}
}
```

The agent:
1. Finds the matching tool definition
2. Executes the tool function with the provided input
3. Returns a tool result with the output
4. Sends the result back to Claude for processing

## Key Implementation Details

### String-Based File Editing

The `edit_file` tool uses simple string replacement rather than AST manipulation or line-based editing. This approach works surprisingly well because:

- Claude understands exactly what text to replace
- It can make precise, targeted changes
- No need for complex parsing or code understanding
- Works with any text file format

### Tool Schema Definition

Each tool includes a JSON schema that tells Claude:
- What parameters it accepts
- What each parameter does
- Whether parameters are required
- Expected data types

### Error Handling

The implementation includes robust error handling:
- File not found errors
- Permission errors
- Invalid tool parameters
- Network connectivity issues
- Graceful degradation when tools fail

### Visual Feedback

The terminal interface uses ANSI color codes:
- Blue for user input
- Yellow for Claude responses
- Green for tool execution
- Clear visual separation between conversation turns

## Differences from Go Implementation

This Python port includes several adaptations:

**Simplified Tool Definitions**: Python's dynamic typing eliminates the need for complex generic schema generation.

**Pathlib Usage**: Modern Python path handling instead of string manipulation.

**Exception Handling**: Pythonic try/except blocks rather than explicit error returns.

**Dictionary-Based Messages**: Claude's Python SDK uses simple dictionaries for messages instead of specialized types.

**UTF-8 Encoding**: Explicit encoding handling for cross-platform compatibility.


## Extending the Agent

Adding new tools is straightforward:

1. Define a tool function:
```python
def my_tool(input_data: Dict[str, Any]) -> str:
    # Tool implementation
    return "result"
```

2. Create a tool definition:
```python
MY_TOOL_DEFINITION = ToolDefinition(
    name="my_tool",
    description="What this tool does and when to use it",
    input_schema={
        "type": "object",
        "properties": {
            "param": {"type": "string", "description": "Parameter description"}
        },
        "required": ["param"]
    },
    function=my_tool
)
```

3. Add to the tools list:
```python
tools = [READ_FILE_DEFINITION, LIST_FILES_DEFINITION, EDIT_FILE_DEFINITION, MY_TOOL_DEFINITION]
```



## Acknowledgments

Based on "How to Build an Agent" by Thorsten Ball (April 15, 2025). The original Go implementation and tutorial provided the foundation for this Python port.
