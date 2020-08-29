"""
Tests sklearn Normalizer converter
"""
import unittest
import warnings

import numpy as np
import torch

from sklearn.impute import SimpleImputer

import hummingbird.ml


class TestSklearnSimpleImputer(unittest.TestCase):
    def _test_simple_imputer(self, model, data):

        data_tensor = torch.from_numpy(data)
        model.fit(data)

        torch_model = hummingbird.ml.convert(model, "torch")

        self.assertIsNotNone(torch_model)
        np.testing.assert_allclose(
            model.transform(data), torch_model.transform(data_tensor), rtol=1e-06, atol=1e-06,
        )

    def test_simple_imputer_float_inputs(self):
        model = SimpleImputer(strategy="mean", fill_value="nan")
        data = np.array([[1, 2], [np.nan, 3], [7, 6]], dtype=np.float32)

        self._test_simple_imputer(model, data)

    def test_simple_imputer_no_nan_inputs(self):
        model = SimpleImputer(missing_values=0, strategy="most_frequent")
        data = np.array([[1, 2], [1, 3], [7, 6]], dtype=np.float32)

        self._test_simple_imputer(model, data)


if __name__ == "__main__":
    unittest.main()
