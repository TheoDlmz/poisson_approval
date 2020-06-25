import math
import random
import itertools
import numpy as np
import sympy as sp
from fractions import Fraction
from decimal import Decimal
from poisson_approval.constants.constants import *
from poisson_approval.utils.DictPrintingInOrder import DictPrintingInOrder
from poisson_approval.utils.DictPrintingInOrderIgnoringZeros import DictPrintingInOrderIgnoringZeros


def initialize_random_seeds(n=0):
    """Initialize the random seeds.

    Parameters
    ----------
    n : int
        The desired random seed. Default: 0.
    """
    random.seed(n)
    np.random.seed(n)


def rand_simplex(d=6):
    """Draw a random point in the simplex.

    Parameters
    ----------
    d : int
        Number of coordinates. In other words, we consider the simplex of dimension `d - 1`.

    Returns
    -------
    numpy.ndarray
        A numpy array of length `d`, whose sum is 1.

    Examples
    --------
        >>> initialize_random_seeds()
        >>> rand_simplex(d=6)  # doctest: +SKIP
        array([0.4236548 , 0.12122838, 0.00393032, 0.05394987, 0.11242599, 0.28481063])
    """
    x = np.sort(np.random.rand(d - 1))
    return np.concatenate((x, [1])) - np.concatenate(([0], x))


def rand_integers_fixed_sum(d, fixed_sum):
    """Generate integers with a given sum (uniformly).

    Parameters
    ----------
    d : int
        The desired number of integers. In other words, we consider a simplex of dimension `d - 1`.
    fixed_sum : int
        The fixed sum.

    Returns
    -------
    numpy.ndarray
        A numpy array of `d` integers, whose sum is `fixed_sum`, and drawn uniformly.

    Examples
    --------
        >>> initialize_random_seeds()
        >>> rand_integers_fixed_sum(d=6, fixed_sum=100)
        array([ 2, 23, 34,  0, 22, 19])
    """
    n_separators = d - 1
    separators = np.concatenate((
        [-1],
        np.sort(np.random.choice(fixed_sum + n_separators, n_separators, replace=False)),
        [fixed_sum + n_separators]))
    return np.array([up - down - 1 for down, up in zip(separators[:-1], separators[1:])])


def rand_simplex_grid(d, denominator):
    """Draw a random point in the simplex, with rational coordinates of a given denominator

    Parameters
    ----------
    d : int
        Number of coordinates. In other words, we consider the simplex of dimension `d - 1`.
    denominator : int
        The coordinates will be fractions with this denominator.

    Returns
    -------
    numpy.ndarray
        A numpy array of length `d`, whose coordinates are fractions of the given denominator, and whose sum is 1.

    Examples
    --------
        >>> initialize_random_seeds()
        >>> rand_simplex_grid(d=3, denominator=100)
        array([Fraction(13, 50), Fraction(13, 20), Fraction(9, 100)], dtype=object)
    """
    return np.array([
        my_division(int(n), denominator)
        for n in rand_integers_fixed_sum(d=d, fixed_sum=denominator)])


