import glob
import os
import re

from yaml import Node
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
        # HACK fix typing.
        base = constructor.construct_scalar(node)  # type: ignore
        if not isinstance(base, str):
            raise YamlenError(f'expected a scalar node, but found {type(base)}')

        path = os.path.join(origin, base)
        if _WILDCARDS_REGEX.match(path):
            paths = glob.iglob(path, recursive=True)
            return [loader.load_from_path(p) for p in paths]
        return loader.load_from_path(path)
