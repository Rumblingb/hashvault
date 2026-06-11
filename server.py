#!/usr/bin/env python3
"""HashVault MCP Server — 7 hash, encode & crypto tools for AI agents.

Zero API keys. Pure Python stdlib. Freemium: 50 free calls, $9/mo unlimited.

Built for AgentPay Labs — one new product every day.
"""

import sys
import json
import re
import hashlib
import hmac
import uuid
import html
import urllib.parse
import base64
import secrets
import string

# ── Rate limiting ───────────────────────────────────────────────────────────
FREE_LIMIT = 50
PRO_KEYS = {"PROL_AGENTPAY_DEMO": "demo"}
STRIPE_LINK = "https://buy.stripe.com/14kg3reZT1Fv9H2288"

PRO_KEY = None
for i, arg in enumerate(sys.argv):
    if arg == "--pro-key" and i + 1 < len(sys.argv):
        PRO_KEY = sys.argv[i + 1]
IS_PRO = PRO_KEY in PRO_KEYS
call_counter = 0


def check_rate_limit():
    if IS_PRO:
        return None
    global call_counter
    call_counter += 1
    if call_counter > FREE_LIMIT:
        return {
            "error": f"Free tier limit ({FREE_LIMIT} calls). Upgrade to Pro ($9/mo unlimited).",
            "isError": True,
            "next_steps": [
                f"Buy Pro: {STRIPE_LINK}",
                "Restart server to reset counter",
                "Use --pro-key PROL_AGENTPAY_DEMO for testing",
            ],
            "calls_used": call_counter,
            "limit": FREE_LIMIT,
        }
    return None


# ── Tool implementations ────────────────────────────────────────────────────


def hash_generate(params):
    """Generate cryptographic hash of input text."""
    text = params.get("text", "")
    algorithm = params.get("algorithm", "sha256").lower()

    algorithms = {
        "md5": hashlib.md5,
        "sha1": hashlib.sha1,
        "sha256": hashlib.sha256,
        "sha512": hashlib.sha512,
        "sha3_256": hashlib.sha3_256,
        "sha3_512": hashlib.sha3_512,
        "blake2b": hashlib.blake2b,
        "blake2s": hashlib.blake2s,
    }

    if algorithm not in algorithms:
        return {
            "status": "error",
            "isError": True,
            "error": f"Unsupported algorithm: '{algorithm}'",
            "supported_algorithms": list(algorithms.keys()),
        }

    if not text:
        return {
            "status": "error",
            "isError": True,
            "error": "No text provided to hash.",
            "next_steps": ["Provide the 'text' parameter."],
        }

    try:
        if algorithm in ("blake2b", "blake2s"):
            h = algorithms[algorithm]()
            h.update(text.encode("utf-8"))
            result = h.hexdigest()
        else:
            h = algorithms[algorithm](text.encode("utf-8"))
            result = h.hexdigest()
    except Exception as e:
        return {"status": "error", "isError": True, "error": str(e)}

    return {
        "status": "success",
        "algorithm": algorithm,
        "input_length": len(text),
        "hash": result,
        "hash_length": len(result),
    }


def hash_compare(params):
    """Compare a hash against input text to verify integrity."""
    text = params.get("text", "")
    expected_hash = params.get("hash", "")
    algorithm = params.get("algorithm", "sha256").lower()

    if not text or not expected_hash:
        return {
            "status": "error",
            "isError": True,
            "error": "Both 'text' and 'hash' parameters are required.",
        }

    result = hash_generate({"text": text, "algorithm": algorithm})
    if result.get("isError"):
        return result

    computed = result["hash"]
    match = computed.lower() == expected_hash.lower()

    return {
        "status": "success",
        "algorithm": algorithm,
        "match": match,
        "computed_hash": computed,
        "expected_hash": expected_hash,
    }


