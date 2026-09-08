from __future__ import annotations

from typing import Any

from azure.core.exceptions import AzureError
from azure.mgmt.servicebus import ServiceBusManagementClient

from app.azure.state.base import ResourceStateProvider


class ServiceBusStateProvider(ResourceStateProvider):

    @property
    def resource_types(self) -> tuple[str, ...]:
        return (
            "microsoft.servicebus/namespaces",
        )

    def get_states(
        self,
        credential: Any,
        subscription_id: str,
    ) -> dict[str, str]:

        client = ServiceBusManagementClient(
            credential,
            subscription_id,
        )

        states: dict[str, str] = {}

        try:

            for namespace in client.namespaces.list():

                if not namespace.id:
                    continue

                resource_group = (
                    self._get_resource_group(
                        namespace.id
                    )
                )

                if not resource_group or not namespace.name:
                    continue

                try:

                    full_namespace = (
                        client.namespaces.get(
                            resource_group,
                            namespace.name,
                        )
                    )

                    properties = getattr(
                        full_namespace,
                        "properties",
                        None,
                    )

                    state = getattr(
                        properties,
                        "status",
                        None,
                    )

                    if state:
                        states[
                            namespace.id.lower()
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