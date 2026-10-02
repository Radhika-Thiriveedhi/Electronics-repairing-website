import time
import random
import string

def generate_id(prefix: str = "ITEM") -> str:
    """Generates a unique human-readable identifier with prefix."""
    timestamp = int(time.time() * 1000) % 1000000
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
    return f"{prefix.upper()}-{timestamp:06d}-{random_str}"
