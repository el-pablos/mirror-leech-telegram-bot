"""
Rate limiting utilities to prevent command spam and abuse.
"""

from collections import defaultdict
from time import time
from asyncio import Lock

from ... import LOGGER


class RateLimiter:
    """
    Rate limiter for user commands.
    Implements token bucket algorithm for flexible rate limiting.
    """
    
    def __init__(self, rate: int = 5, per: int = 60, burst: int = 10):
        """
        Initialize rate limiter.
        
        Args:
            rate: Number of allowed requests
            per: Time period in seconds
            burst: Maximum burst size (tokens in bucket)
        """
        self.rate = rate
        self.per = per
        self.burst = burst
        self.allowance = defaultdict(lambda: burst)
        self.last_check = defaultdict(lambda: time())
        self._lock = Lock()
    
    async def is_allowed(self, user_id: int) -> tuple[bool, float]:
        """
        Check if user is allowed to make a request.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Tuple of (is_allowed, wait_time)
            - is_allowed: True if request is allowed
            - wait_time: Seconds to wait before next request (0 if allowed)
        """
        async with self._lock:
            current = time()
            time_passed = current - self.last_check[user_id]
            self.last_check[user_id] = current
            
            # Add tokens based on time passed
            self.allowance[user_id] += time_passed * (self.rate / self.per)
            
            # Cap at burst limit
            if self.allowance[user_id] > self.burst:
                self.allowance[user_id] = self.burst
            
            # Check if request is allowed
            if self.allowance[user_id] < 1.0:
                # Calculate wait time
                wait_time = (1.0 - self.allowance[user_id]) * (self.per / self.rate)
                return False, wait_time
            else:
                # Consume one token
                self.allowance[user_id] -= 1.0
                return True, 0.0
    
    async def reset_user(self, user_id: int):
        """Reset rate limit for a specific user."""
        async with self._lock:
            self.allowance[user_id] = self.burst
            self.last_check[user_id] = time()
    
    async def get_remaining(self, user_id: int) -> int:
        """Get remaining requests for user."""
        async with self._lock:
            return int(self.allowance[user_id])


class SimpleRateLimiter:
    """
    Simple time-based rate limiter.
    Easier to use but less flexible than token bucket.
    """
    
    def __init__(self, cooldown: int = 2):
        """
        Initialize simple rate limiter.
        
        Args:
            cooldown: Cooldown period in seconds between requests
        """
        self.cooldown = cooldown
        self.last_request = defaultdict(float)
        self._lock = Lock()
    
    async def is_allowed(self, user_id: int) -> tuple[bool, float]:
        """
        Check if user is allowed to make a request.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Tuple of (is_allowed, wait_time)
        """
        async with self._lock:
            current = time()
            last = self.last_request[user_id]
            time_passed = current - last
            
            if time_passed < self.cooldown:
                wait_time = self.cooldown - time_passed
                return False, wait_time
            else:
                self.last_request[user_id] = current
                return True, 0.0
    
    async def reset_user(self, user_id: int):
        """Reset rate limit for a specific user."""
        async with self._lock:
            self.last_request[user_id] = 0.0


# Global rate limiters for different command types
command_rate_limiter = SimpleRateLimiter(cooldown=2)  # 2 seconds between commands
download_rate_limiter = RateLimiter(rate=10, per=60, burst=15)  # 10 downloads per minute, burst 15
upload_rate_limiter = RateLimiter(rate=10, per=60, burst=15)  # 10 uploads per minute, burst 15


async def check_rate_limit(user_id: int, limiter_type: str = "command") -> tuple[bool, str]:
    """
    Check rate limit for user.
    
    Args:
        user_id: Telegram user ID
        limiter_type: Type of limiter ("command", "download", "upload")
        
    Returns:
        Tuple of (is_allowed, message)
        - is_allowed: True if request is allowed
        - message: Error message if not allowed, empty string otherwise
    """
    # Select appropriate limiter
    if limiter_type == "download":
        limiter = download_rate_limiter
    elif limiter_type == "upload":
        limiter = upload_rate_limiter
    else:
        limiter = command_rate_limiter
    
    # Check rate limit
    is_allowed, wait_time = await limiter.is_allowed(user_id)
    
    if not is_allowed:
        wait_seconds = int(wait_time) + 1
        message = f"⏳ Rate limit exceeded. Please wait {wait_seconds} seconds before trying again."
        LOGGER.warning(f"Rate limit exceeded for user {user_id} ({limiter_type}). Wait time: {wait_seconds}s")
        return False, message
    
    return True, ""


async def reset_rate_limit(user_id: int, limiter_type: str = "all"):
    """
    Reset rate limit for user.
    
    Args:
        user_id: Telegram user ID
        limiter_type: Type of limiter to reset ("command", "download", "upload", "all")
    """
    if limiter_type in ["command", "all"]:
        await command_rate_limiter.reset_user(user_id)
    
    if limiter_type in ["download", "all"]:
        await download_rate_limiter.reset_user(user_id)
    
    if limiter_type in ["upload", "all"]:
        await upload_rate_limiter.reset_user(user_id)
    
    LOGGER.info(f"Rate limit reset for user {user_id} ({limiter_type})")

