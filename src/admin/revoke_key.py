"""CLI tool to revoke API keys."""

import argparse
import sys

from ..core.database import close_repository, init_repository


def main() -> None:
    """Revoke an API key by ID."""
    parser = argparse.ArgumentParser(description="Revoke API key for Jobs Scraper API")
    parser.add_argument("--id", type=int, required=True, help="API key ID to revoke")

    args = parser.parse_args()

    try:
        # Initialize database
        repo = init_repository()

        # Deactivate the key
        success = repo.deactivate_api_key(args.id)

        if success:
            print(f"\n✅ API key #{args.id} has been revoked successfully.\n")
        else:
            print(f"\n❌ API key #{args.id} not found.\n")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    finally:
        close_repository()


if __name__ == "__main__":
    main()
