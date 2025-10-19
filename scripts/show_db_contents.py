#!/usr/bin/env python3
"""Display tables and rows from the running Docker-backed Postgres instance."""

from __future__ import annotations

import subprocess
import sys

INSPECT_TABLES = ("users", "projects")


def run_compose_psql(command: str) -> str:
    compose_cmd = [
        "docker",
        "compose",
        "exec",
        "-T",
        "db",
        "psql",
        "-U",
        "postgres",
        "-d",
        "project_registry",
        "-c",
        command,
        "--csv",
    ]
    result = subprocess.run(compose_cmd, capture_output=True, text=True, check=True)
    return result.stdout


def main() -> int:
    try:
        tables_output = run_compose_psql("SELECT tablename FROM pg_tables WHERE schemaname='public';")
    except subprocess.CalledProcessError as exc:
        print("Failed to connect to database. Is docker compose up?")
        print(exc.stderr)
        return exc.returncode or 1

    print("Available tables:")
    print(tables_output.strip() or "(none)")

    for table in INSPECT_TABLES:
        print(f"\nContents of {table}:")
        try:
            rows_output = run_compose_psql(f"SELECT * FROM {table};")
        except subprocess.CalledProcessError as exc:
            print(f"Could not query {table}:")
            print(exc.stderr)
            continue
        print(rows_output.strip() or "(no rows)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
