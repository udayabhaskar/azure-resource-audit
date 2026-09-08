from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AzureResource:
    resource_id: str
    resource_group: str
    resource_name: str
    resource_type: str
    location: str
    state: str
    sku: str
    monthly_cost: float | None
    owner: str
    environment: str
    tags: str