def encode_base64_tool(params):
    """Base64 encode or decode."""
    text = params.get("text", "")
    action = params.get("action", "encode")  # encode or decode

    if not text:
        return {"status": "error", "isError": True, "error": "No text provided."}

    try:
        if action == "encode":
            result = base64.b64encode(text.encode("utf-8")).decode("utf-8")
        elif action == "decode":
            result = base64.b64decode(text.encode("utf-8")).decode("utf-8")
        else:
            return {
                "status": "error",
                "isError": True,
                "error": f"Invalid action: '{action}'. Use 'encode' or 'decode'.",
            }
    except Exception as e:
        return {"status": "error", "isError": True, "error": str(e)}

    return {"status": "success", "action": action, "result": result, "input_length": len(text), "output_length": len(result)}


def encode_url_tool(params):
    """URL encode or decode."""
    text = params.get("text", "")
    action = params.get("action", "encode")  # encode or decode

    if not text:
        return {"status": "error", "isError": True, "error": "No text provided."}

    try:
        if action == "encode":
            result = urllib.parse.quote(text, safe="")
        elif action == "decode":
            result = urllib.parse.unquote(text)
        else:
            return {
                "status": "error",
                "isError": True,
                "error": f"Invalid action: '{action}'. Use 'encode' or 'decode'.",
            }
    except Exception as e:
        return {"status": "error", "isError": True, "error": str(e)}

    return {"status": "success", "action": action, "result": result, "input_length": len(text), "output_length": len(result)}


def encode_html_tool(params):
    """HTML entity encode or decode."""
    text = params.get("text", "")
    action = params.get("action", "encode")  # encode or decode

    if not text:
        return {"status": "error", "isError": True, "error": "No text provided."}

    try:
        if action == "encode":
            result = html.escape(text, quote=True)
        elif action == "decode":
            result = html.unescape(text)
        else:
            return {
                "status": "error",
                "isError": True,
                "error": f"Invalid action: '{action}'. Use 'encode' or 'decode'.",
            }
    except Exception as e:
        return {"status": "error", "isError": True, "error": str(e)}

    return {"status": "success", "action": action, "result": result, "input_length": len(text), "output_length": len(result)}


def crypto_hmac_tool(params):
    """Generate HMAC-SHA256 signature."""
    text = params.get("text", "")
    key = params.get("key", "")
    algorithm = params.get("algorithm", "sha256").lower()

    algo_map = {
        "sha256": hashlib.sha256,
        "sha512": hashlib.sha512,
        "sha1": hashlib.sha1,
        "md5": hashlib.md5,
    }

    if algorithm not in algo_map:
        return {
            "status": "error",
            "isError": True,
            "error": f"Unsupported HMAC algorithm: '{algorithm}'",
            "supported_algorithms": list(algo_map.keys()),
        }

    if not text or not key:
        return {
            "status": "error",
            "isError": True,
            "error": "Both 'text' and 'key' parameters are required.",
        }

    try:
        result = hmac.new(key.encode("utf-8"), text.encode("utf-8"), algo_map[algorithm]).hexdigest()
    except Exception as e:
        return {"status": "error", "isError": True, "error": str(e)}

    return {
        "status": "success",
        "algorithm": f"HMAC-{algorithm.upper()}",
        "hmac": result,
        "text_length": len(text),
        "key_length": len(key),
    }


def crypto_uuid_tool(params):
    """Generate UUID (v4 or v7)."""
    version = params.get("version", "v4")

    if version == "v4":
        result = str(uuid.uuid4())
    elif version == "v7":
        try:
            result = str(uuid.uuid4())  # Python <3.14 fallback
            # Try uuid7 if available (Python 3.14+)
            if hasattr(uuid, "uuid7"):
                result = str(uuid.uuid7())
        except Exception:
            result = str(uuid.uuid4())
    else:
        return {
            "status": "error",
            "isError": True,
            "error": f"Unsupported UUID version: '{version}'. Use 'v4' or 'v7'.",
        }

    return {"status": "success", "version": version, "uuid": result}


