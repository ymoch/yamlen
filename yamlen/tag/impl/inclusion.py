import glob
import os
import re

from yaml import Node, ScalarNode

from yamlen.loader import TagContext, Tag

__all__ = ("InclusionTag",)

_WILDCARDS_REGEX = re.compile(r"^.*(\*|\?|\[!?.+]).*$")


class InclusionTag(Tag):
    def construct(self, node: Node, context: TagContext) -> object:
        origin = context.origin
        if origin is None:
            raise ValueError(
                "cannot decide the target directory because no origin path is given"
            )

        if not isinstance(node, ScalarNode):
            raise ValueError(f"expected a scalar node, but found {node.tag}")

        base = context.constructor.construct_scalar(node)
        if not base:
            raise ValueError("given no path")

        path = os.path.join(origin, str(base))
        if _WILDCARDS_REGEX.match(path):
            paths = glob.iglob(path, recursive=True)
            return [context.loader.load_from_path(p) for p in paths]
        return context.loader.load_from_path(path)
