from __future__ import annotations

from typing import Any

from azure.core.exceptions import AzureError
from azure.mgmt.sql import SqlManagementClient

from app.azure.state.base import ResourceStateProvider


class SqlStateProvider(ResourceStateProvider):

    @property
    def resource_types(self) -> tuple[str, ...]:
        return (
            "microsoft.sql/servers",
            "microsoft.sql/servers/databases",
        )

    def get_states(
        self,
        credential: Any,
        subscription_id: str,
    ) -> dict[str, str]:

        client = SqlManagementClient(
            credential,
            subscription_id,
        )

        states: dict[str, str] = {}

        try:

            for server in client.servers.list():

                if not server.id:
                    continue

                state = getattr(
                    server,
                    "state",
                    None,
                )

                if state:
                    states[
                        server.id.lower()
                    ] = str(state)

                if not server.name:
                    continue

                resource_group = (
                    self._get_resource_group(
                        server.id
                    )
                )

                if not resource_group:
                    continue

                try:

                    databases = (
                        client.databases
                        .list_by_server(
                            resource_group,
                            server.name,
                        )
                    )

                    for database in databases:

                        if not database.id:
                            continue

                        status = getattr(
                            database,
                            "status",
                            None,
                        )

                        if status:
                            states[
                                database.id.lower()
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
            index = (
                parts.index("resourceGroups")
            )

            return parts[index + 1]

        except (
            ValueError,
            IndexError,
        ):
            return None