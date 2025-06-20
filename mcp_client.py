import asyncio
import pathlib
import json
import logging
from openai import OpenAI
from dotenv import load_dotenv
import os
from mcp.client.sse import sse_client
from mcp.client.session import ClientSession
# 🔧 Setup logging without timestamps
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)

# 📥 Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL")
PORT= os.getenv("PORT", "33335")

if not OPENAI_API_KEY or not OPENAI_MODEL:
    raise RuntimeError("Missing OPENAI_API_KEY or OPENAI_MODEL in .env")

client = OpenAI(api_key=OPENAI_API_KEY)

# 🔌 Get SimplifiedFirewallView content
async def fetch_simplified_view():
    async with sse_client(f"http://localhost:{PORT}/sse") as (reader, writer):
        async with ClientSession(reader, writer) as session:
            logging.info("Calling read-view tool for 'SimplifiedFirewallView'")
            result = await session.call_tool("read-view", {"id": "SimplifiedFirewallView"})
            view_text = result.content[0].text
            logging.info("View content received.")
            return view_text

# 🔍 Extract elements and relationships from view
def parse_c4_view(text: str):
    logging.info("Parsing view content...")
    
    try:
        view_json = json.loads(text)
    except json.JSONDecodeError:
        logging.error("Failed to parse view content as JSON.")
        return {"elements": {}, "relationships": []}

    elements = {}
    relationships = []

    for node in view_json.get("nodes", []):
        elem_id = node.get("id")
        title = node.get("title")
        represents = node.get("represents", {}).get("element")
        if elem_id and represents:
            elements[elem_id] = {
                "id": elem_id,
                "title": title,
                "kind": "unknown",
                "description": ""
            }

    logging.info(f"Parsed {len(elements)} elements.")
    return {"elements": elements, "relationships": relationships}

def save_firewall_outputs(firewall_rules: list):
    # Save JSON file
    json_path = pathlib.Path("dist/firewall_rules.json")
    with open(json_path, "w") as jf:
        json.dump({"firewall_rules": firewall_rules}, jf, indent=2)
    logging.info(f"Saved firewall rules to {json_path}")

    # Create Markdown table
    md_lines = [
        "| Source | Port | Destination | Description |",
        "|--------|------|-------------|-------------|"
    ]
    for rule in firewall_rules:
        src = rule.get("source", "")
        dest = rule.get("target", "")
        desc = rule.get("purpose", "")
        port = f"{rule.get('protocol', '')} {rule.get('port', '')}".strip()
        md_lines.append(f"| {src} | {port} | {dest} | {desc} |")

    md_path = pathlib.Path("dist/FirewallRules.md")
    with open(md_path, "w") as mf:
        mf.write("\n".join(md_lines))
    logging.info(f"Saved firewall rules to {md_path}")

# 🤖 Generate firewall table with OpenAI
def generate_firewall_json(data: dict) -> list:
    logging.info("Sending data to OpenAI to generate firewall rules...")

    system_prompt = "You are a security assistant that generates firewall rules in JSON."
    user_prompt = f"""
Given system elements and network connections, generate a JSON array of firewall rules.
Each rule should contain: source, target, port, protocol, and purpose.

Elements:
{json.dumps(data['elements'], indent=2)}

Connections:
{json.dumps(data['relationships'], indent=2)}

If port/protocol is not clearly stated, guess common ones. Format like:
{{ "firewall_rules": [{{"source": "...", "target": "...", "port": "...", "protocol": "...", "purpose": "..."}}] }}
"""

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        model=OPENAI_MODEL,
        response_format={"type": "json_object"}
    )

    logging.info("✅ JSON response received from OpenAI.")
    return json.loads(chat_completion.choices[0].message.content)

# 🚀 Main flow
def main():
    view_text = asyncio.run(fetch_simplified_view())
    print("\n📄 Simplified Firewall View Content:\n")
    print(view_text)
    parsed_data = parse_c4_view(view_text)
    print("\n🔍 Parsed Elements and Relationships:\n")
    print(json.dumps(parsed_data, indent=2))
    response = generate_firewall_json(parsed_data)

    print("\n📋 Generated Firewall Rules:\n")
    for rule in response.get("firewall_rules", []):
        print(f"- {rule['source']} ➡ {rule['target']} ({rule['protocol']}:{rule['port']}) — {rule['purpose']}")

    # Save to files
    save_firewall_outputs(response.get("firewall_rules", []))

if __name__ == "__main__":
    main()
