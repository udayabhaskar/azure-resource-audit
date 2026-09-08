from __future__ import annotations

import logging
from typing import Any

from app.azure.state.base import ResourceStateProvider
from app.azure.state.compute import ComputeStateProvider
from app.azure.state.servicebus import ServiceBusStateProvider
from app.azure.state.web import WebStateProvider
from app.azure.state.sql import SqlStateProvider
from app.azure.state.storage import StorageStateProvider
from app.azure.state.database import PostgreSqlStateProvider
from app.azure.state.keyvault import KeyVaultStateProvider
from app.azure.state.mysql import MySqlStateProvider
from app.azure.state.container_apps import ContainerAppStateProvider


logger = logging.getLogger(
    "azure_resource_audit"
)


class StateProviderRegistry:

    def __init__(self) -> None:

        self._providers = [
            ComputeStateProvider(),
            WebStateProvider(),
            SqlStateProvider(),
            StorageStateProvider(),
            PostgreSqlStateProvider(),
            KeyVaultStateProvider(),
            MySqlStateProvider(),
            ContainerAppStateProvider(),
            ServiceBusStateProvider(),
        ]

    def get_states(
        self,
        credential: Any,
        subscription_id: str,
        resource_types: set[str],
    ) -> dict[str, str]:
        """
        Run only the state providers that support
        resource types present in the subscription.
        """

        states: dict[str, str] = {}

        normalized_resource_types = {
            resource_type.lower()
            for resource_type in resource_types
        }

        for provider in self._providers:

            provider_name = (
                provider.__class__.__name__
            )

            supported_types = {
                resource_type.lower()
                for resource_type
                in provider.resource_types
            }

            if not (
                normalized_resource_types
                & supported_types
            ):
                logger.info(
                    "Skipping state provider %s. "
                    "No supported resource types found.",
                    provider_name,
                )
                continue

            logger.info(
                "Running state provider: %s",
                provider_name,
            )

            try:

                provider_states = (
                    provider.get_states(
                        credential=credential,
                        subscription_id=subscription_id,
                    )
                )

                for resource_id, state in provider_states.items():
                    states[resource_id] = (
                    provider.normalize_state(state)
                )

                logger.info(
                    "State provider %s completed. "
                    "States retrieved: %d",
                    provider_name,
                    len(provider_states),
                )

            except Exception as exc:

                logger.exception(
                    "State provider %s failed. "
                    "Continuing with remaining "
                    "providers. Reason: %s",
                    provider_name,
                    exc,
                )

        return states