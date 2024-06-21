from tsfresh.feature_extraction.data import (
    to_tsdata,
    LongTsFrameAdapter,
    WideTsFrameAdapter,
    TsDictAdapter,
    DaskTsAdapter,
)
from tsfresh.feature_dynamics_extraction.feature_dynamics_data import (
    IterableSplitTsData,
    ApplyableSplitTsData,
)
import pandas as pd
import dask.dataframe as dd
from tests.units.feature_extraction.test_data import DataAdapterTestCase
from tests.fixtures import DaskDataTestCase


class IterableSplitTsDataTestCase(
    DataAdapterTestCase
):  # TODO: Optimise this! Inheritance here makes the unit tests slower...
    """"""

    def test_iter_on_long_data(self):
        df_stacked = self.create_test_data_sample()
        data_stacked = LongTsFrameAdapter(df_stacked, "id", "kind", "val", "sort")
        (
            expected_windowed_tuples,
            window_length,
        ) = self.create_split_up_test_data_expected_tuples()
        split_ts_data = IterableSplitTsData(data_stacked, split_size=window_length)

        # Test equality of object's main members
        self.assertTrue(
            split_ts_data._split_size == window_length
            and split_ts_data.df_id_type == object
        )
        underlying_data_converted_to_tsdata = to_tsdata(split_ts_data._root_ts_data)
        expected_non_windowed_tuples = self.create_test_data_expected_tuples()
        self.assert_tsdata(
            underlying_data_converted_to_tsdata, expected_non_windowed_tuples
        )

        ##TODO test the dask df test case
        df_stacked = self.create

        # Test equality of each chunk...
        self.assert_tsdata(split_ts_data, expected_windowed_tuples)

    def test_iter_on_long_data_no_value_column(self):
        df_stacked = self.create_test_data_sample()
        data_stacked_no_val = LongTsFrameAdapter(df_stacked, "id", "kind", None, "sort")
        (
            expected_windowed_tuples,
            window_length,
        ) = self.create_split_up_test_data_expected_tuples()
        split_ts_data = IterableSplitTsData(
            data_stacked_no_val, split_size=window_length
        )

        # Test equality of object's main members
        self.assertTrue(
            split_ts_data._split_size == window_length
            and split_ts_data.df_id_type == object
        )
        underlying_data_converted_to_tsdata = to_tsdata(split_ts_data._root_ts_data)
        expected_non_windowed_tuples = self.create_test_data_expected_tuples()
        self.assert_tsdata(
            underlying_data_converted_to_tsdata, expected_non_windowed_tuples
        )

        # Test equality of each chunk...
        self.assert_tsdata(split_ts_data, expected_windowed_tuples)

    def test_iter_on_wide_data(self):
        df_wide = self.create_test_data_sample_wide()
        data_wide = WideTsFrameAdapter(df_wide, "id", "sort")
        (
            expected_windowed_tuples,
            window_length,
        ) = self.create_split_up_test_data_expected_tuples_wide()
        split_ts_data = IterableSplitTsData(data_wide, split_size=window_length)

        # Test equality of object's main members
        self.assertTrue(
            split_ts_data._split_size == window_length
            and split_ts_data.df_id_type == object
        )
        underlying_data_converted_to_tsdata = to_tsdata(split_ts_data._root_ts_data)
        expected_non_windowed_tuples = self.create_test_data_expected_tuples_wide()
        self.assert_tsdata(
            underlying_data_converted_to_tsdata, expected_non_windowed_tuples
        )

        # Test equality of each chunk...
        self.assert_tsdata(split_ts_data, expected_windowed_tuples)

    def test_iter_on_wide_data_no_sort_column(self):
        df_wide = self.create_test_data_sample_wide()
        del df_wide["sort"]
        data_wide_no_sort = WideTsFrameAdapter(df_wide, "id", None)

        (
            expected_windowed_tuples,
            window_length,
        ) = self.create_split_up_test_data_expected_tuples_wide()
        split_ts_data = IterableSplitTsData(data_wide_no_sort, split_size=window_length)

        # Test equality of object's main members
        self.assertTrue(
            split_ts_data._split_size == window_length
            and split_ts_data.df_id_type == object
        )
        underlying_data_converted_to_tsdata = to_tsdata(split_ts_data._root_ts_data)
        expected_non_windowed_tuples = self.create_test_data_expected_tuples_wide()
        self.assert_tsdata(
            underlying_data_converted_to_tsdata, expected_non_windowed_tuples
        )

        # Test equality of each chunk...
        self.assert_tsdata(split_ts_data, expected_windowed_tuples)

    def test_iter_on_dict(self):
        df_dict = {
            key: df for key, df in self.create_test_data_sample().groupby(["kind"])
        }
        data_dict = TsDictAdapter(df_dict, "id", "val", "sort")

        (
            expected_windowed_tuples,
            window_length,
        ) = self.create_split_up_test_data_expected_tuples()
        split_ts_data = IterableSplitTsData(data_dict, split_size=window_length)

        # Test equality of object's main members i.e each timeseries
        self.assertTrue(
            split_ts_data._split_size == window_length
            and split_ts_data.df_id_type == object
        )
        underlying_data_converted_to_tsdata = to_tsdata(split_ts_data._root_ts_data)
        expected_non_windowed_tuples = self.create_test_data_expected_tuples()
        self.assert_tsdata(
            underlying_data_converted_to_tsdata, expected_non_windowed_tuples
        )

        # Test equality of each chunk... i.e. each subwindow
        self.assert_tsdata(split_ts_data, expected_windowed_tuples)

    def test_too_large_split_size(self):

        window_length = (
            100000  # this length is too large given the size of the input data
        )

        test_data = to_tsdata(
            self.create_test_data_sample(), "id", "kind", "val", "sort"
        )

        self.assertRaises(ValueError, IterableSplitTsData, test_data, window_length)

    def test_negative_split_size(self):

        window_length = -20

        test_data = to_tsdata(
            self.create_test_data_sample(), "id", "kind", "val", "sort"
        )

        self.assertRaises(ValueError, IterableSplitTsData, test_data, window_length)

    def test_zero_split_size(self):

        window_length = 0  # this length is too large given the size of the input data

        test_data = to_tsdata(
            self.create_test_data_sample(), "id", "kind", "val", "sort"
        )

        self.assertRaises(ValueError, IterableSplitTsData, test_data, window_length)

    def test_fractional_split_size(self):

        window_length = (
            1.50  # does not make physical sense to have non integer window lengths
        )

        test_data = to_tsdata(
            self.create_test_data_sample(), "id", "kind", "val", "sort"
        )

        self.assertRaises(ValueError, IterableSplitTsData, test_data, window_length)

