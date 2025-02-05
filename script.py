import os
import subprocess

def summarize_content(file_path):
    # Run the command to get the summary from Ollama
    result = subprocess.run(['ollama', 'summarize', file_path], capture_output=True, text=True)
    if result.returncode == 0:
        return result.stdout
    else:
        print(f"Error processing {file_path}: {result.stderr}")
        return None

def summarize_repository():
    # Run the command to get the repository-level summary from Ollama
    repo_summary = subprocess.run(['ollama', 'summarize', '.'], capture_output=True, text=True)
    if repo_summary.returncode == 0:
        return repo_summary.stdout
    else:
        print("Error getting repository-level summary:", repo_summary.stderr)
        return None

def main():
    repo_root = os.getenv('GITHUB_WORKSPACE')
    summaries = {}
    
    # Iterate over all files in the repository and summarize each one
    for root, dirs, files in os.walk(repo_root):
        for file in files:
            if file.endswith('.txt'):  # Adjust this to match your file types
                file_path = os.path.join(root, file)
                summary = summarize_content(file_path)
                if summary:
                    summaries[file] = summary
    
    # Get the repository-level summary from Ollama
    repo_summary = summarize_repository()
    if repo_summary:
        print("Repository Summary:\n", repo_summary)
        summaries['repo_summary'] = repo_summary
    
    # Output the summaries (for now just print them; you can format this as needed)
    for file, summary in summaries.items():
        print(f"File: {file}\nSummary: {summary}\n")

if __name__ == "__main__":
    main()
