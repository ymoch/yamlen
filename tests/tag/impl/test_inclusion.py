import os
from io import StringIO

from pytest import fixture, mark, raises

from yamlen.error import YamlenError
from yamlen.loader import Loader
from yamlen.tag.impl.inclusion import InclusionTag


@fixture
def loader():
    loader = Loader()
    loader.add_tag("!include", InclusionTag())
    return loader


def test_given_no_origin(mocker, loader):
    open_mock = mocker.patch("builtins.open")

    stream = StringIO("!include foo.yml")
    with raises(YamlenError) as error_info:
        loader.load(stream)
    assert "no origin" in str(error_info.value)

    open_mock.assert_not_called()


@mark.parametrize(
    ("content", "expected_message"),
    (
        ("!include", "given no path"),
        ("!include []", "expected a scalar node"),
        ("!include {}", "expected a scalar node"),
    ),
)
def test_given_invalid_inclusion(loader, content, expected_message):
    stream = StringIO(content)
    with raises(YamlenError) as error_info:
        loader.load(stream, origin=".")
    assert expected_message in str(error_info.value)


def test_given_current_directory_inclusion(mocker, loader):
    open_mock = mocker.patch("builtins.open")
    open_mock.return_value = StringIO("xxx")

    stream = StringIO("!include foo.yml")
    actual = loader.load(stream, origin="")
    assert actual == "xxx"

    open_mock.assert_called_once_with("foo.yml")


def test_given_recursive_inclusion_error(mocker, loader):
    open_mock = mocker.patch("builtins.open")
    open_mock.return_value = StringIO("\n !foo")

    stream = StringIO("!include foo.yml")
    with raises(YamlenError) as error_info:
        loader.load(stream, origin=".")
    message = str(error_info.value)
    assert "!foo" in message
    assert '", line 1, column 1' in message
    assert '", line 2, column 2' in message

    open_mock.assert_called_once_with(os.path.join(".", "foo.yml"))


def test_given_recursive_inclusion(mocker, loader):
    stream = StringIO(
        """
    list:
      - !include item.yml
      - key: !include value.yml
    recursive: !include recursive.yml
    """
    )
    answer_map = {
        os.path.join("base", "dir", "item.yml"): "item",
        os.path.join("base", "dir", "value.yml"): "value",
        os.path.join("base", "dir", "recursive.yml"): "!include inner.yml",
        os.path.join("base", "dir", "inner.yml"): "inner",
    }
    open_mock = mocker.patch("builtins.open")
    open_mock.side_effect = lambda path: StringIO(answer_map[path])

    actual = loader.load(stream, origin=os.path.join("base", "dir"))
    assert actual == {
        "list": [
            "item",
            {"key": "value"},
        ],
        "recursive": "inner",
    }


def test_given_wildcard_inclusion(mocker, loader):
    iglob_mock = mocker.patch("glob.iglob")
    iglob_mock.side_effect = lambda path, recursive: iter([f"glob:{path}:{recursive}"])

    stream = StringIO(
        r"""
    'asterisk': !include '*.yml'
    'double-asterisk': !include '**.yml'
    'question': !include '?.yml'
    'parenthesis-only-opening': !include '[.yml'
    'parenthesis-only-closing': !include '].yml'
    'empty-parenthesis': !include '[].yml'
    'filled-parenthesis': !include '[abc].yml'
    """
    )
    open_mock = mocker.patch("builtins.open")
    open_mock.side_effect = lambda path: StringIO(path)

    actual = loader.load(stream, origin="base/path/")
    assert isinstance(actual, dict)
    assert actual["asterisk"] == ["glob:base/path/*.yml:True"]
    assert actual["double-asterisk"] == ["glob:base/path/**.yml:True"]
    assert actual["question"] == ["glob:base/path/?.yml:True"]
    assert actual["parenthesis-only-closing"] == "base/path/].yml"
    assert actual["parenthesis-only-opening"] == "base/path/[.yml"
    assert actual["empty-parenthesis"] == "base/path/[].yml"
    assert actual["filled-parenthesis"] == ["glob:base/path/[abc].yml:True"]
