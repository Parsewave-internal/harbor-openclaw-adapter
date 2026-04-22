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
  -a nop \
  --agent-import-path harbor_openclaw:OpenClaw \
  -p path/to/task \
  -m openai/gpt-4o-mini
```

`-a nop` is a throwaway — Harbor requires an agent name to pass CLI
validation, but `--agent-import-path` takes precedence and loads `OpenClaw`
from this package instead.

### Optional runtime env vars (via `--ae`)

All three are opt-in; omit them for a vanilla API-key run.

| Var | Purpose |
|---|---|
| `OPENCLAW_AUTH_PROFILES_PATH` | Path on the host to an `auth-profiles.json` for OAuth/subscription providers. Base64-injected into `$HOME/.openclaw/agents/<id>/agent/auth-profiles.json` in the container, then scrubbed at teardown so a leaked image cannot exfiltrate the token. `OPENCLAW_AUTH_B64` accepts a pre-encoded blob directly. |
| `OPENCLAW_MEMORY_DIR` | Path inside the container to seed into `<workspace>/memory/` before the run; `openclaw memory index --force` is run after seeding (best-effort — falls back to keyword search if the optional vector-index deps aren't installed). |
| `OPENCLAW_PERSONALITY_DIR` | Path inside the container; files are flat-copied (by basename, `-maxdepth 1`) into the workspace root — useful for task-supplied `AGENTS.md` / persona files. |

Example with all three:

```bash
harbor run \
  -a nop \
  --agent-import-path harbor_openclaw:OpenClaw \
  -p path/to/task \
  -m openai/gpt-4o-mini \
  --ae OPENCLAW_AUTH_PROFILES_PATH=$HOME/.openclaw/agents/main/agent/auth-profiles.json \
  --ae OPENCLAW_MEMORY_DIR=/app/optional_memory \
  --ae OPENCLAW_PERSONALITY_DIR=/app/persona
```

## Migration after PR merge

Once [harbor-framework/harbor#1490](https://github.com/harbor-framework/harbor/pull/1490)
lands on PyPI, you no longer need this package. Drop the `--agent-import-path`
flag and switch `-a nop` to `-a openclaw`:

```bash
harbor run -a openclaw -p path/to/task -m openai/gpt-4o-mini
```

## Development

```bash
uv sync --group dev
uv run pytest tests/
```

## License

Apache-2.0
