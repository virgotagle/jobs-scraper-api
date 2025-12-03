"""Test API key authentication functionality."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.security import (
    generate_api_key,
    get_key_prefix,
    hash_api_key,
    verify_api_key,
)


def test_api_key_generation():
    """Test API key generation."""
    print("Testing API key generation...")

    # Generate key
    api_key = generate_api_key()
    print(f"✓ Generated API key: {api_key[:20]}...")

    # Check format
    assert api_key.startswith("sk_live_"), "Key should start with sk_live_"
    assert len(api_key) > 40, "Key should be sufficiently long"
    print("✓ Key format is correct")

    # Test key prefix
    prefix = get_key_prefix(api_key)
    assert prefix.endswith("..."), "Prefix should end with ..."
    assert len(prefix) == 15, "Prefix should be 15 chars (12 + ...)"
    print(f"✓ Key prefix: {prefix}")

    print()


def test_api_key_hashing():
    """Test API key hashing and verification."""
    print("Testing API key hashing...")

    # Generate and hash key
    api_key = generate_api_key()
    key_hash = hash_api_key(api_key)
    print(f"✓ Hashed key: {key_hash[:30]}...")

    # Verify correct key
    assert verify_api_key(api_key, key_hash), "Should verify correct key"
    print("✓ Correct key verification passed")

    # Verify incorrect key
    wrong_key = generate_api_key()
    assert not verify_api_key(wrong_key, key_hash), "Should reject wrong key"
    print("✓ Wrong key verification failed (as expected)")

    print()


def test_multiple_keys():
    """Test that different keys are unique."""
    print("Testing key uniqueness...")

    keys = [generate_api_key() for _ in range(5)]
    assert len(set(keys)) == 5, "All keys should be unique"
    print(f"✓ Generated 5 unique keys")

    print()


if __name__ == "__main__":
    print("=" * 60)
    print("API Key Authentication Tests")
    print("=" * 60)
    print()

    try:
        test_api_key_generation()
        test_api_key_hashing()
        test_multiple_keys()

        print("=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
