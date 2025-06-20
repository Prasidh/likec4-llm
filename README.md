# 🔐 C4 Model to Firewall Documentation (LikeC4 + MCP + OpenAI)
This project uses a LikeC4-based architecture model to automatically generate network firewall documentation. The workflow uses an LLM (via OpenAI) to infer and describe necessary firewall rules by analyzing your system's relationships and producing clean, human-readable output in Markdown and JSON.

## ⚙️ Setup Instructions
### 1. 📦 Prerequisites
Make sure the following versions are installed on your system:

- Node.js: v22.16.0
- Python: 3.13.3
- VSCode with LikeC4 Extension installed

### 2. 📁 Project Structure
```
.
├── src/
│   └── cloud.c4          # Your LikeC4 source model with systems, nodes, and connections
├── dist/
│   ├── FirewallRules.md  # Auto-generated markdown table with firewall rules
│   └── firewall_rules.json # Auto-generated JSON representation of rules
├── mcp_client.py         # Python script that communicates with the MCP server
├── .env                  # Your local secrets and environment variables
├── package.json          # Node.js dependencies (for LikeC4 export, if needed)
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

### 3. 🧪 Virtual Environment & Python Dependencies
Use a virtual environment to isolate dependencies:

```bash
# Create virtual environment
python -m venv env

# Activate (Windows)
env\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

## ⚡ Setup MCP Server with LikeC4
1. Open the project in VSCode
2. Install the LikeC4 extension (from Marketplace)
3. Press `Ctrl + ,` to open Settings
4. Search for "mcp"
5. Open the LikeC4 section
6. Make sure ✅ Enable MCP Server is checked
7. Confirm the MCP server is using port `33335` (default)

Your config should look like:

```json
{
  "servers": {
    "likec4": {
      "type": "sse",
      "url": "http://localhost:33335/sse"
    }
  }
}
```

Update your `.env` file accordingly:

```ini
OPENAI_API_KEY="sk-YourOpenAIKeyHere"
OPENAI_MODEL="gpt-4o"  # or gpt-4o-mini, etc.
```

## 🚀 Run the MCP Client Script
Once everything is configured, generate your firewall documentation:

```bash
python mcp_client.py
```

This will:
- Connect to the MCP server via SSE
- Fetch the SimplifiedFirewallView view from your LikeC4 `.c4` model
- Extract all relationships (source → destination)
- Ask OpenAI to infer firewall rules (port, protocol, description)
- Save output to:
  - `dist/FirewallRules.md` (Markdown)
  - `dist/firewall_rules.json` (JSON)

## 📊 Example Output (Markdown)

| Source             | Port               | Destination               | Description                          |
|--------------------|--------------------|---------------------------|--------------------------------------|
| User Space (Dev)   | TCP 1024-1028      | vpc-cnc-aws-mms-dev-lops  | Mongo Atlas (TCP 1024-1028)          |
| Server Space (Dev) | TCP 1024-1028,9226 | vpc-cnc-aws-mms-dev-lops  | Mongo Atlas (TCP 1024-1028, 9226)    |

## 🧠 Powered By
- LikeC4 — visual modeling for modern architecture
- OpenAI GPT — inference for rule generation
- VSCode MCP Extension

## 🙌 Contributions
Feel free to fork, submit PRs, or open issues for improvements. This tool was built to automate and simplify cloud firewall documentation using AI.
