# -*- coding: utf-8 -*-

"""
This module contains the main function to interact with tsfresh: extract feature dynamics
"""

from collections.abc import Iterable
from dask import dataframe as dd
import pandas as pd

import sys


from tsfresh.feature_extraction.extraction import extract_features 
from tsfresh.feature_dynamics_extraction.feature_dynamics_data import IterableSplitTsData, ApplyableSplitTsData
from tsfresh.feature_extraction.data import to_tsdata
from tsfresh.feature_dynamics_extraction.feature_dynamics_utils import clean_feature_timeseries_name


def extract_feature_dynamics_wrapper(timeseries_container,
                            window_length_mapping = None,
                            feature_timeseries_fc_parameters=None, feature_timeseries_kind_to_fc_parameters=None,
                            feature_dynamics_fc_parameters=None, feature_dynamics_kind_to_fc_parameters=None,
                            column_id=None, column_sort=None, column_kind=None, column_value=None,
                            **kwargs):
    """
    Wrapper for multiple window lengths, useful for ts_kinds
    """


    # Split up the window lengths into groups (and also do the same for the feature time series)
    window_lengths = feature_timeseries_kind_to_fc_parameters.values()
    print(window_lengths)

    # paralellised computation of extracting feature dynamics for a given window length

    # Merge the features together

    # return

