import glob
import os
import re

from yaml import ScalarNode

from yamlen.loader import Context, Tag

_WILDCARDS_REGEX = re.compile(r"^.*(\*|\?|\[!?.+]).*$")


class InclusionTag(Tag):
    def construct_by_context(self, context: Context):
        node = context.node
        if not isinstance(node, ScalarNode):
            raise ValueError(f"expected a scalar node, but found {node.tag}")

        base = context.constructor.construct_scalar(node)
        if not base:
            raise ValueError("given no path")

        path = os.path.join(context.origin, str(base))
        if _WILDCARDS_REGEX.match(path):
            paths = glob.iglob(path, recursive=True)
            return [context.loader.load_from_path(p) for p in paths]
        return context.loader.load_from_path(path)