import dask.dataframe as ddf

class ApplyableSplitTsDataTestCase(DataAdapterTestCase):#TODO refactor
    """ """
    def _create_simple_test_sample_dask(self, chunksize=6):
        return ddf.from_pandas(self.create_test_data_sample(), chunksize=chunksize)

    ##TODO refactor maybe dont need the data dask testcase
    def assert_tsdata_dask(self, result, expected):

        # TODO: Fix this funciton to be
        # able to assert expected dask data == resultant dask data

        self.assertEqual(result.column_id, "id")

        def test_f(chunk):
            return pd.DataFrame(
                {"id": chunk[0], "variable": chunk[1], "value": chunk[2]}
            )

        return_f = result.apply(
            test_f, meta=(("id", "int"), ("variable", "int"), ("value", "int"))
        ).compute()

        pd.testing.assert_frame_equal(
            return_f.reset_index(drop=True),
            expected,
        )

    def test_apply_on_long_data_dask(self):

        dask_input_stacked  = self._create_simple_test_sample_dask() 
        ts_input = DaskTsAdapter(dask_input_stacked, "id", "kind", "val", "sort")

        (
            expected_windowed_tuples,
            window_length,
        ) = self.create_split_up_test_data_expected_tuples()

        # create expected tuples dataset and return
        ts_split_dask_data = ApplyableSplitTsData(ts_input, split_size=window_length)

        # Test equality of object's main members
        self.assertTrue(
            ts_split_dask_data._split_size == window_length
            and ts_split_dask_data.df_id_type == object
        )

        underlying_data_converted_to_tsdata = to_tsdata(ts_split_dask_data._root_ts_data)
        expected_non_windowed_tuples = self.create_test_data_expected_tuples()
        
        # This does not work FIXME - to assert quality of each chunk
        # self.assert_tsdata_dask(
        #       underlying_data_converted_to_tsdata, expected_non_windowed_tuples
        # )

        # # Test equality of each chunk...
        #self.assert_tsdata(ts_split_dask_data, expected_windowed_tuples)
        ##return True

    def test_iter_on_long_data_no_value_column_dask(self):

        dask_input_stacked  = self._create_simple_test_sample_dask()
        ts_input = DaskTsAdapter(dask_input_stacked, "id", "kind", None, "sort")

        (
            expected_windowed_tuples,
            window_length,
        ) = self.create_split_up_test_data_expected_tuples()
        
        ts_split_dask_data_no_value = ApplyableSplitTsData(ts_input, split_size=window_length)

        # Test equality of object's main members
        self.assertTrue(
            ts_split_dask_data_no_value._split_size == window_length
            and ts_split_dask_data_no_value.df_id_type == object
        )

    def test_iter_on_wide_data_dask(self):
        #TODO
        df_wide_dask = self.create_test_data_sample_wide()
        dask_data_wide = DaskTsAdapter(df_wide_dask, "id", "kind", "val", "sort").pivot()
        #WideTsFrameAdapter(df_wide, "id", "sort")
        
        (
            expected_windowed_tuples,
            window_length,
        ) = self.create_split_up_test_data_expected_tuples_wide()
        split_ts_data_wide_dask = ApplyableSplitTsData(dask_data_wide, split_size=window_length)

        # Test equality of object's main members
        self.assertTrue(
            split_ts_data_wide_dask._split_size == window_length
            and split_ts_data_wide_dask.df_id_type == object
        )
        pass

    def test_iter_on_wide_data_no_sort_column_dask(self):
        pass

    def test_iter_on_dict_dask(self):
        pass

    def test_too_large_split_size_dask(self):
        pass

    def test_negative_split_size_dask(self):
        pass

    def test_zero_split_size_dask(self):
        pass

    def test_fractional_split_size_dask(self):
        pass

#TODO remove
ApplyableSplitTsDataTestCase().test_apply_on_long_data_dask()