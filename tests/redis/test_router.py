"""
Tests for RedisRouter orchestration.
"""

import pytest

from codex_bot.redis.router import RedisRouter


@pytest.fixture
def router():
    return RedisRouter()


def test_router_message_registration(router):
    @router.message("test.event")
    async def handler(payload, container):
        pass

    assert "test.event" in router.handlers
    assert len(router.handlers["test.event"]) == 1
    assert router.handlers["test.event"][0][0] == handler
    assert router.handlers["test.event"][0][1] is None


def test_router_message_with_filter(router):
    def test_filter(p):
        return True

    @router.message("filtered.event", filter_func=test_filter)
    async def handler(payload, container):
        pass

    assert router.handlers["filtered.event"][0][1] == test_filter


def test_router_multiple_handlers(router):
    @router.message("multi.event")
    async def h1(p, c):
        pass

    @router.message("multi.event")
    async def h2(p, c):
        pass

    assert len(router.handlers["multi.event"]) == 2