def probability(factory, n_samples, test, conditional_on=None):
    """Probability that a random `something` meets some given test.

    Parameters
    ----------
    factory : callable or tuple
        This can be:

        * Either a callable that takes no input and that outputs a (random) `something`,
        * Or a tuple of such factories (cf. examples below).
    n_samples : int
        Number of samples.
    test : callable or tuple
        This can be:

        * Either a function that take as input(s) the output(s) of the factory(ies) and that returns a Boolean.
        * Or a tuple of such functions (cf. examples below).
    conditional_on : callable
        A function that take as input(s) the output(s) of the factory(ies) and that returns a Boolean.
        Default: always True.

    Returns
    -------
    float or tuple
        This can be:

        * Either the probability that the output(s) generated by `factory` meet(s) `test`, conditional on the fact
          that it meets `conditional_on`, based on a Monte-Carlo estimation of `n_samples` trials.
        * Either a tuple giving this probability for each member of `test`, when `test` is a tuple itself.

    Examples
    --------
    In this basic example with one factory, we estimate the probability that a random float between 0 and 1 is greater
    than .5, conditionally on being greater than .25:

        >>> initialize_random_seeds()
        >>> def rand_number():
        ...     return random.random()
        >>> probability(factory=rand_number, n_samples=1000,
        ...             test=lambda x: x > .5, conditional_on=lambda x: x > .25)
        0.661

    In this example with a tuple of factories, we estimate the probability that a random 2*2 matrix and a random vector
    of size 2, both with integer coefficients between -10 included and 11 excluded, have a dot product that is null,
    conditionally on not being null themselves:

        >>> initialize_random_seeds()
        >>> def rand_matrix():
        ...     return np.random.randint(-10, 11, (2, 2))
        >>> def rand_vector():
        ...     return np.random.randint(-10, 11, 2)
        >>> def test_dot_zero(matrix, vector):
        ...     return np.all(np.dot(matrix, vector) == 0)
        >>> def test_non_trivial(matrix, vector):
        ...     return not np.all(matrix == 0) and not np.all(vector == 0)
        >>> probability(factory=(rand_matrix, rand_vector), n_samples=10000,
        ...             test=test_dot_zero, conditional_on=test_non_trivial)
        0.0003

    In the following example, we estimate the probability that a random float between 0 and 1 is greater than .5,
    and the probability that it is greater than .75, conditionally on being greater than .25:

        >>> initialize_random_seeds()
        >>> def rand_number():
        ...     return random.random()
        >>> probability(factory=rand_number, n_samples=1000,
        ...             test=(lambda x: x > .5, lambda x: x > .75), conditional_on=lambda x: x > .25)
        (0.661, 0.332)

    When using a tuple of tests, the same samples are used to estimate each probability.
    """
    if not isinstance(factory, tuple):
        factory = (factory,)
    is_test_tuple = isinstance(test, tuple)
    if not is_test_tuple:
        test = (test,)
    l_test_success = [0 for the_test in test]
    i_samples = 0
    while i_samples < n_samples:
        somethings = [f() for f in factory]
        if conditional_on is None or conditional_on(*somethings):
            i_samples += 1
            for i_test, the_test in enumerate(test):
                if the_test(*somethings):
                    l_test_success[i_test] += 1
    l_test_rate = [successes / n_samples for successes in l_test_success]
    if is_test_tuple:
        return tuple(l_test_rate)
    else:
        return l_test_rate[0]


def image_distribution(factory, n_samples, f, conditional_on=None):
    """Distribution of ``f(something)`` for a random `something`.

    Parameters
    ----------
    factory : callable or tuple
        This can be:

        * Either a callable that takes no input and that outputs a (random) `something`,
        * Or a tuple of such factories (cf. examples below).
    n_samples : int
        Number of samples.
    f : callable
        A function that take as input(s) the output(s) of the factory(ies).
    conditional_on : callable
        A function that take as input(s) the output(s) of the factory(ies) and that returns a Boolean.
        Default: always True.

    Returns
    -------
    DictPrintingInOrder
        Keys: the obtained outputs for `f`. Values: the probability that `f(something)` has this output when `something`
        is generated by `factory`, conditional on the fact that it meets `conditional_on`,
        based on a Monte-Carlo estimation of `n_samples` trials.

    Examples
    --------
    In this basic example with one factory, we compute the distribution of `n` modulo 10, when `n` is drawn uniformly
    at random between 0 included and 100 excluded, conditionally on the fact that `n` is even:

        >>> initialize_random_seeds()
        >>> def rand_integer():
        ...     return np.random.randint(0, 100)
        >>> def modulo_10(n):
        ...     return n % 10
        >>> def is_even(n):
        ...     return n % 2 == 0
        >>> image_distribution(factory=rand_integer, n_samples=100, f=modulo_10, conditional_on=is_even)
        {0: 0.21, 2: 0.21, 4: 0.2, 6: 0.18, 8: 0.2}

    In this example with a tuple of factories, we compute the distribution of `a mod b`, when `a` is drawn uniformly
    at random between 0 included and 100 excluded, and `b` is drawn uniformly at random between 1 included and 11
    excluded:

        >>> initialize_random_seeds()
        >>> def rand_integer():
        ...     return np.random.randint(0, 100)
        >>> def rand_divider():
        ...     return np.random.randint(1, 11)
        >>> def modulo(a, b):
        ...     return a % b
        >>> image_distribution(factory=(rand_integer, rand_divider),
        ...                    n_samples=100, f=modulo)
        {0: 0.31, 1: 0.16, 2: 0.18, 3: 0.12, 4: 0.07, 5: 0.04, 6: 0.02, 7: 0.08, 9: 0.02}
    """
    if not isinstance(factory, tuple):
        factory = (factory,)
    d_result_occurrences = dict()
    i_samples = 0
    while i_samples < n_samples:
        somethings = [g() for g in factory]
        if conditional_on is None or conditional_on(*somethings):
            i_samples += 1
            result = f(*somethings)
            d_result_occurrences[result] = d_result_occurrences.get(result, 0) + 1
    return DictPrintingInOrder({result: occurrences / n_samples
                                for result, occurrences in d_result_occurrences.items()})


