"""Top-level package for Poisson Approval."""

__author__ = """François Durand"""
__email__ = 'fradurand@gmail.com'
__version__ = '0.26.0'


# Utils
from poisson_approval.utils.computation_engine import computation_engine
from poisson_approval.utils.ComputationEngine import ComputationEngine
from poisson_approval.utils.ComputationEngineNumeric import ComputationEngineNumeric
from poisson_approval.utils.ComputationEngineSymbolic import ComputationEngineSymbolic
from poisson_approval.utils.DictPrintingInOrder import DictPrintingInOrder
from poisson_approval.utils.DictPrintingInOrderIgnoringNone import DictPrintingInOrderIgnoringNone
from poisson_approval.utils.DictPrintingInOrderIgnoringZeros import DictPrintingInOrderIgnoringZeros
from poisson_approval.utils.SetPrintingInOrder import SetPrintingInOrder
from poisson_approval.utils.Util import initialize_random_seeds, rand_simplex, rand_integers_fixed_sum, \
    rand_simplex_grid, probability, image_distribution, isnan, isposinf, isneginf, give_figure, to_callable, \
    product_dict, candidates_to_d_candidate_probability, candidates_to_probabilities, array_to_d_candidate_value, \
    d_candidate_value_to_array, one_over_t, one_over_sqrt_t, one_over_log_t_plus_one, \
    one_over_log_log_t_plus_fourteen, my_division, iterator_integers_fixed_sum, iterate_simplex_grid
from poisson_approval.utils.UtilBallots import ballot_one, ballot_two, ballot_one_two, ballot_one_three, \
    ballot_high_u, ballot_low_u, allowed_ballots
from poisson_approval.utils.UtilCache import cached_property, DeleteCacheMixin, property_deleting_cache
from poisson_approval.utils.UtilMasks import masks_area_naive, masks_area, masks_distribution_naive, \
    masks_distribution, winners_distribution, random_mask, random_masks
from poisson_approval.utils.UtilPreferences import is_hater, is_lover, is_weak_order, sort_weak_order

# Constants
from poisson_approval.constants.constants import *
from poisson_approval.constants.EquilibriumStatus import EquilibriumStatus
from poisson_approval.constants.Focus import Focus

# Simple containers
from poisson_approval.containers.Winners import Winners
from poisson_approval.containers.Scores import Scores
from poisson_approval.containers.AnalyzedStrategies import AnalyzedStrategies

# Events
from poisson_approval.events.Asymptotic import Asymptotic
from poisson_approval.events.Event import Event
from poisson_approval.events.EventDuo import EventDuo
from poisson_approval.events.EventPivotStrict import EventPivotStrict
from poisson_approval.events.EventPivotTij import EventPivotTij
from poisson_approval.events.EventPivotTjk import EventPivotTjk
from poisson_approval.events.EventPivotWeak import EventPivotWeak
from poisson_approval.events.EventTrio import EventTrio
from poisson_approval.events.EventTrio1t import EventTrio1t
from poisson_approval.events.EventTrio2t import EventTrio2t

# Best response
from poisson_approval.best_response.BestResponse import BestResponse
from poisson_approval.best_response.BestResponseAntiPlurality import BestResponseAntiPlurality
from poisson_approval.best_response.BestResponseApproval import BestResponseApproval
from poisson_approval.best_response.BestResponsePlurality import BestResponsePlurality

# Tau-vector
from poisson_approval.tau_vector.TauVector import TauVector

# Strategies
from poisson_approval.strategies.Strategy import Strategy
from poisson_approval.strategies.StrategyTwelve import StrategyTwelve
from poisson_approval.strategies.StrategyThreshold import StrategyThreshold
from poisson_approval.strategies.StrategyOrdinal import StrategyOrdinal

# Profiles
from poisson_approval.profiles.Profile import Profile
from poisson_approval.profiles.ProfileDiscrete import ProfileDiscrete
from poisson_approval.profiles.ProfileNoisyDiscrete import ProfileNoisyDiscrete
from poisson_approval.profiles.ProfileOrdinal import ProfileOrdinal
from poisson_approval.profiles.ProfileCardinal import ProfileCardinal
from poisson_approval.profiles.ProfileCardinalContinuous import ProfileCardinalContinuous
from poisson_approval.profiles.ProfileTwelve import ProfileTwelve
from poisson_approval.profiles.ProfileHistogram import ProfileHistogram

