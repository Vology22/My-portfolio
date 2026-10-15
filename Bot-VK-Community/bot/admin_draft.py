from __future__ import annotations

import json

from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import AdminDraft


async def set_draft(session: AsyncSession, admin_id: int, action: str, data: dict | None = None) -> None:
    draft = await session.get(AdminDraft, admin_id)
    payload = json.dumps(data or {})
    if draft is None:
        session.add(AdminDraft(admin_vk_id=admin_id, action=action, data=payload))
    else:
        draft.action = action
        draft.data = payload
    await session.commit()


async def clear_draft(session: AsyncSession, admin_id: int) -> None:
    draft = await session.get(AdminDraft, admin_id)
    if draft is not None:
        await session.delete(draft)
        await session.commit()


def draft_data(draft: AdminDraft) -> dict:
    return json.loads(draft.data or "{}")
