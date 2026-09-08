from __future__ import annotations

from typing import Any

from azure.core.exceptions import AzureError
from azure.mgmt.storage import StorageManagementClient

from app.azure.state.base import ResourceStateProvider


class StorageStateProvider(ResourceStateProvider):

    @property
    def resource_types(self) -> tuple[str, ...]:
        return (
            "microsoft.storage/storageaccounts",
        )

    def get_states(
        self,
        credential: Any,
        subscription_id: str,
    ) -> dict[str, str]:

        client = StorageManagementClient(
            credential,
            subscription_id,
        )

        states: dict[str, str] = {}

        try:

            for account in client.storage_accounts.list():

                if not account.id:
                    continue

                resource_group = (
                    self._get_resource_group(
                        account.id
                    )
                )

                if not resource_group:
                    continue

                if not account.name:
                    continue

                try:
                    properties = (
                        client.storage_accounts
                        .get_properties(
                            resource_group,
                            account.name,
                        )
                    )

                    status = getattr(
                        properties,
                        "status_of_primary",
                        None,
                    )

                    if status:
                        states[
                            account.id.lower()
                        ] = str(status)

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