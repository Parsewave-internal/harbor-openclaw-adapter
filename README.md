# harbor-openclaw

OpenClaw agent adapter for [Harbor](https://github.com/harbor-framework/harbor).

Run the [OpenClaw](https://github.com/openclaw/openclaw) agent against
Harbor tasks on the upstream `pip install harbor` by supplying
`--agent-import-path harbor_openclaw:OpenClaw`.

## Install

```bash
pip install harbor harbor-openclaw
```

## Usage

```bash
harbor run \
  --agent-import-path harbor_openclaw:OpenClaw \
  -p path/to/task \
  -m openai-codex/gpt-5.4
```

Do **not** pass `-a`. Harbor's factory prefers a known `-a` name over
`--agent-import-path`, so `-a nop --agent-import-path harbor_openclaw:OpenClaw`
would silently run the no-op agent instead of OpenClaw.

### Optional runtime env vars (via `--ae`)

All three are opt-in; omit them for a vanilla API-key run.

| Var | Purpose |
|---|---|
| `OPENCLAW_AUTH_PROFILES_PATH` | Path on the host to an `auth-profiles.json` for OAuth/subscription providers. Base64-injected into `$HOME/.openclaw/agents/<id>/agent/auth-profiles.json` in the container, then scrubbed at teardown so a leaked image cannot exfiltrate the token. |
| `OPENCLAW_AUTH_B64` | Pre-encoded base64 blob of the same `auth-profiles.json`. Takes precedence over `OPENCLAW_AUTH_PROFILES_PATH`. |
| `OPENCLAW_MEMORY_DIR` | Path inside the container to seed into `<workspace>/memory/` before the run; `openclaw memory index --force` is run after seeding (best-effort — falls back to keyword search if the optional vector-index deps aren't installed). |
| `OPENCLAW_PERSONALITY_DIR` | Path inside the container; files are flat-copied (by basename, `-maxdepth 1`) into the workspace root — useful for task-supplied `AGENTS.md` / persona files. |

## Running with Codex CLI subscription (OAuth)

If you want to run OpenClaw with a Codex model (e.g. `openai-codex/gpt-5.4`)
backed by your ChatGPT **subscription**, you need an openclaw-format
`auth-profiles.json` on the host containing the OAuth credential.

The fastest path is to reuse the credential the [Codex CLI](https://github.com/openai/codex)
already stored after you logged in with ChatGPT. The Codex CLI keeps it in
`~/.codex/auth.json`; we re-shape a few fields with `jq` into the
openclaw-format file that this adapter understands. **No local OpenClaw
install is required.**

### 1. Make sure you've logged into the Codex CLI

After running `codex` at least once and completing the browser OAuth,
`~/.codex/auth.json` will exist with `tokens.access_token`,
`tokens.refresh_token`, `tokens.id_token`, and `tokens.account_id` set.

### 2. Convert `~/.codex/auth.json` into openclaw's `auth-profiles.json`

```bash
mkdir -p /tmp/openclaw-auth && jq '{
  version: 1,
  profiles: {
    "openai-codex:default": {
      type: "oauth",
      provider: "openai-codex",
      access: .tokens.access_token,
      refresh: .tokens.refresh_token,
      expires: ((now | floor) * 1000 + 3600000),
      idToken: .tokens.id_token,
      accountId: .tokens.account_id
    }
  }
}' ~/.codex/auth.json > /tmp/openclaw-auth/auth-profiles.json \
  && chmod 600 /tmp/openclaw-auth/auth-profiles.json
```

Re-run this any time the Codex CLI refreshes its token.

### 3. Point the adapter at that file

End-to-end command that runs a Harbor task against your subscription:

```bash
harbor run \
  --agent-import-path harbor_openclaw:OpenClaw \
  -p path/to/task \
  -m openai-codex/gpt-5.4 \
  --ae OPENCLAW_AUTH_PROFILES_PATH=/tmp/openclaw-auth/auth-profiles.json \
  --ae OPENCLAW_MEMORY_DIR=/app/optional_memory \
  --ae OPENCLAW_PERSONALITY_DIR=/app/persona
```

Or with a pre-encoded blob:

```bash
AUTH_B64=$(base64 -w0 /tmp/openclaw-auth/auth-profiles.json)
harbor run \
  --agent-import-path harbor_openclaw:OpenClaw \
  -p path/to/task \
  -m openai-codex/gpt-5.4 \
  --ae OPENCLAW_AUTH_B64=$AUTH_B64 \
  --ae OPENCLAW_MEMORY_DIR=/app/optional_memory \
  --ae OPENCLAW_PERSONALITY_DIR=/app/persona
```

If you leave both `OPENCLAW_AUTH_PROFILES_PATH` and `OPENCLAW_AUTH_B64` out
and the default file (`$HOME/.openclaw/agents/main/agent/auth-profiles.json`)
exists, the adapter picks it up automatically.

At teardown the adapter scrubs the injected blob from the container so a
leaked image can't exfiltrate the OAuth token.

### Alternative: Codex via API key

If you'd rather use a metered API key, drop the `auth-profiles.json` step
entirely and pass the key via `--ae`:

```bash
harbor run \
  --agent-import-path harbor_openclaw:OpenClaw \
  -p path/to/task \
  -m openai-codex/gpt-5.4 \
  --ae OPENAI_API_KEY=$OPENAI_API_KEY
```

## Development

```bash
uv sync --group dev
uv run pytest tests/
```

## License

Apache-2.0
