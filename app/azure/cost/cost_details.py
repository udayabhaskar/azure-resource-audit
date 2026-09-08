from __future__ import annotations

import time
from datetime import date, timedelta
from typing import Any

import pandas as pd
import requests


API_VERSION = "2026-06-01"
MANAGEMENT_SCOPE = "https://management.azure.com/.default"

MAX_POLL_ATTEMPTS = 30
DEFAULT_RETRY_AFTER = 30


class CostDetailsProvider:

    def get_costs(
        self,
        credential: Any,
        subscription_id: str,
    ) -> dict[str, float]:

        start_date, end_date = self._get_last_month_range()

        print(
            f"Generating cost details: "
            f"{start_date} to {end_date}"
        )

        token = credential.get_token(
            MANAGEMENT_SCOPE
        ).token

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        url = (
            "https://management.azure.com"
            f"/subscriptions/{subscription_id}"
            "/providers/Microsoft.CostManagement"
            "/generateCostDetailsReport"
            f"?api-version={API_VERSION}"
        )

        payload = {
            "metric": "ActualCost",
            "timePeriod": {
                "start": start_date,
                "end": end_date,
            },
        }

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=60,
        )

        if response.status_code != 202:
            raise RuntimeError(
                "Cost Details API request failed: "
                f"{response.status_code} "
                f"{response.text}"
            )

        location = response.headers.get("Location")

        if not location:
            raise RuntimeError(
                "Cost Details API did not return "
                "a polling Location."
            )

        retry_after = self._get_retry_after(
            response.headers
        )

        print(
            "Cost report generation started. "
            f"Waiting {retry_after} seconds..."
        )

        time.sleep(retry_after)

        result = self._poll_report(
            credential=credential,
            location=location,
        )

        blob_links = self._get_blob_links(result)

        if not blob_links:
            print("Cost Details API returned no cost files.")
            return {}

        print(
            f"Cost report generated. "
            f"Files: {len(blob_links)}"
        )

        return self._download_and_aggregate(
            blob_links
        )

    @staticmethod
    def _get_last_month_range() -> tuple[str, str]:

        today = date.today()

        first_day_current_month = today.replace(
            day=1
        )

        last_day_previous_month = (
            first_day_current_month
            - timedelta(days=1)
        )

        first_day_previous_month = (
            last_day_previous_month.replace(day=1)
        )

        return (
            first_day_previous_month.isoformat(),
            first_day_current_month.isoformat(),
        )

    @staticmethod
    def _get_retry_after(
        headers: Any,
    ) -> int:

        value = headers.get("Retry-After")

        if value:
            try:
                return max(
                    int(value),
                    1,
                )
            except ValueError:
                pass

        return DEFAULT_RETRY_AFTER

    def _poll_report(
        self,
        credential: Any,
        location: str,
    ) -> dict[str, Any]:

        for attempt in range(
            1,
            MAX_POLL_ATTEMPTS + 1,
        ):

            token = credential.get_token(
                MANAGEMENT_SCOPE
            ).token

            headers = {
                "Authorization": f"Bearer {token}",
            }

            response = requests.get(
                location,
                headers=headers,
                timeout=60,
            )

            if response.status_code == 200:

                result = response.json()

                status = str(
                    result.get(
                        "status",
                        ""
                    )
                ).lower()

                if status in (
                    "completed",
                    "succeeded",
                    "",
                ):
                    return result

            elif response.status_code == 202:

                retry_after = self._get_retry_after(
                    response.headers
                )

                print(
                    f"Cost report still generating. "
                    f"Attempt {attempt}/"
                    f"{MAX_POLL_ATTEMPTS}. "
                    f"Waiting {retry_after} seconds..."
                )

                time.sleep(retry_after)
                continue

            else:

                raise RuntimeError(
                    "Cost Details API polling failed: "
                    f"{response.status_code} "
                    f"{response.text}"
                )

            time.sleep(DEFAULT_RETRY_AFTER)

        raise RuntimeError(
            "Cost Details API report generation "
            "timed out."
        )

    @staticmethod
    def _get_blob_links(
        result: dict[str, Any],
    ) -> list[str]:

        manifest = result.get("manifest", {})

        blobs = manifest.get(
            "blobs",
            [],
        )

        return [
            blob["blobLink"]
            for blob in blobs
            if blob.get("blobLink")
        ]

    @staticmethod
    def _download_and_aggregate(
        blob_links: list[str],
    ) -> dict[str, float]:

        costs: dict[str, float] = {}

        for index, blob_link in enumerate(
            blob_links,
            start=1,
        ):

            print(
                f"Downloading cost file "
                f"{index}/{len(blob_links)}..."
            )

            response = requests.get(
                blob_link,
                timeout=120,
            )

            response.raise_for_status()

            from io import BytesIO

            dataframe = pd.read_csv(
                BytesIO(response.content)
            )

            resource_id_column = (
                CostDetailsProvider
                ._find_column(
                    dataframe,
                    "ResourceId",
                )
            )

            cost_column = (
                CostDetailsProvider
                ._find_column(
                    dataframe,
                    "CostInBillingCurrency",
                )
            )

            if not resource_id_column:
                raise RuntimeError(
                    "Cost report does not contain "
                    "ResourceId."
                )

            if not cost_column:
                raise RuntimeError(
                    "Cost report does not contain "
                    "CostInBillingCurrency."
                )

            for _, row in dataframe.iterrows():

                resource_id = row.get(
                    resource_id_column
                )

                if pd.isna(resource_id):
                    continue

                cost = row.get(
                    cost_column,
                    0,
                )

                try:
                    cost_value = float(
                        cost
                    )
                except (
                    TypeError,
                    ValueError,
                ):
                    continue

                key = str(
                    resource_id
                ).strip().lower()

                if not key:
                    continue

                costs[key] = (
                    costs.get(key, 0.0)
                    + cost_value
                )

        return costs

    @staticmethod
    def _find_column(
        dataframe: pd.DataFrame,
        expected: str,
    ) -> str | None:

        normalized = {
            str(column).strip().lower(): column
            for column in dataframe.columns
        }

        return normalized.get(
            expected.lower()
        )