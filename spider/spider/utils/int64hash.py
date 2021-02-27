import hashlib
from typing import Dict, List


class Int64Hash:
    BYTES = 8
    BITS = BYTES * 8
    BITS_MINUS1 = BITS - 1
    MIN = -(2 ** BITS_MINUS1)
    MAX = 2 ** BITS_MINUS1 - 1

    @classmethod
    def as_dict(cls, texts: List[str]) -> Dict[int, str]:
        return {cls.as_int(text): text for text in texts}  # Intentionally reversed.

    @classmethod
    def as_int(cls, text: str) -> int:
        seed = text.encode()
        hash_digest = hashlib.shake_128(seed).digest(cls.BYTES)
        hash_int = int.from_bytes(hash_digest, byteorder='big', signed=True)
        assert cls.MIN <= hash_int <= cls.MAX
        return hash_int

    @classmethod
    def as_list(cls, texts: List[str]) -> List[int]:
        return [cls.as_int(text) for text in texts]
