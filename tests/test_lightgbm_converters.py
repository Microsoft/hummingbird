"""
Tests LightGBM converters.
"""
import unittest
import warnings

import numpy as np
import torch
import lightgbm as lgb
from hummingbird import convert_sklearn


class TestLGBMConverter(unittest.TestCase):
    def _run_lgbm_classifier_converter(self, num_classes, extra_config={}):
        warnings.filterwarnings("ignore")
        for max_depth in [1, 3, 8, 10, 12, None]:
            model = lgb.LGBMClassifier(n_estimators=10, max_depth=max_depth)
            X = np.random.rand(100, 200)
            X = np.array(X, dtype=np.float32)
            y = np.random.randint(num_classes, size=100)

            model.fit(X, y)

            pytorch_model = convert_sklearn(model, extra_config=extra_config)
            self.assertTrue(pytorch_model is not None)
            np.testing.assert_allclose(
                model.predict_proba(X), pytorch_model(torch.from_numpy(X))[1].data.numpy(), rtol=1e-06, atol=1e-06
            )

    # binary classifier
    def test_lgbm_binary_classifier_converter(self):
        self._run_lgbm_classifier_converter(2)

    # gemm classifier
    def test_lgbm_gemm_classifier_converter(self):
        self._run_lgbm_classifier_converter(2, extra_config={"tree_implementation": "gemm"})

    # tree_trav classifier
    def test_lgbm_tree_trav_classifier_converter(self):
        self._run_lgbm_classifier_converter(2, extra_config={"tree_implementation": "tree_trav"})

    # perf_tree_trav classifier
    def test_lgbm_perf_tree_trav_classifier_converter(self):
        self._run_lgbm_classifier_converter(2, extra_config={"tree_implementation": "perf_tree_trav"})

    # multi classifier
    def test_lgbm_multi_classifier_converter(self):
        self._run_lgbm_classifier_converter(3)

    # gemm multi classifier
    def test_lgbm_gemm_multi_classifier_converter(self):
        self._run_lgbm_classifier_converter(3, extra_config={"tree_implementation": "gemm"})

    # tree_trav multi classifier
    def test_lgbm_tree_trav_multi_classifier_converter(self):
        self._run_lgbm_classifier_converter(3, extra_config={"tree_implementation": "tree_trav"})

    # perf_tree_trav multi classifier
    def test_lgbm_perf_tree_trav_multi_classifier_converter(self):
        self._run_lgbm_classifier_converter(3, extra_config={"tree_implementation": "perf_tree_trav"})

    def _run_lgbm_regressor_converter(self, num_classes, extra_config={}):
        warnings.filterwarnings("ignore")
        for max_depth in [1, 3, 8, 10, 12, None]:
            model = lgb.LGBMRegressor(n_estimators=10, max_depth=max_depth)
            X = np.random.rand(100, 200)
            X = np.array(X, dtype=np.float32)
            y = np.random.randint(num_classes, size=100)

            model.fit(X, y)
            pytorch_model = convert_sklearn(model, extra_config=extra_config)
            self.assertTrue(pytorch_model is not None)
            np.testing.assert_allclose(
                model.predict(X), pytorch_model(torch.from_numpy(X)).numpy().flatten(), rtol=1e-06, atol=1e-06
            )

    # regressor
    def test_lgbm_binary_regressor_converter(self):
        self._run_lgbm_regressor_converter(1000)

    # gemm regressor
    def test_lgbm_gemm_regressor_converter(self):
        self._run_lgbm_regressor_converter(1000, extra_config={"tree_implementation": "gemm"})

    # tree_trav regressor
    def test_lgbm_tree_trav_regressor_converter(self):
        self._run_lgbm_regressor_converter(1000, extra_config={"tree_implementation": "tree_trav"})

    # perf_tree_trav regressor
    def test_lgbm_perf_tree_trav_regressor_converter(self):
        self._run_lgbm_regressor_converter(1000, extra_config={"tree_implementation": "perf_tree_trav"})


if __name__ == "__main__":
    unittest.main()
