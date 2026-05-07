"""harbor-openclaw: run OpenClaw on Harbor via ``--agent-import-path``.

Example::

    harbor run \\
        --agent-import-path harbor_openclaw:OpenClaw \\
        -p path/to/task \\
        -m openai-codex/gpt-5.4

"""

from harbor_openclaw.agent import OpenClaw

__all__ = ["OpenClaw"]
__version__ = "0.1.9"
