"""
String utils module
"""

import base64
from datetime import datetime
import hashlib
from pathlib import Path
from random import choice
import re
import string
import uuid


def make_random_string(size: int) -> str:
    return "".join(choice(string.ascii_letters + string.digits) for _ in range(size))


def encrypt_base64(raw_path: str) -> str:
    """
    base64 Encode Function.
    """
    return base64.b64encode(raw_path.encode()).decode()


def decrypt_base64(path: str) -> str:
    """
    base64 Decode Function
    """
    return base64.b64decode(path).decode()


def not_implemented_msg() -> dict[str, str]:
    not_implemented = {"detail": "Not implemented"}
    return not_implemented


NOT_IMPLEMENTED = {"detail": "Not implemented"}


def name_to_snake(file_name: str) -> str:
    """Convert a PascalCase, camelCase, or kebab-case string to snake_case.

    Args:
        camel: The string to convert.

    Returns:
        The converted string in snake_case.
    """
    # Handle the sequence of uppercase letters followed by a lowercase letter
    snake = re.sub(
        r"([A-Z]+)([A-Z][a-z])",
        lambda m: f"{m.group(1)}_{m.group(2)}",
        file_name,
    )
    # Insert an underscore between a lowercase letter and an uppercase letter
    snake = re.sub(r"([a-z])([A-Z])", lambda m: f"{m.group(1)}_{m.group(2)}", snake)
    # Insert an underscore between a digit and an uppercase letter
    # snake = re.sub(r"([0-9])([A-Z])", lambda m: f"{m.group(1)}_{m.group(2)}", snake)
    # Insert an underscore between a lowercase letter and a digit
    # snake = re.sub(r"([a-z])([0-9])", lambda m: f"{m.group(1)}_{m.group(2)}", snake)
    # Replace hyphens with underscores to handle kebab-case
    snake = snake.replace("-", "_")
    snake = snake.replace(" ", "_")

    return snake.lower()


def generate_unique_filename(
    original_filename: str | None, posfix: str = "_original"
) -> str:
    """Generate unique filename based on hash of original name, timestamp and UUID."""
    if original_filename is None:
        raise ValueError("Filename must be provided")

    # Create hash input string
    timestamp = datetime.now().isoformat()
    unique_id = str(uuid.uuid4())
    base_name = Path(original_filename).stem if original_filename else "file"

    # Combine all components for hashing
    hash_input = f"{base_name}_{timestamp}_{unique_id}"

    # Generate short hash (first 12 chars of SHA256)
    hash_object = hashlib.sha256(hash_input.encode())
    short_hash = hash_object.hexdigest()[:16]

    return f"{short_hash}{posfix}"
