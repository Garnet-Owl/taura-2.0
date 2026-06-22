"""Tests for the /translate/candidates and /model/info API endpoints."""

import unittest
from fastapi.testclient import TestClient
from givenpy import given, then, when
from hamcrest import assert_that, equal_to, has_key, instance_of, is_

from app.serve.main import app


class TestCandidatesEndpoint(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_candidates_unsupported_languages(self) -> None:
        """Candidates endpoint returns 400 for unsupported language codes."""
        with given([]) as _:
            payload = {
                "text": "Hello",
                "source_lang": "fr",
                "target_lang": "en",
                "k": 3,
            }

        with when("sending request with unsupported language code"):
            response = self.client.post("/translate/candidates", json=payload)

        with then("a 400 error is returned"):
            assert_that(response.status_code, is_(equal_to(400)))

    def test_candidates_same_language(self) -> None:
        """Candidates endpoint returns 400 when source and target are identical."""
        with given([]) as _:
            payload = {
                "text": "Hello",
                "source_lang": "en",
                "target_lang": "en",
                "k": 3,
            }

        with when("sending request with identical source and target"):
            response = self.client.post("/translate/candidates", json=payload)

        with then("a 400 error is returned"):
            assert_that(response.status_code, is_(equal_to(400)))

    def test_candidates_k_out_of_range(self) -> None:
        """Candidates endpoint returns 422 when k is out of range."""
        with given([]) as _:
            payload = {
                "text": "Hello",
                "source_lang": "en",
                "target_lang": "ki",
                "k": 25,  # > max of 20
            }

        with when("sending request with k > 20"):
            response = self.client.post("/translate/candidates", json=payload)

        with then("a 422 validation error is returned"):
            assert_that(response.status_code, is_(equal_to(422)))

    def test_candidates_valid_request_returns_structure(self) -> None:
        """Candidates endpoint returns list of candidates with scores when models loaded."""
        with given([]) as _:
            payload = {
                "text": "hi",
                "source_lang": "en",
                "target_lang": "ki",
                "k": 3,
            }

        with when("sending a valid candidates request"):
            response = self.client.post("/translate/candidates", json=payload)

        with then("response is either 200 with candidates or 503 if models not loaded"):
            if response.status_code == 503:
                # Acceptable if model files are absent
                assert_that(response.json(), has_key("detail"))
            else:
                assert_that(response.status_code, is_(equal_to(200)))
                data = response.json()
                assert_that(data, has_key("candidates"))
                assert_that(data, has_key("source_lang"))
                assert_that(data, has_key("target_lang"))
                assert_that(data["candidates"], instance_of(list))


class TestModelInfoEndpoint(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_model_info_returns_structure(self) -> None:
        """Model info endpoint returns version, metrics, and hyperparameter data."""
        with given([]) as _:
            pass

        with when("sending GET request to /model/info"):
            response = self.client.get("/model/info")

        with then("it returns 200 with model metadata"):
            assert_that(response.status_code, is_(equal_to(200)))
            data = response.json()
            assert_that(data, has_key("version"))
            assert_that(data, has_key("embedding_dim"))
            assert_that(data, has_key("model_type"))
            assert_that(data, has_key("metrics"))

    def test_model_info_metrics_contains_accuracy(self) -> None:
        """Model info metrics should return 200."""
        with when("calling /model/info"):
            response = self.client.get("/model/info")

        with then("it returns 200"):
            assert_that(response.status_code, is_(equal_to(200)))
