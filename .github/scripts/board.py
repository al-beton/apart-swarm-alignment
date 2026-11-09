"""Keep an issue's Status on the project board equal to its queue label.

Run by `.github/workflows/board.yml` on every issue event, with the issue's node
id, labels (a JSON list) and state in the environment, and `GH_TOKEN` set to the
`PROJECT_TOKEN` secret. It adds the issue to the board (adding one already there
returns its item) and sets its Status to its queue label's column, Done once
closed, or clears it when the issue has no queue label.

Implements: team/board-follows-labels
"""

import json
import os
import subprocess

PROJECT = "PVT_kwHOAOxafc4BqyPG"  # Al's project 2
FIELD = "PVTSSF_lAHOAOxafc4BqyPGzhpHwh4"  # its Status field
COLUMNS = {  # queue label -> the Status option for its column
    "ready": "a01d4fde",
    "in-progress": "3fc57595",
    "in-review": "e6ef7de0",
    "blocked": "aa728341",
    "on-hold": "d168af83",
}
DONE = "f4c3e9c6"

ADD = """mutation($project: ID!, $issue: ID!) {
  addProjectV2ItemById(input: {projectId: $project, contentId: $issue}) { item { id } }
}"""
SET = """mutation($project: ID!, $item: ID!, $field: ID!, $option: String!) {
  updateProjectV2ItemFieldValue(input: {projectId: $project, itemId: $item,
    fieldId: $field, value: {singleSelectOptionId: $option}}) { projectV2Item { id } }
}"""
CLEAR = """mutation($project: ID!, $item: ID!, $field: ID!) {
  clearProjectV2ItemFieldValue(input: {projectId: $project, itemId: $item,
    fieldId: $field}) { projectV2Item { id } }
}"""


def status_option(labels, state):
    """The Status option for an issue with these labels, or None for no Status."""
    if state == "closed":
        return DONE
    for label, option in COLUMNS.items():
        if label in labels:
            return option
    return None


def sync(issue, labels, state, graphql):
    """Put the issue on the board and set (or clear) its Status."""
    added = graphql(ADD, project=PROJECT, issue=issue)
    item = added["addProjectV2ItemById"]["item"]["id"]
    option = status_option(labels, state)
    if option:
        graphql(SET, project=PROJECT, item=item, field=FIELD, option=option)
    else:
        graphql(CLEAR, project=PROJECT, item=item, field=FIELD)


def gh_graphql(query, **variables):
    args = ["gh", "api", "graphql", "-f", f"query={query}"]
    for name, value in variables.items():
        args += ["-f", f"{name}={value}"]
    done = subprocess.run(args, capture_output=True, text=True, check=True)
    return json.loads(done.stdout)["data"]


def main():
    sync(
        os.environ["ISSUE"],
        json.loads(os.environ["LABELS"]),
        os.environ["STATE"],
        gh_graphql,
    )


if __name__ == "__main__":
    main()
