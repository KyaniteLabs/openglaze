"""Tests for dual-provider LLM fallback (cloud primary + local fallback)."""

from __future__ import annotations

import os
import time
from unittest.mock import MagicMock, patch

import pytest

from core.ai.llm_fallback import (
    CloudConfig,
    FallbackTelemetryEvent,
    LocalFallbackConfig,
    check_local_health,
    try_cloud_then_local,
    _call_cloud,
    _call_local,
    _cloud_config_from_env,
    _local_config_from_env,
)


class TestCloudConfigFromEnv:
    def test_defaults(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            config = _cloud_config_from_env()
        assert config.provider == "anthropic"
        assert config.timeout == 30.0

    def test_custom_values(self) -> None:
        env = {
            "OPENGLAZE_CLOUD_PROVIDER": "openai",
            "OPENGLAZE_CLOUD_BASE_URL": "https://api.openai.com/v1",
            "OPENGLAZE_CLOUD_API_KEY": "sk-test-key",
            "OPENGLAZE_CLOUD_MODEL": "gpt-4o",
            "OPENGLAZE_CLOUD_TIMEOUT_SECONDS": "60",
        }
        with patch.dict(os.environ, env, clear=True):
            config = _cloud_config_from_env()
        assert config.provider == "openai"
        assert config.base_url == "https://api.openai.com/v1"
        assert config.api_key == "sk-test-key"
        assert config.model == "gpt-4o"
        assert config.timeout == 60.0


class TestLocalConfigFromEnv:
    def test_defaults_fall_through_to_lm_studio(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            config = _local_config_from_env()
        assert "127.0.0.1" in config.base_url or "localhost" in config.base_url

    def test_custom_values(self) -> None:
        env = {
            "OPENGLAZE_LOCAL_FALLBACK_BASE_URL": "http://ollama:11434/v1",
            "OPENGLAZE_LOCAL_FALLBACK_MODEL": "llama3",
        }
        with patch.dict(os.environ, env, clear=True):
            config = _local_config_from_env()
        assert config.base_url == "http://ollama:11434/v1"
        assert config.model == "llama3"


class TestCheckLocalHealth:
    def test_healthy_endpoint(self) -> None:
        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch("core.ai.llm_fallback.requests.get", return_value=mock_response):
            assert check_local_health("http://localhost:1234/v1") is True

    def test_unreachable_endpoint(self) -> None:
        import requests as req

        with patch("core.ai.llm_fallback.requests.get", side_effect=req.ConnectionError):
            assert check_local_health("http://localhost:9999") is False

    def test_timeout(self) -> None:
        import requests as req

        with patch("core.ai.llm_fallback.requests.get", side_effect=req.Timeout):
            assert check_local_health("http://localhost:9999") is False


class TestTryCloudThenLocal:
    def _make_cloud_config(self, provider="anthropic") -> CloudConfig:
        return CloudConfig(
            provider=provider,
            base_url="https://api.anthropic.com/v1/messages",
            api_key="sk-test-key",
            model="claude-sonnet-4-20250514",
            timeout=5.0,
        )

    def _make_local_config(self) -> LocalFallbackConfig:
        return LocalFallbackConfig(
            base_url="http://localhost:1234/v1",
            model="llama3",
        )

    def test_cloud_succeeds_no_fallback(self) -> None:
        """When cloud succeeds, return immediately without hitting local."""
        cloud_config = self._make_cloud_config()
        local_config = self._make_local_config()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "content": [{"type": "text", "text": "Glaze advice"}],
        }

        with patch("core.ai.llm_fallback.requests.post", return_value=mock_response):
            result = try_cloud_then_local(
                messages=[{"role": "user", "content": "test"}],
                cloud_config=cloud_config,
                local_config=local_config,
            )

        assert result["message"]["content"] == "Glaze advice"

    def test_cloud_fails_local_succeeds(self) -> None:
        """When cloud fails, fall back to local provider."""
        cloud_config = self._make_cloud_config()
        local_config = self._make_local_config()
        telemetry_events: list[FallbackTelemetryEvent] = []

        def on_fallback(event: FallbackTelemetryEvent) -> None:
            telemetry_events.append(event)

        import requests as req

        cloud_error = req.Timeout("cloud timed out")
        local_response = MagicMock()
        local_response.status_code = 200
        local_response.json.return_value = {
            "choices": [{"message": {"content": "Local response"}}],
        }

        # Mock health check as successful
        health_response = MagicMock()
        health_response.status_code = 200

        def mock_post(url, **kwargs):
            if "anthropic" in url:
                raise cloud_error
            return local_response

        def mock_get(url, **kwargs):
            return health_response

        with patch("core.ai.llm_fallback.requests.post", side_effect=mock_post), \
             patch("core.ai.llm_fallback.requests.get", side_effect=mock_get):
            result = try_cloud_then_local(
                messages=[{"role": "user", "content": "test"}],
                cloud_config=cloud_config,
                local_config=local_config,
                on_fallback=on_fallback,
            )

        assert result["message"]["content"] == "Local response"
        assert len(telemetry_events) == 1
        assert telemetry_events[0].fallback_success is True
        assert telemetry_events[0].cloud_provider == "anthropic"

    def test_cloud_fails_local_unreachable(self) -> None:
        """When both cloud and local fail, raise RuntimeError."""
        cloud_config = self._make_cloud_config()
        local_config = self._make_local_config()

        import requests as req

        with patch("core.ai.llm_fallback.requests.post", side_effect=req.Timeout("cloud timeout")), \
             patch("core.ai.llm_fallback.requests.get", side_effect=req.ConnectionError("local down")):
            with pytest.raises(RuntimeError, match="not reachable"):
                try_cloud_then_local(
                    messages=[{"role": "user", "content": "test"}],
                    cloud_config=cloud_config,
                    local_config=local_config,
                )

    def test_no_cloud_configured_uses_local(self) -> None:
        """When cloud is not configured, use local directly."""
        cloud_config = CloudConfig(provider="anthropic", base_url="", api_key="")
        local_config = self._make_local_config()

        local_response = MagicMock()
        local_response.status_code = 200
        local_response.json.return_value = {
            "choices": [{"message": {"content": "Direct local response"}}],
        }

        with patch("core.ai.llm_fallback.requests.post", return_value=local_response):
            result = try_cloud_then_local(
                messages=[{"role": "user", "content": "test"}],
                cloud_config=cloud_config,
                local_config=local_config,
            )

        assert result["message"]["content"] == "Direct local response"

    def test_no_providers_configured_raises(self) -> None:
        """When no provider is configured, raise RuntimeError."""
        cloud_config = CloudConfig(provider="anthropic", base_url="", api_key="")
        local_config = LocalFallbackConfig(base_url="", model="")

        with pytest.raises(RuntimeError, match="No cloud or local"):
            try_cloud_then_local(
                messages=[{"role": "user", "content": "test"}],
                cloud_config=cloud_config,
                local_config=local_config,
            )

    def test_openai_compatible_cloud(self) -> None:
        """OpenAI-compatible cloud provider works correctly."""
        cloud_config = self._make_cloud_config(provider="openai")
        cloud_config.base_url = "https://api.openai.com/v1/chat/completions"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "OpenAI response"}}],
        }

        with patch("core.ai.llm_fallback.requests.post", return_value=mock_response):
            result = try_cloud_then_local(
                messages=[{"role": "user", "content": "test"}],
                cloud_config=cloud_config,
                local_config=LocalFallbackConfig(base_url="", model=""),
            )

        assert result["message"]["content"] == "OpenAI response"


class TestFallbackTelemetryEvent:
    def test_telemetry_dataclass(self) -> None:
        event = FallbackTelemetryEvent(
            cloud_provider="anthropic",
            cloud_error="Timeout: cloud timed out",
            fallback_provider="local",
            fallback_success=True,
            cloud_latency_ms=5000.0,
            fallback_latency_ms=1200.0,
        )
        assert event.cloud_provider == "anthropic"
        assert event.fallback_success is True
        assert event.cloud_latency_ms == 5000.0

    def test_default_timestamp(self) -> None:
        before = time.time()
        event = FallbackTelemetryEvent()
        after = time.time()
        assert before <= event.timestamp <= after
