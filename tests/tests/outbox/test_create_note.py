from bovine_tortoise.models import OutboxEntry

from tests.utils import get_activity_from_json
from tests.utils.blog_test_env import blog_test_env  # noqa: F401


async def test_buffalo_create_note(blog_test_env):  # noqa F811
    item = get_activity_from_json("data/buffalo_create_note_1.json")

    result = await blog_test_env.send_to_outbox(item)

    assert result.status_code == 202

    assert await OutboxEntry.filter(actor=blog_test_env.actor).count() == 1
    entry = await OutboxEntry.filter(actor=blog_test_env.actor).get()
    assert entry.content == item

    result = await blog_test_env.get_from_outbox()
    assert result["id"].endswith(blog_test_env.local_user.get_outbox())  # FIXME?
    assert result["type"] == "OrderedCollection"

    # LABEL: ap-c2s-add-to-outbox
    assert result["totalItems"] == 1
    created_item = result["orderedItems"][0]
    assert created_item == item

    assert created_item["type"] == "Create"
    assert isinstance(created_item["object"], dict)
    object_item = created_item["object"]

    assert object_item["type"] == "Note"

    # LABEL: fedi-objects-are-accessible-via-id
    object_id = object_item["id"]

    result = await blog_test_env.get_activity(object_id)
    assert result["type"] == "Note"
    assert "@context" in result
