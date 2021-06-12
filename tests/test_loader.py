from io import StringIO
from typing import Optional

from pytest import raises
from yaml import Node, ScalarNode

from yamlen import TagContext
from yamlen.error import YamlenError
from yamlen.loader import Loader, Tag


class BypassTag(Tag):
    def __init__(self, expected_path: Optional[str]):
        self._expected_path = expected_path

    def construct(self, node: Node, context: TagContext) -> object:
        assert context.origin == self._expected_path

        assert isinstance(node, ScalarNode)
        return context.constructor.construct_scalar(node)


def test_load_given_invalid_content():
    loader = Loader()
    with raises(YamlenError) as error_info:
        loader.load(StringIO("!invalid"))
    assert '", line 1, column 1' in str(error_info.value)


def test_load_all():
    stream = StringIO("1\n---\n!bypass 123\n---\n!x\n---\n2")

    loader = Loader()
    loader.add_tag("!bypass", BypassTag(expected_path=None))
    actual = loader.load_all(stream)
    assert next(actual) == 1
    assert next(actual) == "123"
    with raises(YamlenError):
        next(actual)
    with raises(StopIteration):
        next(actual)


def test_load_from_path_not_found(mocker):
    mocker.patch("builtins.open", side_effect=FileNotFoundError("message"))

    loader = Loader()
    with raises(YamlenError):
        loader.load_from_path("/////foo/bar/baz")


def test_load_from_path(mocker):
    content = StringIO("!bypass xyz")
    open_mock = mocker.patch("builtins.open", return_value=content)

    loader = Loader()
    loader.add_tag("!bypass", BypassTag(expected_path="path/to"))
    actual = loader.load_from_path("path/to/scenario.yml")
    assert actual == "xyz"

    assert content.closed
    open_mock.assert_called_once_with("path/to/scenario.yml")


def test_load_all_from_path_not_found(mocker):
    mocker.patch("builtins.open", side_effect=FileNotFoundError("message"))

    loader = Loader()
    objs = loader.load_all_from_path("/////foo/bar/baz")
    with raises(YamlenError):
        next(objs)


def test_load_all_from_path(mocker):
    content = StringIO("1\n---\n!bypass abc\n---\n!x\n---\n2\n")
    open_mock = mocker.patch("builtins.open", return_value=content)

    loader = Loader()
    loader.add_tag("!bypass", BypassTag(expected_path="path/to"))
    actual = loader.load_all_from_path("path/to/scenario.yml")
    assert next(actual) == 1
    assert next(actual) == "abc"
    with raises(YamlenError):
        next(actual)
    with raises(StopIteration):
        next(actual)

    assert content.closed
    open_mock.assert_called_once_with("path/to/scenario.yml")
