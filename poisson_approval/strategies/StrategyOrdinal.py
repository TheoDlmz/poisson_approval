from poisson_approval.strategies.StrategyThreshold import StrategyThreshold
from poisson_approval.utils.DictPrintingInOrderIgnoringZeros import DictPrintingInOrderIgnoringZeros


class StrategyOrdinal(StrategyThreshold):
    """
    A strategy profile for an ordinal preference profile.

    :param d_ranking_ballot: a dictionary whose keys are rankings and values are ballots, e.g. 'abc': 'ab'. A
        ballot can be '' if the behavior of these voters is not specified in the strategy.
    :param profile: an optional profile ("context" in which the strategy is used).

        >>> sigma = StrategyOrdinal({'abc': 'a', 'bac': 'ab', 'cab': 'c'})
        >>> sigma
        StrategyOrdinal({'abc': 'a', 'bac': 'ab', 'cab': 'c'})
        >>> print(type(sigma.d_ranking_ballot))
        <class 'poisson_approval.utils.DictPrintingInOrderIgnoringZeros.DictPrintingInOrderIgnoringZeros'>
        >>> print(sorted(sigma.d_ranking_ballot))
        ['abc', 'acb', 'bac', 'bca', 'cab', 'cba']
        >>> print(sigma)
        <abc: a, bac: ab, cab: c>
        >>> sigma.abc
        'a'
        >>> sigma.a_bc
        'a'
        >>> sigma.ab_c
        'a'
        >>> sigma.d_ranking_threshold['abc']
        1
    """

    def __init__(self, d_ranking_ballot=None, profile=None):
        # Populate the dictionary and check for typos in the input
        if d_ranking_ballot is None:
            d_ranking_ballot = dict()
        # Prepare the dictionary of thresholds
        d_ranking_threshold = DictPrintingInOrderIgnoringZeros()
        for ranking, ballot in d_ranking_ballot.items():
            if ballot == '':
                d_ranking_threshold[ranking] = None
            elif ballot == ranking[0]:
                d_ranking_threshold[ranking] = 1
            elif ballot in {ranking[:2], ranking[1::-1]}:
                d_ranking_threshold[ranking] = 0
            else:
                raise ValueError('Unknown strategy: ' + ballot)
        # Call parent class
        super().__init__(d_ranking_threshold=d_ranking_threshold, profile=profile)

    def __eq__(self, other):
        """Equality test.

            >>> sigma = StrategyOrdinal({'abc': 'a', 'bac': 'ab', 'cab': 'c'})
            >>> sigma == StrategyOrdinal({'abc': 'a', 'bac': 'ab', 'cab': 'c'})
            True
        """
        return isinstance(other, StrategyOrdinal) and self.d_ranking_ballot == other.d_ranking_ballot

    def __repr__(self):
        return 'StrategyOrdinal(%r)' % self.d_ranking_ballot

    def _repr_pretty_(self, p, cycle):
        # https://stackoverflow.com/questions/41453624/tell-ipython-to-use-an-objects-str-instead-of-repr-for-output
        p.text(str(self) if not cycle else '...')
