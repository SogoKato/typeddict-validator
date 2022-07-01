from typing import (
    Any,
    Type,
    TypeGuard,
    TypeVar,
    Union,
    get_args,
    get_origin,
    is_typeddict,
)


T = TypeVar("T")


def validate_typeddict(
    d: dict[str, Any], t: Type[T], *, silent: bool = False
) -> TypeGuard[T]:
    """Recursively validates whether the dict object matches given TypedDict.

    This supports generic types and Union (including Optional).

    Args:
        d (dict[str, Any]): a dict object to be validated.
        t (Type[TypedDict]): a type object of TypedDict.
        silent (bool): will return False instead of raising DictMissingKeyException or DictValueTypeMismatchException when True.

    Returns:
        bool: a TypeGuard that annotates the dict obeject matches given TypedDict.

    Raises:
        DictMissingKeyException: raised when the dict object is missing any key defined in given TypedDict.
        DictValueTypeMismatchException: raised when any value of the dict object does not match definition of given TypedDict.
        ValueError: raised when argument t is not a type object of TypedDict.
    """
    if not is_typeddict(t):
        raise ValueError("t must be a type object of TypedDict.")
    try:
        for k, vt in t.__annotations__.items():
            if k not in d.keys():
                raise DictMissingKeyException(key=k)
            _validate_value(k=k, v=d[k], expected=vt)
    except (DictMissingKeyException, DictValueTypeMismatchException) as e:
        if silent:
            return False
        else:
            raise e
    return True


def _get_args(tp: Any):
    args = get_args(tp)
    for arg in args:
        if get_origin(arg) is Union:
            return set(args + get_args(arg))
    return set(args)


def _validate_value(k: str, v: Any, expected: Any):
    def raise_():
        raise DictValueTypeMismatchException(key=k, expected=expected, actual=type(v))

    origin_type_expected = get_origin(expected)
    if origin_type_expected is Union:
        _raise_if_mismatch(k=k, v=v, expected=expected, actual=v)
    elif origin_type_expected == list:
        if not isinstance(v, list):
            raise_()
        for v_ in v:
            _raise_if_mismatch(k=k, v=v_, expected=expected, actual=v)
    elif origin_type_expected == dict:
        if not isinstance(v, dict):
            raise_()
        for v_ in v.values():
            _raise_if_mismatch(k=k, v=v_, expected=expected, actual=v)
    elif is_typeddict(expected):
        validate_typeddict(v, expected)
    elif type(v) != expected:
        raise_()


def _raise_if_mismatch(k: str, v: Any, expected: Any, actual: Any):
    args = _get_args(expected)
    if Any in args:
        return
    if type(v) in args:
        return
    err_count = 0
    for arg in args:
        try:
            _validate_value(k=k, v=v, expected=arg)
        except DictValueTypeMismatchException:
            err_count += 1
    if err_count < len(args):
        # OK if any of args did not raise error.
        return
    raise DictValueTypeMismatchException(key=k, expected=expected, actual=actual)


class DictMissingKeyException(Exception):
    """Indicates the dict object is missing any key defined in given TypedDict.

    Attributes:
        key (str): the name of missing key.
    """

    key: str

    def __init__(self, key: str) -> None:
        self.key = key


class DictValueTypeMismatchException(Exception):
    """Indicates any value of the dict object does not match definition of given TypedDict.

    Attributes:
        key (str): the name of key that its value does not match definition.
        expected (Type): the type of value of key defined in TypedDict.
        expected_type_name (str): the name(s) of type(s) of expected. It will be multiple when expected is Union or Optional.
        actual (Type): the type of value of key in dict.
        actual_type_name (str): the name of type of actual.
    """

    key: str
    expected: Type
    expected_type_name: str
    actual: Type
    actual_type_name: str

    def __init__(self, key: str, expected: Type, actual: Type) -> None:
        self.key = key
        self.expected = expected
        self.actual = actual
        self.expected_type_name = (
            expected.__name__
            if expected.__class__.__name__ == "type"
            else expected.__class__.__name__
        )
        if expected == Union:
            self.expected_type_name = "one of " + ", ".join(
                [t.__class__.__name__ for t in expected.__args__]
            )
        self.actual_type_name = (
            actual.__name__
            if actual.__class__.__name__ == "type"
            else actual.__class__.__name__
        )
