from __future__ import annotations

from typing import Any

from azure.core.exceptions import AzureError
from azure.mgmt.web import WebSiteManagementClient

from app.azure.state.base import ResourceStateProvider


class WebStateProvider(ResourceStateProvider):

    @property
    def resource_types(self) -> tuple[str, ...]:
        return (
            "microsoft.web/sites",
            "microsoft.web/serverfarms",
        )

    def get_states(
        self,
        credential: Any,
        subscription_id: str,
    ) -> dict[str, str]:

        client = WebSiteManagementClient(
            credential,
            subscription_id,
        )

        states: dict[str, str] = {}

        try:

            # App Services
            for app in client.web_apps.list():

                if not app.id:
                    continue

                state = getattr(
                    app,
                    "state",
                    None,
                )

                if state:
                    states[
                        app.id.lower()
                    ] = str(state)

            # App Service Plans
            for plan in client.app_service_plans.list():

                if not plan.id:
                    continue

                state = getattr(
                    plan,
                    "status",
                    None,
                )

                if state:
                    states[
                        plan.id.lower()
                    ] = str(state)

        except AzureError:
            raise

        finally:
            client.close()

        return states