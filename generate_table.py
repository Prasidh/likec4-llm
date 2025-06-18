import os
import json
import re
import subprocess
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

# Configuration constants
MODEL_JSON_PATH = Path('./dist/model.json')
TABLE_OUTPUT_PATH = Path('./dist/FirewallRules.md')
OPENAI_MODEL = "gpt-4o-mini-2024-07-18"

client = None

def configure_llm():
    """Load environment variables and configure the OpenAI client."""
    global client
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found. Please add it to your .env file.")
    client = OpenAI(api_key=api_key)
    print("OpenAI client configured successfully.")

def export_model_to_json():
    """Exports the LikeC4 model to a JSON file by running the npm script."""
    print("Step 1: Exporting LikeC4 model to JSON via npm script...")
    if not Path('./package.json').exists():
        raise FileNotFoundError("package.json not found. This script must be run from the project root.")

    DIST_DIR = Path('./dist')
    DIST_DIR.mkdir(exist_ok=True)
    command = "npm run export:json"

    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, check=True
        )
        if result.stderr:
            print(f"[npm script stderr]:\n{result.stderr}")
        print(f"Model exported successfully to {MODEL_JSON_PATH}")
    except subprocess.CalledProcessError as e:
        print(f"Error exporting LikeC4 model. Return code: {e.returncode}")
        print(f"Stdout: {e.stdout}\nStderr: {e.stderr}")
        raise

def get_structured_model_data():
    """
    Reads model.json and intelligently filters the data to only include elements
    that are part of a relationship, reducing the prompt size and complexity for the LLM.
    """
    print("Step 2: Parsing and intelligently filtering model.json...")
    if not MODEL_JSON_PATH.exists():
        raise FileNotFoundError(f"'{MODEL_JSON_PATH}' not found. Please run 'npm run export:json' first.")

    with open(MODEL_JSON_PATH, 'r', encoding='utf-8') as f:
        model = json.load(f)

    all_elements = model.get('elements', {})
    involved_element_ids = set()
    relationships = []

    # The 'relations' object in the JSON contains nested source/target objects.
    for rel_id, details in model.get('relations', {}).items():
        # FIXED: Extract the 'model' key which holds the element ID string.
        # This resolves the "unhashable type: 'dict'" error.
        source_id = details.get('source', {}).get('model')
        target_id = details.get('target', {}).get('model')

        if source_id and target_id:
            involved_element_ids.add(source_id)
            involved_element_ids.add(target_id)
            relationships.append({
                "source": source_id,
                "target": target_id,
                "description": details.get('title', 'No description')
            })

    # Now, filter the elements to include only those that are part of a relationship.
    filtered_elements = {
        element_id: {
            "title": details.get('title'),
            "kind": details.get('kind'),
            "description": details.get('description'),
            "technology": details.get('technology')
        }
        for element_id, details in all_elements.items()
        if element_id in involved_element_ids
    }

    if not relationships:
        print("Warning: No relationships found in the model. The output will be empty.")

    return {"elements": filtered_elements, "relationships": relationships}

def call_openai_llm_for_json(connections_data: dict):
    """
    Sends the pre-processed and filtered connection data to OpenAI and asks it to infer firewall rules.
    """
    print(f"Step 3: Sending request to OpenAI LLM ({OPENAI_MODEL}) for firewall rule generation...")
    if not client:
        raise ValueError("OpenAI client is not configured. Run configure_llm() first.")

    system_prompt = (
        "You are a senior network security engineer. Your task is to analyze a structured JSON "
        "object describing system architecture and generate a precise list of firewall rules. "
        "You will respond ONLY with a valid JSON object containing a single key 'rules', which is a list of rule objects."
    )

    user_prompt = f"""
Analyze the following architecture data and generate a list of firewall rules.

Follow these instructions exactly:
1.  **Identify Source and Destination**: For each relationship, find the corresponding source and target elements in the `elements` dictionary. You MUST parse the `description` field of each element to find the 'Network ID:'. Use that ID as the value for the 'source' and 'destination' fields in the final rule.
2.  **Identify Port and Protocol**: Infer the port and protocol directly from the relationship's `description` field. The format is typically 'Description (PROTOCOL PORT)'. Extract this information accurately (e.g., 'connects (TCP 443)' -> 'TCP 443'). If a port cannot be determined, use 'Any'.
3.  **Use Relationship Description**: The `description` for each rule must be the full `description` from the corresponding relationship.
4.  **Format Output**: The final output must be a JSON object with a single key "rules", which contains a list of rule objects.

The response must conform to this JSON schema:
{{
  "rules": [
    {{
      "source": "string",
      "destination": "string",
      "port": "string",
      "description": "string"
    }}
  ]
}}

Here is the filtered architecture data:
{json.dumps(connections_data, indent=2)}

Generate the completed JSON object now.
"""

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            model=OPENAI_MODEL,
            response_format={"type": "json_object"}
        )
        print("JSON response received from LLM.")
        response_content = chat_completion.choices[0].message.content
        return json.loads(response_content)
    except Exception as e:
        print(f"An error occurred while calling the OpenAI API: {e}")
        raise

def format_json_to_markdown(rules_json: dict) -> str:
    """Converts the JSON list of rules from the LLM into a Markdown table."""
    print("Step 4: Formatting JSON data into a Markdown table...")
    rules = rules_json.get("rules", [])
    if not rules:
        return "No rules were generated by the LLM."

    header = "| Source | Port | Destination | Description |\n"
    separator = "|--------|------|-------------|-------------|\n"

    rows = [
        f"| {rule.get('source', 'N/A')} | {rule.get('port', 'N/A')} | {rule.get('destination', 'N/A')} | {rule.get('description', 'N/A')} |"
        for rule in rules
    ]

    return header + separator + "\n".join(rows) + "\n"

def save_table(markdown_table: str):
    """Saves the generated markdown table to a file."""
    print(f"Step 5: Saving table to {TABLE_OUTPUT_PATH}...")
    try:
        with open(TABLE_OUTPUT_PATH, 'w', encoding='utf-8') as f:
            f.write(markdown_table)
        print("Table saved successfully!")
    except IOError as e:
        print(f"Error saving table file: {e}")
        raise

def main():
    """Main function to run the documentation generation pipeline."""
    try:
        configure_llm()
        export_model_to_json()
        connections_data = get_structured_model_data()

        if not connections_data.get("relationships"):
            print("Execution stopped because no relationships were found in the model.")
            save_table("No rules could be generated because the C4 model does not contain any relationships.")
            return

        rules_as_json = call_openai_llm_for_json(connections_data)
        markdown_table = format_json_to_markdown(rules_as_json)
        save_table(markdown_table)

        print("\n--- Generated Table ---")
        print(markdown_table)
        print(f"--- End of Table --- (Saved to {TABLE_OUTPUT_PATH})")
    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()