def crypto_random_tool(params):
    """Generate cryptographically secure random string."""
    length = int(params.get("length", 32))
    charset_name = params.get("charset", "alphanumeric")

    charsets = {
        "alphanumeric": string.ascii_letters + string.digits,
        "alpha": string.ascii_letters,
        "numeric": string.digits,
        "lowercase": string.ascii_lowercase,
        "uppercase": string.ascii_uppercase,
        "hex": string.hexdigits.lower(),
        "printable": string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{}|;:,.<>?",
        "urlsafe": string.ascii_letters + string.digits + "-_",
    }

    if charset_name not in charsets:
        return {
            "status": "error",
            "isError": True,
            "error": f"Unsupported charset: '{charset_name}'",
            "supported_charsets": list(charsets.keys()),
        }

    if length < 1 or length > 4096:
        return {"status": "error", "isError": True, "error": "Length must be between 1 and 4096."}

    charset = charsets[charset_name]
    result = "".join(secrets.choice(charset) for _ in range(length))

    return {
        "status": "success",
        "length": length,
        "charset": charset_name,
        "entropy_bits": round(length * (len(charset).bit_length() - 1), 1),
        "result": result,
    }


# ── Tool Registry ───────────────────────────────────────────────────────────

TOOLS = {
    "hash_generate": {
        "fn": hash_generate,
        "description": "Generate cryptographic hash (MD5, SHA-1, SHA-256, SHA-512, SHA3, BLAKE2) of input text.",
        "params": {
            "text": {"type": "string", "required": True, "description": "Text to hash."},
            "algorithm": {"type": "string", "required": False, "default": "sha256", "description": "Hash algorithm: md5, sha1, sha256, sha512, sha3_256, sha3_512, blake2b, blake2s."},
        },
    },
    "hash_compare": {
        "fn": hash_compare,
        "description": "Compare a hash against input text to verify data integrity.",
        "params": {
            "text": {"type": "string", "required": True, "description": "Text to hash and compare."},
            "hash": {"type": "string", "required": True, "description": "Expected hash value."},
            "algorithm": {"type": "string", "required": False, "default": "sha256", "description": "Hash algorithm."},
        },
    },
    "encode_base64": {
        "fn": encode_base64_tool,
        "description": "Base64 encode or decode text.",
        "params": {
            "text": {"type": "string", "required": True, "description": "Text to encode/decode."},
            "action": {"type": "string", "required": False, "default": "encode", "description": "Action: 'encode' or 'decode'."},
        },
    },
    "encode_url": {
        "fn": encode_url_tool,
        "description": "URL encode or decode text (percent-encoding).",
        "params": {
            "text": {"type": "string", "required": True, "description": "Text to encode/decode."},
            "action": {"type": "string", "required": False, "default": "encode", "description": "Action: 'encode' or 'decode'."},
        },
    },
    "encode_html": {
        "fn": encode_html_tool,
        "description": "HTML entity encode or decode text.",
        "params": {
            "text": {"type": "string", "required": True, "description": "Text to encode/decode."},
            "action": {"type": "string", "required": False, "default": "encode", "description": "Action: 'encode' or 'decode'."},
        },
    },
    "crypto_hmac": {
        "fn": crypto_hmac_tool,
        "description": "Generate HMAC signature using a secret key.",
        "params": {
            "text": {"type": "string", "required": True, "description": "Text to sign."},
            "key": {"type": "string", "required": True, "description": "Secret key for HMAC."},
            "algorithm": {"type": "string", "required": False, "default": "sha256", "description": "HMAC algorithm: sha256, sha512, sha1, md5."},
        },
    },
    "crypto_uuid": {
        "fn": crypto_uuid_tool,
        "description": "Generate a UUID (v4 random or v7 time-ordered).",
        "params": {
            "version": {"type": "string", "required": False, "default": "v4", "description": "UUID version: 'v4' or 'v7'."},
        },
    },
    "crypto_random": {
        "fn": crypto_random_tool,
        "description": "Generate cryptographically secure random string.",
        "params": {
            "length": {"type": "integer", "required": False, "default": 32, "description": "Length of random string (1-4096)."},
            "charset": {"type": "string", "required": False, "default": "alphanumeric", "description": "Charset: alphanumeric, alpha, numeric, lowercase, uppercase, hex, printable, urlsafe."},
        },
    },
}

