"""
Copyright (c) 2024 The D-FINE Authors. All Rights Reserved.
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))

import argparse, thop
from calflops import calculate_flops
from engine.core import YAMLConfig
from engine.logger_module import get_logger

import torch
import torch.nn as nn

RED, GREEN, BLUE, YELLOW, ORANGE, RESET = "\033[91m", "\033[92m", "\033[94m", "\033[93m", "\033[38;5;208m", "\033[0m"
logger = get_logger(__name__)

def custom_repr(self):
    return f'{{Tensor:{tuple(self.shape)}}} {original_repr(self)}'
original_repr = torch.Tensor.__repr__
torch.Tensor.__repr__ = custom_repr

def main(args, ):
    """main
    """
    cfg = YAMLConfig(args.config, resume=None)
    class Model_for_flops(nn.Module):
        def __init__(self, ) -> None:
            super().__init__()
            self.model = cfg.model.deploy()

        def forward(self, images):
            outputs = self.model(images)
            return outputs

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = Model_for_flops().eval().to(device)

    try:
        flops, macs, _ = calculate_flops(model=model,
                                        input_shape=(1, 3, *cfg.yaml_cfg['eval_spatial_size']),
                                        output_as_string=True,
                                        output_precision=4,
                                        print_detailed=True)
    except:
        logger.warning(RED + "calculate_flops failed.. using thop instead.." + RESET)
        macs = thop.profile(model, inputs=[torch.randn(size=(1, 3, *cfg.yaml_cfg['eval_spatial_size']), device=device)], verbose=False)[0]
        macs, flops = thop.clever_format([macs, macs * 2], format="%.3f")
    params = sum(p.numel() for p in model.parameters())
    print("Model FLOPs:%s   MACs:%s   Params:%s \n" %(flops, macs, params))

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--config', '-c', default= "configs/dfine/dfine_hgnetv2_l_coco.yml", type=str)
    args = parser.parse_args()

    main(args)
