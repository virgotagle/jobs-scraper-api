"""CLI tool to generate new API keys."""

import argparse
import sys

from ..core.database import close_repository, init_repository
from ..core.security import generate_api_key, get_key_prefix, hash_api_key


def main() -> None:
    """Generate and store a new API key."""
    parser = argparse.ArgumentParser(
        description="Generate API key for Jobs Scraper API"
    )
    parser.add_argument("--name", required=True, help="Name of the key owner")
    parser.add_argument("--email", required=True, help="Email of the key owner")
    parser.add_argument("--company", help="Company name (optional)")
    parser.add_argument(
        "--rate-limit",
        type=int,
        default=1000,
        help="Requests per hour limit (default: 1000)",
    )

    args = parser.parse_args()

    try:
        # Initialize database
        repo = init_repository()
        if repo is None:
            print("❌ Error: Failed to initialize database repository")
            sys.exit(1)

        # Check if email already has an active key
        existing = repo.get_api_key_by_email(args.email)
        if existing and existing.is_active is True:
            print(f"❌ Error: Email '{args.email}' already has an active API key")
            print(f"   Key prefix: {existing.key_prefix}")
            print(f"   Created: {existing.created_at}")
            sys.exit(1)

        # Generate API key
        api_key = generate_api_key()
        key_hash = hash_api_key(api_key)
        key_prefix = get_key_prefix(api_key)

        # Save to database
        created_key = repo.create_api_key(
            key_hash=key_hash,
            key_prefix=key_prefix,
            name=args.name,
            email=args.email,
            company=args.company,
            rate_limit=args.rate_limit,
        )

        # Display results
        print("\n✅ API Key generated successfully!")
        print(f"   ID: {created_key.id}")
        print(f"   Name: {args.name}")
        print(f"   Email: {args.email}")
        if args.company:
            print(f"   Company: {args.company}")
        print(f"   Rate Limit: {args.rate_limit} requests/hour")
        print(f"\n   API Key: {api_key}")
        print("\n⚠️  IMPORTANT: Save this key securely - it won't be shown again!\n")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    finally:
        close_repository()


if __name__ == "__main__":
    main()
