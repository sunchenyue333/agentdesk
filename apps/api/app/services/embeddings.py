import hashlib
import math

EMBEDDING_DIMENSIONS = 1536


def embed_text(text: str) -> list[float]:
    """Deterministic local embedding placeholder for Phase 3 demos without an API key."""
    vector = [0.0] * EMBEDDING_DIMENSIONS
    tokens = [token.lower() for token in text.split() if token.strip()]

    if not tokens:
        return vector

    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], "big") % EMBEDDING_DIMENSIONS
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vector[index] += sign

    magnitude = math.sqrt(sum(value * value for value in vector))
    if magnitude == 0:
        return vector

    return [value / magnitude for value in vector]

