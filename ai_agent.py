import os
import sys
import subprocess
import json
import argparse
import requests
import re
import platform
from typing import List, Dict, Any, Optional, Tuple
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Default to Gemini
DEFAULT_API = "gemini"

class TaskAgent:
    def __init__(self, api_type: str = DEFAULT_API):
        self.api_type = api_type
        self.api_key = self._get_api_key()
        self.is_windows = platform.system() == "Windows"

    def _get_api_key(self) -> str:
        if self.api_type == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not set. Please add it to your .env file.")
            return api_key
        elif self.api_type == "gemini":
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY not set. Please add it to your .env file.")
            return api_key
        raise ValueError(f"Unsupported API type: {self.api_type}")

    def generate_plan(self, task_description: str, feedback: Optional[str] = None) -> List[Dict[str, str]]:
        context = task_description
        if feedback:
            context += f"\n\nPrevious attempt feedback: {feedback}"

        # Add specific instructions for C/C++ prompt output handling
        file_creation_hint = (
            "For file creation: Use 'touch' only for empty files. "
            "For files that need content, use 'WRITE_FILE:filename:content' as a special command. "
            "For C/C++ programs, always include 'fflush(stdout);' after printf statements without newlines to ensure prompts are displayed. "
            "For C++ programs, use 'std::cout << ... << std::flush;' to ensure output is displayed immediately."
        )
        
        os_hint = (
            "This is a Windows system using cmd.exe. Avoid using bash-specific syntax."
            if self.is_windows else
            "This is a Unix-like system. Use standard bash commands."
        )
        
        context += f"\n\nImportant notes: {file_creation_hint} {os_hint}"

        if self.api_type == "openai":
            return self._generate_plan_openai(context)
        elif self.api_type == "gemini":
            return self._generate_plan_gemini(context)
        raise ValueError(f"Unsupported API type: {self.api_type}")

    def _generate_plan_openai(self, context: str) -> List[Dict[str, str]]:
        prompt = f"""
        You are an AI agent that generates executable commands for a computer.
        Based on the task description, generate a sequence of commands to achieve the task.
        
        IMPORTANT GUIDELINES:
        1. For empty files use: 'touch filename'
        2. For files that need content, use this special format: 
           WRITE_FILE:filename:file_content_here
           (This is a special command our system understands)
        3. For C programs:
           - Always add 'fflush(stdout);' after printf statements without newlines
           - Example: printf("Enter number: "); fflush(stdout);
        4. For C++ programs:
           - Use 'std::cout << "Prompt: " << std::flush;' for immediate display
        5. Include proper compilation commands with appropriate flags
        
        For each step include:
        1. A description of what the command does
        2. The exact command to run

        Task: {context}

        Format your response as a JSON array of objects with 'description' and 'command' keys.
        Example:
        [
            {{"description": "Create a directory for the project", "command": "mkdir project"}},
            {{"description": "Create a C file with proper output handling", "command": "WRITE_FILE:add.c:#include <stdio.h>\\n\\nint main() {{\\n    int a, b;\\n    printf(\\"Enter first number: \\"); fflush(stdout);\\n    scanf(\\"%d\\", &a);\\n    printf(\\"Enter second number: \\"); fflush(stdout);\\n    scanf(\\"%d\\", &b);\\n    printf(\\"Sum: %d\\n\\", a+b);\\n    return 0;\\n}}"}},
            {{"description": "Compile the C program", "command": "gcc -o add add.c"}},
            {{"description": "Run the program", "command": "./add"}}
        ]
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2
        }
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        if response.status_code != 200:
            print(f"Error: API returned status code {response.status_code}")
            print(response.text)
            return []

        result = response.json()
        content = result["choices"][0]["message"]["content"]

        try:
            json_match = re.search(r'\[\s*{.*}\s*\]', content, re.DOTALL)
            if json_match:
                content = json_match.group(0)
            return json.loads(content)
        except json.JSONDecodeError as e:
            print(f"Error parsing API response: {e}")
            print(f"Raw response: {content}")
            return []

    def _generate_plan_gemini(self, context: str) -> List[Dict[str, str]]:
        prompt = f"""
        You are an AI agent that generates executable commands for a computer.
        Based on the task description, generate a sequence of commands to achieve the task.
        
        IMPORTANT GUIDELINES:
        1. For empty files use: 'touch filename'
        2. For files that need content, use this special format: 
           WRITE_FILE:filename:file_content_here
           (This is a special command our system understands)
        3. For C programs:
           - Always add 'fflush(stdout);' after printf statements without newlines
           - Example: printf("Enter number: "); fflush(stdout);
        4. For C++ programs:
           - Use 'std::cout << "Prompt: " << std::flush;' for immediate display
        5. Include proper compilation commands with appropriate flags
        
        For each step include:
        1. A description of what the command does
        2. The exact command to run

        Task: {context}

        Format your response as a JSON array of objects with 'description' and 'command' keys.
        Example:
        [
            {{"description": "Create a directory for the project", "command": "mkdir project"}},
            {{"description": "Create a C file with proper output handling", "command": "WRITE_FILE:add.c:#include <stdio.h>\\n\\nint main() {{\\n    int a, b;\\n    printf(\\"Enter first number: \\"); fflush(stdout);\\n    scanf(\\"%d\\", &a);\\n    printf(\\"Enter second number: \\"); fflush(stdout);\\n    scanf(\\"%d\\", &b);\\n    printf(\\"Sum: %d\\n\\", a+b);\\n    return 0;\\n}}"}},
            {{"description": "Compile the C program", "command": "gcc -o add add.c"}},
            {{"description": "Run the program", "command": "./add"}}
        ]
        Return ONLY the JSON array and no other text.
        """
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.2,
                "topK": 32,
                "topP": 1,
                "maxOutputTokens": 1024
            }
        }

        model = "gemini-2.0-flash"
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"

        print(f"Querying Gemini model: {model}")
        response = requests.post(api_url, headers=headers, json=payload)

        if response.status_code != 200:
            print(f"Error: API returned status code {response.status_code}")
            print(response.text)
            return []

        result = response.json()

        try:
            content = result["candidates"][0]["content"]["parts"][0]["text"]
            json_match = re.search(r'\[\s*{.*}\s*\]', content, re.DOTALL)
            if json_match:
                content = json_match.group(0)
            content = content.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(content)
            return parsed if isinstance(parsed, list) else []
        except (KeyError, json.JSONDecodeError) as e:
            print(f"Error parsing Gemini response: {e}")
            print(f"Raw response: {json.dumps(result, indent=2)}")
            return []

    def _write_file(self, filename: str, content: str) -> bool:
        """Write content to a file."""
        try:
            # Create directory if it doesn't exist
            directory = os.path.dirname(filename)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error writing file {filename}: {e}")
            return False

    def display_plan(self, plan: List[Dict[str, str]]) -> None:
        print("\n📋 Generated Task Plan:")
        print("=" * 50)
        for i, step in enumerate(plan, 1):
            print(f"Step {i}:")
            print(f"  Description: {step['description']}")
            
            # Handle special file writing commands for display
            if step['command'].startswith("WRITE_FILE:"):
                parts = step['command'].split(':', 2)
                if len(parts) >= 3:
                    filename = parts[1]
                    content = parts[2]
                    # Truncate content display if too long
                    if len(content) > 100:
                        content = content[:100] + "..."
                    print(f"  Command: Write content to {filename}")
                    print(f"  Content preview: {content}")
                else:
                    print(f"  Command: {step['command']}")
            else:
                print(f"  Command: {step['command']}")
            
            print("-" * 50)

    def get_approval(self) -> bool:
        while True:
            response = input("\nDo you approve this plan? (y/n): ").strip().lower()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False

    def execute_plan(self, plan: List[Dict[str, str]]) -> List[Tuple[Dict[str, str], bool, str]]:
        results = []
        for i, step in enumerate(plan, 1):
            command = step['command']
            print(f"\nExecuting Step {i}: {step['description']}")
            
            # Handle special file writing command
            if command.startswith("WRITE_FILE:"):
                parts = command.split(':', 2)
                if len(parts) >= 3:
                    filename = parts[1]
                    content = parts[2]
                    print(f"Writing content to {filename}")
                    success = self._write_file(filename, content)
                    if success:
                        print(f"✅ Successfully created {filename}")
                        results.append((step, True, f"Created {filename}"))
                    else:
                        print(f"❌ Failed to create {filename}")
                        results.append((step, False, f"Failed to create {filename}"))
                        break
                else:
                    print(f"❌ Invalid WRITE_FILE command format")
                    results.append((step, False, "Invalid WRITE_FILE command format"))
                    break
            else:
                # Regular command execution
                print(f"Command: {command}")
                try:
                    # Use interactive mode for program execution to handle stdio properly
                    if self._is_program_execution(command):
                        print("\n--- Program Output Start ---")
                        # Run process with interactive stdin/stdout for program execution
                        process = subprocess.Popen(
                            command, 
                            shell=True,
                            stdin=None,  # Use terminal's stdin
                            stdout=None, # Use terminal's stdout
                            stderr=None, # Use terminal's stderr
                            text=True
                        )
                        process.wait()
                        print("--- Program Output End ---\n")
                        results.append((step, process.returncode == 0, "Interactive execution"))
                        if process.returncode != 0:
                            print(f"❌ Program exited with code {process.returncode}")
                            break
                    else:
                        # Standard command execution for non-program commands
                        output = subprocess.run(
                            command, 
                            shell=True, 
                            check=True, 
                            text=True, 
                            capture_output=True
                        )
                        print(f"✅ Success")
                        if output.stdout.strip():
                            print("Output:")
                            for line in output.stdout.strip().split('\n'):
                                print(f"  {line}")
                        results.append((step, True, output.stdout))
                except subprocess.CalledProcessError as e:
                    print(f"❌ Error executing command:")
                    if e.stderr:
                        for line in e.stderr.strip().split('\n'):
                            print(f"  {line}")
                    results.append((step, False, e.stderr))
                    break
                
        return results
    
    def _is_program_execution(self, command: str) -> bool:
        """Check if the command is executing a program rather than a shell command."""
        # List of shell commands that shouldn't trigger interactive mode
        shell_commands = ["cd", "mkdir", "rm", "cp", "mv", "touch", "ls", "dir", "gcc", "g++", "make", "cmake"]
        
        # Clean the command for inspection (remove options, etc)
        cmd_parts = command.strip().split()
        if not cmd_parts:
            return False
            
        cmd_name = cmd_parts[0]
        if "/" in cmd_name or "\\" in cmd_name:  # Path-based command
            cmd_name = os.path.basename(cmd_name)
            
        # Check for typical program execution patterns
        if cmd_name.endswith(".exe") or cmd_name.startswith("./"):
            return True
        
        # Check if it's not a common shell command
        if cmd_name not in shell_commands and not cmd_name.startswith("git"):
            # Look for executable without path or extension (like "python" or a compiled binary)
            return "." not in cmd_name
            
        return False

    def check_success(self) -> bool:
        while True:
            response = input("\nWas the task successfully completed? (y/n): ").strip().lower()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False

    def get_feedback(self) -> str:
        print("\nPlease explain why the task failed or what needs to be fixed:")
        return input("> ").strip()

    def run_task(self, task_description: str) -> None:
        feedback = None
        success = False

        while not success:
            print(f"\n🤖 Processing task: {task_description}")
            plan = self.generate_plan(task_description, feedback)
            if not plan:
                print("Failed to generate a plan. Please try again with a clearer task description.")
                return
            self.display_plan(plan)
            if not self.get_approval():
                print("Plan rejected. Exiting.")
                return
            self.execute_plan(plan)
            success = self.check_success()
            if not success:
                feedback = self.get_feedback()
                print("Refining approach based on feedback...")
            else:
                print("✅ Task completed successfully!")

def main():
    parser = argparse.ArgumentParser(description='AI Task Agent')
    parser.add_argument('--api', type=str, default=DEFAULT_API, help=f'API to use (default: {DEFAULT_API})')
    args = parser.parse_args()

    print("=" * 50)
    print("🤖 AI Task Agent")
    print("=" * 50)

    try:
        agent = TaskAgent(api_type=args.api)
        task = input("Enter your task description: ")
        agent.run_task(task)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user. Exiting.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()