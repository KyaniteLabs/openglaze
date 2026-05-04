"""Dual-provider LLM fallback: cloud primary with local fallback.

When a cloud provider (Anthropic, OpenAI, etc.) is configured, the system
attempts the cloud call first with a configurable timeout. If the cloud call
fails (timeout, connection error, HTTP error), the system falls back to a
local provider (LM Studio / Ollama). A health check confirms the local
provider is reachable before attempting the fallback call.

Telemetry events are emitted on fallback activation for monitoring.
"""

import json
import logging
import os
import time
from dataclasses import dataclass, field
from typing import Any, Optional

import requests
from requests.exceptions import ConnectionError, Timeout

logger = logging.getLogger(__name__)


@dataclass
class FallbackTelemetryEvent:
    """Telemetry event emitted when fallback is activated."""

    timestamp: float = field(default_factory=time.time)
    cloud_provider: str = ""
    cloud_error: str = ""
    fallback_provider: str = ""
    fallback_success: bool = False
    cloud_latency_ms: float = 0.0
    fallback_latency_ms: float = 0.0


@dataclass
class CloudConfig:
    """Cloud provider configuration from environment variables."""

    provider: str = ""
    base_url: str = ""
    api_key: str = ""
    model: str = ""
    timeout: float = 30.0


@dataclass
class LocalFallbackConfig:
    """Local fallback provider configuration from environment variables."""

    base_url: str = ""
    model: str = ""


def _cloud_config_from_env() -> CloudConfig:
    """Resolve cloud provider configuration from OPENGLAZE_CLOUD_* env vars."""
    return CloudConfig(
        provider=os.environ.get("OPENGLAZE_CLOUD_PROVIDER", "anthropic").strip().lower(),
        base_url=os.environ.get("OPENGLAZE_CLOUD_BASE_URL", "").strip(),
        api_key=os.environ.get("OPENGLAZE_CLOUD_API_KEY", "").strip(),
        model=os.environ.get("OPENGLAZE_CLOUD_MODEL", "").strip(),
        timeout=float(os.environ.get("OPENGLAZE_CLOUD_TIMEOUT_SECONDS", "30")),
    )


def _local_config_from_env() -> LocalFallbackConfig:
    """Resolve local fallback configuration from OPENGLAZE_LOCAL_FALLBACK_* env vars."""
    return LocalFallbackConfig(
        base_url=os.environ.get(
            "OPENGLAZE_LOCAL_FALLBACK_BASE_URL",
            os.environ.get("LM_STUDIO_URL", "http://127.0.0.1:1234/v1"),
        ).strip(),
        model=os.environ.get(
            "OPENGLAZE_LOCAL_FALLBACK_MODEL",
            os.environ.get("LM_STUDIO_MODEL", ""),
        ).strip(),
    )


def _cloud_base_url(config: CloudConfig) -> str:
    """Resolve the full endpoint URL for the cloud provider."""
    if config.base_url:
        return config.base_url.rstrip("/")

    if config.provider == "anthropic":
        return "https://api.anthropic.com/v1/messages"
    if config.provider in ("openai", "openai-compatible"):
        return "https://api.openai.com/v1/chat/completions"
    return config.base_url


def _build_cloud_payload(
    config: CloudConfig, messages: list[dict[str, Any]], stream: bool = False
) -> dict[str, Any]:
    """Build the request payload for the cloud provider."""
    if config.provider == "anthropic":
        system = messages[0]["content"] if messages else ""
        anthropic_messages = messages[1:] if len(messages) > 1 else []
        return {
            "model": config.model or "claude-sonnet-4-20250514",
            "max_tokens": 4096,
            "system": system,
            "messages": anthropic_messages,
            "stream": stream,
        }
    # OpenAI-compatible
    return {
        "model": config.model or "gpt-4o-mini",
        "messages": messages,
        "max_tokens": 4096,
        "stream": stream,
    }


