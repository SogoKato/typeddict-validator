from typing import (
    Any,
    Literal,
    Type,
    TypeGuard,
    TypeVar,
    Union,
    get_args,
    get_origin,
    get_type_hints,
    is_typeddict,
)

try:
    from typing import NotRequired
except ImportError:
    from typing_extensions import NotRequired


T = TypeVar("T")


def _is_not_required(vt):
    """Check if a type annotation is NotRequired"""
    # Method 1: Direct origin check
    origin = get_origin(vt)
    if origin is NotRequired:
        return True
    
    # Method 2: Check __origin__ attribute directly
    if hasattr(vt, '__origin__') and vt.__origin__ is NotRequired:
        return True
    
    # Method 3: Check type representation (fallback for edge cases)
    type_str = str(vt)
    if type_str.startswith('typing.NotRequired[') or type_str.startswith('typing_extensions.NotRequired['):
        return True
    
    return False


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
        # Get optional keys from TypedDict metadata  
        optional_keys = getattr(t, '__optional_keys__', set())
        hints = get_type_hints(t, globalns=globals(), localns=locals())
        t.__annotations__.update(hints)
        for k, vt in t.__annotations__.items():
            # Check if this is a NotRequired field using both methods
            is_not_required_by_annotation = _is_not_required(vt)
            is_not_required_by_metadata = k in optional_keys
            is_not_required = is_not_required_by_annotation or is_not_required_by_metadata
            
            if k not in d.keys() and is_not_required:
                continue
            elif k not in d.keys():
                raise DictMissingKeyException(key=k)
            elif is_not_required_by_annotation:
                # Only extract inner type if we detected NotRequired in the annotation
                vt = get_args(vt)[0]

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
    elif origin_type_expected is Literal:
        if v not in get_args(expected):
            raise DictValueTypeMismatchException(key=k, expected=expected, actual=v)
    elif type(v) != expected:
        raise_()


def _raise_if_mismatch(k: str, v: Any, expected: Any, actual: Any):
    args = _get_args(expected)
    if Any in args:
        return
    if type(v) in args:
        return
    err_count = 0
    error = None
    type_mismatch_error = None
    for arg in args:
        try:
            _validate_value(k=k, v=v, expected=arg)
        except (DictValueTypeMismatchException, DictMissingKeyException) as e:
            err_count += 1
            if error is None:
                error = e
            # Prioritize DictValueTypeMismatchException over DictMissingKeyException
            if isinstance(e, DictValueTypeMismatchException):
                type_mismatch_error = e
    if get_origin(expected) is Union and err_count < len(args):
        # OK if at least one of args did not raise error.
        return
    elif error is None:
        # OK if any of args did not raise error.
        return
    # If we have a type mismatch error, prefer it over missing key errors
    if type_mismatch_error is not None:
        raise type_mismatch_error
    raise error


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
