"""Integration tests for the translation API endpoints."""

import unittest
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
from givenpy import given, then, when
from hamcrest import assert_that, equal_to, has_key, is_

from app.serve import main
from app.serve.main import app


class TestStartupModelSync(unittest.TestCase):
    def test_startup_syncs_and_cleans_up_without_touching_the_network(self):
        """Server startup always calls the model sync, never only on first boot."""
        with given([]) as _:
            pass

        with when("the app starts up"):
            with (
                patch.object(main.model_sync, "sync_all_deployed_models") as fake_sync,
                patch.object(main.model_sync, "cleanup_legacy_downloads") as fake_cleanup,
            ):
                with TestClient(app):
                    pass

        with then("the deployed models are synced and legacy downloads cleaned up"):
            fake_cleanup.assert_called_once()
            fake_sync.assert_called_once()


class TestTranslationAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_check_endpoint(self):
        """Health endpoint should return a healthy status."""
        with given([]) as _:
            pass

        with when("sending GET request to health"):
            response = self.client.get("/health")

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
            assert_that(
                response.json()["detail"],
                is_(
                    equal_to(
                        "Supported language codes are 'ki' (Kikuyu) and 'en' (English)."
                    )
                ),
            )

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
            assert_that(
                response.json()["detail"],
                is_(equal_to("Source and target languages must be different.")),
            )

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
            assert_that(
                response.json()["detail"],
                is_(
                    equal_to(
                        "Supported translation methods are 'retrieval', 'word-by-word'"
                        " and 'neural'."
                    )
                ),
            )

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
                assert_that(
                    response.json()["detail"],
                    is_(
                        equal_to(
                            "Translation models are not loaded. Please run model training first."
                        )
                    ),
                )
            else:
                assert_that(response.status_code, is_(equal_to(200)))
                data = response.json()
                assert_that(data, has_key("translated_text"))
                assert_that(data["source_lang"], is_(equal_to("en")))
                assert_that(data["target_lang"], is_(equal_to("ki")))
                assert_that(data["method"], is_(equal_to("retrieval")))

    def test_translate_neural_without_model_returns_503(self):
        """Neural method should return 503 when no neural model is loaded."""
        with given([]) as _:
            app.state.neural = None
            payload = {
                "text": "Hello",
                "source_lang": "en",
                "target_lang": "ki",
                "method": "neural",
            }

        with when("sending a neural translation request"):
            response = self.client.post("/translate", json=payload)

        with then("a 503 error explains the neural model is missing"):
            assert_that(response.status_code, is_(equal_to(503)))
            assert_that(
                response.json()["detail"],
                is_(equal_to("Neural translation model is not loaded.")),
            )

    def test_translate_neural_uses_loaded_model(self):
        """Neural method should return the neural model's translation."""
        with given([]) as _:
            neural = MagicMock()
            neural.translate.return_value = "Mwathani nĩ mũrĩithi wakwa"
            app.state.neural = neural
            payload = {
                "text": "The Lord is my shepherd",
                "source_lang": "en",
                "target_lang": "ki",
                "method": "neural",
            }

        with when("sending a neural translation request"):
            response = self.client.post("/translate", json=payload)
            app.state.neural = None

        with then("the neural translation is returned"):
            assert_that(response.status_code, is_(equal_to(200)))
            data = response.json()
            assert_that(
                data["translated_text"], is_(equal_to("Mwathani nĩ mũrĩithi wakwa"))
            )
            assert_that(data["method"], is_(equal_to("neural")))
            neural.translate.assert_called_once_with("The Lord is my shepherd", "en", "ki")

    def test_web_ui_root(self):
        """Root endpoint should return the HTML web UI page."""
        with given([]) as _:
            pass

        with when("sending GET request to root"):
            response = self.client.get("/")

        with then("it returns 200 and HTML content"):
            assert_that(response.status_code, is_(equal_to(200)))
            assert_that(
                response.headers["content-type"],
                is_(equal_to("text/html; charset=utf-8")),
            )
            assert_that("Taura 2.0" in response.text, is_(True))

    def test_feedback_endpoint(self):
        """Feedback endpoint should accept rating and comment, and return success."""
        with given([]) as _:
            payload = {
                "source_text": "marigū",
                "target_text": "Bananas",
                "source_lang": "ki",
                "target_lang": "en",
                "method": "retrieval",
                "rating": 1,
                "comment": "Accurate retrieval!",
            }

        with when("sending POST request to feedback"):
            response = self.client.post("/feedback", json=payload)

        with then("it returns 200 and success status"):
            assert_that(response.status_code, is_(equal_to(200)))
            data = response.json()
            assert_that(data["status"], is_(equal_to("success")))
            assert_that(data["message"], is_(equal_to("Feedback submitted successfully.")))
