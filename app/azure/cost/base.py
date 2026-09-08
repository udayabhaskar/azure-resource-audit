from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class CostProvider(ABC):

    @abstractmethod
    def get_costs(
        self,
        credential: Any,
        subscription_id: str,
    ) -> dict[str, float]:
        """Return Resource ID -> cost."""
        raise NotImplementedError