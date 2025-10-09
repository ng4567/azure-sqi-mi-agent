# Install Dependencies

- install uv package manager: [link](https://docs.astral.sh/uv/getting-started/installation/)
- install bcp: [link](https://learn.microsoft.com/en-us/sql/tools/bcp-utility?view=sql-server-ver17&tabs=windows)

Cloud Dependencies Needed:
- Azure AI Foundry
- Deployed LLM in Foundry that supports tool calling 
- Azure SQL DB Managed Instance

# Create Virtual Environment

### Mac/Linux:

```bash
uv venv .venv/
source .venv/bin/activate
uv sync
```

### Windows:

```powershell
uv venv .venv/
.venv\Scripts\activate.ps1
uv sync
```

# API Credentials

* Navigate to your Azure Foundry Instance
* Fill in the .env-template with required credentials from Foundry
* Rename .env-template to .env

# Usage

To run: 
```bash
uv run agent.py
```
