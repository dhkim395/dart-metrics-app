"""
간단한 메모리 캐시 (TTL 지원).

사용 예:
    from app.cache import cache
    
    # 저장
    cache.set("samsung", {"per": 41.5}, ttl_seconds=3600)
    
    # 조회
    data = cache.get("samsung")
    if data:
        return data  # 캐시 적중!
    else:
        # 새로 계산 후 저장
        data = compute()
        cache.set("samsung", data, ttl_seconds=3600)
        return data
"""
import time
from typing import Any, Optional


class MemoryCache:
    """간단한 메모리 캐시. 키 → (값, 만료시간)."""
    
    def __init__(self):
        self._store: dict[str, tuple[Any, float]] = {}
        # 통계
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """캐시 조회. 만료된 키는 None 반환."""
        if key not in self._store:
            self.misses += 1
            return None
        
        value, expires_at = self._store[key]
        if time.time() > expires_at:
            # 만료됨 → 삭제 후 None
            del self._store[key]
            self.misses += 1
            return None
        
        self.hits += 1
        return value
    
    def set(self, key: str, value: Any, ttl_seconds: int = 3600) -> None:
        """캐시 저장. 기본 TTL 1시간."""
        expires_at = time.time() + ttl_seconds
        self._store[key] = (value, expires_at)
    
    def delete(self, key: str) -> bool:
        """캐시 삭제."""
        if key in self._store:
            del self._store[key]
            return True
        return False
    
    def clear(self) -> int:
        """전체 삭제. 삭제된 개수 반환."""
        count = len(self._store)
        self._store.clear()
        return count
    
    def stats(self) -> dict:
        """캐시 통계."""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        return {
            "total_keys": len(self._store),
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": round(hit_rate, 2),
        }


# 모듈 레벨 싱글톤
cache = MemoryCache()