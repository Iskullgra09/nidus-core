"""Apply Alembic migrations to the test database (POSTGRES_TEST_DB)."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from app.core.config import settings  # noqa: E402


def main() -> None:
    os.environ["ALEMBIC_DATABASE_URL"] = settings.TEST_DATABASE_URL
    print(f"Migrating test database: {settings.POSTGRES_TEST_DB}")
    subprocess.run(
        ["uv", "run", "alembic", "upgrade", "head"],
        cwd=BACKEND_DIR,
        check=True,
    )
    print("Test database migration complete.")


if __name__ == "__main__":
    main()
