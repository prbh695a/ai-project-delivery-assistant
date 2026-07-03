from __future__ import annotations

from typing import Any

import requests


class OpenProjectClient:
    """Small OpenProject API client using API-key based Basic Auth."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        verify_ssl: bool | str = True,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.verify_ssl = verify_ssl

    def get_current_user(self) -> dict[str, Any]:
        url = f"{self.base_url}/api/v3/users/me"
        response = requests.get(
            url,
            auth=("apikey", self.api_key),
            headers={"Accept": "application/json"},
            timeout=30,
            verify=self.verify_ssl,
        )
        response.raise_for_status()
        return response.json()

    def get_work_packages(self, project_identifier: str) -> list[dict[str, Any]]:
        url = f"{self.base_url}/api/v3/projects/{project_identifier}/work_packages"
        response = requests.get(
            url,
            auth=("apikey", self.api_key),
            headers={"Accept": "application/json"},
            timeout=60,
            verify=self.verify_ssl,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("_embedded", {}).get("elements", [])
