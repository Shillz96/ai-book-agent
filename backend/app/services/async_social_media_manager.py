from typing import Dict, List, Optional, Any
import asyncio
import logging

from .social_media_manager import SocialMediaManager

logger = logging.getLogger(__name__)

class AsyncSocialMediaManager:
    """Light-weight asynchronous wrapper for the existing synchronous
    SocialMediaManager.  

    This class delegates all blocking network I/O to a background thread
    via ``asyncio.to_thread`` so calls can be awaited concurrently.  It keeps
    the public interface intentionally minimal – just the operations that the
    rest of the codebase currently uses – and therefore stays <100 LOC to
    respect the project guideline for small, focused files.

    NOTE: No behaviour is changed; we only expose an *async* facade to allow
    the orchestrator to run multiple posts in parallel without blocking the
    event loop.
    """

    def __init__(self, config: Dict[str, str]):
        # Underlying synchronous manager holds all auth state.
        self._sync_manager = SocialMediaManager(config)

    # ---------------------------------------------------------------------
    # Public helpers we expose (all simple pass-throughs)
    # ---------------------------------------------------------------------

    def get_platform_status(self) -> Dict[str, bool]:
        """Return availability of each configured platform."""
        return self._sync_manager.get_platform_status()

    def test_platform_connection(self, platform: str) -> Dict[str, Any]:
        """Quick connectivity test – still synchronous because it is rarely
        called and fine to block in HTTP handlers."""
        return self._sync_manager.test_platform_connection(platform)

    # ------------------------------------------------------------------
    # Asynchronous posting helpers
    # ------------------------------------------------------------------

    async def post_content(
        self,
        platform: str,
        content: str,
        media_urls: Optional[List[str]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Asynchronously publish *content* on *platform*.

        Internally defers to the synchronous ``SocialMediaManager.post_content``
        in a worker thread so multiple calls can be executed concurrently via
        ``asyncio.gather``.
        """
        return await asyncio.to_thread(
            self._sync_manager.post_content,
            platform,
            content,
            media_urls,
            **kwargs,
        )

    # ------------------------------------------------------------------
    # Compatibility helpers (place-holders – still blocking inside thread)
    # ------------------------------------------------------------------

    def schedule_post(
        self,
        platform: str,
        content: str,
        scheduled_time: str,
        media_urls: Optional[List[str]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Backward-compatibility shim for the (currently unfinished)
        scheduling API used in *backend/main.py*.

        Implementation simply defers to the synchronous manager **now** so we
        don't introduce functional changes while still allowing the codebase
        to run. When a real scheduler is introduced, this method can be
        upgraded to queue jobs in APScheduler.
        """
        logger.warning("schedule_post is a stub – executing immediately")
        return self._sync_manager.post_content(platform, content, media_urls) 