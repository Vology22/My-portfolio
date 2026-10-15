from __future__ import annotations

import random


def new_random_id() -> int:
    """random_id для messages.send / wall.post — 0 может привести к молчаливой склейке
    одинаковых сообщений, отправленных в один момент времени, поэтому берём случайное."""
    return random.randint(-(2**31), 2**31 - 1)
