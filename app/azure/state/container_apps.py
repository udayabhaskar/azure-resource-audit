from __future__ import annotations

from typing import Any

from azure.core.exceptions import AzureError
from azure.mgmt.appcontainers import ContainerAppsAPIClient

from app.azure.state.base import ResourceStateProvider


class ContainerAppStateProvider(ResourceStateProvider):

    @property
    def resource_types(self) -> tuple[str, ...]:
        return (
            "microsoft.app/containerapps",
        )

    def get_states(
        self,
        credential: Any,
        subscription_id: str,
    ) -> dict[str, str]:

        client = ContainerAppsAPIClient(
            credential,
            subscription_id,
        )

        states: dict[str, str] = {}

        try:

            for app in client.container_apps.list_by_subscription():

                if not app.id:
                    continue

                properties = getattr(
                    app,
                    "properties",
                    None,
                )

                state = getattr(
                    properties,
                    "running_status",
                    None,
                )

                if state:
                    states[
                        app.id.lower()
                    ] = str(state)

        except AzureError:
            raise

        finally:
            client.close()

        return states