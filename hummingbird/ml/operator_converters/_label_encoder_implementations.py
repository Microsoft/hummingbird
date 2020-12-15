# -------------------------------------------------------------------------
# Copyright (c) 2020 Supun Nakandala. All Rights Reserved.
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
Base classes for LabelEncoders
"""

import torch
import numpy as np

from ._base_operator import BaseOperator


class StringLabelEncoder(BaseOperator, torch.nn.Module):
    def __init__(self, classes, device):
        super(StringLabelEncoder, self).__init__(transformer=True)
        self.regression = False
        self.num_columns = len(classes)
        self.max_word_length = max([len(cat) for cat in classes])
        while self.max_word_length % 4 != 0:
            self.max_word_length += 1

        data_type = "|S" + str(self.max_word_length)
        self.max_word_length = self.max_word_length // 4

        # Sort the classes and convert to torch.int32
        classes_conv = torch.from_numpy(np.array(sorted(set(classes)), dtype=data_type).view(np.int32))
        classes_conv = classes_conv.view(1, -1, self.max_word_length)

        self.condition_tensors = torch.nn.Parameter(torch.IntTensor(classes_conv), requires_grad=False)

    def forward(self, x):
        x = x.view(-1, 1, self.max_word_length)
        try:
            result = torch.prod(self.condition_tensors == x, dim=2).nonzero(as_tuple=True)[1]
            assert result.shape[0] == x.shape[0]
            return result
        except AssertionError:
            raise ValueError(
                "x ({}) contains previously unseen labels. condition_tensors: {}".format(x, self.condition_tensors)
            )


class NumericLabelEncoder(BaseOperator, torch.nn.Module):
    def __init__(self, classes, device):
        super(NumericLabelEncoder, self).__init__(transformer=True)
        self.regression = False
        self.check_tensor = torch.nn.Parameter(torch.IntTensor(classes), requires_grad=False)

    def forward(self, x):
        x = x.view(-1, 1)

        return torch.argmax(torch.eq(x, self.check_tensor).int(), dim=1)