def _false_for_fraction(f):
    """Decorator to return False when the input is a Fraction (cf. usages below)."""
    def _f(x):
        if isinstance(x, Fraction):
            return False
        return f(x)
    _f.__doc__ = f.__doc__
    return _f


@_false_for_fraction
def isnan(x):
    """Is nan.

    Parameters
    ----------
    x : Number

    Returns
    -------
    bool
        True if `x` is nan.

    Notes
    -----
    This extends the usual numpy function ``isnan`` to fractions and sympy expressions.

    Examples
    --------
        >>> values = [sp.sqrt(3) - sp.sqrt(2), sp.nan,
        ...           sp.oo, - sp.oo,
        ...           sp.Rational(3, 5), Fraction(3, 5),
        ...           1, 0.42, np.inf, -np.inf, np.nan]
        >>> print([x for x in values if isnan(x)])
        [nan, nan]
    """
    if isinstance(x, sp.Expr):
        return x == sp.nan
    else:
        return np.isnan(x)


@_false_for_fraction
def isposinf(x):
    """Is positive infinity.

    Parameters
    ----------
    x : Number

    Returns
    -------
    bool
        True if `x` is positive infinity.

    Notes
    -----
    This extends the usual numpy function ``isposinf`` to fractions and sympy expressions.

    Examples
    --------
        >>> values = [sp.sqrt(3) - sp.sqrt(2), sp.nan,
        ...           sp.oo, - sp.oo,
        ...           sp.Rational(3, 5), Fraction(3, 5),
        ...           1, 0.42, np.inf, -np.inf, np.nan]
        >>> print([x for x in values if isposinf(x)])
        [oo, inf]
    """
    if isinstance(x, sp.Expr):
        return x == sp.oo
    else:
        return np.isposinf(x)


@_false_for_fraction
def isneginf(x):
    """Is negative infinity.

    Parameters
    ----------
    x : Number

    Returns
    -------
    bool
        True if `x` is negative infinity.

    Notes
    -----
    This extends the usual numpy function ``isneginf`` to fractions and sympy expressions.

    Examples
    --------
        >>> values = [sp.sqrt(3) - sp.sqrt(2), sp.nan,
        ...           sp.oo, - sp.oo,
        ...           sp.Rational(3, 5), Fraction(3, 5),
        ...           1, 0.42, np.inf, -np.inf, np.nan]
        >>> print([x for x in values if isneginf(x)])
        [-oo, -inf]
    """
    if isinstance(x, sp.Expr):
        return x == - sp.oo
    else:
        return np.isneginf(x)


