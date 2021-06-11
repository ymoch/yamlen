from io import StringIO
from unittest.mock import call

from pytest import fixture, raises

from yamlen.error import YamlenError
from yamlen.loader import Loader
from yamlen.tag.impl.inclusion import InclusionTag


@fixture
def loader() -> Loader:
    loader = Loader()
    loader.add_tag("!include", InclusionTag())
    return loader


def test_load_given_invalid_content(loader):
    stream = StringIO("!invalid")
    with raises(YamlenError) as error_info:
        loader.load(stream)
    assert '", line 1, column 1' in str(error_info.value)


def test_load_all(mocker, loader):
    stream = StringIO("1\n---\n!include inner/foo.yml\n---\n!x\n---\n2")
    included_content = StringIO("foo")

    open_mock = mocker.patch("builtins.open")
    open_mock.return_value = included_content

    actual = loader.load_all(stream)
    assert next(actual) == 1
    assert next(actual) == "foo"
    with raises(YamlenError):
        next(actual)
    with raises(StopIteration):
        next(actual)

    assert included_content.closed
    open_mock.assert_called_once_with("./inner/foo.yml")


def test_load_from_path_not_found(mocker, loader):
    mocker.patch("builtins.open", side_effect=FileNotFoundError("message"))
    with raises(YamlenError):
        loader.load_from_path("/////foo/bar/baz")


def test_load_from_path(mocker, loader):
    content = StringIO("!include inner/foo.yml")
    included_content = StringIO("foo")

    open_mock = mocker.patch("builtins.open")
    open_mock.side_effect = [content, included_content]

    actual = loader.load_from_path("path/to/scenario.yml")
    assert actual == "foo"

    assert content.closed
    assert included_content.closed
    open_mock.assert_has_calls(
        [call("path/to/scenario.yml"), call("path/to/inner/foo.yml")]
    )


def test_load_all_from_path_not_found(mocker, loader):
    mocker.patch("builtins.open", side_effect=FileNotFoundError("message"))

    objs = loader.load_all_from_path("/////foo/bar/baz")
    with raises(YamlenError):
        next(objs)


def test_load_all_from_path(mocker, loader):
    content = StringIO("1\n---\n!include inner/foo.yml\n---\n!x\n---\n2\n")
    included_content = StringIO("foo")

    open_mock = mocker.patch("builtins.open")
    open_mock.side_effect = [content, included_content]

    actual = loader.load_all_from_path("path/to/scenario.yml")
    assert next(actual) == 1
    assert next(actual) == "foo"
    with raises(YamlenError):
        next(actual)
    with raises(StopIteration):
        next(actual)

    assert content.closed
    assert included_content.closed
    open_mock.assert_has_calls(
        [call("path/to/scenario.yml"), call("path/to/inner/foo.yml")]
    )
