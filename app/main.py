from __future__ import annotations

import logging
from dataclasses import replace

import yaml

from app.auth.azure_auth import (
    get_azure_credential,
    get_subscriptions,
    select_subscription,
)
from app.azure.cost import CostDetailsProvider
from app.azure.resource_graph import get_resource_inventory
from app.azure.resources import normalize_resources
from app.azure.state.registry import StateProviderRegistry
from app.reporting.excel import export_inventory


CONFIG_FILE = "config/config.yaml"

logger = logging.getLogger(
    "azure_resource_audit"
)


def load_config() -> dict:
    """Load application configuration."""

    try:
        with open(
            CONFIG_FILE,
            "r",
            encoding="utf-8",
        ) as file:
            return yaml.safe_load(file) or {}

    except FileNotFoundError as exc:
        raise RuntimeError(
            f"Configuration file not found: {CONFIG_FILE}"
        ) from exc

    except yaml.YAMLError as exc:
        raise RuntimeError(
            f"Invalid YAML configuration: {exc}"
        ) from exc


def main() -> None:

    logger.info(
        "Starting Azure Resource Audit Tool."
    )

    print("=" * 70)
    print("AZURE RESOURCE AUDIT TOOL")
    print("=" * 70)
    print()

    # --------------------------------------------------
    # Configuration
    # --------------------------------------------------

    logger.info(
        "Loading application configuration."
    )

    config = load_config()

    cost_config = config.get(
        "cost",
        {},
    )

    cost_enabled = bool(
        cost_config.get(
            "enabled",
            False,
        )
    )

    logger.info(
        "Cost collection enabled: %s",
        cost_enabled,
    )

    # --------------------------------------------------
    # Authentication
    # --------------------------------------------------

    logger.info(
        "Authenticating with Azure CLI."
    )

    credential = get_azure_credential()

    logger.info(
        "Azure authentication successful."
    )

    # --------------------------------------------------
    # Subscription selection
    # --------------------------------------------------

    logger.info(
        "Retrieving available Azure subscriptions."
    )

    subscriptions = get_subscriptions()

    subscription = select_subscription(
        subscriptions
    )

    subscription_id = subscription["id"]
    subscription_name = subscription["name"]

    logger.info(
        "Selected subscription: %s (%s)",
        subscription_name,
        subscription_id,
    )

    # --------------------------------------------------
    # Resource inventory
    # --------------------------------------------------

    logger.info(
        "Retrieving Azure resources."
    )

    print("Retrieving Azure resources...")

    resources = get_resource_inventory(
        credential=credential,
        subscription_id=subscription_id,
    )

    logger.info(
        "Azure resources discovered: %d",
        len(resources),
    )

    print(
        f"Total resources discovered: "
        f"{len(resources)}"
    )

    # --------------------------------------------------
    # Resource state enrichment
    # --------------------------------------------------

    logger.info(
        "Retrieving resource states."
    )

    print("Retrieving resource states...")

    state_registry = StateProviderRegistry()

    resource_types = {
        str(resource.get("type", "")).lower()
        for resource in resources
        if resource.get("type")
    }

    states = state_registry.get_states(
        credential=credential,
        subscription_id=subscription_id,
        resource_types=resource_types,
    )

    logger.info(
        "Resource states retrieved: %d",
        len(states),
    )

    print(
        f"Resource states retrieved: "
        f"{len(states)}"
    )

    # --------------------------------------------------
    # Resource normalization
    # --------------------------------------------------

    logger.info(
        "Normalizing resource data."
    )

    print("Normalizing resource data...")

    inventory = normalize_resources(
        resources=resources,
        states=states,
    )

    logger.info(
        "Resources normalized: %d",
        len(inventory),
    )

    print(
        f"Resources normalized: "
        f"{len(inventory)}"
    )

    # --------------------------------------------------
    # Cost enrichment
    # --------------------------------------------------

    monthly_costs: dict[str, float] = {}

    if cost_enabled:

        logger.info(
            "Monthly cost collection enabled."
        )

        print(
            "Retrieving monthly cost data..."
        )

        try:

            cost_provider = (
                CostDetailsProvider()
            )

            monthly_costs = (
                cost_provider.get_costs(
                    credential=credential,
                    subscription_id=subscription_id,
                )
            )

            logger.info(
                "Resource costs retrieved: %d",
                len(monthly_costs),
            )

            print(
                f"Resource costs retrieved: "
                f"{len(monthly_costs)}"
            )

        except Exception as exc:

            logger.warning(
                "Cost retrieval failed. "
                "Monthly Cost will be N/A. "
                "Reason: %s",
                exc,
            )

            print(
                "WARNING: Cost retrieval failed."
            )

            print(
                f"Reason: {exc}"
            )

            print(
                "Monthly Cost will be reported as N/A."
            )

    else:

        logger.info(
            "Cost collection disabled."
        )

        print(
            "Cost retrieval disabled. "
            "Monthly Cost will be N/A."
        )

    # --------------------------------------------------
    # Apply cost data
    # --------------------------------------------------

    inventory = [
        replace(
            resource,
            monthly_cost=(
                monthly_costs.get(
                    resource.resource_id.lower()
                )
                if cost_enabled
                and resource.resource_id.lower()
                in monthly_costs
                else None
            ),
        )
        for resource in inventory
    ]

    logger.info(
        "Cost enrichment completed."
    )

    # --------------------------------------------------
    # Excel report
    # --------------------------------------------------

    logger.info(
        "Generating Excel report."
    )

    print("Generating Excel report...")

    report_path = export_inventory(
        resources=inventory,
        subscription_name=subscription_name,
        subscription_id=subscription_id,
    )

    logger.info(
        "Excel report generated: %s",
        report_path,
    )

    print(
        f"Report generated: {report_path}"
    )

    # --------------------------------------------------
    # Completion
    # --------------------------------------------------

    logger.info(
        "Azure Resource Audit completed successfully."
    )

    print()
    print("=" * 70)
    print("RESOURCE AUDIT COMPLETED SUCCESSFULLY")
    print("=" * 70)


if __name__ == "__main__":
    main()