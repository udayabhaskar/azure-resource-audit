from __future__ import annotations

import json
import shutil
import subprocess
from typing import Any

from azure.core.exceptions import ClientAuthenticationError
from azure.identity import AzureCliCredential


AZURE_MANAGEMENT_SCOPE = "https://management.azure.com/.default"


def get_az_command() -> str:
    """Locate the Azure CLI executable."""

    az_command = shutil.which("az") or shutil.which("az.cmd")

    if not az_command:
        raise RuntimeError(
            "Azure CLI was not found in PATH. "
            "Please install Azure CLI and ensure 'az' is available "
            "from the current PowerShell session."
        )

    return az_command


def get_azure_credential() -> AzureCliCredential:
    """Create and validate an Azure CLI credential."""

    get_az_command()

    credential = AzureCliCredential()

    try:
        credential.get_token(AZURE_MANAGEMENT_SCOPE)
    except ClientAuthenticationError as exc:
        raise RuntimeError(
            "Azure authentication failed. Please run 'az login' "
            "and try again."
        ) from exc

    return credential


def get_subscriptions() -> list[dict[str, Any]]:
    """Return all enabled Azure subscriptions available to the user."""

    az_command = get_az_command()

    result = subprocess.run(
        [
            az_command,
            "account",
            "list",
            "--all",
            "--query",
            "[?state=='Enabled']",
            "-o",
            "json",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(
            "Unable to retrieve Azure subscriptions: "
            f"{result.stderr.strip()}"
        )

    try:
        subscriptions = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "Azure CLI returned invalid subscription data."
        ) from exc

    if not subscriptions:
        raise RuntimeError(
            "No enabled Azure subscriptions were found."
        )

    return subscriptions


def select_subscription(
    subscriptions: list[dict[str, Any]],
) -> dict[str, Any]:
    """Display subscriptions and allow interactive selection."""

    print()
    print("=" * 70)
    print("AVAILABLE AZURE SUBSCRIPTIONS")
    print("=" * 70)

    for index, subscription in enumerate(subscriptions, start=1):
        print(
            f"[{index}] {subscription.get('name', 'Unknown')}"
            f" ({subscription.get('id', 'Unknown')})"
        )

    print()

    while True:
        selection = input("Select subscription number: ").strip()

        try:
            index = int(selection)
        except ValueError:
            print("Invalid selection. Please enter a number.")
            continue

        if 1 <= index <= len(subscriptions):
            selected = subscriptions[index - 1]
            break

        print(
            f"Invalid selection. Enter a number between "
            f"1 and {len(subscriptions)}."
        )

    az_command = get_az_command()

    result = subprocess.run(
        [
            az_command,
            "account",
            "set",
            "--subscription",
            selected["id"],
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(
            "Unable to select Azure subscription: "
            f"{result.stderr.strip()}"
        )

    print()
    print("Selected Subscription")
    print("-" * 70)
    print(f"Name : {selected['name']}")
    print(f"ID   : {selected['id']}")
    print(f"Tenant: {selected.get('tenantId', 'Unknown')}")
    print()

    return selected