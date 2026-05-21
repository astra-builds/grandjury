"""Unit tests for GrandJury SDK."""

import os
import pytest
from unittest.mock import patch, MagicMock


def test_import():
    """SDK imports without errors and exposes a sane version string."""
    from grandjury import GrandJury, Span, __version__
    # Don't hard-code version; just verify the format (e.g. "2.3.2")
    assert isinstance(__version__, str)
    assert __version__.count(".") >= 2  # major.minor.patch at minimum
    assert __version__.split(".")[0].isdigit()


def test_zero_config_no_key():
    """No API key → constructor accepts empty key without raising (silent init).

    The SDK raises only when an authenticated method is called without a key
    (see test_results_empty_without_key). Construction itself is silent.
    """
    with patch.dict(os.environ, {}, clear=True):
        os.environ.pop("GRANDJURY_API_KEY", None)
        from grandjury.sdk import GrandJury
        gj = GrandJury(api_key="")
        assert gj._api_key == ""


def test_zero_config_from_env():
    """Reads GRANDJURY_API_KEY from env."""
    with patch.dict(os.environ, {"GRANDJURY_API_KEY": "gj_sk_live_test123"}):
        from grandjury.sdk import GrandJury
        gj = GrandJury()
        assert gj._api_key == "gj_sk_live_test123"


def test_legacy_project_id_accepted():
    """Legacy project_id param accepted without error."""
    from grandjury.sdk import GrandJury
    gj = GrandJury(api_key="test", project_id="old-format-uuid")
    assert gj._api_key == "test"


def test_trace_noop_without_key():
    """trace() returns None when no API key."""
    from grandjury.sdk import GrandJury
    gj = GrandJury(api_key="")
    result = gj.trace(input="hello", output="world")
    assert result is None


def test_trace_returns_inference_id():
    """trace() returns inference ID on success."""
    from grandjury.sdk import GrandJury
    gj = GrandJury(api_key="gj_sk_live_test")

    mock_resp = MagicMock()
    mock_resp.status_code = 200

    with patch("requests.post", return_value=mock_resp):
        result = gj.trace(input="hello", output="world")
        assert result is not None
        assert result.startswith("gj_inf_")


def test_trace_silent_failure():
    """trace() silently returns None on network error."""
    from grandjury.sdk import GrandJury
    gj = GrandJury(api_key="gj_sk_live_test")

    with patch("requests.post", side_effect=Exception("network error")):
        result = gj.trace(input="hello", output="world")
        assert result is None


def test_results_empty_without_key():
    """results() raises an informative error when no API key is set.

    The SDK is silent on construction but raises on authenticated method
    calls, with a message pointing users to sign-up + token-generation URLs.
    """
    from grandjury.sdk import GrandJury
    gj = GrandJury(api_key="")
    with pytest.raises(RuntimeError, match="Authentication required"):
        gj.results()


def test_namespaces_exist():
    """models, benchmarks, analytics namespaces exist."""
    from grandjury.sdk import GrandJury
    gj = GrandJury(api_key="test")
    assert hasattr(gj, "models")
    assert hasattr(gj, "benchmarks")
    assert hasattr(gj, "analytics")
    assert callable(gj.models.list)
    assert callable(gj.benchmarks.list)
    assert callable(gj.analytics.vote_histogram)


def test_observe_decorator():
    """@gj.observe wraps function correctly."""
    from grandjury.sdk import GrandJury
    gj = GrandJury(api_key="gj_sk_live_test")

    mock_resp = MagicMock()
    mock_resp.status_code = 200

    @gj.observe(name="test_fn", model="test-model")
    def my_func(prompt):
        return f"response to {prompt}"

    with patch("requests.post", return_value=mock_resp):
        result = my_func("hello")
        assert result == "response to hello"


def test_span_context_manager():
    """gj.span() context manager submits trace on exit."""
    from grandjury.sdk import GrandJury
    gj = GrandJury(api_key="gj_sk_live_test")

    mock_resp = MagicMock()
    mock_resp.status_code = 200

    with patch("requests.post", return_value=mock_resp) as mock_post:
        with gj.span("test_op", input="hello") as s:
            s.set_output("world")
        assert mock_post.called


def test_generate_inference_id_format():
    """Inference IDs have correct format."""
    from grandjury.sdk import _generate_inference_id
    iid = _generate_inference_id()
    assert iid.startswith("gj_inf_")
    parts = iid.split("_")
    assert len(parts) == 4  # gj, inf, timestamp, random
