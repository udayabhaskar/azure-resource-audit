from __future__ import annotations

from typing import Any

from azure.core.exceptions import AzureError
from azure.mgmt.keyvault import KeyVaultManagementClient

from app.azure.state.base import ResourceStateProvider


class KeyVaultStateProvider(ResourceStateProvider):

    @property
    def resource_types(self) -> tuple[str, ...]:
        return (
            "microsoft.keyvault/vaults",
        )

    def get_states(
        self,
        credential: Any,
        subscription_id: str,
    ) -> dict[str, str]:

        client = KeyVaultManagementClient(
            credential,
            subscription_id,
        )

        states: dict[str, str] = {}

        try:

            for vault in client.vaults.list():

                if not vault.id or not vault.name:
                    continue

                resource_group = (
                    self._get_resource_group(
                        vault.id
                    )
                )

                if not resource_group:
                    continue

                try:

                    full_vault = (
                        client.vaults.get(
                            resource_group,
                            vault.name,
                        )
                    )

                    properties = getattr(
                        full_vault,
                        "properties",
                        None,
                    )

                    state = getattr(
                        properties,
                        "provisioning_state",
                        None,
                    )

                    if state:
                        states[
                            vault.id.lower()
                        ] = str(state)

                except AzureError:
                    continue

        except AzureError:
            raise

        finally:
            client.close()

        return states

    @staticmethod
    def _get_resource_group(
        resource_id: str,
    ) -> str | None:

        parts = resource_id.strip(
            "/"
        ).split("/")

        try:

            index = parts.index(
                "resourceGroups"
            )

            return parts[index + 1]

        except (
            ValueError,
            IndexError,
        ):
            return None