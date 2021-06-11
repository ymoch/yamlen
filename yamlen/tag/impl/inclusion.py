import glob
import os
import re

from yaml import Node, ScalarNode
from yaml.constructor import BaseConstructor

from yamlen.error import YamlenError
from yamlen.loader import Loader, Tag

_WILDCARDS_REGEX = re.compile(r'^.*(\*|\?|\[!?.+]).*$')


class InclusionTag(Tag):

    def construct(
        self,
        loader: Loader,
        constructor: BaseConstructor,
        node: Node,
        origin: str = '.',
    ) -> object:
        if not isinstance(node, ScalarNode):
            raise YamlenError(f'expected a scalar node, but found {node.tag}')

        base = constructor.construct_scalar(node)
        if not base:
            raise YamlenError('given no path')

        path = os.path.join(origin, str(base))
        if _WILDCARDS_REGEX.match(path):
            paths = glob.iglob(path, recursive=True)
            return [loader.load_from_path(p) for p in paths]
        return loader.load_from_path(path)
