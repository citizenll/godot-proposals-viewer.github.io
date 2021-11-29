#!/usr/bin/env python

import json
import os
from typing import Any, List

import requests


def main() -> None:
    # Change to the directory where the script is located,
    # so that the script can be run from any location.
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    print("[*] Fetching proposal JSON pages...")

    all_proposals: List[List[Any]] = []

    page = 1
    # We'll set the number of pages to a "finite" number once we make a request.
    num_pages = 10000

    while page <= num_pages:
        if num_pages == 10000:
            print(f"    Requesting batch of proposals {page}...")
        else:
            print(f"    Requesting batch of proposals {page}/{num_pages}...")
        request = requests.get(
            f"https://api.github.com/repos/godotengine/godot-proposals/issues?state=open&per_page=100&page={page}",
            headers={"Accept": "application/vnd.github.squirrel-girl-preview"},
        )

        if num_pages == 10000:
            # We don't know the number of pages yet, so figure it out.
            links_in_header = request.headers["Link"].split(",")
            for link in links_in_header:
                if '"last"' in link:
                    # Get the page number after the `page` query parameter.
                    num_pages = int(link.split("&page")[1][1:3])

        request_dict = json.loads(request.text)

        for proposal in request_dict:
            # Only include fields we use on the frontend.
            # Use an optimized array form to avoid including dozens of thousands
            # of string keys in the JSON.
            all_proposals.append(
                [
                    proposal["id"],
                    proposal["number"],
                    proposal["title"],
                    proposal["created_at"],
                    proposal["html_url"],
                    proposal["user"]["login"],
                    proposal["comments"],
                    [label["name"] for label in proposal["labels"]],
                    [proposal["reactions"]["+1"], proposal["reactions"]["-1"]],
                ]
            )

        page += 1

    print("[*] Saving proposals.json...")

    with open("proposals.json", "w") as file:
        json.dump(all_proposals, file)

    print("[*] Success!")


if __name__ == "__main__":
    main()