def give_figure(n, singular, plural=None):
    """Combine a number with a unit, whose word can be singular or plural.

    Parameters
    ----------
    n : int
        The number.
    singular : str
        The singular word.
    plural : str
        The plural word. Default: the singular with a final 's'.

    Returns
    -------
    str
        The number and the word.

    Examples
    --------
        >>> give_figure(1, 'apple')
        '1 apple'
        >>> give_figure(2, 'apple')
        '2 apples'
        >>> give_figure(1, 'equilibrium', 'equilibria')
        '1 equilibrium'
        >>> give_figure(2, 'equilibrium', 'equilibria')
        '2 equilibria'
    """
    if n <= 1:
        return str(n) + ' ' + singular
    else:
        if plural is None:
            return str(n) + ' ' + singular + 's'
        else:
            return str(n) + ' ' + plural


def to_callable(o):
    """Convert to a callable.

    Parameters
    ----------
    o : object

    Returns
    -------
    callable
        The conversion of `o` to a callable.

    Examples
    --------
    If `o` is callable, then return `o`:

        >>> def square(x):
        ...     return x**2
        >>> my_function = to_callable(square)
        >>> my_function(4)
        16

    If `o` is not callable, then return a function ``*args, **kwargs -> o``:

        >>> x = 42
        >>> my_function = to_callable(x)
        >>> my_function('some_argument', keyword='some_value')
        42
    """
    if callable(o):
        return o
    else:
        def my_function(*args, **kwargs):
            return o
        return my_function


def product_dict(d_key_possible_values):
    """Iterable: product of dictionaries.

    Source: https://stackoverflow.com/questions/5228158/cartesian-product-of-a-dictionary-of-lists.

    Parameters
    ----------
    d_key_possible_values
        To each key, associate a list of possible values (cf. example below).

    Yields
    ------
    dict
        A dictionary that, to each key, associates one of its possible values. All elements of the Cartesian product
        are returned this way.

    Examples
    --------
        >>> d_key_possible_values = {'foo': [0, 1], 'bar': ['a', 'b', 'c']}
        >>> for d_key_value in product_dict(d_key_possible_values):
        ...     print(d_key_value)
        {'foo': 0, 'bar': 'a'}
        {'foo': 0, 'bar': 'b'}
        {'foo': 0, 'bar': 'c'}
        {'foo': 1, 'bar': 'a'}
        {'foo': 1, 'bar': 'b'}
        {'foo': 1, 'bar': 'c'}
    """
    keys = d_key_possible_values.keys()
    vals = d_key_possible_values.values()
    for instance in itertools.product(*vals):
        yield dict(zip(keys, instance))


def candidates_to_d_candidate_probability(candidates):
    """Convert a set of candidates to a dictionary of probabilities (random tie-break).

    Parameters
    ----------
    candidates : set
        A subset of ``{'a', 'b', 'c'}``. Typically: a set of winners.

    Returns
    -------
    DictPrintingInOrderIgnoringZeros
        Key: ``'a'``, ``'b'`` or ``'c'``. Value: the probability of this candidate winning with a uniformly random
        tie-break.

    Examples
    --------
        >>> winners = {'a', 'b'}
        >>> candidates_to_d_candidate_probability(winners)
        {'a': Fraction(1, 2), 'b': Fraction(1, 2)}
    """
    n_candidates = len(candidates)
    return DictPrintingInOrderIgnoringZeros({
        candidate: Fraction(1, n_candidates) if candidate in candidates else 0 for candidate in CANDIDATES})


def candidates_to_probabilities(candidates):
    """Convert a set of candidates to an array of probabilities (random tie-break).

    Parameters
    ----------
    candidates : set
        A subset of ``{'a', 'b', 'c'}``. Typically: a set of winners.

    Returns
    -------
    ndarray
        Array of size 3. For example, the first coefficient is the probability that candidate `a` win by a random
        tie-break.

    Examples
    --------
        >>> winners = {'a', 'b'}
        >>> candidates_to_probabilities(winners)
        array([Fraction(1, 2), Fraction(1, 2), 0], dtype=object)
    """
    n_candidates = len(candidates)
    return np.array([Fraction(1, n_candidates) if candidate in candidates else 0 for candidate in CANDIDATES])


