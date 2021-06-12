import glob
import os
import re

from yaml import Node, ScalarNode
from yaml.constructor import BaseConstructor

from yamlen.loader import Context, Loader, Tag

_WILDCARDS_REGEX = re.compile(r"^.*(\*|\?|\[!?.+]).*$")


class InclusionTag(Tag):
    def construct_by_context(self, context: Context):
        return self.construct(
            context.loader,
            context.constructor,
            context.node,
            context.origin,
        )

    def construct(
        self,
        loader: Loader,
        constructor: BaseConstructor,
        node: Node,
        origin: str = ".",
    ) -> object:
        if not isinstance(node, ScalarNode):
            raise ValueError(f"expected a scalar node, but found {node.tag}")

        base = constructor.construct_scalar(node)
        if not base:
            raise ValueError("given no path")

        path = os.path.join(origin, str(base))
        if _WILDCARDS_REGEX.match(path):
            paths = glob.iglob(path, recursive=True)
            return [loader.load_from_path(p) for p in paths]
        return loader.load_from_path(path)
