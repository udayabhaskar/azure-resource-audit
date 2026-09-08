from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ResourceStateProvider(ABC):
    """
    Base contract for Azure resource state providers.
    """

    @property
    @abstractmethod
    def resource_types(self) -> tuple[str, ...]:
        """
        Azure resource types supported by this provider.
        """
        raise NotImplementedError

    @abstractmethod
    def get_states(
        self,
        credential: Any,
        subscription_id: str,
    ) -> dict[str, str]:
        """
        Return a mapping of Azure Resource ID to state.

        Resources that cannot be determined by the provider
        should not be added to the returned mapping.
        """
        raise NotImplementedError

    @staticmethod
    def normalize_state(state: Any) -> str:
        """
        Convert Azure SDK enum values and strings into
        clean report-friendly state values.
        """

        if state is None:
            return "N/A"

        value = getattr(
            state,
            "value",
            state,
        )

        value = str(value).strip()

        if not value:
            return "N/A"

        # Handle values such as:
        # DatabaseStatus.ONLINE
        # AccountStatus.AVAILABLE
        # VaultProvisioningState.SUCCEEDED
        if "." in value:
            value = value.rsplit(
                ".",
                1,
            )[1]

        return value.replace(
            "_",
            " ",
        ).title()