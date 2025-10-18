import os
import json
import zipfile
import shutil
import tempfile
from typing import List, Dict, Any

def analyze_repository(repo_path: str) -> Dict[str, Any]:
    """
    Analyzes a repository to identify frontend and backend services.

    Args:
        repo_path: The path to the repository (can be a folder or a zip file).

    Returns:
        A dictionary with the analysis results.
    """
    services = []
    datastores = []

    # --- Path Correction for Windows ---
    # Replace backslashes with forward slashes for consistency
    repo_path = repo_path.replace('\\', '/')
    
    # --- ZIP File Handling ---
    if zipfile.is_zipfile(repo_path):
        # Create a temporary directory to extract the zip file
        temp_dir = tempfile.mkdtemp()
        try:
            with zipfile.ZipFile(repo_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            # Analyze the extracted contents
            services = _find_services(temp_dir)
        finally:
            # Clean up the temporary directory
            shutil.rmtree(temp_dir)
    # --- Directory Handling ---
    elif os.path.isdir(repo_path):
        services = _find_services(repo_path)
    # --- Error Handling for Invalid Paths ---
    else:
        raise ValueError(f"The provided path is not a valid directory or zip file: {repo_path}")

    return {
        "services": services,
        "datastores": datastores  # Placeholder for future implementation
    }

def _find_services(directory: str) -> List[Dict[str, Any]]:
    """
    Finds services in a given directory by looking for package.json files.
    """
    services = []
    # --- Recursive Directory Traversal ---
    for root, _, files in os.walk(directory):
        if "package.json" in files:
            package_json_path = os.path.join(root, "package.json")
            try:
                with open(package_json_path, "r", encoding='utf-8') as f:
                    package_data = json.load(f)
                
                # --- Dependency Analysis ---
                dependencies = package_data.get("dependencies", {})
                service_info = None

                # --- Service Type Determination ---
                if "react" in dependencies:
                    service_info = {
                        "name": package_data.get("name", os.path.basename(root)),
                        "path": os.path.relpath(root, directory).replace('\\', '/'),
                        "type": "frontend",
                        "port": 5173  # Default port for frontend
                    }
                elif "express" in dependencies:
                    service_info = {
                        "name": package_data.get("name", os.path.basename(root)),
                        "path": os.path.relpath(root, directory).replace('\\', '/'),
                        "type": "backend",
                        "port": 3000  # Default port for backend
                    }
                
                # --- Service Registration ---
                if service_info:
                    services.append(service_info)
            except json.JSONDecodeError:
                print(f"Warning: Could not parse JSON from {package_json_path}")
            except Exception as e:
                print(f"An error occurred while processing {package_json_path}: {e}")

    return services

if __name__ == '__main__':
    # This block provides an example of how to use the analyze_repository function.
    # It is executed only when the script is run directly.

    # --- Setup for Demonstration ---
    # Create a dummy repository structure for testing purposes
    test_repo_dir = "test_repo"
    if os.path.exists(test_repo_dir):
        shutil.rmtree(test_repo_dir)
    
    # Define paths for frontend and backend services
    frontend_dir = os.path.join(test_repo_dir, "my-react-app")
    backend_dir = os.path.join(test_repo_dir, "my-express-server")
    os.makedirs(frontend_dir)
    os.makedirs(backend_dir)

    # --- Dummy package.json Creation ---
    # Frontend package.json with 'react'
    frontend_pkg = {
        "name": "frontend-app",
        "dependencies": {"react": "18.2.0"}
    }
    with open(os.path.join(frontend_dir, "package.json"), "w") as f:
        json.dump(frontend_pkg, f, indent=2)

    # Backend package.json with 'express'
    backend_pkg = {
        "name": "backend-server",
        "dependencies": {"express": "4.18.2"}
    }
    with open(os.path.join(backend_dir, "package.json"), "w") as f:
        json.dump(backend_pkg, f, indent=2)

    print(f"Created dummy repository at: {os.path.abspath(test_repo_dir)}")

    # --- Analysis Execution ---
    # Analyze the created directory
    try:
        analysis_result = analyze_repository(test_repo_dir)
        print("\n--- Analysis Result ---")
        print(json.dumps(analysis_result, indent=4))
        print("-----------------------\n")
    except Exception as e:
        print(f"An error occurred during analysis: {e}")

    # --- Cleanup ---
    # Optional: Clean up the dummy repository
    # shutil.rmtree(test_repo_dir)
    # print("Cleaned up dummy repository.")
