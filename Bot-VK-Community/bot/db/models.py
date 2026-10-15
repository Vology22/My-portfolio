from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class PostStatus(str, enum.Enum):
    PENDING = "pending"       # ждёт модерации
    ACTIVE = "active"         # одобрен, публикуется по расписанию
    REJECTED = "rejected"     # отклонён модератором
    PAUSED = "paused"         # автор отписался от сообщества
    FROZEN = "frozen"         # ждём ответа автора на периодическое подтверждение
    DELETED = "deleted"       # удалён (вручную или по истечении срока ответа)


class User(Base):
    __tablename__ = "users"

    vk_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(128), default="")
    last_name: Mapped[str] = mapped_column(String(128), default="")
    is_subscribed: Mapped[bool] = mapped_column(Boolean, default=False)
    subscribed_checked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    posts: Mapped[list["Post"]] = relationship(back_populates="author")


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), unique=True)

    posts: Mapped[list["Post"]] = relationship(back_populates="category")
    sources: Mapped[list["CompetitorSource"]] = relationship(back_populates="category")


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    author_vk_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.vk_id"))
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id"))
    is_paid: Mapped[bool] = mapped_column(Boolean)
    text: Mapped[str] = mapped_column(Text, default="")
    attachments: Mapped[str] = mapped_column(Text, default="")  # CSV VK attachment-строк, напр. "photo1_2,photo1_3"
    status: Mapped[PostStatus] = mapped_column(Enum(PostStatus), default=PostStatus.PENDING)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    approved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_renewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    frozen_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    wall_post_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    author: Mapped["User"] = relationship(back_populates="posts")
    category: Mapped["Category"] = relationship(back_populates="posts")


class PostDraft(Base):
    """Черновик объявления, которое пользователь ещё заполняет в диалоге с ботом.

    Состояние визарда хранится в БД (а не в памяти процесса), чтобы перезапуск бота
    не обрывал незавершённую подачу объявления.
    """

    __tablename__ = "post_drafts"

    user_vk_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.vk_id"), primary_key=True)
    step: Mapped[str] = mapped_column(String(32))  # category | paid | text | attachments | confirm
    category_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("categories.id"), nullable=True)
    is_paid: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    text: Mapped[str] = mapped_column(Text, default="")
    attachments: Mapped[str] = mapped_column(Text, default="")
    # Если заполнено — визард редактирует существующий пост, а не создаёт новый
    editing_post_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("posts.id"), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class AdminDraft(Base):
    """Аналог PostDraft, но для многошаговых админских сценариев без слэш-команд
    (ввод числа дней, текста уведомления, названия категории, темы/города для отчёта
    по конкурентам, ссылки на источник). `data` — JSON-строка с промежуточными данными
    между шагами одного сценария."""

    __tablename__ = "admin_drafts"

    admin_vk_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    action: Mapped[str] = mapped_column(String(64))
    data: Mapped[str] = mapped_column(Text, default="{}")
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class Setting(Base):
    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    value: Mapped[str] = mapped_column(Text)


class NotificationEvent(str, enum.Enum):
    NEW_SUBSCRIBER = "new_subscriber"
    NEW_UNSUBSCRIBER = "new_unsubscriber"
    NEW_COMMENT = "new_comment"
    NEW_LIKE = "new_like"
    NEW_MESSAGE = "new_message"


class NotificationPreference(Base):
    """Персональная настройка того, какие события админ/модератор хочет получать
    от бота (🛠 Админ-панель → 🔔 Мои уведомления). Отсутствие строки для пары
    (admin_vk_id, event_type) означает enabled=True по умолчанию — строка
    создаётся только при первом переключении."""

    __tablename__ = "notification_preferences"

    admin_vk_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    event_type: Mapped[NotificationEvent] = mapped_column(Enum(NotificationEvent), primary_key=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)


class CompetitorSource(Base):
    __tablename__ = "competitor_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    group_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    name: Mapped[str] = mapped_column(String(256), default="")
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id"))
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    added_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    # unix-время последнего забранного поста, чтобы wall.get не пересматривал всю стену каждый раз
    last_polled_post_date: Mapped[int | None] = mapped_column(Integer, nullable=True)

    category: Mapped["Category"] = relationship(back_populates="sources")


class RepostedPost(Base):
    __tablename__ = "reposted_posts"
    __table_args__ = (UniqueConstraint("source_group_id", "source_post_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_group_id: Mapped[int] = mapped_column(BigInteger)
    source_post_id: Mapped[int] = mapped_column(Integer)
    our_wall_post_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reposted_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class CompetitorMember(Base):
    """Снапшот участников сообщества-конкурента (используется списком источников
    аггрегатора, CompetitorSource) — на каждом опросе сравнивается с текущим
    списком участников, чтобы понять, кто вступил новый. См.
    bot/modules/audience/poller.py и ТЗ_новые_функции.txt, блок 3."""

    __tablename__ = "competitor_members"

    group_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    vk_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)


class CandidateStatus(str, enum.Enum):
    NEW = "new"
    CONTACTED = "contacted"
    DISMISSED = "dismissed"


class CompetitorAudienceCandidate(Base):
    """Кандидат, прошедший фильтры (мин. друзей/подписчиков/город/ключевые слова
    в тематических подписках) — карточка для РУЧНОЙ обработки администратором в
    🎯 Аудитория конкурентов. Никаких автоматических действий (заявки в друзья,
    рассылка) бот с кандидатом не производит — см. ТЗ_новые_функции.txt, блок 3,
    про осознанный отказ от массовой автоматизации."""

    __tablename__ = "competitor_audience_candidates"

    vk_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    source_group_id: Mapped[int] = mapped_column(BigInteger)
    first_name: Mapped[str] = mapped_column(String(128), default="")
    last_name: Mapped[str] = mapped_column(String(128), default="")
    friends_count: Mapped[int] = mapped_column(Integer, default=0)
    followers_count: Mapped[int] = mapped_column(Integer, default=0)
    city: Mapped[str] = mapped_column(String(128), default="")
    matched_keyword: Mapped[str | None] = mapped_column(String(128), nullable=True)
    status: Mapped[CandidateStatus] = mapped_column(Enum(CandidateStatus), default=CandidateStatus.NEW)
    found_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class CompetitorSnapshot(Base):
    __tablename__ = "competitor_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    query: Mapped[str] = mapped_column(String(256))
    city: Mapped[str] = mapped_column(String(128), default="")
    group_id: Mapped[int] = mapped_column(BigInteger)
    group_name: Mapped[str] = mapped_column(String(256), default="")
    members_count: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    captured_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
