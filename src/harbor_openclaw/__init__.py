"""harbor-openclaw: run OpenClaw on Harbor via ``--agent-import-path``.

Example::

    harbor run \\
        -a nop \\
        --agent-import-path harbor_openclaw:OpenClaw \\
        -p path/to/task \\
        -m openai/gpt-4o-mini

This package is a standalone shim for use with clean upstream Harbor until
https://github.com/harbor-framework/harbor/pull/1490 merges. After the PR
merges, ``-a openclaw`` works without this package.
"""

from harbor_openclaw.agent import OpenClaw

__all__ = ["OpenClaw"]
__version__ = "0.1.4"
