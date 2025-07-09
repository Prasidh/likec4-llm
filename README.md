
# 🔐 C4 Model to Firewall Documentation (LikeC4 + MCP + OpenAI)

This project uses a LikeC4-based architecture model to automatically generate network firewall documentation. The workflow leverages a large language model (via OpenAI) to infer and describe firewall rules by analyzing your system's architecture and generating human-readable documentation in Markdown and JSON formats.

---

## ⚙️ Setup Instructions

### 1. 📦 Prerequisites

Make sure the following versions are installed on your system:

- Node.js: v22.16.0  
- Python: 3.13.3  
- VSCode with LikeC4 Extension installed

---

### 2. 📁 Project Structure

```
.
├── src/
│   └── cloud.c4                 # Your LikeC4 source model with systems, nodes, and connections
├── dist/
│   ├── FirewallRules.md         # Auto-generated markdown table with firewall rules
│   └── firewall_rules.json      # Auto-generated JSON representation of rules
├── mcp_client.py               # Python script that communicates with the MCP server
├── generate_models.py          # New script to auto-generate LikeC4 models using OpenAI
├── .env                        # Your local secrets and environment variables
├── package.json                # Node.js dependencies (for LikeC4 export, if needed)
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

---

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

---

## ⚡ Setup MCP Server with LikeC4

1. Open the project in VSCode  
2. Install the LikeC4 extension (from Marketplace)  
3. Press `Ctrl + ,` to open Settings  
4. Search for "mcp"  
5. Open the LikeC4 section  
6. Enable ✅ MCP Server  
7. Make sure it runs on port `33335`  

Your `settings.json` should look like:

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

Update your `.env` file with OpenAI credentials:

```ini
OPENAI_API_KEY="sk-YourOpenAIKeyHere"
OPENAI_MODEL="gpt-4o"  # or gpt-4o-mini, etc.
```

---

## 🚀 Run the MCP Client Script

Once setup is complete, generate firewall documentation:

```bash
python mcp_client.py
```

This will:

- Connect to the MCP server via SSE  
- Fetch the `SimplifiedFirewallView` from the LikeC4 `.c4` model  
- Analyze system relationships  
- Ask OpenAI to infer firewall rules  
- Output to:
  - `dist/FirewallRules.md`
  - `dist/firewall_rules.json`

---

## 🧠 Generate LikeC4 Models from Natural Language

You can now auto-generate C4 models directly from descriptions using `generate_models.py`.

### 🔧 Example Command:

```bash
python generate_models.py "Design a C4 model for a multi-tenant SaaS platform named 'QuantumLeap Analytics'." \
"The primary user is a 'Data Analyst' who interacts with the platform to build and run data models." \
"The 'Data Analyst' uses a 'Web App' built with React, which serves as the main user interface." \
"The 'Web App' sends GraphQL requests to a central 'API Gateway' built with Apollo Server and Node.js." \
"The 'API Gateway' routes requests to several backend microservices." \
"One microservice is the 'Authentication Service', written in Go, which manages user identity and permissions using a 'PostgreSQL Database'." \
"Another is the 'Query Engine Service', a Python service that executes user-submitted data models against a 'Data Warehouse'." \
"There is also a 'Job Scheduler Service', built with Java, that manages long-running asynchronous tasks using a 'Redis' queue for job management." \
"The platform integrates with 'Stripe' as an external system for handling customer subscriptions." \
"For observability, all services send logs and metrics to an external 'Datadog' monitoring platform." \
"A second user, the 'Support Engineer', uses an internal 'Admin Portal' to manage user accounts and troubleshoot issues." \
-o quantumleap_platform.c4
```

This will generate a valid LikeC4 model file named `quantumleap_platform.c4`.

---

## 📊 Example Output (FirewallRules.md)

| Source              | Port                 | Destination              | Description                          |
|---------------------|----------------------|---------------------------|--------------------------------------|
| User Space (Dev)    | TCP 1024-1028        | vpc-cnc-aws-mms-dev-lops | Mongo Atlas (TCP 1024-1028)          |
| Server Space (Dev)  | TCP 1024-1028, 9226  | vpc-cnc-aws-mms-dev-lops | Mongo Atlas (TCP 1024-1028, 9226)    |

---

## 💡 Powered By

- **LikeC4** — Visual modeling for modern architecture  
- **OpenAI GPT** — Inference for model and firewall rule generation  
- **VSCode MCP Extension**

---

## 🙌 Contributions

Fork this project, submit PRs, or open issues — especially if you want to expand AI generation capabilities or support other C4 views.

---
