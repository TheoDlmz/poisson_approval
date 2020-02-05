import numpy as np
from fractions import Fraction
from math import isclose
from poisson_approval.best_response.BestResponse import BestResponse
from poisson_approval.constants.constants import *
from poisson_approval.utils.Util import isnan, ballot_one, ballot_one_two
from poisson_approval.utils.UtilCache import cached_property


class BestResponseApproval(BestResponse):
    """Best response for a given ordinal type of voter in Approval voting.

    The main objective of this class is to compute :attr:`threshold_utility`.

    It also provides the string :attr:`justification`, indicating which sub-algorithm was used. Nowadays, possible
    values are ``'Asymptotic method'``, ``'Simplified asymptotic method'``, ``'Easy vs difficult pivot'``,
    ``'Difficult vs easy pivot'``, ``'Offset method'``, ``'Offset method with trio approximation correction'``.

    Parameters
    ----------
    Cf. :class:`BestResponse`.

    Attributes
    ----------
    Cf. :class:`BestResponse`
    """

    ASYMPTOTIC = 'Asymptotic method'
    ASYMPTOTIC_SIMPLIFIED = 'Simplified asymptotic method'
    EASY_VS_DIFFICULT = 'Easy vs difficult pivot'
    DIFFICULT_VS_EASY = 'Difficult vs easy pivot'
    OFFSET_METHOD = 'Offset method'
    OFFSET_METHOD_WITH_TRIO_APPROXIMATION_CORRECTION = 'Offset method with trio approximation correction'

    # =======
    # Results
    # =======

    @cached_property
    def results_asymptotic_method(self):
        """tuple (threshold_utility, justification) : Results according to the asymptotic method. Cf.
        :attr:`threshold_utility` and :attr:`justification`. The threshold utility may be NaN, because this method is
        not always sufficient.
        """
        threshold_utility = ((
            self.pivot_tij.asymptotic * Fraction(1, 2)
            + self.trio_1t.asymptotic * Fraction(1, 3) + self.trio_2t.asymptotic * Fraction(1, 6)
        ) / (
            self.pivot_tij.asymptotic * Fraction(1, 2) + self.pivot_tjk.asymptotic * Fraction(1, 2)
            + self.trio_1t.asymptotic * Fraction(2, 3) + self.trio_2t.asymptotic * Fraction(1, 3)
        )).limit
        justification = self.ASYMPTOTIC
        return threshold_utility, justification

    @cached_property
    def results_limit_pivot_theorem(self):
        """tuple (threshold_utility, justification) : Results according to the limit pivot theorem.
        Cf. :attr:`threshold_utility` and :attr:`justification`. If the tau-vector has two consecutive zeros, the
        theorem does not apply and this method returns ``nan, ''``.
        """
        if self.tau.has_two_consecutive_zeros:
            return np.nan, ''

        def multiply(tau_something, phi_something):
            return 0 if tau_something == 0 else tau_something * phi_something

        # Pivot ij
        # --------
        score_ij_in_duo_ij = (multiply(self.tau_i, self.duo_ij.phi[self.i])
                              + multiply(self.tau_ij, self.duo_ij.phi[self.ij])
                              + multiply(self.tau_ik, self.duo_ij.phi[self.ik]))
        score_k_in_duo_ij = (multiply(self.tau_k, self.duo_ij.phi[self.k])
                             + multiply(self.tau_ik, self.duo_ij.phi[self.ik])
                             + multiply(self.tau_jk, self.duo_ij.phi[self.jk]))
        pivot_ij_easy = score_ij_in_duo_ij > score_k_in_duo_ij
        pivot_ij_tight = isclose(score_ij_in_duo_ij, score_k_in_duo_ij)
        pivot_ij_easy_or_tight = pivot_ij_easy or pivot_ij_tight
        # Pivot jk
        # --------
        score_jk_in_duo_jk = (multiply(self.tau_j, self.duo_jk.phi[self.j])
                              + multiply(self.tau_ij, self.duo_jk.phi[self.ij])
                              + multiply(self.tau_jk, self.duo_jk.phi[self.jk]))
        score_i_in_duo_jk = (multiply(self.tau_i, self.duo_jk.phi[self.i])
                             + multiply(self.tau_ij, self.duo_jk.phi[self.ij])
                             + multiply(self.tau_ik, self.duo_jk.phi[self.ik]))
        pivot_jk_easy = score_jk_in_duo_jk > score_i_in_duo_jk
        pivot_jk_tight = isclose(score_jk_in_duo_jk, score_i_in_duo_jk)
        pivot_jk_easy_or_tight = pivot_jk_easy or pivot_jk_tight
        # Case distinction of the theorem
        # -------------------------------
        if pivot_ij_easy_or_tight and pivot_jk_easy_or_tight:
            # Both pivots are easy => We can forget the trios.
            threshold_utility = ((
                self.pivot_tij.asymptotic * Fraction(1, 2)
            ) / (
                self.pivot_tij.asymptotic * Fraction(1, 2) + self.pivot_tjk.asymptotic * Fraction(1, 2)
            )).limit
            justification = self.ASYMPTOTIC_SIMPLIFIED
        elif pivot_ij_easy_or_tight:
            # ... but pivot jk is difficult.
            threshold_utility = 1
            justification = self.EASY_VS_DIFFICULT
        elif pivot_jk_easy_or_tight:
            # ... but pivot ij is difficult.
            threshold_utility = 0
            justification = self.DIFFICULT_VS_EASY
        else:
            # Both pivots are difficult => offset method.
            # Due to approximations in trio event, psi_k and psi_i may exceptionally be greater than 1 (whereas
            # in difficult pivots, we know that they must be strictly lower than 1). In that case, the formulas
            # for the offset method will fail, so we must be cautious.
            psi_k_greater_but_close_to_one = False
            if self.trio.psi[self.k] >= 1:
                if isclose(self.trio.psi[self.k], 1, rel_tol=1e-1):
                    psi_k_greater_but_close_to_one = True
                else:  # pragma: no cover
                    raise AssertionError('Unexpected: self.trio.psi[self.k] = %s > 1' % self.trio.psi[self.k])
            psi_i_greater_but_close_to_one = False
            if self.trio.psi[self.i] >= 1:
                if isclose(self.trio.psi[self.i], 1, rel_tol=1e-1):
                    psi_i_greater_but_close_to_one = True
                else:  # pragma: no cover
                    raise AssertionError('Unexpected: self.trio.psi[self.i] = %s > 1' % self.trio.psi[self.i])
            if psi_i_greater_but_close_to_one and psi_k_greater_but_close_to_one:  # pragma: no cover
                raise AssertionError('Unexpected: both psi_i and psi_k are greater and close to 1.')
            elif psi_k_greater_but_close_to_one:
                # pij ~= inf, pjk < inf ==> u = 1
                threshold_utility = 1
                justification = self.OFFSET_METHOD_WITH_TRIO_APPROXIMATION_CORRECTION
            elif psi_i_greater_but_close_to_one:
                # pij < inf, pjk ~= inf ==> u = 0
                threshold_utility = 0
                justification = self.OFFSET_METHOD_WITH_TRIO_APPROXIMATION_CORRECTION
            else:
                # General case of the offset method (at last!)
                pij = (1 + self.trio.psi[self.ik]) / (1 - self.trio.psi[self.k])
                pjk = (1 + self.trio.psi[self.j]) * self.trio.psi[self.i] ** 2 / (1 - self.trio.psi[self.i])
                p1t = self.trio.psi[self.i]
                p2t = self.trio.psi[self.ij]
                threshold_utility = (pij / 2 + p1t / 3 + p2t / 6) / (pij / 2 + pjk / 2 + p1t * 2 / 3 + p2t / 3)
                justification = self.OFFSET_METHOD
        return threshold_utility, justification

    @cached_property
    def results(self):
        """tuple (threshold_utility, justification) : Cf. :attr:`threshold_utility` and :attr:`justification`.
        These results use:

        * :meth:`results_asymptotic_method` if there are two consecutive zeros in the "compass diagram" of the
          tau-vector,
        * :meth:`results_limit_pivot_theorem` otherwise.
        """
        if self.tau.has_two_consecutive_zeros:
            return self.results_asymptotic_method
        else:
            return self.results_limit_pivot_theorem

    @cached_property
    def ballot(self):
        """str : This can be a valid ballot (e.g. ``'a'`` or ``'ab'`` if `ranking` is ``'abc'``) or
        ``'utility-dependent'``.
        """
        if isnan(self.threshold_utility):
            raise ValueError('Unable to compute threshold utility')  # pragma: no cover
        elif isclose(self.threshold_utility, 1):
            return ballot_one(self.ranking)
        elif isclose(self.threshold_utility, 0, abs_tol=1E-9):
            return ballot_one_two(self.ranking)
        else:
            return UTILITY_DEPENDENT