import json
import logging
import uuid

import aiohttp
from quart import Quart, request
from tortoise.contrib.quart import register_tortoise

from bovine_tortoise.models import Actor, InboxEntry, Following, Follower
from bovine_tortoise.actions import follow, fetch_post
from bovine_tortoise import ManagedDataStore
from bovine_tortoise.outbox import send_activity
from bovine_tortoise.processors import store_in_database

from .utils import build_create_note_activity_from_data_base_case


log_format = "[%(asctime)s] %(levelname)-8s %(name)-12s %(message)s"

logging.basicConfig(
    level=logging.INFO,
    format=log_format,
    filename=("debug_admin.log"),
)


app = Quart(__name__)
username = "helge"


@app.before_serving
async def startup():
    app.config["session"] = aiohttp.ClientSession()


@app.get("/")
async def index():
    actor = await Actor.get_or_none(account=username)
    entries = await InboxEntry.filter(actor=actor).all()

    contents = [[entry.id, entry.content] for entry in entries]

    return contents[::-1]


@app.get("/follow")
async def get_follow():
    actor = await Actor.get_or_none(account=username)
    following = await Following.filter(actor=actor).all()
    follower = await Follower.filter(actor=actor).all()

    following_list = [x.account for x in following]
    follower_list = [x.account for x in follower]

    return {"follower": follower_list, "following": following_list}


@app.route("/add_follow", methods=["POST"])
async def add_follow():
    store = ManagedDataStore()
    local_user = await store.get_user(username)
    data = await request.get_json()

    remote_account = data["account"]

    print(remote_account)

    await follow(app.config["session"], local_user, remote_account)

    print("done")

    return {}


@app.route("/cleanup")
async def cleanup_timeline():
    max_id = request.args.get("max_id")
    actor = await Actor.get_or_none(account=username)
    await InboxEntry.filter(actor=actor).filter(id__lt=max_id).delete()

    return {"status": "done"}


async def send_activity_wrapper(list_of_args):
    await send_activity(*list_of_args)


@app.route("/post", methods=["POST"])
async def handle_post():
    store = ManagedDataStore()
    local_user = await store.get_user(username)
    data = await request.get_json()

    local_path = f"{username}/{str(uuid.uuid4())}"
    url = f"https://mymath.rocks/testing_notes/{local_path}"

    create = build_create_note_activity_from_data_base_case(
        local_user.get_account(), url, data
    )

    logging.info("Posting")
    logging.info(json.dumps(create))

    app.add_background_task(
        send_activity_wrapper, (app.config["session"], local_user, create, local_path)
    )

    return {}


@app.route("/fetch", methods=["POST"])
async def fetch_url():
    store = ManagedDataStore(inbox_processors=[store_in_database])
    local_user = await store.get_user(username)
    data = await request.get_json()

    url = data["url"]

    logging.info(f"Fetching {url}")

    app.add_background_task(fetch_post, app.config["session"], local_user, url)

    return {}


register_tortoise(
    app,
    db_url="sqlite://db.sqlite3",
    modules={"models": ["bovine_tortoise.models"]},
    generate_schemas=False,
)