def extract_feature_dynamics(timeseries_container,
                             window_length = None,
                             feature_timeseries_fc_parameters=None, feature_timeseries_kind_to_fc_parameters=None,
                             feature_dynamics_fc_parameters=None, feature_dynamics_kind_to_fc_parameters=None,
                             column_id=None, column_sort=None, column_kind=None, column_value=None,
                             **kwargs):
    """
    Extract feature dynamics from a time series.
    This process involves calling `extract_features` on the original time series which produces a new set of columns - feature time series.
    Then for each of these features generated, they are again windowed and `extract_features` is called again producing a set
    of feature-dynamics or sub-features.

    The details of this function are explained in the following paper "Data Mining on Extremely Long Time Series"
    see at https://ieeexplore.ieee.org/document/9679945.

    :param timeseries_container: The pandas.DataFrame with the time series to compute the features for.
    :type timeseries_container: pandas.DataFrame or dask.DataFrame.

    :param window_length: The size of the window from which the first set of features is extracted.
    :type sub_feature_split: int

    :param feature_timeseries_fc_parameters: mapping from feature calculator names to parameters.
           These are applied to the first set of features generated.
    :type sub_default_fc_parameters: dict

    :param feature_timeseries_kind_to_fc_parameters: apping from kind names to objects of the same type as the ones for
            default_fc_parameters.These are applied to the first set of features generated.
    :type sub_kind_to_fc_parameters: dict

    :param feature_dynamics_fc_parameters: mapping from feature calculator names to parameters. Only those names
           which are keys in this dict will be calculated. See the class:`ComprehensiveFCParameters` for
           more information.
    :type default_fc_parameters: dict

    :param feature_dynamics_kind_to_fc_parameters: mapping from kind names to objects of the same type as the ones for
            default_fc_parameters. If you put a kind as a key here, the fc_parameters
            object (which is the value), will be used instead of the default_fc_parameters. This means that kinds, for
            which kind_of_fc_parameters doe not have any entries, will be ignored by the feature selection.
    :type kind_to_fc_parameters: dict

    :param column_id: The name of the id column to group by. Please see :ref:`data-formats-label`.
    :type column_id: str

    :param column_sort: The name of the sort column. Please see :ref:`data-formats-label`.
    :type column_sort: str

    :param column_kind: The name of the column keeping record on the kind of the value.
            Please see :ref:`data-formats-label`.
    :type column_kind: str

    :param column_value: The name for the column keeping the value itself. Please see :ref:`data-formats-label`.
    :type column_value: str

    :param kwargs: optional keyword arguments passed to `extract_features`.
    :type kwargs: dict

    :return: DataFrame of the extracted feature dynamics.
    :rtype: pandas.DataFrame or dask.DataFrame

    Examples
    ========

    >>> import pandas as pd
    >>> from tsfresh.examples.robot_execution_failures import download_robot_execution_failures, load_robot_execution_failures
    >>> from tsfresh.feature_extraction import extract_features, extract_features_on_sub_features

    >>> download_robot_execution_failures()
    >>> timeseries, y = load_robot_execution_failures()

    >>> extracted_sub_features = extract_features_on_sub_features(timeseries_container=timeseries,
                                                                  sub_feature_split=11,
                                                                  column_id="id",
                                                                  column_sort="time"))

    """

    # TODO: Add assert that ensures window length conforms with the size of the data
    # TODO: Add assert that timeseries is long enough for feature dynamics
    # TODO: New windowing scheme (dictionary)
    ts_data = to_tsdata(timeseries_container, column_id=column_id, column_sort=column_sort, column_kind=column_kind, column_value=column_value)
    if isinstance(ts_data, Iterable):
        split_ts_data = IterableSplitTsData(ts_data, window_length)
    else:
        split_ts_data = ApplyableSplitTsData(ts_data, window_length)

    feature_timeseries = extract_features(split_ts_data, default_fc_parameters=feature_timeseries_fc_parameters,
                                          kind_to_fc_parameters=feature_timeseries_kind_to_fc_parameters, **kwargs, pivot=False)

    column_kind = column_kind or "variable"
    column_id = column_id or "id"
    column_sort = column_sort or "sort"
    column_value = column_value or "value"

    # The feature names include many "_", which will confuse tsfresh where the sub feature name ends
    # and where the real feature name starts.
    # Also, we split up the index into the id and the sort
    # We need to do this separately for dask dataframes,
    # as the return type is not a list, but already a dataframe.
    # We also need to drop values that contain NaNs.
    if isinstance(feature_timeseries, dd.DataFrame):
        feature_timeseries = feature_timeseries.reset_index(drop=True)

        feature_timeseries[column_kind] = feature_timeseries[column_kind].apply(lambda col: clean_feature_timeseries_name(col, window_length), meta=(column_kind, object))

        feature_timeseries[column_sort] = feature_timeseries[column_id].apply(lambda x: x[1], meta=(column_id, "int64"))
        feature_timeseries[column_id] = feature_timeseries[column_id].apply(lambda x: x[0], meta=(column_id, ts_data.df_id_type))

        # Need to drop features for all windows which contain at least one NaN
        target_list = (feature_timeseries[feature_timeseries[column_value].isnull()][column_kind].unique().compute())
        feature_timeseries = feature_timeseries[~feature_timeseries[column_kind].isin(target_list)]
    else:
        feature_timeseries = pd.DataFrame(
            feature_timeseries, columns=[column_id, column_kind, column_value]
        )

        # Need to drop features for all windows which contain at least one NaN
        target_list = feature_timeseries[feature_timeseries[column_value].isnull()][column_kind].unique()

        feature_timeseries = feature_timeseries[~feature_timeseries[column_kind].isin(target_list)]
           
        feature_timeseries[column_kind] = feature_timeseries[column_kind].apply(lambda col: clean_feature_timeseries_name(col, window_length))
    
        feature_timeseries[column_sort] = feature_timeseries[column_id].apply(lambda x: x[1])

        feature_timeseries[column_id] = feature_timeseries[column_id].apply(lambda x: x[0])

    # Coerce time series values, which include boolean values, integers, and floats, which are 
    # currently stored as dtype: "object" into floats.
    feature_timeseries[column_value] = pd.to_numeric(feature_timeseries[column_value]) 

    feature_timeseries_ts_data = to_tsdata(feature_timeseries, column_id=column_id, column_sort=column_sort,column_kind=column_kind, column_value=column_value)
    
    X = extract_features(feature_timeseries_ts_data, column_id=column_id, column_sort=column_sort, column_kind=column_kind, column_value=column_value,
                         default_fc_parameters=feature_dynamics_fc_parameters, kind_to_fc_parameters=feature_dynamics_kind_to_fc_parameters,
                         **kwargs)    

    # Drop all feature dynamics that are associated with at least one NaN.
    if isinstance(feature_timeseries, dd.DataFrame):
        cols_to_keep = X.isna().compute().any() == False
        X = X.loc[:, cols_to_keep.tolist()]
    else:
        X = X.dropna(axis="columns", how="any")

    return X
