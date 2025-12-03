"""CLI tool to list API keys."""

import argparse

from ..core.database import close_repository, init_repository


def main() -> None:
    """List API keys with optional filters."""
    parser = argparse.ArgumentParser(description="List API keys for Jobs Scraper API")
    parser.add_argument(
        "--all", action="store_true", help="Show all keys including inactive"
    )
    parser.add_argument("--email", help="Filter by email address")

    args = parser.parse_args()

    try:
        # Initialize database
        repo = init_repository()
        if repo is None:
            print("❌ Error: Failed to initialize database repository")
            return

        # Get API keys
        if args.email:
            api_key = repo.get_api_key_by_email(args.email)
            api_keys = [api_key] if api_key else []
        elif args.all:
            api_keys = repo.get_all_api_keys()
        else:
            api_keys = repo.get_all_active_api_keys()

        if not api_keys:
            print("No API keys found.")
            return

        # Display keys
        print(
            f"\n{'ID':<5} {'Prefix':<15} {'Name':<25} {'Email':<30} {'Active':<8} {'Requests':<10} {'Created':<20}"
        )
        print("-" * 125)

        for key in api_keys:
            active = "✓" if getattr(key, "is_active", False) else "✗"
            created = key.created_at.strftime("%Y-%m-%d %H:%M:%S")
            print(
                f"{key.id:<5} {key.key_prefix:<15} {key.name:<25} {key.email:<30} "
                f"{active:<8} {key.request_count:<10} {created:<20}"
            )

        print(f"\nTotal: {len(api_keys)} key(s)\n")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        close_repository()


if __name__ == "__main__":
    main()
