import json, os


# load the configuration file with the backend specification
filedir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(filedir,"config.json"), "r") as infile:
    config = json.load(infile)


# import the functions from the specified backend
if config['backend'] == 'python':
    from .python_backend.matrix import *
    from .python_backend.nonlinearity import *
    from .python_backend.rand import *
elif config['backend'] == 'pytorch':
    from .pytorch_backend.matrix import *
    from .pytorch_backend.nonlinearity import *
    from .pytorch_backend.rand import *
else:
    raise ValueError(
    "Unknown backend {}".format(config['backend'])
    )


# ----- COMMON FUNCTIONALITY ----- #


def fold(func, a):
    """
    Combines the result of a function over iterable a.

    For example:

    '''
    from collections import namedtuple
    from operator import add

    coords = namedtuple("coordinates", ["x", "y"])

    a = coords(1,2)
    b = fold(add, a) # 3

    a = list(a)
    b = fold(add, a) # 3

    '''

    Args:
        func (callable): a function with two arguments
        a (iterable: e.g., list or named tuple)

    Returns:
        float

    """
    result = 0
    for x in a:
        result = func(result, x)
    return result

def accumulate(func, a):
    """
    Accumulates the result of a function over iterable a.

    For example:

    '''
    from collections import namedtuple

    def square(x):
        return x**2

    coords = namedtuple("coordinates", ["x", "y"])

    a = coords(1,2)
    b = accumulate(square, a) # 5

    a = list(a)
    b = accumulate(add, a) # 5

    '''

    Args:
        func (callable): a function with one argument
        a (iterable: e.g., list or named tuple)

    Returns:
        float

    """
    return sum(func(x) for x in a)

def apply(func, a):
    """
    Applies a function over iterable a, giving back an
    object of the same type as a. That is, b[i] = func(a[i]).

    For example:

    '''
    from collections import namedtuple
    from operator import mul
    from cytoolz import partial

    # create a function to divide by 2
    halve = partial(mul, 0.5)

    coords = namedtuple("coordinates", ["x", "y"])

    a = coords(1,2)
    b = apply(halve, a) # coordinates(x=0.5, y=1.0)

    a = list(a)
    b = apply(halve, a) # [0.5,1.0]

    '''

    Args:
        func (callable): a function with a single argument
        a (iterable: e.g., list or named tuple)

    Returns:
        object of type(a)

    """
    lst = [func(x) for x in a]
    try:
        return type(a)(*lst)
    except TypeError:
        return type(a)(lst)

def apply_(func_, a):
    """
    Applies an in place function over iterable a.

    That is, a[i] = func(a[i]).

    For example:

    '''
    from collections import namedtuple
    import numpy as np
    import numexpr as ne

    # create an in place function to divide an array by 2
    def halve_(x: np.ndarray) -> None:
        ne.evaluate('0.5 * x', out=x)

    coords = namedtuple("coordinates", ["x", "y"])

    a = coords(np.ones(1), 2 * np.ones(1))
    apply_(halve_, a) # a = coordinates(x=np.array(0.5), y=np.array(1.0))

    a = list(a)
    apply_(halve_, a) # a = [np.array(0.25), np.array(0.5)]

    '''

    Args:
        func_ (callable): an in place function of a single argument
        a (iterable: e.g., list or named tuple)

    Returns:
        None

    """
    for x in a:
        func_(x)

def mapzip(func, a, b):
    """
    Applies a function over the zip of iterables a and b,
    giving back an object of the same type as a. That is,
    c[i] = func(a[i], b[i]).

    For example:

    ```
    from collections import namedtuple
    from operator import add

    coords = namedtuple("coordinates", ["x", "y"])

    a = coords(1,2)
    b = coords(2,3)

    c = mapzip(add, a, b) # coordinates(x=2, y=4)

    a = list(a)
    b = list(b)

    c = mapzip(add, a, b) # [2, 4]
    ```

    Args:
        func (callable): a function with two arguments
        a (iterable; e.g., list or namedtuple)
        b (iterable; e.g., list or namedtuple)

    Returns:
        object of type(a)

    """
    lst = [func(x[0], x[1]) for x in zip(a, b)]
    try:
        return type(a)(*lst)
    except TypeError:
        return type(a)(lst)

def mapzip_(func_, a, b):
    """
    Applies an in place function over the zip of iterables a and b,
    storing the result in a. That is,
    a[i] = func(a[i], b[i]).

    For example:

    ```
    from collections import namedtuple
    import numpy as np
    import numexpr as ne

    def add_(x: np.ndarray, y: np.ndarray) -> None:
        ne.evaluate('x + y', out=x)

    coords = namedtuple("coordinates", ["x", "y"])

    a = coords(np.array([1]), np.array([2]))
    b = coords(np.array([3]), np.array([4]))

    mapzip_(add_, a, b) # a = coordinates(x=4, y=6)

    a = list(a)
    b = list(b)

    mapzip_(add_, a, b) # a = [7, 10]
    ```

    Args:
        func (callable): an in place function with two arguments
        a (iterable; e.g., list or namedtuple)
        b (iterable; e.g., list or namedtuple)

    Returns:
        None

    """
    for i in range(len(a)):
        func_(a[i], b[i])
