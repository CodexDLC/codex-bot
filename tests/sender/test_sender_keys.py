from codex_bot.sender.sender_keys import SenderKeys


def test_user_key_int():
    key = SenderKeys.user(12345)
    assert key == "sender:user:12345"


def test_user_key_str():
    key = SenderKeys.user("67890")
    assert key == "sender:user:67890"


def test_channel_key_str():
    key = SenderKeys.channel("booking_feed_1")
    assert key == "sender:channel:booking_feed_1"
