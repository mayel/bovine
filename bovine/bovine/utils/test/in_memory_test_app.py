import logging
import sys
from unittest.mock import AsyncMock

import aiohttp
import pytest
from bovine_core.utils.signature_checker import SignatureChecker
from quart import Quart

from bovine import get_bovine_user
from bovine.clients import get_public_key
from bovine.server import default_configuration
from bovine.types import LocalActor
from bovine.utils import dump_incoming_inbox_to_stdout
from bovine.utils.in_memory_store import InMemoryUserStore

from . import get_user_keys

log_format = "[%(asctime)s] %(levelname)-8s %(name)-12s %(message)s"
logging.basicConfig(level=logging.DEBUG, format=log_format, stream=sys.stderr)


async def silly(*args):
    print("Coroutine silly called with", args)
    return


signature_checker = SignatureChecker(get_public_key)

public_key, private_key = get_user_keys()
local_actor = LocalActor(
    "user",
    "https://my_domain/activitypub/user",
    public_key,
    private_key,
    "Person",
).set_inbox_process(dump_incoming_inbox_to_stdout)

data_store = InMemoryUserStore()
data_store.add_user(local_actor)
data_store.add_user(get_bovine_user("my_domain"))

app = Quart(__name__)
app.config.update(
    {
        "DOMAIN": "my_domain",
        "validate_signature": signature_checker.validate_signature,
        "get_user": data_store.get_user,
        "session": AsyncMock(aiohttp.ClientSession),
        "inbox_getter": silly,
    }
)
app.register_blueprint(default_configuration)


@pytest.fixture
def test_client_with_authorization():
    app.config["validate_signature"] = AsyncMock()
    app.config["validate_signature"].return_value = "public_key"

    client = app.test_client()

    return client


@pytest.fixture
def test_client_with_bearer_authorization():
    app.config["account_name_or_none_for_token"] = AsyncMock()
    app.config["account_name_or_none_for_token"].return_value = "user"
    app.config["validate_signature"] = AsyncMock()
    app.config["validate_signature"].return_value = None

    client = app.test_client()

    return client


@pytest.fixture
def test_client_without_authorization():
    app.config["validate_signature"] = AsyncMock()
    app.config["validate_signature"].return_value = "public_key"

    client = app.test_client()

    return client
