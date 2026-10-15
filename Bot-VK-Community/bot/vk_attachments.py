from __future__ import annotations

from typing import Iterable


def attachments_to_string(attachments: Iterable | None) -> str:
    """Преобразует список вложений (сообщения ИЛИ поста стены — обе VK-модели имеют
    одинаковую форму {type, <type>: {...}}) в строку для параметра attachments
    методов wall.post/wall.get: "photo<owner_id>_<id>[_<access_key>]"."""
    parts: list[str] = []
    for att in attachments or []:
        obj = getattr(att, att.type.value, None)
        if obj is None:
            continue
        piece = f"{att.type.value}{obj.owner_id}_{obj.id}"
        access_key = getattr(obj, "access_key", None)
        if access_key:
            piece += f"_{access_key}"
        parts.append(piece)
    return ",".join(parts)
