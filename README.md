What if `__future__` was filled with all kinds of unwise things?

    pip install terrible-ideas

## Usage

    >>> from terrible_ideas import dict_sort
    >>> d = {3: 4, 1: 7, 9: 23}
    >>> d.sort()
    >>> d
    {1: 7, 3: 4, 9: 23}

By importing a feature, it is enabled automatically.

## List of features

- `dict_sort`: Adds a `.sort()` method to dicts.
- `iterable_int`: Makes ints iterable; `iter(8) == iter(range(8))`
- `spellcheck_classes`: Performs spellchecking on variable names within classes
- `float_slicing`: `"wat"[0.5:] == "vat"`
- `weak_typing`: Allows all kind of operations that normally lead to type
  errors, e.g. adding a string and a list

## Contributing

I'm happy with outside contributions, under the following conditions:

- The feature is sufficiently terrible
- It follows the existing code in style, formatting, and structure
- If it breaks IPython (merely by being imported), it is not enabled when
  `IS_IPYTHON`
