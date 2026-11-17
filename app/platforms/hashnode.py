"""Hashnode integration — publishes an article via the GraphQL API.

How to get the credentials:
    1. https://hashnode.com/settings/developer -> Generate New Token
       -> .env as HASHNODE_PAT
    2. Publication id: run this query with your token (see README):

       query { me { publications(first: 5) { edges { node { id url } } } } }

       -> .env as HASHNODE_PUBLICATION_ID

Docs: https://apidocs.hashnode.com/  (endpoint: https://gql.hashnode.com)
"""

import httpx

from app import config
from app.platforms.base import BasePlatform
from app.utils import title_from_message

PUBLISH_MUTATION = """
mutation PublishPost($input: PublishPostInput!) {
  publishPost(input: $input) {
    post {
      url
    }
  }
}
"""


class Hashnode(BasePlatform):
    name = "Hashnode"

    def post(self, message: str):
        if not config.HASHNODE_PAT or not config.HASHNODE_PUBLICATION_ID:
            return self.failure(
                "HASHNODE_PAT / HASHNODE_PUBLICATION_ID are not set in .env"
            )

        title = title_from_message(message)
        payload = {
            "query": PUBLISH_MUTATION,
            "variables": {
                "input": {
                    "publicationId": config.HASHNODE_PUBLICATION_ID,
                    "title": title,
                    "contentMarkdown": message,
                }
            },
        }
        headers = {
            "Authorization": config.HASHNODE_PAT,
            "Content-Type": "application/json",
        }

        try:
            response = httpx.post(
                "https://gql.hashnode.com/",
                headers=headers,
                json=payload,
                timeout=self.timeout,
            )
        except httpx.HTTPError as exc:
            return self.failure(f"Hashnode request failed: {exc}")

        try:
            data = response.json()
        except ValueError:
            return self.failure(self.error_text(response))

        # GraphQL reports problems inside an "errors" array with HTTP 200.
        if data.get("errors"):
            message_text = data["errors"][0].get("message", "Unknown GraphQL error")
            return self.failure(f"Hashnode: {message_text}")

        post_url = (data.get("data", {}).get("publishPost", {}) or {}).get("post", {})
        if not post_url or not post_url.get("url"):
            return self.failure("Hashnode did not return a post URL")

        return self.success(post_url["url"])
