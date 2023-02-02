from unittest.mock import patch
import json

from bovine.utils.test.in_memory_test_app import app
from bovine_tortoise.processors import default_inbox_process
from bovine_tortoise.test_database import db_url  # noqa: F401
from bovine_tortoise.models import InboxEntry

from tests.utils import create_actor_and_local_user, build_inbox_item_from_json


@patch("bovine_core.clients.signed_http.signed_post")
async def test_mastodon_announce_then_undo(mock_signed_post, db_url):  # noqa F811
    async with app.app_context():
        actor, local_user = await create_actor_and_local_user()
        like_item = build_inbox_item_from_json("test_data/mastodon_announce_1.json")
        undo_item = build_inbox_item_from_json(
            "test_data/mastodon_announce_1_undo.json"
        )

        like_item_id = like_item.get_data()["id"]

        await default_inbox_process(like_item, local_user)
        assert await InboxEntry.filter(actor=actor).count() == 1

        inbox_entry = await InboxEntry.filter(actor=actor).get()

        assert inbox_entry.content_id == like_item_id
        assert inbox_entry.content["type"] == "Announce"

        # FIXME: Should fetch actual object

        await default_inbox_process(undo_item, local_user)

        assert await InboxEntry.filter(actor=actor).count() == 0
