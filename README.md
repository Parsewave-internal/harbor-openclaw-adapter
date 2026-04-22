# harbor-openclaw

OpenClaw agent adapter for [Harbor](https://github.com/harbor-framework/harbor).

A standalone shim so users on the upstream `pip install harbor` can run the
[OpenClaw](https://github.com/openclaw/openclaw) agent against Harbor tasks
*today*, before the native integration
([harbor-framework/harbor#1490](https://github.com/harbor-framework/harbor/pull/1490))
merges.

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
| `OPENCLAW_AUTH_PROFILES_PATH` | Path on the host to an `auth-profiles.json` for OAuth/subscription providers. Base64-injected into `$HOME/.openclaw/agents/<id>/agent/auth-profiles.json` in the container, then scrubbed at teardown so a leaked image cannot exfiltrate the token. `OPENCLAW_AUTH_B64` accepts a pre-encoded blob directly. |
| `OPENCLAW_MEMORY_DIR` | Path inside the container to seed into `<workspace>/memory/` before the run; `openclaw memory index --force` is run after seeding (best-effort — falls back to keyword search if the optional vector-index deps aren't installed). |
| `OPENCLAW_PERSONALITY_DIR` | Path inside the container; files are flat-copied (by basename, `-maxdepth 1`) into the workspace root — useful for task-supplied `AGENTS.md` / persona files. |

## Running with Codex CLI subscription (OAuth)

If you want to run OpenClaw with a Codex model (e.g. `openai-codex/gpt-5.4`)
backed by your ChatGPT **subscription** rather than a metered API key, you
need an openclaw-format `auth-profiles.json` containing the OAuth credential.

### 1. Install the OpenClaw CLI locally (one-off)

```bash
npm install -g openclaw
```

If you do not have Node 22+, bootstrap it via nvm first:

```bash
curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.2/install.sh | bash
export NVM_DIR="$HOME/.nvm"
. "$NVM_DIR/nvm.sh"
nvm install 22 && nvm alias default 22
npm install -g openclaw
```

### 2. Log in once — creates `auth-profiles.json`

Register a local agent profile and run one no-op command to trigger
OpenClaw's Codex OAuth flow:

```bash
openclaw agents add main \
  --model openai-codex/gpt-5.4 \
  --workspace "$HOME/openclaw-ws" \
  --non-interactive

openclaw agent --agent main --message "hello"
```

The first invocation opens a browser for OAuth; complete the ChatGPT login.
After that you'll find:

```
$HOME/.openclaw/agents/main/agent/auth-profiles.json
```

### 3. Point the adapter at that file

End-to-end command that runs a Harbor task with your subscription:

```bash
harbor run \
  --agent-import-path harbor_openclaw:OpenClaw \
  -p path/to/task \
  -m openai-codex/gpt-5.4 \
  --ae OPENCLAW_AUTH_PROFILES_PATH=$HOME/.openclaw/agents/main/agent/auth-profiles.json \
  --ae OPENCLAW_MEMORY_DIR=/app/optional_memory \
  --ae OPENCLAW_PERSONALITY_DIR=/app/persona
```

If you leave `OPENCLAW_AUTH_PROFILES_PATH` out and the default file
(`$HOME/.openclaw/agents/main/agent/auth-profiles.json`) exists, the adapter
picks it up automatically. You can also hand over a pre-encoded blob with
`--ae OPENCLAW_AUTH_B64=$(base64 -w0 <path>)`.

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

## Migration after PR merge

Once [harbor-framework/harbor#1490](https://github.com/harbor-framework/harbor/pull/1490)
lands on PyPI, you no longer need this package. Drop the
`--agent-import-path` flag and pass `-a openclaw`:

```bash
harbor run -a openclaw -p path/to/task -m openai-codex/gpt-5.4
```

## Development

```bash
uv sync --group dev
uv run pytest tests/
```

## License

Apache-2.0
