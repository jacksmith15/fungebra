# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog] and this project adheres to
[Semantic Versioning].

Types of changes are:
* **Security** in case of vulnerabilities.
* **Deprecated** for soon-to-be removed features.
* **Added** for new features.
* **Changed** for changes in existing functionality.
* **Removed** for now removed features.
* **Fixed** for any bug fixes.

## [Unreleased]
### Added
* `fungebra.Function`. Function decorator to allow use of expression
  syntax and method chaining.
* Expression syntax for `Function` callables:
  * `+` - function composition.
  * `|` - function piping/chaining.
  * `**` - right-associative function piping/chaining.
  * `<<` - left-handed partial application.
  * `>>` - right-handed partial application.
  * `-` - shortcut for `map`.
  * `<` - shortcut for `filter`.
  * `>` - shortcut for `reduce`.
* Methods for `Function` callables:
  * `collect` - collect arguments before psasing.
  * `expand` - unpack single argument before passing.
  * `compose(*others)` - return composition of this function with
    `others`.
  * `pipe(func)` - return function which passes output of this function
    to `func`
  * `partial(*args, **kwargs)` - left-handed partial application.
  * `rpartial(*args, **kwargs)` - right-handed partial application.
  * `map` - shortcut for `partial(map, self)`.
  * `lmap` - same as `map` but returns a `list`.
  * `filter([filter_func])` - pipe output of this function to filter,
    or create filter from self if no arguments passed.
  * `reduce([reduce_func])` - pipe output of this function to reducer,
    or create reducer from self if not arguments passed.
* Top-level helpers:
  * `identity` - shortcut for `Function(lambda _: _)`
  * `pipeline(*funcs)` - return a left-to-right pipeline from a series
    of functions.
  * `Args` - dataclass for arguments, used for passing mixed positional
    and keyword arguments through pipes or into partial applications.
* `fungebra.functions` modules containing a number of commonly useful
  `Function` callables.
* Project started :)

## [0.0.0]
Nothing here.

[Unreleased]: https://github.com/jacksmith15/fungebra/compare/initial..HEAD

[Keep a Changelog]: http://keepachangelog.com/en/1.0.0/
[Semantic Versioning]: http://semver.org/spec/v2.0.0.html
