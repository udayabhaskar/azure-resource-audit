from __future__ import annotations

from typing import Any

from azure.core.exceptions import AzureError
from azure.mgmt.rdbms.mysql_flexibleservers import (
    MySQLManagementClient,
)

from app.azure.state.base import ResourceStateProvider


class MySqlStateProvider(ResourceStateProvider):

    @property
    def resource_types(self) -> tuple[str, ...]:
        return (
            "microsoft.dbformysql/flexibleservers",
        )

    def get_states(
        self,
        credential: Any,
        subscription_id: str,
    ) -> dict[str, str]:

        client = MySQLManagementClient(
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

        except AzureError:
            raise

        finally:
            client.close()

        return states