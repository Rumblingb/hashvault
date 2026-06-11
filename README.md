# 🔐 HashVault MCP

> Your AI agent's cryptography and encoding toolkit. 8 pure-Python tools. Zero API keys.

[![MCP Server](https://img.shields.io/badge/MCP-Server-blue)](https://smithery.ai/servers/vishar-rumbling/hashvault)
[![Python](https://img.shields.io/badge/Python-3.9%2B-green)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
[![Pro](https://img.shields.io/badge/Pro-%249%2Fmo-blueviolet)](https://buy.stripe.com/14kg3reZT1Fv9H2288)

**8 pure-Python hash, encode, and crypto tools. Zero API keys. Freemium with 50 free calls. $9/mo Pro unlimited.**

---

## 🎯 Why HashVault?

AI agents need to hash data, encode strings, verify integrity, and generate secure tokens — constantly. Instead of importing hashlib and base64 in every agent script, HashVault MCP gives you **8 battle-tested, production-ready security tools** in a single MCP server.

Every tool is:
- **100% Python stdlib** — no external dependencies beyond `mcp`
- **Read-only, idempotent** — safe for any agent to call
- **Error-as-result** — never throws exceptions, always returns structured JSON
- **Rate-limited** — free tier with clear upgrade path

---

## 🛠️ Tools

| Tool | Description | Example Use Case |
|------|-------------|-----------------|
| `hash_generate` | MD5, SHA-1, SHA-256, SHA-512, SHA3, BLAKE2 | Verify file integrity, generate checksums |
| `hash_compare` | Compare hash against text to verify integrity | Validate downloaded files, check data corruption |
| `encode_base64` | Base64 encode/decode | Encode binary data, decode API tokens |
| `encode_url` | URL percent-encode/decode | Encode query parameters, decode URLs |
| `encode_html` | HTML entity encode/decode | Sanitize user input, decode HTML entities |
| `crypto_hmac` | HMAC-SHA256/512 signature generation | API authentication, webhook verification |
| `crypto_uuid` | UUID v4/v7 generation | Generate unique IDs, database keys |
| `crypto_random` | Secure random string generation | API keys, tokens, passwords |

---

## 📦 Installation

### Smithery (Recommended)
```bash
npx smithery install hashvault --client claude
```

### Manual (Python)
```bash
git clone https://github.com/Rumblingb/hashvault.git
cd hashvault
pip install -r requirements.txt
python3 server.py
```

### Claude Desktop Config
```json
{
  "mcpServers": {
    "hashvault": {
      "command": "python3",
      "args": ["server.py"],
      "cwd": "/path/to/hashvault"
    }
  }
}
```

---

## 💰 Pricing

| Tier | Price | Limits |
|------|-------|--------|
| **Free** | $0 | 50 calls per server start |
| **Pro** | $9/mo | Unlimited calls |

**[Upgrade to Pro →](https://buy.stripe.com/14kg3reZT1Fv9H2288)**

Pro users get:
- Unlimited calls across all 8 tools
- Priority support via GitHub Issues
- Access to new tools before free tier

---

## 🧪 Usage Examples

### Generate SHA-256 hash
```json
{
  "tool": "hash_generate",
  "text": "Hello, World!",
  "algorithm": "sha256"
}
```
→ `dffd6021bb2bd5b0af676290809ec3a53191dd81c7f70a4b28688a362182986f`

### Verify hash integrity
```json
{
  "tool": "hash_compare",
  "text": "Hello, World!",
  "hash": "dffd6021bb2bd5b0af676290809ec3a53191dd81c7f70a4b28688a362182986f",
  "algorithm": "sha256"
}
```
→ `{"match": true}`

### Base64 encode
```json
{
  "tool": "encode_base64",
  "text": "Hello, World!",
  "action": "encode"
}
```
→ `SGVsbG8sIFdvcmxkIQ==`

### URL encode
```json
{
  "tool": "encode_url",
  "text": "hello world & friends",
  "action": "encode"
}
```
→ `hello%20world%20%26%20friends`

### Generate HMAC signature
```json
{
  "tool": "crypto_hmac",
  "text": "order_id=12345&amount=99.99",
  "key": "secret-api-key-2024",
  "algorithm": "sha256"
}
```
→ Signature for webhook/API verification

### Generate UUID
```json
{
  "tool": "crypto_uuid",
  "version": "v4"
}
```
→ `550e8400-e29b-41d4-a716-446655440000`

### Generate secure random string
```json
{
  "tool": "crypto_random",
  "length": 64,
  "charset": "urlsafe"
}
```
→ 64-character URL-safe random token

---

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│         MCP Client (Claude, etc.)    │
└────────────┬────────────────────────┘
             │ JSON-RPC over stdio
┌────────────▼────────────────────────┐
│         HashVault MCP Server         │
│                                      │
│  ┌──────────┐  ┌───────────┐        │
│  │ Rate Lim  │  │  Tool     │        │
│  │ (free 50) │  │  Registry │        │
│  └──────────┘  └─────┬─────┘        │
│                      │               │
│   ┌──────────────────┼──────────┐    │
│   │                  │          │    │
│  Hash│Encode│HMAC│UUID│Random│ ...  │
│      │B64URL│    │    │      │      │
│      │HTML  │    │    │      │      │
└──────┴──────┴────┴────┴──────┴──────┘
     All tools: Python stdlib only
```

---

## 🔄 Error Handling

All tools return errors INSIDE the response (never throw exceptions):
```json
{
  "status": "error",
  "isError": true,
  "error": "Unsupported algorithm: 'rot13'",
  "supported_algorithms": ["md5", "sha1", "sha256", "sha512", "sha3_256", "sha3_512", "blake2b", "blake2s"]
}
```

Rate limit exceeded:
```json
{
  "error": "Free tier limit (50 calls). Upgrade to Pro ($9/mo unlimited).",
  "isError": true,
  "next_steps": [
    "Buy Pro: https://buy.stripe.com/14kg3reZT1Fv9H2288",
    "Restart server to reset counter",
    "Use --pro-key PROL_AGENTPAY_DEMO for testing"
  ],
  "calls_used": 50,
  "limit": 50
}
```

---

## 📄 License

MIT — see [LICENSE](LICENSE)

---

**Part of the AgentPay Labs ecosystem** — [More MCP Servers](https://rumblingb.github.io/mcp-directory/)

[![smithery badge](https://smithery.ai/badge/vishar-rumbling/hashvault)](https://smithery.ai/servers/vishar-rumbling/hashvault)
