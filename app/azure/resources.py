from __future__ import annotations

from typing import Any

from app.models.resource import AzureResource


OWNER_TAGS = (
    "Owner",
    "owner",
    "AppOwner",
    "ApplicationOwner",
    "ServiceOwner",
)

ENVIRONMENT_TAGS = (
    "Environment",
    "environment",
    "Env",
    "ENV",
    "EnvironmentName",
)


def _get_tag_value(
    tags: dict[str, Any] | None,
    tag_names: tuple[str, ...],
) -> str:

    if not tags:
        return "Unknown"

    normalized_tags = {
        str(key).lower(): str(value).strip()
        for key, value in tags.items()
        if value is not None
    }

    for tag_name in tag_names:

        value = normalized_tags.get(tag_name.lower())

        if value:
            return value

    return "Unknown"


def _format_tags(
    tags: dict[str, Any] | None,
) -> str:

    if not tags:
        return "No Tags"

    formatted = [
        f"{key}={value}"
        for key, value in tags.items()
        if value is not None
    ]

    return "; ".join(formatted) if formatted else "No Tags"


def _get_sku(resource: dict[str, Any]) -> str:

    sku = resource.get("sku")

    if not sku:
        return "N/A"

    if isinstance(sku, dict):

        name = sku.get("name")

        if name:
            return str(name)

        tier = sku.get("tier")

        if tier:
            return str(tier)

    return "N/A"


def normalize_resources(
    resources: list[dict[str, Any]],
    states: dict[str, str],
) -> list[AzureResource]:

    inventory = []

    for resource in resources:

        resource_id = str(
            resource.get("id", "")
        )

        tags = resource.get("tags")

        state = states.get(
            resource_id.lower(),
            "N/A",
        )

        inventory.append(
            AzureResource(
                resource_id=resource_id,
                resource_group=str(
                    resource.get(
                        "resourceGroup",
                        "Unknown",
                    )
                ),
                resource_name=str(
                    resource.get(
                        "name",
                        "Unknown",
                    )
                ),
                resource_type=str(
                    resource.get(
                        "type",
                        "Unknown",
                    )
                ),
                location=str(
                    resource.get(
                        "location",
                        "Unknown",
                    )
                ),
                state=state,
                sku=_get_sku(resource),
                monthly_cost=None,
                owner=_get_tag_value(
                    tags,
                    OWNER_TAGS,
                ),
                environment=_get_tag_value(
                    tags,
                    ENVIRONMENT_TAGS,
                ),
                tags=_format_tags(tags),
            )
        )

    return inventory