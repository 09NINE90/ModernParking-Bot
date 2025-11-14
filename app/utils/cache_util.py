import asyncio
import time
from typing import Any, Optional


class InMemoryCache:
    """Простой кэш в памяти с поддержкой TTL (времени жизни ключей)."""

    def __init__(self):
        self._cache = {}
        self._lock = asyncio.Lock()

    async def set(self, key: int, value: Any, ttl: Optional[int] = None):
        """
        Сохраняет значение по ключу.
        :param key: ключ (например, user_id)
        :param value: сохраняемое значение
        :param ttl: время жизни (в секундах), по истечении удаляется
        """
        expire_time = time.time() + ttl if ttl else None
        async with self._lock:
            self._cache[key] = (value, expire_time)

    async def get(self, key: int) -> Optional[Any]:
        """Возвращает значение по ключу или None, если не найдено или истек TTL."""
        async with self._lock:
            item = self._cache.get(key)
            if not item:
                return None

            value, expire_time = item
            if expire_time and time.time() > expire_time:
                # срок жизни истёк — удаляем
                del self._cache[key]
                return None

            return value

    async def get_all(self):
        return self._cache

    async def delete(self, key: int):
        """Удаляет элемент из кэша по ключу."""
        async with self._lock:
            self._cache.pop(key, None)

    async def clear(self):
        """Полностью очищает кэш."""
        async with self._lock:
            self._cache.clear()

    async def cleanup_expired(self):
        """Удаляет все устаревшие элементы (можно вызывать периодически)."""
        async with self._lock:
            now = time.time()
            expired_keys = [k for k, (_, t) in self._cache.items() if t and now > t]
            for k in expired_keys:
                del self._cache[k]
