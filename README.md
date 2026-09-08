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

## Supported resource states

State information is currently collected for:

- Virtual Machines
- Managed Disks
- App Services
- App Service Plans
- Azure SQL
- Azure Storage
- PostgreSQL Flexible Server
- MySQL Flexible Server
- Key Vault
- Azure Container Apps
- Azure Service Bus

Not every Azure resource exposes a useful operational state through the management APIs. Those resources are still included in the report, but their state is shown as `N/A`.

The state collection is implemented using separate providers, so additional Azure services can be added later without changing the main audit logic.

## Requirements

You'll need:

- Python 3.10 or later
- Azure CLI
- Access to at least one Azure subscription

Check that Python and Azure CLI are available:

```powershell
python --version
az --version