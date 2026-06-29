import csv
import io
import os
import unittest
from datetime import datetime, timezone

os.environ["NEXTLEVEL_SKIP_USER_SEED"] = "1"
os.environ["NEXTLEVEL_ADMIN_PIN"] = "1234"
os.environ["FLASK_SECRET_KEY"] = "test-secret"

import main


class FakeQueryResult:
    def __init__(self, docs):
        self.docs = [dict(doc) for doc in docs]

    def sort(self, sort_spec, direction=None):
        if isinstance(sort_spec, list):
            sorted_docs = self.docs
            for key, order in reversed(sort_spec):
                sorted_docs = sorted(
                    sorted_docs,
                    key=lambda doc: doc.get(key, ""),
                    reverse=order < 0
                )
            self.docs = sorted_docs
            return self

        self.docs = sorted(
            self.docs,
            key=lambda doc: doc.get(sort_spec, ""),
            reverse=direction < 0
        )
        return self

    def limit(self, count):
        self.docs = self.docs[:count]
        return self

    def __iter__(self):
        return iter(self.docs)


class FakeCollection:
    def __init__(self, docs=None):
        self.docs = [dict(doc) for doc in docs or []]

    def find(self, query=None, projection=None):
        return FakeQueryResult([
            self._apply_projection(doc, projection)
            for doc in self.docs
            if self._matches(doc, query or {})
        ])

    def find_one(self, query=None, projection=None, sort=None):
        docs = list(self.find(query, projection))
        if sort:
            docs = list(FakeQueryResult(docs).sort(sort))
        return docs[0] if docs else None

    def insert_one(self, doc):
        self.docs.append(dict(doc))
        return None

    def update_one(self, query, update, upsert=False):
        doc = self.find_one(query)
        if doc is None:
            if not upsert:
                return None
            doc = dict(query)
            self.docs.append(doc)
        else:
            doc = self._actual_doc(doc)

        for key, value in update.get("$set", {}).items():
            doc[key] = value
        for key, value in update.get("$inc", {}).items():
            doc[key] = doc.get(key, 0) + value
        for key, value in update.get("$addToSet", {}).items():
            doc.setdefault(key, [])
            for item in value.get("$each", []):
                if item not in doc[key]:
                    doc[key].append(item)
        return None

    def _actual_doc(self, doc):
        username = doc.get("username")
        for stored in self.docs:
            if stored.get("username") == username:
                return stored
        return doc

    def _matches(self, doc, query):
        for key, expected in query.items():
            value = doc.get(key)
            if isinstance(value, list):
                if expected not in value:
                    return False
            elif value != expected:
                return False
        return True

    def _apply_projection(self, doc, projection):
        if not projection:
            return dict(doc)
        projected = {}
        for key, enabled in projection.items():
            if enabled and key in doc:
                projected[key] = doc[key]
        return projected


class AdminWorkflowTests(unittest.TestCase):
    def setUp(self):
        main.app.config["TESTING"] = True
        main.app.secret_key = "test-secret"
        self.userpass = FakeCollection([
            {"username": "Team Alpha"},
            {"username": "Team Beta"},
            {"username": "Team Gamma"},
        ])
        self.teampts = FakeCollection([
            {
                "username": "Team Alpha",
                "points": 20,
                "questions": ["Q1", "Q2"],
                "updated_at": datetime(2026, 6, 29, 12, 0, tzinfo=timezone.utc),
            },
            {
                "username": "Team Beta",
                "points": 20,
                "questions": ["Q1"],
                "updated_at": datetime(2026, 6, 29, 12, 5, tzinfo=timezone.utc),
            },
        ])
        self.score_audit = FakeCollection()
        main.userpass = self.userpass
        main.teampts = self.teampts
        main.score_audit = self.score_audit

    def test_leaderboard_ranks_ties_and_registered_teams(self):
        rows = main.get_leaderboard_rows(include_registered=True)

        self.assertEqual(
            [(row["rank"], row["username"], row["points"]) for row in rows],
            [
                (1, "Team Alpha", 20),
                (1, "Team Beta", 20),
                (3, "Team Gamma", 0),
            ],
        )

    def test_admin_adjust_score_creates_team_and_audit_entry(self):
        client = main.app.test_client()
        with client.session_transaction() as session:
            session["admin_authenticated"] = True

        response = client.post("/admin/scores/adjust", data={
            "username": "Team Gamma",
            "delta": "15",
            "reason": "mentor bonus verified",
            "actor": "Susan",
        })

        self.assertEqual(response.status_code, 302)
        team = self.teampts.find_one({"username": "Team Gamma"})
        self.assertEqual(team["points"], 15)
        audit = self.score_audit.find_one({"username": "Team Gamma"})
        self.assertEqual(audit["reason"], "mentor bonus verified")
        self.assertEqual(audit["previous_points"], 0)
        self.assertEqual(audit["new_points"], 15)
        self.assertEqual(audit["actor"], "Susan")

    def test_admin_adjust_score_requires_reason(self):
        client = main.app.test_client()
        with client.session_transaction() as session:
            session["admin_authenticated"] = True

        response = client.post("/admin/scores/adjust", data={
            "username": "Team Alpha",
            "delta": "5",
            "reason": "",
        })

        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Reason is required", response.data)

    def test_admin_export_scores_csv_includes_registered_teams(self):
        client = main.app.test_client()
        with client.session_transaction() as session:
            session["admin_authenticated"] = True

        response = client.get("/admin/export/scores.csv")

        self.assertEqual(response.status_code, 200)
        rows = list(csv.reader(io.StringIO(response.data.decode("utf-8"))))
        self.assertEqual(rows[0], ["rank", "team", "points", "questions_completed", "last_updated"])
        self.assertIn(["3", "Team Gamma", "0", "0", ""], rows)


if __name__ == "__main__":
    unittest.main()
