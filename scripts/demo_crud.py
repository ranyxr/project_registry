#!/usr/bin/env python3
"""Demonstrate project CRUD operations against the running API."""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid
from datetime import date, timedelta
from pprint import pprint

BASE_URL = "http://localhost:8000"
REGISTER_URL = f"{BASE_URL}/auth/register"
TOKEN_URL = f"{BASE_URL}/auth/token"
PROJECTS_COLLECTION_URL = f"{BASE_URL}/projects/"


def main() -> int:
    suffix = uuid.uuid4().hex[:8]
    email = f"demo_{suffix}@example.com"
    password = "DemoPass123!"
    register_payload = {
        "email": email,
        "password": password,
        "full_name": "Demo User",
    }
    register_body = json.dumps(register_payload).encode()

    try:
        with urllib.request.urlopen(
            urllib.request.Request(
                REGISTER_URL,
                data=register_body,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
        ) as response:
            register_result = json.loads(response.read())
    except urllib.error.HTTPError as exc:
        print("Registration failed:")
        print(exc.read().decode())
        raise

    print("Registered user:")
    pprint(register_result)

    token_payload = urllib.parse.urlencode({"username": email, "password": password}).encode()
    with urllib.request.urlopen(
        urllib.request.Request(
            TOKEN_URL,
            data=token_payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
    ) as response:
        token_result = json.loads(response.read())

    token = token_result["access_token"]
    auth_header = {"Authorization": f"Bearer {token}"}
    print("\nReceived access token.")

    create_payload = {
        "name": "Demo Project",
        "description": "Project created from the CRUD demo script.",
        "expiration_date": str(date.today() + timedelta(days=30)),
    }
    with urllib.request.urlopen(
        urllib.request.Request(
            PROJECTS_COLLECTION_URL,
            data=json.dumps(create_payload).encode(),
            headers={**auth_header, "Content-Type": "application/json"},
            method="POST",
        )
    ) as response:
        project = json.loads(response.read())

    project_id = project["id"]
    print("\nCreated project:")
    pprint(project)

    with urllib.request.urlopen(
        urllib.request.Request(
            PROJECTS_COLLECTION_URL,
            headers=auth_header,
            method="GET",
        )
    ) as response:
        projects = json.loads(response.read())

    print("\nListed projects:")
    pprint(projects)

    with urllib.request.urlopen(
        urllib.request.Request(
            f"{PROJECTS_COLLECTION_URL}{project_id}",
            headers=auth_header,
            method="GET",
        )
    ) as response:
        project_detail = json.loads(response.read())

    print("\nFetched project detail:")
    pprint(project_detail)

    update_payload = {"description": "Updated project description."}
    with urllib.request.urlopen(
        urllib.request.Request(
            f"{PROJECTS_COLLECTION_URL}{project_id}",
            data=json.dumps(update_payload).encode(),
            headers={**auth_header, "Content-Type": "application/json"},
            method="PATCH",
        )
    ) as response:
        updated_project = json.loads(response.read())

    print("\nUpdated project:")
    pprint(updated_project)

    with urllib.request.urlopen(
        urllib.request.Request(
            f"{PROJECTS_COLLECTION_URL}{project_id}",
            headers=auth_header,
            method="DELETE",
        )
    ) as response:
        delete_status = response.status

    print("\nDeleted project (204 expected). Status:", delete_status)

    return 0


if __name__ == "__main__":
    sys.exit(main())