def array_to_d_candidate_value(values):
    """Convert an array to a dictionary of candidates and values

    Parameters
    ----------
    values : ndarray
        An array of size 3.

    Returns
    -------
    DictPrintingInOrderIgnoringZeros
        The corresponding dictionary.

    Examples
    --------
        >>> values = [42, 51, 69]
        >>> array_to_d_candidate_value(values)
        {'a': 42, 'b': 51, 'c': 69}
    """
    return DictPrintingInOrderIgnoringZeros({candidate: value for candidate, value in zip(CANDIDATES, values)})


def d_candidate_value_to_array(d_candidate_value):
    """Convert a dictionary of candidates and values to an array

    Parameters
    ----------
    d_candidate_value : dict
        Key: ``'a'``, ``'b'`` or ``'c'``.

    Returns
    -------
    ndarray
        The corresponding array.

    Examples
    --------
        >>> d_candidate_value = {'a': 42, 'b': 51, 'c': 69}
        >>> d_candidate_value_to_array(d_candidate_value)
        array([42, 51, 69])
    """
    return np.array([d_candidate_value[candidate] for candidate in CANDIDATES])


def one_over_t(t):
    """Function `1 / t`.

    When used as an update ratio (cf. :meth:`ProfileCardinal.fictitious_play`), this amounts to computing the arithmetic
    mean.

    Parameters
    ----------
    t : Number

    Returns
    -------
    Number

    Examples
    --------
        >>> one_over_t(2)
        Fraction(1, 2)
    """
    return my_division(1, t)


def one_over_sqrt_t(t):
    """Function `1 / sqrt(t)`.

    This function is provided as an example of update ratio for :meth:`ProfileCardinal.fictitious_play`.

    Parameters
    ----------
    t : Number

    Returns
    -------
    Number

    Examples
    --------
        >>> one_over_sqrt_t(2)
        0.7071067811865475
    """
    return my_division(1, math.sqrt(t))


def one_over_log_t_plus_one(t):
    """Function `1 / log(t + 1)`.

    This function is provided as an example of update ratio for :meth:`ProfileCardinal.fictitious_play`. The constant
    1 in the denominator is the smallest integer such that `f(t = 2) < 1`.

    Parameters
    ----------
    t : Number

    Returns
    -------
    Number

    Examples
    --------
        >>> one_over_log_t_plus_one(2)
        0.9102392266268373
    """
    return my_division(1, math.log(t + 1))


def one_over_log_log_t_plus_fourteen(t):
    """Function `1 / log(log(t + 14))`.

    This function is provided as an example of update ratio for :meth:`ProfileCardinal.fictitious_play`. The constant
    14 in the denominator is the smallest integer such that `f(t = 1) < 1`.

    Parameters
    ----------
    t : Number

    Returns
    -------
    Number

    Examples
    --------
        >>> one_over_log_log_t_plus_fourteen(2)
        0.9806022744169713
    """
    return my_division(1, math.log(math.log(t + 14)))


def my_division(x, y):
    """
    Division of two numbers, trying to be exact if it is reasonable.

    Parameters
    ----------
    x : Number
    y : Number

    Returns
    -------
    Number
        The division of `x` by `y`.

    Examples
    --------
    Typical usages:

        >>> my_division(6, 2)
        3
        >>> my_division(5, 2)
        Fraction(5, 2)

    If `x` or `y` is a float, then the result is a float:

        >>> my_division(Fraction(5, 2), 0.1)
        25.0
        >>> my_division(0.1, Fraction(5, 2))
        0.04

    If `x` and `y` are integers, decimals, fractions or sympy expressions, then the result is symbolic:

        >>> my_division(2, Fraction(5, 2))
        Fraction(4, 5)
        >>> my_division(Decimal('0.1'), Fraction(5, 2))
        Fraction(1, 25)
        >>> my_division(sp.sqrt(3), 2)
        sqrt(3)/2

    Possible errors:

        >>> my_division(1, 0)
        Traceback (most recent call last):
        ZeroDivisionError: division by zero
        >>> my_division(1, 'foo')
        Traceback (most recent call last):
        TypeError: unsupported operand type(s) for /: 'Fraction' and 'str'

    """
    if y == 0:
        raise ZeroDivisionError('division by zero')
    if isinstance(x, float) or isinstance(y, float):
        return x / y
    if not isinstance(x, sp.Rational):
        try:
            x = Fraction(x)
        except (TypeError, ValueError):
            pass
    if not isinstance(y, sp.Rational):
        try:
            y = Fraction(y)
        except (TypeError, ValueError):
            pass
    result = x / y
    if isinstance(result, Fraction) and result.denominator == 1:
        return result.numerator
    else:
        return result


