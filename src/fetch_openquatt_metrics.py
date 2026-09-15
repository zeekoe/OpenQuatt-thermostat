#!/usr/bin/env python3
"""Library for fetching selected OpenQuatt entity values.

Works on CPython and on MicroPython devices that provide `urequests`.
"""

try:
    import ujson as json
except ImportError:
    import json

try:
    import urequests as requests_compat
except ImportError:
    requests_compat = None

try:
    import urllib.error
    import urllib.request
except ImportError:
    urllib = None

DEFAULT_DETAIL = "all"

class FetchError(Exception):
    pass


def _quote_plus(value):
    if not isinstance(value, str):
        value = str(value)
    data = value.encode("utf-8")
    pieces = []
    for byte in data:
        if (
            48 <= byte <= 57
            or 65 <= byte <= 90
            or 97 <= byte <= 122
            or byte in b"-_.~"
        ):
            pieces.append(chr(byte))
        elif byte == 32:
            pieces.append("+")
        else:
            pieces.append("%%%02X" % byte)
    return "".join(pieces)


def _urlencode_form(fields):
    parts = []
    for key, value in fields:
        parts.append("%s=%s" % (_quote_plus(key), _quote_plus(value)))
    return "&".join(parts)


def build_request_body(display_fields, detail=DEFAULT_DETAIL):
    entities_value = "\n".join(
        "%s\t%s\t%s" % (key, domain, name) for key, domain, name in display_fields
    )
    payload = _urlencode_form((("detail", detail), ("entities", entities_value)))
    return payload.encode("utf-8")


def _response_json(response):
    if hasattr(response, "json"):
        try:
            return response.json()
        except Exception:
            pass

    content = getattr(response, "content", None)
    if content is None and hasattr(response, "read"):
        content = response.read()
    if isinstance(content, bytes):
        content = content.decode("utf-8")
    return json.loads(content)


def _fetch_entities_with_urequests(url, detail, display_fields):
    body = build_request_body(display_fields, detail)
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = None
    try:
        response = requests_compat.post(url, data=body, headers=headers)
        status_code = getattr(response, "status_code", 200)
        if status_code >= 400:
            raise FetchError("HTTP error: %s" % status_code)
        return _response_json(response)
    except FetchError:
        raise
    except Exception as exc:
        raise FetchError("Connection error: %s" % exc)
    finally:
        if response is not None and hasattr(response, "close"):
            response.close()


def _fetch_entities_with_urllib(url, detail, display_fields):
    request = urllib.request.Request(
        url,
        data=build_request_body(display_fields, detail),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise FetchError("HTTP error: %s %s" % (exc.code, exc.reason))
    except urllib.error.URLError as exc:
        raise FetchError("Connection error: %s" % exc.reason)
    except ValueError as exc:
        raise FetchError("Invalid JSON response: %s" % exc)


def fetch_entities(url, detail, display_fields):
    if requests_compat is not None:
        return _fetch_entities_with_urequests(url, detail, display_fields)
    if urllib is not None:
        return _fetch_entities_with_urllib(url, detail, display_fields)
    raise FetchError("No supported HTTP client found; install urequests")


def format_entity_value(entity):
    if not entity:
        return "missing"
    if entity.get("state") is not None:
        return str(entity["state"])
    if entity.get("value") is not None:
        value = entity["value"]
        unit = entity.get("uom")
        if unit:
            return "%s %s" % (value, unit)
        return str(value)
    return "NA"


def extract_selected_values(payload, display_fields):
    entities = payload.get("entities", {})
    return [
        {
            "key": key,
            "domain": domain,
            "label": name,
            "value": format_entity_value(entities.get(key)),
        }
        for key, domain, name in display_fields
    ]


def fetch_openquatt_metrics(
    url, display_fields, detail=DEFAULT_DETAIL
):
    payload = fetch_entities(url, detail, display_fields)
    return {
        "ok": payload.get("ok", False),
        "results": extract_selected_values(payload, display_fields),
        "missing": payload.get("missing", []),
        "errors": payload.get("errors", []),
        "payload": payload,
    }
