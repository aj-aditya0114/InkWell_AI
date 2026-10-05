"""Entry point for the refactored Blog Writer application.

Import `app` from this file wherever you previously imported the compiled
graph from the original single-file script.
"""

from app.graph import app

__all__ = ["app"]


if __name__ == "__main__":
    print("Blog Writer graph loaded successfully.")
    print("Import with: from main import app")
