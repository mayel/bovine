class ActorBuilder:
    def __init__(self, name, actor_type="Person"):
        self.name = name
        self.actor_type = actor_type
        self.account_url = None
        self.public_key = None

    def with_account_url(self, account_url):
        self.account_url = account_url
        return self

    def with_public_key(self, public_key):
        self.public_key = public_key
        return self

    def build(self):
        return {
            "@context": self._build_context(),
            "name": self.name,
            "preferredUsername": self.name,
            "type": self.actor_type,
            **self._build_account_urls(),
            **self._build_private_key(),
        }

    def _build_context(self):
        if self.public_key:
            return [
                "https://www.w3.org/ns/activitystreams",
                "https://w3id.org/security/v1",
            ]

        return "https://www.w3.org/ns/activitystreams"

    def _build_account_urls(self):
        if not self.account_url:
            return {}
        return {
            "id": self.account_url,
            "inbox": self.account_url + "/inbox",
            "outbox": self.account_url + "/outbox",
        }

    def _build_private_key(self):
        if self.public_key:
            return {
                "publicKey": {
                    "id": self.account_url + "#main-key",
                    "owner": self.account_url,
                    "publicKeyPem": self.public_key,
                }
            }
        return {}
