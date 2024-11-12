import torch
import torch.nn as nn


class WideAndDeepModel(nn.Module):
    def __init__(self, input_dim):
        super(WideAndDeepModel, self).__init__()

        # Phần "wide" - một lớp tuyến tính đơn giản
        self.wide = nn.Linear(input_dim, 1)

        # Phần "deep" - mạng nơ-ron sâu với nhiều tầng ẩn
        self.deep = nn.Sequential(
            nn.Linear(input_dim, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(0.3),  # Dropout để giảm overfitting

            nn.Linear(256, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.3),

            nn.Linear(128, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(0.2),

            nn.Linear(64, 32),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.Dropout(0.2),

            nn.Linear(32, 16),
            nn.BatchNorm1d(16),
            nn.ReLU(),
            nn.Dropout(0.1),

            nn.Linear(16, 1)
        )

    def forward(self, x):
        # Tính đầu ra của phần "wide"
        wide_output = self.wide(x)

        # Tính đầu ra của phần "deep"
        deep_output = self.deep(x)

        # Kết hợp đầu ra của phần "wide" và "deep"
        output = wide_output + deep_output
        return output