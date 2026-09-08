from __future__ import annotations

from typing import Any

from azure.core.exceptions import AzureError
from azure.mgmt.compute import ComputeManagementClient

from app.azure.state.base import ResourceStateProvider


class ComputeStateProvider(ResourceStateProvider):

    @property
    def resource_types(self) -> tuple[str, ...]:
        return (
            "microsoft.compute/virtualmachines",
            "microsoft.compute/disks",
        )

    def get_states(
        self,
        credential: Any,
        subscription_id: str,
    ) -> dict[str, str]:

        client = ComputeManagementClient(
            credential,
            subscription_id,
        )

        states: dict[str, str] = {}

        for vm in client.virtual_machines.list_all():

            if not vm.id:
                continue

            try:
                resource_group = vm.id.split("/")[4]

                instance_view = client.virtual_machines.instance_view(
                    resource_group,
                    vm.name,
                )

                state = "Unknown"

                for status in instance_view.statuses or []:

                    code = status.code or ""

                    if code.startswith("PowerState/"):
                        state = code.split("/", 1)[1]
                        break

                states[vm.id.lower()] = state

            except (AzureError, IndexError):
                states[vm.id.lower()] = "Unknown"

        for disk in client.disks.list():

            if disk.id:
                states[disk.id.lower()] = (
                    "Attached"
                    if disk.managed_by
                    else "Unattached"
                )

        return states