import os
import sys
import argparse
import numpy as np

import torch
from torchvision import transforms, datasets
import torch.utils.data as data
from DDAM import DDAMNet
import matplotlib.pyplot as plt
import itertools

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

model = DDAMNet(num_class=7)
checkpoint = torch.load(args.model_path, map_location=device)
model.load_state_dict(checkpoint['model_state_dict'])
model.to(device)