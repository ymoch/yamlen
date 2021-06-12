"""Loaders."""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from contextlib import contextmanager
from functools import partial
from typing import Any, Iterator, Optional, TextIO

from yaml import Node, MarkedYAMLError
from yaml import load as _load, load_all as _load_all
from yaml.composer import Composer
from yaml.constructor import BaseConstructor, SafeConstructor
from yaml.parser import Parser
from yaml.reader import Reader
from yaml.resolver import Resolver
from yaml.scanner import Scanner

from .error import YamlenError, on_node

__all__ = ("Loader", "Tag", "TagContext")


class TagContext:
    """
    A tag construction context.
    """

    def __init__(
        self,
        loader: Loader,
        constructor: BaseConstructor,
        origin: Optional[str] = None,
    ):
        self._loader = loader
        self._constructor = constructor
        self._origin = origin

    @property
    def loader(self) -> Loader:
        """
        Returns a current YAML loader.
        """
        return self._loader

    @property
    def constructor(self) -> BaseConstructor:
        """
        Returns a PyYAML constructor.
        """
        return self._constructor

    @property
    def origin(self) -> Optional[str]:
        """
        Returns the origin path of the loading file if exists.
        """
        return self._origin


class Tag(ABC):
    @abstractmethod
    def construct(self, node: Node, context: TagContext) -> Any:
        """
        Construct the corresponding Python object to the given node.
        """


class Loader:
    def __init__(self):
        self._origin: Optional[str] = None

        class _Ctor(SafeConstructor):
            pass

        class _Loader(Reader, Scanner, Parser, Composer, _Ctor, Resolver):
            def __init__(self, stream):
                Reader.__init__(self, stream)
                Scanner.__init__(self)
                Parser.__init__(self)
                Composer.__init__(self)
                SafeConstructor.__init__(self)

        self._ctor = _Ctor
        self._Loader = _Loader

    def add_tag(self, name: str, tag: Tag) -> None:
        self._ctor.add_constructor(name, partial(self._apply_tag, tag))

    def load(self, stream: TextIO, origin: Optional[str] = None) -> object:
        """
        Parse the first YAML document in a stream and produce the corresponding Python object.
        """
        try:
            with self._on_origin(origin):
                return _load(stream, self._Loader)
        except MarkedYAMLError as error:
            raise YamlenError(cause=error)

    def load_from_path(self, path: str) -> object:
        """
        Parse the first YAML document in a file and produce the corresponding Python object.
        """
        origin = os.path.dirname(path)
        try:
            with open(path) as stream:
                return self.load(stream, origin)
        except FileNotFoundError as error:
            raise YamlenError(cause=error)

    def load_all(self, stream: TextIO, origin: Optional[str] = None) -> Iterator:
        """
        Parse all YAML documents in a stream and produce corresponding Python objects.
        """
        try:
            with self._on_origin(origin):
                yield from _load_all(stream, self._Loader)
        except MarkedYAMLError as error:
            raise YamlenError(cause=error)

    def load_all_from_path(self, path: str) -> Iterator:
        """
        Parse all YAML documents in a file and produce corresponding Python objects.
        """
        origin = os.path.dirname(path)
        try:
            with open(path) as stream:
                yield from self.load_all(stream, origin)
        except FileNotFoundError as error:
            raise YamlenError(cause=error)

    def _apply_tag(self, tag: Tag, ctor: BaseConstructor, node: Node) -> object:
        context = TagContext(loader=self, constructor=ctor, origin=self._origin)
        with on_node(node):
            return tag.construct(node, context)

    @contextmanager
    def _on_origin(self, origin: Optional[str]) -> Iterator:
        original = self._origin
        self._origin = origin
        try:
            yield
        finally:
            self._origin = original
