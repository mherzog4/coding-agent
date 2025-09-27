from dotenv import load_dotenv
import os
import json
from typing import Dict, Any, Callable, List
from pathlib import Path
from anthropic import Anthropic

load_dotenv()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")


def get_user_message():
    """Get user input from stdin, return (message, success)"""
    try:
        line = input()
        return line, True
    except EOFError:
        return "", False


class ToolDefinition:
    def __init__(
        self,
        name: str,
        description: str,
        input_schema: Dict[str, Any],
        function: Callable[[Dict[str, Any]], str],
    ):
        self.name = name
        self.description = description
        self.input_schema = input_schema
        self.function = function


def read_file(input_data: Dict[str, Any]) -> str:
    """Read the contents of a file"""
    path = input_data.get("path", "")
    try:
        with open(path, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"


def list_files(input_data: Dict[str, Any]) -> str:
    """List files and directories at a given path"""
    path = input_data.get("path", ".")

    try:
        files = []
        start_path = Path(path)

        for item in start_path.rglob("*"):
            try:
                rel_path = item.relative_to(start_path)

                if item.is_dir():
                    files.append(str(rel_path) + "/")
                else:
                    files.append(str(rel_path))
            except (OSError, ValueError):
                continue

        return json.dumps(files)

    except Exception as e:
        return f"Error listing files: {str(e)}"


def create_new_file(file_path: str, content: str) -> str:
    """Create a new file with the given content"""
    try:
        path = Path(file_path)

        path.parent.mkdir(parents=True, exist_ok=True)

        path.write_text(content, encoding="utf-8")

        return f"Successfully created file {file_path}"

    except Exception as e:
        return f"Failed to create file: {str(e)}"


def edit_file(input_data: Dict[str, Any]) -> str:
    """Edit a file by replacing old_str with new_str"""
    path = input_data.get("path", "")
    old_str = input_data.get("old_str", "")
    new_str = input_data.get("new_str", "")

    if not path or old_str == new_str:
        return "Error: invalid input parameters"

    try:
        try:
            with open(path, "r", encoding="utf-8") as file:
                content = file.read()
        except FileNotFoundError:
            if old_str == "":
                return create_new_file(path, new_str)
            else:
                return f"Error: file {path} not found"

        new_content = content.replace(old_str, new_str)

        if content == new_content and old_str != "":
            return "Error: old_str not found in file"

        with open(path, "w", encoding="utf-8") as file:
            file.write(new_content)

        return "OK"

    except Exception as e:
        return f"Error editing file: {str(e)}"


READ_FILE_DEFINITION = ToolDefinition(
    name="read_file",
    description="Read the contents of a given relative file path. Use this when you want to see what's inside a file. Do not use this with directory names.",
    input_schema={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "The relative path of a file in the working directory.",
            }
        },
        "required": ["path"],
    },
    function=read_file,
)


LIST_FILES_DEFINITION = ToolDefinition(
    name="list_files",
    description="List files and directories at a given path. If no path is provided, lists files in the current directory.",
    input_schema={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Optional relative path to list files from. Defaults to current directory if not provided.",
            }
        },
    },
    function=list_files,
)


EDIT_FILE_DEFINITION = ToolDefinition(
    name="edit_file",
    description="""Make edits to a text file.

Replaces 'old_str' with 'new_str' in the given file. 'old_str' and 'new_str' MUST be different from each other.

If the file specified with path doesn't exist, it will be created.
""",
    input_schema={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "The path to the file"},
            "old_str": {
                "type": "string",
                "description": "Text to search for - must match exactly and must only have one match exactly",
            },
            "new_str": {
                "type": "string",
                "description": "Text to replace old_str with",
            },
        },
        "required": ["path", "old_str", "new_str"],
    },
    function=edit_file,
)


class Agent:
    def __init__(self, client, get_user_message_func, tools=None):
        self.client = client
        self.get_user_message = get_user_message_func
        self.tools = tools or []

    def run(self):
        """Run the agent conversation loop"""
        conversation = []

        print("Chat with Claude (use 'ctrl-c' to quit)")

        read_user_input = True

        try:
            while True:
                if read_user_input:
                    print("\033[94mYou\033[0m: ", end="")
                    user_input, ok = self.get_user_message()
                    if not ok:
                        break

                    user_message = {"role": "user", "content": user_input}
                    conversation.append(user_message)

                message = self.run_inference(conversation)

                conversation.append({"role": "assistant", "content": message.content})

                tool_results = []
                for content in message.content:
                    if content.type == "text":
                        print(f"\033[93mClaude\033[0m: {content.text}")
                    elif content.type == "tool_use":
                        result = self.execute_tool(
                            content.id, content.name, content.input
                        )
                        tool_results.append(result)

                if len(tool_results) == 0:
                    read_user_input = True
                    continue

                read_user_input = False
                conversation.append({"role": "user", "content": tool_results})

        except KeyboardInterrupt:
            print("\nGoodbye!")
        except Exception as e:
            print(f"Error: {e}")

    def execute_tool(
        self, tool_id: str, name: str, input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a tool and return the result"""

        tool_def = None
        for tool in self.tools:
            if tool.name == name:
                tool_def = tool
                break

        if tool_def is None:
            return {
                "type": "tool_result",
                "tool_use_id": tool_id,
                "content": "tool not found",
                "is_error": True,
            }

        print(f"\033[92mtool\033[0m: {name}({json.dumps(input_data)})")

        try:
            response = tool_def.function(input_data)
            return {"type": "tool_result", "tool_use_id": tool_id, "content": response}
        except Exception as e:
            return {
                "type": "tool_result",
                "tool_use_id": tool_id,
                "content": str(e),
                "is_error": True,
            }

    def run_inference(self, conversation):
        """Make API call to Claude"""

        anthropic_tools = []
        for tool in self.tools:
            anthropic_tools.append(
                {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.input_schema,
                }
            )

        params = {
            "model": "claude-3-7-sonnet-20250219",
            "max_tokens": 1024,
            "messages": conversation,
        }

        if anthropic_tools:
            params["tools"] = anthropic_tools

        message = self.client.messages.create(**params)
        return message


def main():
    client = Anthropic(api_key=ANTHROPIC_API_KEY)

    tools = [READ_FILE_DEFINITION, LIST_FILES_DEFINITION, EDIT_FILE_DEFINITION]
    agent = Agent(client, get_user_message, tools)
    agent.run()


if __name__ == "__main__":
    main()