def iterator_integers_fixed_sum(d, fixed_sum):
    """Iterate over vectors of integers with a fixed sum.

    Parameters
    ----------
    d : int
        The desired number of integers. In other words, we consider a simplex of dimension `d - 1`.
    fixed_sum : int
        The fixed sum.

    Yields
    ------
    tuple
        Each tuple of `d` integers, whose sum is `fixed_sum`.

    Examples
    --------
        >>> for t in iterator_integers_fixed_sum(d=3, fixed_sum=2):
        ...     print(t)
        (2, 0, 0)
        (1, 1, 0)
        (1, 0, 1)
        (0, 2, 0)
        (0, 1, 1)
        (0, 0, 2)
    """
    if d == 1:
        yield fixed_sum,
    else:
        for i in range(fixed_sum, -1, -1):
            for r in iterator_integers_fixed_sum(d - 1, fixed_sum - i):
                yield (i, *r)


def iterate_simplex_grid(d, denominator):
    """Iterate over the points in the simplex, with rational coordinates of a given denominator

    Parameters
    ----------
    d : int
        Number of coordinates. In other words, we consider the simplex of dimension `d - 1`.
    denominator : int or iterable
        The coordinates will be fractions with this denominator. If an iterable is given, we consider each
        denominator given by the iterable.

    Returns
    -------
    tuple
        Each tuple of length `d`, whose coordinates are fractions of the given denominator, and whose sum is 1.

    Examples
    --------
        >>> for t in iterate_simplex_grid(d=3, denominator=range(1, 3)):
        ...     print(t)
        (1, 0, 0)
        (0, 1, 0)
        (0, 0, 1)
        (1, 0, 0)
        (Fraction(1, 2), Fraction(1, 2), 0)
        (Fraction(1, 2), 0, Fraction(1, 2))
        (0, 1, 0)
        (0, Fraction(1, 2), Fraction(1, 2))
        (0, 0, 1)
    """
    if isinstance(denominator, int):
        denominators = [denominator]
    else:
        denominators = denominator
    for current_denominator in denominators:
        for t in iterator_integers_fixed_sum(d, fixed_sum=current_denominator):
            yield tuple(my_division(x, current_denominator) for x in t)


def my_range(start, end, step):
    """Iterable `range` adapted for fractions.

    Parameters
    ----------
    start : Number
        Start value (included).
    end : Number
        End value (excluded).
    step : Number
        Increment of the counter.

    Examples
    --------
        >>> for x in my_range(0, 1, Fraction(1, 3)):
        ...     print(x)
        0
        1/3
        2/3

        >>> for x in my_range(1, 0, - Fraction(1, 3)):
        ...     print(x)
        1
        2/3
        1/3
    """
    val = start
    if step > 0:
        while val < end:
            yield val
            val += step
    else:
        while val > end:
            yield val
            val += step


def my_sign(x):
    """Sign.

    Parameters
    ----------
    x : Number

    Returns
    -------
    int
        Sign of x.

    Examples
    --------
        >>> my_sign(1.5)
        1
        >>> my_sign(0)
        0
        >>> my_sign(-4.2)
        -1
    """
    if x > 0:
        return 1
    elif x < 0:
        return -1
    else:
        return 0
