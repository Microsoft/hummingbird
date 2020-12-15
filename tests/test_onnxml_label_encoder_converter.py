"""
Tests onnxml LabelEncoder converter
"""
import unittest
import warnings

import numpy as np
from sklearn.preprocessing import LabelEncoder
import torch

from hummingbird.ml._utils import onnx_ml_tools_installed, onnx_runtime_installed, lightgbm_installed
from hummingbird.ml import convert

if onnx_ml_tools_installed():
    from onnxmltools import convert_sklearn
    from onnxmltools.convert.common.data_types import Int32TensorType as IntTensorType_onnx
    from onnxmltools.convert.common.data_types import Int64TensorType as LongTensorType_onnx
    from onnxmltools.convert.common.data_types import StringTensorType as StringTensorType_onnx
    from onnxmltools.convert.common.data_types import FloatTensorType as FloatTensorType_onnx

if onnx_runtime_installed():
    import onnxruntime as ort


class TestONNXLabelEncoder(unittest.TestCase):

    # Test LabelEncoder with longs
    @unittest.skipIf(
        not (onnx_ml_tools_installed() and onnx_runtime_installed()), reason="ONNXML test requires ONNX, ORT and ONNXMLTOOLS"
    )
    def test_model_label_encoder_int_onnxml(self):
        model = LabelEncoder()
        X = np.array([1, 4, 5, 2, 0, 2], dtype=np.int64)
        model.fit(X)

        # Create ONNX-ML model
        onnx_ml_model = convert_sklearn(model, initial_types=[("input", LongTensorType_onnx(X.shape))])

        # Create ONNX model by calling converter
        onnx_model = convert(onnx_ml_model, "onnx", X)

        # Get the predictions for the ONNX-ML model
        session = ort.InferenceSession(onnx_ml_model.SerializeToString())
        output_names = [session.get_outputs()[i].name for i in range(len(session.get_outputs()))]
        inputs = {session.get_inputs()[0].name: X}
        onnx_ml_pred = np.array(session.run(output_names, inputs)).ravel()

        # Get the predictions for the ONNX model
        onnx_pred = onnx_model.transform(X).ravel()

        # Check that predicted values match
        np.testing.assert_allclose(onnx_ml_pred, onnx_pred, rtol=1e-06, atol=1e-06)

    # Test LabelEncoder with strings
    # @unittest.skipIf(
    #     not (onnx_ml_tools_installed() and onnx_runtime_installed()), reason="ONNXML test requires ONNX, ORT and ONNXMLTOOLS"
    # )
    # def test_model_label_encoder_str_onnxml(self):
    #     model = LabelEncoder()
    #     data = [
    #         "paris",
    #         "milan",
    #         "amsterdam",
    #         "tokyo",
    #     ]
    #     model.fit(data)

    #     # max word length is the smallest number which is divisible by 4 and larger than or equal to the length of any word
    #     max_word_length = 12
    #     view_args = [-1, max_word_length // 4]
    #     str_dtype = "|S" + str(max_word_length)
    #     np_arr = np.array(data, dtype=str_dtype).view(np.int32)

    #     # pytorch_input = torch.from_numpy(np_arr).view(*view_args)
    #     data_np = np_arr.reshape(*view_args)

    #     onnx_ml_model = convert_sklearn(
    #         model, initial_types=[("input", LongTensorType_onnx([4, max_word_length // 4]))]
    #     )

    #     # TODO: not having the sample input here throws:
    #     # File "../hummingbird/hummingbird/ml/convert.py", line 184, in _convert_onnxml
    #     #     assert len(shape) == 2
    #     #     AssertionError
    #     # onnx_model = convert(onnx_ml_model, "onnx" )
    #     onnx_model = convert(onnx_ml_model, "onnx", data_np)

    #     # Get the predictions for the ONNX-ML model
    #     session = ort.InferenceSession(onnx_ml_model.SerializeToString())
    #     output_names = [session.get_outputs()[i].name for i in range(len(session.get_outputs()))]
    #     inputs = {session.get_inputs()[0].name: data}
    #     onnx_ml_pred = session.run(output_names, inputs)

    #     # Get the predictions for the ONNX model
    #     onnx_pred = onnx_model.transform(data_np)

    #     # Check that predicted values match
    #     np.testing.assert_allclose(onnx_ml_pred, onnx_pred, rtol=1e-06, atol=1e-06)

    @unittest.skipIf(
        not (onnx_ml_tools_installed() and onnx_runtime_installed()), reason="ONNXML test requires ONNX, ORT and ONNXMLTOOLS"
    )
    # if the model is corrupt, we should get a RuntimeError
    def test_onnx_label_encoder_converter_raises_rt(self):
        warnings.filterwarnings("ignore")
        model = LabelEncoder()
        X = np.array([1, 4, 5, 2, 0, 2], dtype=np.int64)
        model.fit(X)

        # generate test input
        onnx_ml_model = convert_sklearn(model, initial_types=[("float_input", FloatTensorType_onnx(X.shape))])
        onnx_ml_model.graph.node[0].attribute[0].name = "".encode()

        self.assertRaises(RuntimeError, convert, onnx_ml_model, "onnx", X)


if __name__ == "__main__":
    unittest.main()
