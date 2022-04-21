# typeddict-validator
Validates Python's TypedDict

## Requirements

* Python 3.10 or higher

## About

This is a utility to validate a dict object using TypedDict. It recursively checks whether the dict has necessary keys and the values has appropriate type. It will be useful when you deserialize the json or yaml data, such as an API request or any file.

Currently supported types are generic types and Union (including Optional).

## Usage

```python
>>> from typing import TypedDict
>>> from validate import validate_typeddict
>>>
>>> PersonDict = TypedDict("PersonDict", {"name": str, "age": int, "interests": list[str]})
>>>
>>> person = {"name": "Taro Yamada", "age": 30, "interests": ["programming", "painting"]}
>>>
>>> if validate_typeddict(person, PersonDict):
...     print("It's PersonDict!")
```

```
It's PersonDict!
```

```python
>>> robot = {"name": "Doraemon"}
>>>
>>> if validate_typeddict(robot, PersonDict):
...     print("It's PersonDict!")
```

```
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/app/validate/validate.py", line 37, in validate_typeddict
    raise DictMissingKeyException(key=k)
validate.validate.DictMissingKeyException
```

See [validate/validate_test.py](validate/validate_test.py) for more examples.

## Tests

```sh
docker run --mount source=$(pwd),target=/app,type=bind python:latest python3 -m unittest -v /app/validate/validate_test.py
```
