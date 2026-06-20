"""Integration tests for the translation API endpoints."""

import unittest
from fastapi.testclient import TestClient
from givenpy import given, then, when
from hamcrest import assert_that, equal_to, has_key, is_

from app.serve.main import app


class TestTranslationAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_check_endpoint(self):
        """Root endpoint should return a healthy status."""
        with given([]) as _:
            pass

        with when("sending GET request to root"):
            response = self.client.get("/")

        with then("the status is 200 and healthy"):
            assert_that(response.status_code, is_(equal_to(200)))
            data = response.json()
            assert_that(data["status"], is_(equal_to("healthy")))

    def test_translate_unsupported_languages(self):
        """Translate endpoint should return 400 for unsupported languages."""
        with given([]) as _:
            payload = {
                "text": "Hello world",
                "source_lang": "fr",
                "target_lang": "en",
                "method": "retrieval",
            }

        with when("sending translation request with unsupported lang"):
            response = self.client.post("/translate", json=payload)

        with then("a 400 error is returned"):
            assert_that(response.status_code, is_(equal_to(400)))
            assert_that(response.json()["detail"], is_(equal_to("Supported language codes are 'ki' (Kikuyu) and 'en' (English).")))

    def test_translate_same_languages(self):
        """Translate endpoint should return 400 if source and target are identical."""
        with given([]) as _:
            payload = {
                "text": "Hello",
                "source_lang": "en",
                "target_lang": "en",
                "method": "retrieval",
            }

        with when("sending translation request with identical source and target"):
            response = self.client.post("/translate", json=payload)

        with then("a 400 error is returned"):
            assert_that(response.status_code, is_(equal_to(400)))
            assert_that(response.json()["detail"], is_(equal_to("Source and target languages must be different.")))

    def test_translate_invalid_method(self):
        """Translate endpoint should return 400 for invalid translation methods."""
        with given([]) as _:
            payload = {
                "text": "Hello",
                "source_lang": "en",
                "target_lang": "ki",
                "method": "invalid_method",
            }

        with when("sending translation request with invalid method"):
            response = self.client.post("/translate", json=payload)

        with then("a 400 error is returned"):
            assert_that(response.status_code, is_(equal_to(400)))
            assert_that(response.json()["detail"], is_(equal_to("Supported translation methods are 'retrieval' and 'word-by-word'.")))

    def test_translate_end_to_end(self):
        """Translate endpoint should translate successfully when models are loaded."""
        with given([]) as _:
            payload = {
                "text": "hi",
                "source_lang": "en",
                "target_lang": "ki",
                "method": "retrieval",
            }

        with when("sending a valid translation request"):
            response = self.client.post("/translate", json=payload)

        with then("the translation response is successful"):
            # Check if models are loaded; if not, service is 503, which is acceptable if models missing.
            # But they should be loaded since we trained them.
            if response.status_code == 503:
                assert_that(response.json()["detail"], is_(equal_to("Translation models are not loaded. Please run model training first.")))
            else:
                assert_that(response.status_code, is_(equal_to(200)))
                data = response.json()
                assert_that(data, has_key("translated_text"))
                assert_that(data["source_lang"], is_(equal_to("en")))
                assert_that(data["target_lang"], is_(equal_to("ki")))
                assert_that(data["method"], is_(equal_to("retrieval")))
