# Yamlen - a Thin PyYAML Wrapper

[![CircleCI](https://circleci.com/gh/ymoch/yamlen.svg?style=svg)][Circle CI]
[![Codecov](https://codecov.io/gh/ymoch/yamlen/branch/main/graph/badge.svg)][Codecov]

## Features
- Contextual tag construction.

## Examples

### Create a Loader
```
>>> from yamlen import Loader
>>> loader = Loader()

```


### Load YAML documents in Streams

```
>>> from io import StringIO

>>> stream = StringIO("foo")
>>> loader.load(stream)
'foo'

>>> stream = StringIO("foo\n---\nbar")
>>> list(loader.load_all(stream))
['foo', 'bar']

```

### Load YAML Documents in Files.

```
>>> import os
>>> from tempfile import TemporaryDirectory

>>> with TemporaryDirectory() as dir_path:
...     path = os.path.join(dir_path, "example.yml")
...     with open(path, "w") as f:
...         _ = f.write("foo")
...     loader.load_from_path(path)
'foo'

>>> with TemporaryDirectory() as dir_path:
...     path = os.path.join(dir_path, "example.yml")
...     with open(path, "w") as f:
...         _ = f.write("foo\n---\nbar")
...     list(loader.load_all_from_path(path))
['foo', 'bar']

```

### Contextual tag construction: include another YAML file.

```
>>> from yamlen.tag.impl.inclusion import InclusionTag
>>> loader.add_tag("!include", InclusionTag())

```

```
>>> with TemporaryDirectory() as dir_path:
...     foo_path = os.path.join(dir_path, "foo.yml")
...     bar_path = os.path.join(dir_path, "bar.yml")
...     with open(foo_path, "w") as f:
...         _ = f.write(f"!include ./bar.yml")
...     with open(bar_path, "w") as f:
...         _ = f.write("bar")
...     loader.load_from_path(foo_path)
'bar'

```

[Circle CI]: https://circleci.com/gh/ymoch/yamlen
[Codecov]: https://codecov.io/gh/ymoch/yamlen
