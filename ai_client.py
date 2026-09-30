import time
import json
import hashlib
from threading import Lock
from collections import OrderedDict
from functools import lru_cache

from google import genai
from google.genai import types

from config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    MAX_OUTPUT_TOKENS,
    TEMPERATURE,
)


# ============================================================
# SETTINGS
# ============================================================

# Your screenshot shows Gemini 3.5 Flash = 5 RPM.
# We wait at least 13 seconds between actual Gemini requests.
MIN_REQUEST_INTERVAL = 13

# Keep generated answers in memory.
# Repeating the same request will NOT call Gemini again.
CACHE_SIZE = 100

# Cached responses expire after 1 hour.
CACHE_TTL = 60 * 60


# ============================================================
# INTERNAL STATE
# ============================================================

_response_cache = OrderedDict()
_cache_lock = Lock()

_last_request_time = 0.0
_request_lock = Lock()


# ============================================================
# GEMINI CLIENT
# ============================================================

@lru_cache(maxsize=1)
def get_client() -> genai.Client:
    """
    Create and cache the Gemini client.
    """

    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured. "
            "Create a .env file and add your Gemini API key."
        )

    return genai.Client(
        api_key=GEMINI_API_KEY
    )


# ============================================================
# CACHE HELPERS
# ============================================================

def _make_cache_key(
    prompt: str,
    system_instruction: str | None,
    mode: str,
    schema: dict | None = None,
) -> str:
    """
    Create a unique cache key for a Gemini request.
    """

    data = {
        "prompt": prompt,
        "system_instruction": system_instruction,
        "mode": mode,
        "schema": schema,
        "model": GEMINI_MODEL,
    }

    raw = json.dumps(
        data,
        sort_keys=True,
        ensure_ascii=False,
        default=str,
    )

    return hashlib.sha256(
        raw.encode("utf-8")
    ).hexdigest()


def _get_cached_response(cache_key: str):
    """
    Return a cached response if it exists and has not expired.
    """

    with _cache_lock:

        item = _response_cache.get(cache_key)

        if item is None:
            return None

        timestamp, response_text = item

        # Expired
        if time.time() - timestamp > CACHE_TTL:
            del _response_cache[cache_key]
            return None

        # Move recently used item to the end
        _response_cache.move_to_end(cache_key)

        return response_text


def _save_cached_response(
    cache_key: str,
    response_text: str,
):
    """
    Save a Gemini response in the local cache.
    """

    with _cache_lock:

        _response_cache[cache_key] = (
            time.time(),
            response_text,
        )

        _response_cache.move_to_end(cache_key)

        # Remove oldest items if cache is full
        while len(_response_cache) > CACHE_SIZE:
            _response_cache.popitem(last=False)


# ============================================================
# RATE LIMIT PROTECTION
# ============================================================

def _wait_for_rate_limit():
    """
    Make sure we do not send Gemini requests too quickly.

    Gemini 3.5 Flash currently shows 5 RPM in the user's
    Google AI Studio project.
    """

    global _last_request_time

    with _request_lock:

        now = time.time()

        elapsed = now - _last_request_time

        if elapsed < MIN_REQUEST_INTERVAL:

            wait_time = (
                MIN_REQUEST_INTERVAL - elapsed
            )

            print(
                f"Gemini rate-limit protection: "
                f"waiting {wait_time:.1f} seconds..."
            )

            time.sleep(wait_time)

        _last_request_time = time.time()


# ============================================================
# GEMINI REQUEST
# ============================================================

def _generate_with_retry(
    client,
    prompt: str,
    config,
    retries: int = 2,
):
    """
    Call Gemini and retry temporary 503 errors.

    We intentionally use only 2 attempts so that temporary
    errors do not create unnecessary API traffic.
    """

    last_error = None

    for attempt in range(retries):

        try:

            # Protect the free-tier RPM limit.
            _wait_for_rate_limit()

            return client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=config,
            )

        except Exception as exc:

            last_error = exc
            error_text = str(exc)

            is_temporary = (
                "503" in error_text
                or "UNAVAILABLE" in error_text
            )

            # Do NOT retry every kind of error.
            # Quota/authentication/request errors should
            # immediately be shown to the application.
            if not is_temporary:
                raise

            if attempt < retries - 1:

                wait_time = 8

                print(
                    "Gemini is temporarily unavailable. "
                    f"Retrying in {wait_time} seconds..."
                )

                time.sleep(wait_time)

    raise RuntimeError(
        "Gemini is currently experiencing high demand. "
        "Please try again in a few minutes."
    ) from last_error


# ============================================================
# NORMAL TEXT GENERATION
# ============================================================

def generate_text(
    prompt: str,
    system_instruction: str | None = None,
) -> str:
    """
    Generate normal text using Gemini.

    Repeated identical requests are served from the
    local cache instead of calling Gemini again.
    """

    cache_key = _make_cache_key(
        prompt=prompt,
        system_instruction=system_instruction,
        mode="text",
    )

    # --------------------------------------------------------
    # CHECK CACHE
    # --------------------------------------------------------

    cached = _get_cached_response(cache_key)

    if cached is not None:

        print(
            "Gemini cache hit - "
            "no API request made."
        )

        return cached

    # --------------------------------------------------------
    # CALL GEMINI
    # --------------------------------------------------------

    print(
        "Gemini cache miss - "
        "sending API request."
    )

    client = get_client()

    config = types.GenerateContentConfig(
        temperature=TEMPERATURE,
        max_output_tokens=MAX_OUTPUT_TOKENS,
        system_instruction=system_instruction,
    )

    response = _generate_with_retry(
        client,
        prompt,
        config,
    )

    text = (response.text or "").strip()

    if not text:
        raise RuntimeError(
            "Gemini returned an empty response."
        )

    # --------------------------------------------------------
    # SAVE RESULT
    # --------------------------------------------------------

    _save_cached_response(
        cache_key,
        text,
    )

    return text


# ============================================================
# JSON GENERATION
# ============================================================

def generate_json(
    prompt: str,
    schema: dict,
    system_instruction: str | None = None,
) -> str:
    """
    Generate structured JSON using Gemini.

    Repeated identical JSON requests are served from
    the local cache.
    """

    cache_key = _make_cache_key(
        prompt=prompt,
        system_instruction=system_instruction,
        mode="json",
        schema=schema,
    )

    # --------------------------------------------------------
    # CHECK CACHE
    # --------------------------------------------------------

    cached = _get_cached_response(cache_key)

    if cached is not None:

        print(
            "Gemini JSON cache hit - "
            "no API request made."
        )

        return cached

    # --------------------------------------------------------
    # CALL GEMINI
    # --------------------------------------------------------

    print(
        "Gemini JSON cache miss - "
        "sending API request."
    )

    client = get_client()

    config = types.GenerateContentConfig(
        temperature=0.2,
        max_output_tokens=MAX_OUTPUT_TOKENS,
        response_mime_type="application/json",
        response_schema=schema,
        system_instruction=system_instruction,
    )

    response = _generate_with_retry(
        client,
        prompt,
        config,
    )

    text = (response.text or "").strip()

    if not text:
        raise RuntimeError(
            "Gemini returned an empty JSON response."
        )

    # --------------------------------------------------------
    # SAVE RESULT
    # --------------------------------------------------------

    _save_cached_response(
        cache_key,
        text,
    )

    return text