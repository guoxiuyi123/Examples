import os, sys, argparse
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from pathlib import Path

from engine.core import YAMLConfig
from engine.logger_module import get_logger
from engine.misc.visualizer import plot_sample

logger = get_logger(__name__)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', type=str, default='configs/deimv2/test.yml')
    parser.add_argument('-n', '--num', type=int, default=20)
    parser.add_argument('-s', '--split', type=str, default='train', choices=['train', 'val'])
    args = parser.parse_args()

    cfg = YAMLConfig(args.config)

    if args.split == 'train':
        data_loader = cfg.train_dataloader
    elif args.split == 'val':
        data_loader = cfg.val_dataloader
    output_dir = Path('dataloader_output')
    output_dir.mkdir(exist_ok=True)

    data_loader.set_epoch(10)
    for idx, (samples, targets) in enumerate(data_loader):
        if data_loader.dataset.remap_mscoco_category:
            plot_sample((samples, targets), data_loader.dataset.category2name, output_dir / f"batch_{idx}.png", data_loader.dataset.label2category)
        else:
            plot_sample((samples, targets), data_loader.dataset.category2name, output_dir / f"batch_{idx}.png")
        
        logger.info(f'index:{idx + 1} plot....')

        if (idx + 1) >= args.num:
            break

    logger.info('done...')