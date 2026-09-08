
# Azure Resource Audit Tool

A Python tool I built to quickly audit Azure resources across a subscription and generate an Excel inventory report.

The main goal is to get a simple view of what resources exist, where they are, what state they are in, who owns them, which environment they belong to, and their SKU.

The tool is read-only and does not make any changes to Azure resources.

## What it does

The tool currently collects:

- Resource Group
- Resource name
- Resource type
- Azure region
- Resource state (where supported)
- SKU
- Owner
- Environment
- Tags
- Monthly cost (optional)

It uses Azure Resource Graph to discover resources and Azure management APIs to get the state of supported resource types.

If a resource doesn't have tags, the report shows `No Tags`.

If Owner or Environment information isn't available, it shows `Unknown`.

If SKU or State isn't available, it shows `N/A`.

## Requirements

You'll need:

- Python 3.10 or later
- Azure CLI
- Access to at least one Azure subscription

Check that Python and Azure CLI are available:

```powershell
python --version
az --version
````
Quick Setup
1. Clone the repository
git clone https://github.com/udayabhaskar/azure-resource-audit.git
cd azure-resource-audit
2. Create a Python virtual environment
python -m venv .venv

Activate it:

.\.venv\Scripts\Activate.ps1
3. Install dependencies
pip install -r requirements.txt

Optional:

pip check
4. Login to Azure

The tool uses your Azure CLI login:

az login
5. Run the audit
python run.py

The tool will display the Azure subscriptions available to your account and ask you to select one.

The generated Excel report will be available under:

output/

Logs will be available under:

logs/
Cost Configuration

Cost collection is optional.

The configuration file is:

config/config.yaml

To disable cost collection:

cost:
  enabled: false

To enable cost collection:

cost:
  enabled: true

When cost collection is disabled or unavailable, the report shows N/A for Monthly Cost.
