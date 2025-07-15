import subprocess
import sys
import os

def export_likec4_diagrams():
    """
    Executes the LikeC4 CLI command to export all views as PNG images.
    """

    command = [
        "npx", 
        "likec4", 
        "export", 
        "png", 
        "-o", 
        "./dist/images"
    ]

    print(f"Running command: {' '.join(command)}")
    print("-" * 30)

    try:

        is_windows = sys.platform.startswith('win')
        result = subprocess.run(
            command, 
            check=True, 
            capture_output=True, 
            text=True, 
            shell=is_windows
        )

        # Print the standard output from the command
        print("Command executed successfully.")
        if result.stdout:
            print("\n--- LikeC4 Output ---\n")
            print(result.stdout)
        
        # In case there are warnings or other info on stderr but the command still succeeds
        if result.stderr:
            print("\n--- Stderr ---\n")
            print(result.stderr)

        print(f"\n✅ Success! Images saved to the '{os.path.join('dist', 'images')}' directory.")

    except FileNotFoundError:
        print("\n❌ ERROR: 'npx' command not found.")
        print("Please ensure that Node.js and npm are installed and accessible in your system's PATH.")
        sys.exit(1)
        
    except subprocess.CalledProcessError as e:
        # This block runs if the command returns a non-zero exit code (an error).
        print("\n❌ ERROR: The LikeC4 export command failed.")
        print(f"Return Code: {e.returncode}")
        
        if e.stdout:
            print("\n--- Standard Output ---\n")
            print(e.stdout)
        
        if e.stderr:
            print("\n--- Error Output ---\n")
            print(e.stderr)
        
        sys.exit(1)
        
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    export_likec4_diagrams()