# ── Tool schemas for MCP tools/list ─────────────────────────────────────────

TOOL_SCHEMAS = []
for name, info in TOOLS.items():
    properties = {}
    required = []
    for pname, pinfo in info["params"].items():
        prop = {"type": pinfo["type"], "description": pinfo["description"]}
        if "default" in pinfo:
            prop["default"] = pinfo["default"]
        properties[pname] = prop
        if pinfo.get("required"):
            required.append(pname)

    TOOL_SCHEMAS.append(
        {
            "name": name,
            "description": info["description"],
            "inputSchema": {"type": "object", "properties": properties, "required": required},
        }
    )


# ── MCP stdio handler ───────────────────────────────────────────────────────

import asyncio


async def handle_request(request):
    """Handle a single JSON-RPC request."""
    rid = request.get("id")
    method = request.get("method", "")
    params = request.get("params", {})

    if method == "initialize":
        return json.dumps(
            {
                "jsonrpc": "2.0",
                "id": rid,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "hashvault", "version": "1.0.0"},
                },
            }
        )

    if method == "tools/list":
        return json.dumps({"jsonrpc": "2.0", "id": rid, "result": {"tools": TOOL_SCHEMAS}})

    if method == "tools/call":
        tool_name = params.get("name", "")
        tool_params = params.get("arguments", {})

        if tool_name not in TOOLS:
            return json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": rid,
                    "result": {
                        "content": [
                            {"type": "text", "text": json.dumps({"error": f"Unknown tool: {tool_name}", "isError": True})}
                        ]
                    },
                }
            )

        # Rate limit check
        limit_check = check_rate_limit()
        if limit_check:
            return json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": rid,
                    "result": {"content": [{"type": "text", "text": json.dumps(limit_check)}]},
                }
            )

        try:
            result = TOOLS[tool_name]["fn"](tool_params)
        except Exception as e:
            result = {"status": "error", "isError": True, "error": str(e), "next_steps": ["Check input parameters.", "Report this issue if it persists."]}

        return json.dumps(
            {
                "jsonrpc": "2.0",
                "id": rid,
                "result": {"content": [{"type": "text", "text": json.dumps(result)}]},
            }
        )

    if method == "notifications/initialized":
        return None

    return json.dumps({"jsonrpc": "2.0", "id": rid, "error": {"code": -32601, "message": f"Method not found: {method}"}})


async def main():
    """MCP stdio main loop."""
    tier = "PRO (unlimited)" if IS_PRO else f"FREE ({FREE_LIMIT} calls)"
    print(f"HashVault MCP v1.0.0 — {tier}", file=sys.stderr)
    print(f"Pro upgrade: {STRIPE_LINK}", file=sys.stderr)

    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    loop = asyncio.get_event_loop()
    await loop.connect_read_pipe(lambda: protocol, sys.stdin)

    writer_transport, writer_protocol = await loop.connect_write_pipe(
        asyncio.streams.FlowControlMixin, sys.stdout
    )
    writer = asyncio.StreamWriter(writer_transport, writer_protocol, reader, loop)

    buffer = b""
    while True:
        try:
            data = await reader.read(65536)
            if not data:
                break
            buffer += data

            while b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)
                line = line.strip()
                if not line:
                    continue
                try:
                    request = json.loads(line.decode("utf-8"))
                except json.JSONDecodeError:
                    continue

                response = await handle_request(request)
                if response:
                    writer.write((response + "\n").encode())
                    await writer.drain()
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            break


if __name__ == "__main__":
    asyncio.run(main())
