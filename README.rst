typeddict-validator
===================

Validates Python's TypedDict

`日本語の説明はこちら / Description in
Japanese <https://qiita.com/SogoK/items/a29b339e7c4b6c7b8f17>`__

About
-----

This is a utility to validate a dict object using TypedDict. It
recursively checks whether the dict has necessary keys and the values
has appropriate type. It will be useful when you deserialize the json or
yaml data, such as an API request or any file.

Currently supported types are generic types and Union (including
Optional).

Requirements
------------

-  Python 3.10 or higher

Installation
------------

`https://pypi.org/project/typeddict-validator/ <https://pypi.org/project/typeddict-validator/>`__

.. code:: sh

   pip install typeddict-validator

Usage
-----

.. code:: python

   >>> from typing import TypedDict
   >>> from typeddict_validator import validate_typeddict
   >>>
   >>> PersonDict = TypedDict("PersonDict", {"name": str, "age": int, "interests": list[str]})
   >>>
   >>> person = {"name": "Taro Yamada", "age": 30, "interests": ["programming", "painting"]}
   >>>
   >>> if validate_typeddict(person, PersonDict):
   ...     print("It's a PersonDict!")

::

   It's a PersonDict!

By default, it will raise an error when the dict object does not match.

.. code:: python

   >>> robot = {"name": "Doraemon"}
   >>>
   >>> if validate_typeddict(robot, PersonDict):
   ...     print("It's a PersonDict!")

::

   Traceback (most recent call last):
     File "<stdin>", line 1, in <module>
     File "/app/typeddict_validator/validate.py", line 37, in validate_typeddict
       raise DictMissingKeyException(key=k)
   typeddict_validator.validate.DictMissingKeyException

You can use ``silent=True`` option not to raise an error.

.. code:: python

   >>> if not validate_typeddict(robot, PersonDict, silent=True):
   ...     print("It's not a PersonDict!!")

::

   It's not a PersonDict!!

See
`typeddict_validator/validate_test.py <typeddict_validator/validate_test.py>`__
for more examples.

Tests
-----

.. code:: sh

   docker run --mount source=$(pwd),target=/app,type=bind python:latest python3 -m unittest -v /app/typeddict_validator/validate_test.py
