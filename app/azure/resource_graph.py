from __future__ import annotations

from typing import Any

from azure.mgmt.resourcegraph import ResourceGraphClient
from azure.mgmt.resourcegraph.models import QueryRequest


def get_resource_inventory(
    credential: Any,
    subscription_id: str,
) -> list[dict[str, Any]]:
    """
    Retrieve all Azure resources from the selected subscription.

    Uses Azure Resource Graph with pagination.
    """

    client = ResourceGraphClient(credential)

    query = """
    Resources
    | project
        id,
        name,
        type,
        resourceGroup,
        location,
        sku,
        tags
    | order by resourceGroup asc, type asc, name asc
    """

    resources: list[dict[str, Any]] = []
    skip_token: str | None = None

    while True:

        request = QueryRequest(
            subscriptions=[subscription_id],
            query=query,
            options={
                "resultFormat": "objectArray",
                "top": 1000,
            },
        )

        if skip_token:
            request.options["skipToken"] = skip_token

        response = client.resources(request)

        if response.data:
            resources.extend(response.data)

        skip_token = getattr(response, "skip_token", None)

        if not skip_token:
            break

    return resources