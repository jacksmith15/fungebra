[![Build Status](https://travis-ci.com/jacksmith15/fungebra.svg?token=JrMQr8Ynsmu5tphpTQ2p&branch=master)](https://travis-ci.com/jacksmith15/fungebra)
# Fungebra
Wrapper to allow algebraic manipulation and composition of functions. An abstract callable provides methods for chaining and combining functions, and defines an expression syntax for doing the same.

The aims of this package are purely academic; I do not recommend using this if you respect the people who must read your code.

```python
from fungebra import Function
from external_library import other_func

@Function
def my_func():
    ...

other_func = Function(other_func)
```

## Expression syntax

In the following examples:
- `f`, `g`, `h` are `Function` wrapped callables.
- `x` is an arbitrary argument.

### Function composition

```python
(f + g)(x) == f.compose(g)(x) == f(g(x))
```

```python
(f | g)(x) == f.pipe(g)(x) == g(f(x))
```

```python
[1, 2, 3] | f == f([1, 2, 3])
```

```python
[1, 2, 3] | f.collect == f(1, 2, 3)
```

### Partial application

```python
(f << (1, 2, 3))(x) == f.partial(1, 2, 3)(x) == f(1, 2, 3, x)
```

```python
(f << {"opt": "val"})(x) == f.partial({"opt": "val"})(x) == f(x, opt="val")
```

```python
(f << Args(1, 2, opt="val"))(x) == f.partial(1, 2, opt="val")(x) == f(1, 2, x, opt="val")
```

```python
(f >> (1, 2, 3))(x) == f.rpartial(1, 2, 3)(x) == f(x, 1, 2, 3)
```

### Map, filter, reduce

#### Map
```python
(- f)(x) == f.map(x) == map(f, x)
```

```python
(f - g)(x) == f.compose(g.map)(x) == map(g, f(x))
```

#### Filter
```python
(f < g)(x) == f.filter(g)() == filter(g, f(x))
```

#### Reduce
```python
(f > g)(x) == f.reduce(g)(x) == reduce(g, f(x))
```

#### Combining
```python
(- f > g)(x) == (f >= g)(x) == f.map.reduce(g)(x) == reduce(g, map(f, x))
```

```python
(- f < g > h)(x) == f.map.filter(g).reduce(h)(x) == reduce(h, filter(g, map(f, x)))
```

```python
(f <= g)(x) == f.map.filter(g)(x) == filter(g, map(f, x))
```

## Functions
A number of compatible `Function` callables are provided in `fungebra.functions`. The `operator` standard library is re-exported as `Function` objects.

### Examples
```python
from fungebra import Function, operator as op
from fungebra.functions import less, fnot, itemgetter

greater_or_equal = less | fnot

@Function
def get_old_items_sort_by_name_desc(min_age: int):
    """Filter a known schema on old items, and sort by name descending."""
    return itemgetter("hits").filter(
        itemgetter("age") | greater_or_equal(min_age)
    ).pipe(
        F(sorted) << {"key": itemgetter("name") | ord | op.neg}
    ).pipe(list)

get_old_items_sort_by_name_desc(2)(
    {
        "hits": [
            {"age": 1, "name": "B"},
            {"age": 2, "name": "A"},
            {"age": 3, "name": "C"},
        ]
    }
) == [
    {"age": 3, "name": "C"},
    {"age": 2, "name": "A"},
]
```

```python
from fungebra import Function
from fungebra.functions import (
    iffy, less, constantly, caller
)

@Function
def truncate_below(minimum: int) -> int: 
    """Truncate arguments below a threshold."""
    return caller(minimum).map([less, constantly]) | iffy.expand

truncate_below(0).lmap([-1, 2, 4]) == [0, 2, 4]
```

# Requirements
This package is currently tested for Python 3.6.

# Installation
This project is not currently packaged and so must be installed manually.

Clone the project with the following command:
```
git clone https://github.com/jacksmith15/fungebra.git
```

Package requirements may be installed via `pip install -r requirements.txt`. Use of a [virtualenv](https://virtualenv.pypa.io/) is recommended.

# Development
1. Clone the repository: `git clone git@github.com:jacksmith15/fungebra.git && cd fungebra`
2. Install the requirements: `pip install -r requirements.txt -r requirements-test.txt`
3. Run `pre-commit install`
4. Run the tests: `bash run_test.sh -c -a`

This project uses the following QA tools:
- [PyTest](https://docs.pytest.org/en/latest/) - for running unit tests.
- [PyLint](https://www.pylint.org/) - for enforcing code style.
- [MyPy](http://mypy-lang.org/) - for static type checking.
- [Travis CI](https://travis-ci.org/) - for continuous integration.
- [Black](https://black.readthedocs.io/en/stable/) - for uniform code formatting.

# License
This project is distributed under the MIT license.
