# Implements: commits/named-paths, review/review-finished, merging/stacked-retarget, merging/main-stays-green, merging/merge-when-clean
import json
import unittest

from deliver import (
    MergeRefused,
    closing_lines,
    commit,
    merge,
    review_finished,
    review_state,
    unsafe_paths,
)


def summary(sha, status):
    state = {"code_review": {"commit_sha": sha, "status": status}}
    return {"body": f"<!-- codex-review-state:v1 {json.dumps(state)} -->\n## Codex"}


class FakeGh:
    """Answers the commands `merge` runs; records every one."""

    def __init__(  # noqa: PLR0913 (one knob per thing a test varies)
        self,
        checks=("success",),
        unresolved=0,
        stacked=(102,),
        review="abc",
        history=None,
        before=None,
    ):
        self.calls = []
        # blocking-checks runs for the head commit, oldest first, by conclusion.
        self.checks = checks
        self.unresolved = unresolved
        self.stacked = stacked
        # The commit Codex last finished reviewing; the head is "abc".
        self.review = review
        # Each commit's parents and the files it changes against its first parent.
        self.history = history or {}
        # What the branch had changed by each commit, against where it left main.
        self.before = before or {}

    def __call__(self, *args):
        self.calls.append(args)
        threads = [{"isResolved": False}] * self.unresolved + [{"isResolved": True}]
        pr = {"reviewThreads": {"nodes": threads}}
        answers = {
            ("pr", "view"): {
                "number": 101,
                "title": "improve(workflow): one routine (#7)",
                "body": "## Issues\nCloses #7\n\n## Notes\nNone",
                "headRefName": "7-one-routine",
                "baseRefName": "main",
                "headRefOid": "abc",
                "files": [{"path": "src/one.py"}, {"path": "tests/test_one.py"}],
            },
            ("pr", "list"): [{"number": n} for n in self.stacked],
            ("repo", "view"): {"owner": {"login": "o"}, "name": "r"},
            ("api", "graphql"): {"data": {"repository": {"pullRequest": pr}}},
            ("run", "list"): [{"databaseId": 7}],
        }
        if args[0] == "api" and args[1].endswith("/comments"):
            done = [summary(self.review, "completed")] if self.review else []
            return json.dumps([{"body": "@codex review"}, *done])
        if args[0] == "api" and "/check-runs" in args[1]:
            runs = [
                {"name": "blocking-checks", "conclusion": c, "started_at": f"t{i}"}
                for i, c in enumerate(self.checks)
            ]
            runs = runs[::-1]  # newest first, like GitHub
            # Without filter=all, GitHub answers only the latest run per name.
            if "filter=all" not in args[1]:
                runs = runs[:1]
            return json.dumps({"check_runs": runs})
        if args[0] == "git":
            return self.git(*args[1:])
        return json.dumps(answers[args[:2]]) if args[:2] in answers else ""

    def git(self, command, *args):
        commit = args[-1]
        if command == "rev-list":
            return " ".join([commit, *self.history.get(commit, ((), ()))[0]])
        if command == "merge-base":
            return "base"
        if command == "diff" and args[-2] == "base":
            # What the branch had changed before the merge: its own files then.
            return "\n".join(self.before.get(commit, ("src/one.py",)))
        if command == "diff":
            return "\n".join(self.history.get(commit, ((), ()))[1])
        return ""

    def index(self, *prefix):
        return next(i for i, c in enumerate(self.calls) if c[: len(prefix)] == prefix)