def _build_cloud_headers(config: CloudConfig) -> dict[str, str]:
    """Build request headers for the cloud provider."""
    if config.provider == "anthropic":
        headers = {
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        if config.api_key:
            headers["x-api-key"] = config.api_key
        return headers

    headers = {"Content-Type": "application/json"}
    if config.api_key:
        headers["Authorization"] = f"Bearer {config.api_key}"
    return headers


def _parse_cloud_response(config: CloudConfig, response: requests.Response) -> dict[str, Any]:
    """Parse the cloud provider response into a normalized format."""
    data = response.json()
    if config.provider == "anthropic":
        content_blocks = data.get("content", [])
        text = ""
        for block in content_blocks:
            if block.get("type") == "text":
                text += block.get("text", "")
        return {"message": {"content": text}, "raw": data}

    # OpenAI-compatible
    choices = data.get("choices", [])
    if choices:
        message = choices[0].get("message", {})
        return {"message": {"content": message.get("content", "")}, "raw": data}
    return {"message": {"content": ""}, "raw": data}


def check_local_health(base_url: str, timeout: float = 5.0) -> bool:
    """Health check: confirm the local fallback provider is reachable.

    Returns True if the endpoint responds to a lightweight request.
    """
    url = base_url.rstrip("/")
    # Try the /v1/models endpoint for OpenAI-compatible servers
    try:
        response = requests.get(f"{url}/models", timeout=timeout)
        return response.status_code == 200
    except (Timeout, ConnectionError, OSError):
        pass

    # Fallback: try a minimal completions ping
    try:
        response = requests.get(f"{url}/", timeout=timeout)
        return response.status_code in (200, 404)
    except (Timeout, ConnectionError, OSError):
        return False


def _call_cloud(
    config: CloudConfig, messages: list[dict[str, Any]]
) -> tuple[dict[str, Any], FallbackTelemetryEvent]:
    """Attempt the cloud provider call. Returns (response, telemetry)."""
    telemetry = FallbackTelemetryEvent(cloud_provider=config.provider)
    url = _cloud_base_url(config)
    headers = _build_cloud_headers(config)
    payload = _build_cloud_payload(config, messages, stream=False)

    start = time.monotonic()
    try:
        response = requests.post(
            url, json=payload, headers=headers, timeout=config.timeout
        )
        telemetry.cloud_latency_ms = (time.monotonic() - start) * 1000

        if response.status_code != 200:
            telemetry.cloud_error = f"HTTP {response.status_code}: {response.text[:200]}"
            raise RuntimeError(telemetry.cloud_error)

        return _parse_cloud_response(config, response), telemetry
    except (Timeout, ConnectionError) as exc:
        telemetry.cloud_latency_ms = (time.monotonic() - start) * 1000
        telemetry.cloud_error = f"{type(exc).__name__}: {exc}"
        raise
    except RuntimeError:
        raise
    except Exception as exc:
        telemetry.cloud_latency_ms = (time.monotonic() - start) * 1000
        telemetry.cloud_error = f"{type(exc).__name__}: {exc}"
        raise


def _call_local(
    local_config: LocalFallbackConfig,
    messages: list[dict[str, Any]],
    timeout: float = 90.0,
) -> tuple[dict[str, Any], float]:
    """Attempt the local fallback call. Returns (response, latency_ms)."""
    url = local_config.base_url.rstrip("/")
    endpoint = f"{url}/chat/completions"
    headers = {"Content-Type": "application/json"}

    payload = {
        "model": local_config.model,
        "messages": messages,
        "max_tokens": 4096,
        "stream": False,
    }

    start = time.monotonic()
    response = requests.post(endpoint, json=payload, headers=headers, timeout=timeout)
    latency_ms = (time.monotonic() - start) * 1000

    if response.status_code != 200:
        raise RuntimeError(
            f"Local fallback HTTP {response.status_code}: {response.text[:200]}"
        )

    data = response.json()
    choices = data.get("choices", [])
    if choices:
        message = choices[0].get("message", {})
        return {"message": {"content": message.get("content", "")}, "raw": data}, latency_ms
    return {"message": {"content": ""}, "raw": data}, latency_ms


def try_cloud_then_local(
    messages: list[dict[str, Any]],
    cloud_config: Optional[CloudConfig] = None,
    local_config: Optional[LocalFallbackConfig] = None,
    on_fallback: Optional[Any] = None,
) -> dict[str, Any]:
    """Try cloud provider first, fall back to local on failure.

    Args:
        messages: Chat messages in standard format.
        cloud_config: Cloud provider config (resolved from env if None).
        local_config: Local fallback config (resolved from env if None).
        on_fallback: Optional callback(telemetry_event) for custom telemetry.

    Returns:
        Normalized response dict with 'message.content' key.

    Raises:
        RuntimeError: If both cloud and local fail, or cloud is not configured.
    """
    cloud = cloud_config or _cloud_config_from_env()
    local = local_config or _local_config_from_env()

    # If no cloud base URL or API key is set, skip cloud entirely
    cloud_url = _cloud_base_url(cloud)
    if not cloud_url or (cloud.provider == "anthropic" and not cloud.api_key):
        logger.info("Cloud provider not configured, using local provider directly")
        if not local.base_url:
            raise RuntimeError("No cloud or local provider configured")
        result, _ = _call_local(local, messages)
        return result

    # Attempt cloud call
    try:
        result, telemetry = _call_cloud(cloud, messages)
        return result
    except (Timeout, ConnectionError, RuntimeError, OSError) as cloud_exc:
        logger.warning(
            "Cloud provider %s failed: %s. Checking local fallback.",
            cloud.provider,
            cloud_exc,
        )

        # Health check local fallback
        if not check_local_health(local.base_url):
            raise RuntimeError(
                f"Cloud provider failed ({cloud_exc}) and local fallback "
                f"at {local.base_url} is not reachable"
            ) from cloud_exc

        if not local.model:
            raise RuntimeError(
                f"Cloud provider failed ({cloud_exc}) and OPENGLAZE_LOCAL_FALLBACK_MODEL "
                f"is not configured"
            ) from cloud_exc

        # Attempt local fallback
        telemetry = FallbackTelemetryEvent(
            cloud_provider=cloud.provider,
            cloud_error=str(cloud_exc),
            fallback_provider="local",
        )
        try:
            result, latency_ms = _call_local(local, messages)
            telemetry.fallback_success = True
            telemetry.fallback_latency_ms = latency_ms
            logger.info(
                "Fallback to local provider succeeded (%.0fms)", latency_ms
            )

            # Emit telemetry
            if on_fallback:
                on_fallback(telemetry)
            _emit_fallback_telemetry(telemetry)

            return result
        except (Timeout, ConnectionError, RuntimeError, OSError) as local_exc:
            telemetry.fallback_success = False
            _emit_fallback_telemetry(telemetry)
            raise RuntimeError(
                f"Cloud failed ({cloud_exc}) and local fallback also failed ({local_exc})"
            ) from local_exc


def _emit_fallback_telemetry(event: FallbackTelemetryEvent) -> None:
    """Log fallback telemetry as a structured JSON event."""
    logger.info(
        "LLM fallback telemetry: %s",
        json.dumps({
            "event": "llm_fallback",
            "cloud_provider": event.cloud_provider,
            "cloud_error": event.cloud_error,
            "fallback_provider": event.fallback_provider,
            "fallback_success": event.fallback_success,
            "cloud_latency_ms": round(event.cloud_latency_ms, 1),
            "fallback_latency_ms": round(event.fallback_latency_ms, 1),
            "timestamp": event.timestamp,
        }),
    )
