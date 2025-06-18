# C4 Model to Docs Generator

This project transforms LikeC4 architecture models into human-readable firewall rule documentation. By treating your LikeC4 `.c4` files as the source of truth, the system ensures your network documentation stays aligned with your evolving architecture.

The pipeline uses a Python script to:
- Export your LikeC4 model to structured JSON,
- Parse and interpret system relationships,
- Query the OpenAI API to infer necessary firewall rules,
- And generate a clean, version-controllable Markdown table.

This approach minimizes manual effort and maximizes architectural clarity—making your infrastructure both visual and actionable.

---

## 📁 File Structure

The project is organized to separate the source model, the generation script, and the output artifacts.

```
.
├── src/
│   ├── cloud.c4              # The source LikeC4 model defining your architecture.
│   └── generate_table.py     # The main Python script to orchestrate the process.
│
├── dist/
│   ├── model.json            # The auto-generated JSON export of the LikeC4 model.
│   └── FirewallRules.md      # The final, auto-generated firewall rules table.
│
├── .env                      # Local environment variables (contains API keys).
├── package.json              # Node.js dependencies for LikeC4.
└── requirements.txt          # Python dependencies for the generation script.
```

---

## ⚙️ How It Works

The process follows a simple, automated pipeline:

1. **Export Model**  
   The Python script executes `npm run export:json`, using the LikeC4 CLI to compile your `.c4` architecture into a structured JSON format (`dist/model.json`).

2. **Parse & Filter**  
   The script reads the exported JSON and extracts the components and their interconnections—especially focusing on elements relevant to firewall rules such as data flow, source, and destination.

3. **LLM Inference**  
   This filtered data is sent to OpenAI's API (`gpt-4o-mini`) with a prompt designed to simulate a network engineer's reasoning. The LLM infers the correct ports, protocols, and communication paths, returning a structured JSON object.

4. **Format Output**  
   The response is parsed and cleaned.

5. **Generate Table**  
   Finally, a Markdown table is generated and saved in `dist/FirewallRules.md`.

---

## 🧰 Setup

Follow these steps to set up the project on your local machine.

### Prerequisites

- [Node.js](https://nodejs.org/) (LTS version recommended)  
- [Python](https://www.python.org/) (3.8 or newer)

### 1. Install Dependencies

```bash
# Install Node.js packages (for LikeC4)
npm install

# Install Python packages
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the project root with your OpenAI API key:

```
OPENAI_API_KEY="sk-YourSecretApiKeyHere"
```

---

## 🚀 Execution

To generate the firewall rules documentation, run:

```bash
python src/generate_table.py
```

The script prints progress logs to the console. After completion, check the `dist/FirewallRules.md` file for the updated rules table.

To regenerate the table after changes, just update `src/cloud.c4` and rerun the script.

---

## 🧠 Powered by

- [LikeC4](https://likec4.dev) — to model and visualize your architecture
- [OpenAI GPT](https://platform.openai.com) — to reason about system communication
