import os
import requests
import json

def parse_ollama_response(response: str) -> dict:
    # Handle multi-part JSON-like response
    json_objects = []
    for line in response.text.splitlines():
        if line.strip():  # Skip empty lines
            try:
                json_objects.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"Skipping invalid line: {line}. Error: {e}")
    return json_objects

def call_ollama_api(model_name: str, prompt: str, api_url: str = "http://localhost:11434/api/generate") -> dict:
    """
    Calls the Ollama API to generate text from a given model and prompt.

    :param model_name: The name of the model to use (e.g., 'llama2').
    :param prompt: The input text prompt for the model.
    :param api_url: The API endpoint for Ollama (default is https://localhost:11434/api/generate).
    :return: A dictionary containing the API response.
    """
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "model": model_name,
        "prompt": prompt
    }

    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        parsedresponse = parse_ollama_response(response)
        # return parsedresponse.json()
        return parsedresponse

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        raise {"error": str(e)}

def check_model_exists(model_name: str, api_url: str = "http://localhost:11434/api/tags") -> bool:
    """
    Checks if a specified model exists on the Ollama API.

    :param model_name: The name of the model to check.
    :param api_url: The API endpoint for listing available models (default is http://localhost:11434/api/models).
    :return: True if the model exists, False otherwise.
    """
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        models = response.json().get("models", [])
        model_names = [model["name"].split(":")[0] for model in models]
        return model_name in model_names
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while checking the model: {e}")
        raise {"error": str(e)}
    
def download_ollama_model(model_name: str, api_url: str = "http://localhost:11434/api/pull") -> dict:
    """
    Downloads a specified model from the Ollama API.

    :param model_name: The name of the model to download (e.g., 'llama2').
    :param api_url: The API endpoint for downloading models (default is http://localhost:11434/api/pull).
    :return: A dictionary containing the API response.
    """
    if check_model_exists(model_name):
        print(f"Model '{model_name}' already exist.")
        return 0
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "model": model_name
    }
    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        parsedresponse = parse_ollama_response(response)
        return parsedresponse
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        raise {"error": str(e)}

def summarize_repository(file_summaries):
    # Run the command to get the summary from Ollama
    # model = "deepseek-r1"
    model = "deepseek-coder-v2"
    download_ollama_model(model)
    prompt_text = f"Summarize the following for a readme.md:\n{file_summaries}"
    result = call_ollama_api(model, prompt_text)
    return result

def main():
    folder_path = os.getenv('GITHUB_WORKSPACE')
    summaries = {}
    CODE_FILE_EXTENSIONS = {
        # Web Development
        ".html",    # HTML files
        ".htm",     # Alternative HTML extension
        ".css",     # CSS stylesheets
        ".scss",    # SASS stylesheets
        ".less",    # LESS stylesheets
        ".js",      # JavaScript
        ".jsx",     # React JavaScript
        ".ts",      # TypeScript
        ".tsx",     # React TypeScript
        ".php",     # PHP scripts
        ".asp",     # Active Server Pages
        ".aspx",    # ASP.NET pages
        ".vue",     # Vue.js components
        ".svelte",  # Svelte components

        # General Programming
        ".py",      # Python
        ".pyc",     # Compiled Python
        ".java",    # Java
        ".class",   # Compiled Java
        ".cs",      # C#
        ".cpp",     # C++
        ".cc",      # Alternative C++ extension
        ".c",       # C
        ".h",       # C/C++ header files
        ".hpp",     # C++ header files
        ".go",      # Go
        ".rs",      # Rust
        ".rb",      # Ruby
        ".pl",      # Perl
        ".swift",   # Swift
        ".kt",      # Kotlin
        ".m",       # Objective-C/MATLAB
        ".scala",   # Scala
        ".erl",     # Erlang
        ".ex",      # Elixir
        ".elm",     # Elm
        ".lua",     # Lua
        ".r",       # R
        ".sh",      # Shell scripts
        ".bash",    # Bash scripts
        ".ps1",     # PowerShell scripts

        # Database
        ".sql",     # SQL scripts
        ".psql",    # PostgreSQL scripts
        ".tsql",    # T-SQL scripts

        # Configuration & Data
        ".json",    # JSON files
        ".xml",     # XML files
        ".yaml",    # YAML files
        ".yml",     # Alternative YAML extension
        ".toml",    # TOML files
        ".ini",     # INI configuration files
        ".conf",    # Configuration files
        ".env",     # Environment variables

        # Documentation
        ".md",      # Markdown
        ".rst",     # reStructuredText
        ".tex",     # LaTeX
        ".adoc",    # AsciiDoc

        # Mobile Development
        ".swift",   # iOS Swift
        ".kt",      # Android Kotlin
        ".gradle",  # Gradle build files
        ".plist",   # iOS property lists

        # Game Development
        ".unity",   # Unity scripts
        ".gd",      # Godot scripts
        ".cs",      # Unity C# scripts
        ".lua",     # Game scripting

        # Build & Package
        ".cmake",   # CMake files
        ".make",    # Makefiles
        ".rake",    # Ruby make
        ".gemspec", # Ruby gem specifications
        ".nuspec",  # NuGet specifications
    }

    # Iterate over all files in the directory
    for root, dirs, files in os.walk(folder_path):
        # Skip .git folders
        if '.git' in root.split(os.sep):
            continue

        for file in files:
            # Ignore files without valid code extensions
            if not any(file.endswith(ext) for ext in CODE_FILE_EXTENSIONS):
                continue

            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    summary = f.read()
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                continue

            if summary:
                summaries[file_path] = summary

    # Get the repository-level summary from Ollama
    repo_summary = summarize_repository(summaries)
    if repo_summary:
        summary_file_path = os.path.join(folder_path, "readme.md")
        try:
            with open(summary_file_path, 'w', encoding='utf-8') as summary_file:
                summary_file.write(summary)
            print(f"Summaries written to {summary_file_path}")
        except Exception as e:
            print(f"Error writing summary file: {e}")

if __name__ == "__main__":
    main()