class DeliverTests(unittest.TestCase):
    def test_review_finished_reads_the_state_marker_not_the_first_comment(self):
        comments = [{"body": "@codex review"}, summary("abc", "running")]
        self.assertFalse(review_finished(review_state(comments), "abc"))
        comments[1] = summary("abc", "completed")
        self.assertTrue(review_finished(review_state(comments), "abc"))
        self.assertIsNone(review_state([{"body": "Looks good"}]))

    def test_review_finished_only_on_the_latest_commit(self):
        state = review_state([summary("old", "completed")])
        self.assertFalse(review_finished(state, "new"))

    def test_named_paths_refuse_everything_and_run_output(self):
        self.assertEqual(
            unsafe_paths([".", "-A", "src/x.py", "runs/scratch/a", "./runs"]),
            [".", "-A", "runs/scratch/a", "./runs"],
        )
        self.assertEqual(unsafe_paths(["runs/x"], allow_runs=True), [])
        self.assertEqual(unsafe_paths(["src", "tests/test_x.py"]), [])

    def test_named_paths_commit_only_what_they_name(self):
        calls = []
        commit(["a.py", "b.md"], ["Subject", "Body"], run=lambda *a: calls.append(a))
        self.assertEqual(calls[0], ("git", "add", "--", "a.py", "b.md"))
        made = calls[1]
        self.assertEqual(made[:2], ("git", "commit"))
        self.assertIn("--only", made)
        self.assertEqual(made[made.index("--") :], ("--", "a.py", "b.md"))

    def test_merge_when_clean_keeps_the_closing_block(self):
        body = "## Issues\nCloses #7\nRefs #3\n\nCloses nothing here"
        self.assertEqual(closing_lines(body), ["Closes #7", "Refs #3"])

    def test_stacked_retarget_happens_before_the_branch_is_deleted(self):
        gh = FakeGh()
        merge(101, gh, pause=lambda seconds: None)
        retarget = gh.index("pr", "edit", "102", "--base", "main")
        squash = gh.index("pr", "merge", "101", "--squash")
        delete = gh.index("git", "push", "origin", "--delete", "7-one-routine")
        self.assertLess(retarget, squash)
        self.assertLess(squash, delete)
        merged = gh.calls[squash]
        self.assertNotIn("--delete-branch", merged)
        self.assertIn("improve(workflow): one routine (#7)", merged)
        self.assertIn("Closes #7", merged[merged.index("--body") + 1])

    def test_main_stays_green_reruns_checks_after_merging(self):
        gh = FakeGh(stacked=())
        merge(101, gh, pause=lambda seconds: None)
        dispatch = gh.index("workflow", "run", "blocking-checks.yml", "--ref", "main")
        watch = gh.index("run", "watch", "7")
        self.assertLess(gh.index("pr", "merge"), dispatch)
        self.assertLess(dispatch, watch)
        self.assertIn("--exit-status", gh.calls[watch])

    def test_merge_when_clean_a_pass_counts_despite_a_later_skipped_run(self):
        # Marking a pull request ready right after a push starts a run whose
        # payload still says draft, so it is skipped, and it can start after
        # the run that passed.
        gh = FakeGh(checks=("skipped", "success", "skipped"))
        merge(101, gh, pause=lambda seconds: None)
        self.assertTrue([c for c in gh.calls if c[:2] == ("pr", "merge")])
        self.assertIn("abc/check-runs", gh.calls[gh.index("api")][1])

    def test_merge_when_clean_refuses_red_checks_open_threads_or_no_codex_review(self):
        for gh in (
            FakeGh(checks=("failure",)),
            FakeGh(checks=("success", "failure")),
            FakeGh(checks=("skipped",)),
            FakeGh(checks=()),
            FakeGh(unresolved=1),
            FakeGh(review=None),
            FakeGh(review="old"),
        ):
            with self.assertRaises(MergeRefused):
                merge(101, gh, pause=lambda seconds: None)
            self.assertFalse([c for c in gh.calls if c[:2] == ("pr", "merge")])

    def test_merge_when_clean_a_plain_merge_of_main_needs_no_second_round(self):
        # Codex reviewed "def"; "abc" merged main into it, touching only main's files,
        # and so did the merge under it, so the reviewed commit is two merges down.
        history = {
            "abc": (("mid", "main2"), ("README.md", "src/other.py")),
            "mid": (("def", "main1"), ("docs/guide.md",)),
        }
        gh = FakeGh(review="def", history=history)
        merge(101, gh, pause=lambda seconds: None)
        self.assertTrue([c for c in gh.calls if c[:2] == ("pr", "merge")])
        # A review of the plain merge in between counts too.
        gh = FakeGh(review="mid", history=history)
        merge(101, gh, pause=lambda seconds: None)
        self.assertTrue([c for c in gh.calls if c[:2] == ("pr", "merge")])

    def test_merge_when_clean_a_merge_that_changes_the_pull_requests_files_needs_review(
        self,
    ):
        for history in (
            # A merge whose resolution edits one of the pull request's own files.
            {"abc": (("def", "main1"), ("README.md", "src/one.py"))},
            # An ordinary commit after the review.
            {"abc": (("def",), ("tests/test_one.py",))},
            # A plain merge, but on a commit Codex hasn't reviewed either.
            {"abc": (("ghi", "main1"), ("README.md",)), "ghi": (("def",), ())},
        ):
            self.refused(FakeGh(review="def", history=history))
        # A merge that puts back as main has it a file the branch had changed,
        # so the pull request's files no longer list it.
        history = {"abc": (("def", "main1"), ("src/two.py",))}
        before = {"def": ("src/one.py", "src/two.py")}
        self.refused(FakeGh(review="def", history=history, before=before))

    def refused(self, gh):
        with self.assertRaises(MergeRefused):
            merge(101, gh, pause=lambda seconds: None)
        self.assertFalse([c for c in gh.calls if c[:2] == ("pr", "merge")])


if __name__ == "__main__":
    unittest.main()
