import tomllib
import subprocess
import os
import sys
import argparse

def flatten_secrets(d, prefix=""):
    """
    Recursively flattens a dictionary into a list of (key, value) pairs.
    E.g., {'connections': {'gsheets': {'spreadsheet': '...'}}} 
    becomes [('CONNECTIONS_GSHEETS_SPREADSHEET', '...')]
    """
    flat = []
    for k, v in d.items():
        key = f"{prefix}_{k}".upper() if prefix else k.upper()
        if isinstance(v, dict):
            flat.extend(flatten_secrets(v, key))
        else:
            flat.append((key, str(v)))
    return flat

def set_heroku_config():
    parser = argparse.ArgumentParser(description="Set Heroku config vars from Streamlit secrets.")
    parser.add_argument("--app", help="Heroku app name (optional if running in a git repo linked to Heroku)")
    args = parser.parse_args()

    # Get the project root directory
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    secrets_path = os.path.join(root_dir, ".streamlit/secrets.toml")
    
    if not os.path.exists(secrets_path):
        print(f"Error: {secrets_path} not found.")
        sys.exit(1)

    print(f"Reading secrets from {secrets_path}...")
    
    with open(secrets_path, "rb") as f:
        try:
            secrets = tomllib.load(f)
        except Exception as e:
            print(f"Error parsing TOML: {e}")
            sys.exit(1)

    flat_secrets = flatten_secrets(secrets)
    
    if not flat_secrets:
        print("No secrets found to set.")
        return

    # Filter out empty or None values if any
    flat_secrets = [(k, v) for k, v in flat_secrets if v is not None]

    print(f"Found {len(flat_secrets)} variables. Setting them on Heroku...")

    # We run 'heroku config:set' with all variables at once
    cmd = ["heroku", "config:set"]
    if args.app:
        cmd.extend(["--app", args.app])
    
    for key, value in flat_secrets:
        cmd.append(f"{key}={value}")

    try:
        # Run the command
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()

        if process.returncode == 0:
            print("Successfully updated Heroku config vars.")
            if stdout:
                print(stdout)
        else:
            print("Error updating Heroku config vars:")
            if stderr:
                print(stderr)
            else:
                print(stdout)
            sys.exit(process.returncode)

    except FileNotFoundError:
        print("Error: 'heroku' command not found. Please ensure Heroku CLI is installed and in your PATH.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    set_heroku_config()
