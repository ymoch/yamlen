"""Error handling."""

from contextlib import contextmanager
from typing import Optional, Iterator

from yaml import Mark, Node


class YamlenError(RuntimeError):
    def __init__(self, cause: Exception, mark: Optional[Mark] = None):
        self._cause = cause
        self._mark = mark

    def __str__(self) -> str:
        lines = []
        if self._cause:
            lines.append(str(self._cause))
        if self._mark:
            lines.append(str(self._mark))
        return "\n".join(lines)


@contextmanager
def on_node(node: Node) -> Iterator:
    try:
        yield
    except Exception as error:
        raise YamlenError(mark=node.start_mark, cause=error)