# Iterables
from poisson_approval.iterables.IterableProfileDiscreteGrid import IterableProfileDiscreteGrid
from poisson_approval.iterables.IterableProfileHistogramGrid import IterableProfileHistogramGrid
from poisson_approval.iterables.IterableProfileNoisyDiscreteGrid import IterableProfileNoisyDiscreteGrid
from poisson_approval.iterables.IterableProfileOrdinalGrid import IterableProfileOrdinalGrid
from poisson_approval.iterables.IterableProfileTwelveGrid import IterableProfileTwelveGrid
from poisson_approval.iterables.IterableSimplexGrid import IterableSimplexGrid
from poisson_approval.iterables.IterableStrategyOrdinal import IterableStrategyOrdinal
from poisson_approval.iterables.IterableStrategyThresholdGrid import IterableStrategyThresholdGrid
from poisson_approval.iterables.IterableStrategyTwelve import IterableStrategyTwelve
from poisson_approval.iterables.IterableTauVectorGrid import IterableTauVectorGrid

# Random factories
from poisson_approval.random_factories.RandConditional import RandConditional
from poisson_approval.random_factories.RandProfileDiscreteGridUniform import RandProfileDiscreteGridUniform
from poisson_approval.random_factories.RandProfileDiscreteUniform import RandProfileDiscreteUniform
from poisson_approval.random_factories.RandProfileHistogramGridUniform import RandProfileHistogramGridUniform
from poisson_approval.random_factories.RandProfileHistogramUniform import RandProfileHistogramUniform
from poisson_approval.random_factories.RandProfileNoisyDiscreteGridUniform import RandProfileNoisyDiscreteGridUniform
from poisson_approval.random_factories.RandProfileNoisyDiscreteUniform import RandProfileNoisyDiscreteUniform
from poisson_approval.random_factories.RandProfileOrdinalGridUniform import RandProfileOrdinalGridUniform
from poisson_approval.random_factories.RandProfileOrdinalUniform import RandProfileOrdinalUniform
from poisson_approval.random_factories.RandProfileTwelveGridUniform import RandProfileTwelveGridUniform
from poisson_approval.random_factories.RandProfileTwelveUniform import RandProfileTwelveUniform
from poisson_approval.random_factories.RandSimplexGridUniform import RandSimplexGridUniform
from poisson_approval.random_factories.RandSimplexUniform import RandSimplexUniform
from poisson_approval.random_factories.RandStrategyOrdinalUniform import RandStrategyOrdinalUniform
from poisson_approval.random_factories.RandStrategyThresholdGridUniform import RandStrategyThresholdGridUniform
from poisson_approval.random_factories.RandStrategyThresholdUniform import RandStrategyThresholdUniform
from poisson_approval.random_factories.RandStrategyTwelveUniform import RandStrategyTwelveUniform
from poisson_approval.random_factories.RandTauVectorGridUniform import RandTauVectorGridUniform
from poisson_approval.random_factories.RandTauVectorUniform import RandTauVectorUniform

# Meta-analysis
from poisson_approval.meta_analysis.NiceStatsProfileOrdinal import NiceStatsProfileOrdinal
from poisson_approval.meta_analysis.binary_plots import BinaryAxesSubplotPoisson, binary_figure
from poisson_approval.meta_analysis.binary_shortcuts import binary_plot_n_equilibria, \
    binary_plot_winners_at_equilibrium, binary_plot_winning_frequencies, binary_plot_convergence, \
    XyyToProfile
from poisson_approval.meta_analysis.ternary_plots import TernaryAxesSubplotPoisson, ternary_figure
from poisson_approval.meta_analysis.ternary_shortcuts import ternary_plot_n_equilibria, \
    ternary_plot_winners_at_equilibrium, ternary_plot_winning_frequencies, ternary_plot_convergence, \
    SimplexToProfile
