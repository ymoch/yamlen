# yamlen - a Thin PyYAML Wrapper

## Features
- Contextual tag construction.

## Examples

### Load YAML documents in Streams

```python
from io import StringIO
from yamlen import Loader

loader = Loader()

stream = StringIO("foo")
assert loader.load(stream) == "foo"

stream = StringIO("foo\n---\nbar")
assert list(loader.load_all(stream)) == ["foo", "bar"]

```

### Load YAML Documents in Files.

```python
import os
from tempfile import TemporaryDirectory
from yamlen import Loader

loader = Loader()

with TemporaryDirectory() as temp_dir:
    path = os.path.join(temp_dir.name, "example.yml")
    with open(path, "w") as f:
        f.write("foo\n---\nbar")

    assert loader.load_from_path(path) == "foo"
    assert list(loader.load_all_from_path(path)) == ["foo", "bar"]
```

### Contextual tag construction: include another YAML file.

```python
import os
from tempfile import TemporaryDirectory
from yamlen import Loader
from yamlen.tag.impl.inclusion import InclusionTag

loader = Loader()
loader.add_tag("!include", InclusionTag())

with TemporaryDirectory() as temp_dir:
    foo_path = os.path.join(temp_dir.name, "foo.yml")
    with open(foo_path, "w") as f:
        f.write("!include ./bar.yml")
        
    bar_path = os.path.join(temp_dir.name, "bar.yml")
    with open(bar_path, "w") as f:
        f.write("bar")

    assert loader.load_from_path(foo_path) == "bar"
```
