import json, argparse
from engine.core import YAMLConfig

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', '-c', default= "configs/dfine/dfine_hgnetv2_l_coco.yml", type=str)
    args = parser.parse_args()

    cfg = YAMLConfig(args.config, resume=None)
    print(json.dumps(cfg.__dict__, indent=4, ensure_ascii=False))