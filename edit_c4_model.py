import openai
import argparse
import os
from dotenv import load_dotenv # Import the load_dotenv function

# --- Load environment variables from .env file ---
# This should be called at the beginning of your script.
load_dotenv()

def edit_likec4_model(existing_model_path, edit_prompt, api_key):
    """
    Edits an existing C4 model file based on a user prompt.

    Args:
        existing_model_path (str): The file path to the existing .c4 model.
        edit_prompt (str): The user's instruction on what to change.
        api_key (str): Your OpenAI API key.

    Returns:
        str: The updated C4 model in LikeC4 DSL format, or an error message.
    """
    if not api_key:
        return "Error: OpenAI API key not found. Please set the OPENAI_API_KEY environment variable in your .env file."

    openai.api_key = api_key

    try:
        with open(existing_model_path, 'r') as f:
            existing_model_content = f.read()
    except FileNotFoundError:
        return f"Error: Input file not found at '{existing_model_path}'"
    except Exception as e:
        return f"Error reading file '{existing_model_path}': {e}"

    # Instruction prompt tailored for editing
    instruction_prompt = f"""
You are an expert software architect specializing in the LikeC4 DSL. Your task is to intelligently **edit** an existing LikeC4 model based on a user's request.

**Rules:**
1.  Carefully analyze the provided "EXISTING LikeC4 MODEL".
2.  Understand the user's "EDITING INSTRUCTIONS".
3.  Apply the requested changes to the model. This might involve adding, removing, or modifying elements, relationships, or views.
4.  Ensure the final output is a single, complete, and valid LikeC4 code block.
5.  **DO NOT** add any explanations, comments, or apologies in your response. Only output the raw, updated LikeC4 code.

--- EXISTING LikeC4 MODEL ---
```likec4
{existing_model_content}
```

--- EDITING INSTRUCTIONS ---
"{edit_prompt}"

Now, provide the complete and updated LikeC4 code block reflecting these changes.
"""

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert in modifying LikeC4 DSL code based on instructions. You will be given an existing model and an edit prompt, and you must return the complete, updated code."},
                {"role": "user", "content": instruction_prompt}
            ]
        )
        return _process_llm_response(response)
    except Exception as e:
        return f"An unexpected error occurred during editing: {e}"

def _process_llm_response(response):
    """Helper function to process the API response and clean the C4 code."""
    try:
        c4_code = response.choices[0].message.content.strip()

        # Clean up the response to remove markdown code block fences
        if c4_code.startswith("```likec4"):
            c4_code = c4_code[len("```likec4"):].strip()
        if c4_code.startswith("```"):
            c4_code = c4_code[len("```"):].strip()
        if c4_code.endswith("```"):
            c4_code = c4_code[:-len("```")].strip()

        # Basic validation for the LikeC4 format
        if 'model {' in c4_code and 'views {' in c4_code and 'specification {' in c4_code:
            return c4_code
        else:
            return f"Error: The model did not return valid LikeC4 code. Please check the response:\n{c4_code}"

    except openai.APIError as e:
        return f"Error: OpenAI API returned an API Error: {e}"
    except openai.APIConnectionError as e:
        return f"Error: Failed to connect to OpenAI API: {e}"
    except openai.RateLimitError as e:
        return f"Error: OpenAI API request exceeded rate limit: {e}"
    except Exception as e:
        return f"An unexpected error occurred while processing the response: {e}"

def save_to_file(content, filename):
    """Saves the given content to a file, creating the directory if it doesn't exist."""
    try:
        output_dir = os.path.dirname(filename)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            
        if not filename.endswith('.c4'):
            filename += '.c4'
            
        with open(filename, 'w') as f:
            f.write(content)
        print(f"✅ Successfully saved model to {filename}")
    except IOError as e:
        print(f"Error: Could not write to file {filename}. Reason: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Edit an existing C4 model file for the LikeC4 extension using a prompt. Assumes files are in the 'src' directory.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument(
        'input_file',
        metavar='INPUT_FILE',
        type=str,
        help="Name of the existing .c4 model file inside the 'src' directory."
    )
    parser.add_argument(
        'prompt',
        metavar='PROMPT',
        type=str,
        help='A descriptive prompt of the changes to make (e.g., "Add a Redis cache").'
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Name of the output .c4 file. It will be saved in the 'src' directory. \nIf not provided, the input file will be overwritten."
    )

    args = parser.parse_args()
    api_key = os.getenv("OPENAI_API_KEY")

    # --- UPDATED: Automatically handle 'src' directory path ---
    # Construct the full path for the input file
    input_file_path = args.input_file
    if not input_file_path.startswith(('src/', 'src\\')):
        input_file_path = os.path.join('src', input_file_path)

    print(f"⏳ Editing model '{input_file_path}' based on your prompt...")
    
    if not os.path.exists(input_file_path):
        print(f"❌ Error: Input file not found at '{input_file_path}'")
    else:
        c4_model_code = edit_likec4_model(input_file_path, args.prompt, api_key)
        
        if c4_model_code and not c4_model_code.startswith("Error"):
            # Determine the output path, ensuring it's in the 'src' directory
            if args.output:
                output_path = args.output
                if not output_path.startswith(('src/', 'src\\')):
                    output_path = os.path.join('src', output_path)
            else:
                # If no output is specified, use the full input path to overwrite
                output_path = input_file_path
            
            save_to_file(c4_model_code, output_path)
        else:
            print(f"\n❌ {c4_model_code}")
