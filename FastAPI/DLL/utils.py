import time
from functools import wraps
from typing import Callable, Any
from fastapi import HTTPException, Depends, Request
from redis.asyncio import Redis

class RateLimitConfig:
    def __init__(self, max_calls: int, period: int):
        self.max_calls = max_calls
        self.period = period


class RateLimiter:
    def __init__(self, redis_client: Redis, config: RateLimitConfig):
        self.redis_client = redis_client
        self.config = config

    def rate_limit(self):
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            @wraps(func)
            async def wrapper(request: Request, *args, token_data: dict = Depends(), **kwargs) -> Any:
                username = token_data.email
                if not username:
                    raise HTTPException(status_code=401, detail="Unauthorized")

                url_path = request.url.path
                key = f"rate_limit:{username}:{url_path}"
                now = time.time()

                timestamps = await self.redis_client.lrange(key, 0, -1)
                timestamps = [float(ts) for ts in timestamps if ts]

                timestamps = [ts for ts in timestamps if now - ts < self.config.period]

                if len(timestamps) >= self.config.max_calls:
                    wait = self.config.period - (now - timestamps[0])
                    raise HTTPException(
                        status_code=429,
                        detail=f"Rate limit exceeded for {url_path}. Retry after {wait:.2f} seconds"
                    )
                timestamps.append(now)
                async with self.redis_client.pipeline() as pipe:
                    await pipe.delete(key)
                    await pipe.rpush(key, *map(str, timestamps))
                    await pipe.expire(key, self.config.period)
                    await pipe.execute()

                return await func(request, *args, token_data=token_data, **kwargs)
            return wrapper
        return decorator
