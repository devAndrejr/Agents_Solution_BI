import os

def get_project_root():
    return os.path.abspath(os.path.dirname(__file__))

def identify_files_for_cleanup():
    project_root = get_project_root()

    # Directories and files to keep (based on README and common project structure)
    # This list is more about what *should* be there, rather than what to explicitly keep.
    # The focus is on identifying what to *remove*.
    core_project_elements = [
        '.env',
        '.gitignore',
        'auth_users.db',
        'auth.py',
        'pytest.ini',
        'README.md',
        'requirements.in',
        'requirements.txt',
        'run_app.py', # Can be kept for convenience
        'streamlit_app.py',
        'ui_components.py',
        'core/',
        'data/',
        'docs/',
        'generated_charts/',
        'logs/',
        'pages/',
        'scripts/',
        'tests/',
        '.github/workflows/ci.yml',
    ]

    # Directories and files commonly considered temporary, cache, or non-essential for core application
    # These are candidates for deletion.
    candidates_for_deletion = [
        '__pycache__/',
        '.mypy_cache/',
        '.pytest_cache/',
        'pytest-cache-files-l2wg2ocd/',
        'venv/', # Virtual environment, can be recreated
        'desktop.ini', # Windows system file
        '.github/desktop.ini', # Windows system file
        '.github/workflows/desktop.ini', # Windows system file
        'final_cleanup_temp.py', # Self-cleaning script
        'inspect_parquet.py', # Utility script, not core app
        'secao.txt', # Log/session transcript
    ]

    # Convert to absolute paths for clarity in output
    full_paths_to_delete = []
    for item in candidates_for_deletion:
        full_paths_to_delete.append(os.path.join(project_root, item))

    return full_paths_to_delete

def generate_cleanup_script(files_to_delete, script_name="delete_unnecessary_files.bat"):
    project_root = get_project_root()
    script_path = os.path.join(project_root, script_name)

    # Use 'del' for files and 'rmdir /s /q' for directories on Windows
    # For cross-platform, could use 'rm -rf' but user specified win32
    script_content = """@echo off
"""
    script_content += "echo This script will delete the following files and directories:\n"
    for item_path in files_to_delete:
        script_content += f"echo - {item_path}\n"
    script_content += "\n"
    script_content += "pause\n" # Pause to allow user to review

    for item_path in files_to_delete:
        if item_path.endswith('/') or os.path.isdir(item_path): # Check if it's a directory
            script_content += f"echo Deleting directory: {item_path}\n"
            script_content += f"rmdir /s /q \"{item_path}\"\n"
        else: # Assume it's a file
            script_content += f"echo Deleting file: {item_path}\n"
            script_content += f"del /f /q \"{item_path}\"\n"
    
    script_content += "\n"
    script_content += "echo Cleanup complete.\n"
    script_content += "pause\n"

    with open(script_path, 'w') as f:
        f.write(script_content)
    print(f"Cleanup script generated at: {script_path}")
    print("Please review the script content before running it.")
    print("To run, open Command Prompt or PowerShell, navigate to the project root, and execute:")
    print(f"  {script_name}")

if __name__ == "__main__":
    print("Identifying files and directories for cleanup...")
    files_to_delete = identify_files_for_cleanup()

    if files_to_delete:
        print("\n--- Files and Directories Recommended for Deletion ---")
        for f in files_to_delete:
            print(f"- {f}")
        print("\n--- Action ---")
        generate_cleanup_script(files_to_delete)
    else:
        print("No unnecessary files or directories identified for cleanup.")