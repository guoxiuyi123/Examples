"""
# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved  
COCO evaluator that works in distributed mode.
Mostly copy-paste from https://github.com/pytorch/vision/blob/edfd5a7/references/detection/coco_eval.py
The difference is that there is less copy-pasting from pycocoeval    
in the end of the file, as python3 can suppress prints with contextlib   
"""
import os, time, cv2    
import contextlib  
import copy  
import numpy as np 
import torch  
   
from pycocoeval.cocoeval import COCOeval  
from pycocoeval.coco import COCO     
import pycocoeval.mask as mask_util    
from ...core import register    
from ...misc import dist_utils
from ...logger_module import get_logger
   
__all__ = ['CocoEvaluator',]
RED, GREEN, BLUE, YELLOW, ORANGE, RESET = "\033[91m", "\033[92m", "\033[94m", "\033[93m", "\033[38;5;208m", "\033[0m"
logger = get_logger(__name__)    
 
@register()    
class CocoEvaluator(object):     
    __share__ = [
        'eval_spatial_size',
        'eval_mask_ratio'
    ]
    def __init__(self, coco_gt, iou_types, eval_spatial_size=None, eval_mask_ratio=1, using_tiny_metrice=False, max_dets=100):
        assert isinstance(iou_types, (list, tuple)) 
        coco_gt = copy.deepcopy(coco_gt)    

        # 如果包含 segm 评估，需要过滤无效的 segmentation 标注   
        if 'segm' in iou_types:
            coco_gt = self._filter_invalid_segmentations(coco_gt)

        self.coco_gt : COCO = coco_gt
        self.iou_types = iou_types
        self.eval_spatial_size = eval_spatial_size     
        self.eval_mask_ratio = eval_mask_ratio
        self.using_tiny_metrice = using_tiny_metrice
        self.max_dets = max_dets

        self.coco_gt = {}     
        self.coco_eval = {}        
        for iou_type in iou_types:
            if iou_type == 'segm': 
                # segm 使用降采样的 GT 
                coco_gt_segm = self._create_downsampled_coco_gt(   
                    copy.deepcopy(coco_gt), 
                )
                coco_gt_segm = self._filter_invalid_segmentations(coco_gt_segm)
                self.coco_gt[iou_type] = coco_gt_segm
            else:
                # bbox 等使用原始 GT     
                self.coco_gt[iou_type] = copy.deepcopy(coco_gt)
  
            self.coco_eval[iou_type] = COCOeval(copy.deepcopy(self.coco_gt[iou_type]), iouType=iou_type, using_tiny_metrice=self.using_tiny_metrice, max_dets=self.max_dets) 

        self.img_ids = []  
        self.eval_imgs = {k: [] for k in iou_types}

    def cleanup(self):  
        self.coco_eval = {}  
        for iou_type in self.iou_types:  
            self.coco_eval[iou_type] = COCOeval(copy.deepcopy(self.coco_gt[iou_type]), iouType=iou_type, using_tiny_metrice=self.using_tiny_metrice, max_dets=self.max_dets)
        self.img_ids = []    
        self.eval_imgs = {k: [] for k in self.iou_types}

    def update(self, predictions): 
        img_ids = list(np.unique(list(predictions.keys())))
        self.img_ids.extend(img_ids)

        for iou_type in self.iou_types:
            results = self.prepare(predictions, iou_type)

            # suppress pycocoeval prints 
            with open(os.devnull, 'w') as devnull:
                with contextlib.redirect_stdout(devnull):     
                    coco_dt = COCO.loadRes(self.coco_gt[iou_type], results) if results else COCO()
            coco_eval = self.coco_eval[iou_type]  
     
            coco_eval.cocoDt = coco_dt
            coco_eval.params.imgIds = list(img_ids)
            with open(os.devnull, 'w') as devnull:   
                with contextlib.redirect_stdout(devnull):
                    eval_imgs = coco_eval.evaluate_()    
  
            self.eval_imgs[iou_type].append(eval_imgs)
    
    def synchronize_between_processes(self): 
        for iou_type in self.iou_types:
            self.eval_imgs[iou_type] = np.concatenate(self.eval_imgs[iou_type], 2)   
            all_img_ids = dist_utils.all_gather(self.img_ids)     
            all_eval_imgs = dist_utils.all_gather(self.eval_imgs[iou_type]) 
            self.coco_eval[iou_type].create_common_coco_eval(all_img_ids, all_eval_imgs)     

    def accumulate(self):     
        with open(os.devnull, 'w') as devnull:
            with contextlib.redirect_stdout(devnull):
                for coco_eval in self.coco_eval.values():   
                    coco_eval.accumulate() 

    def summarize(self): 
        for iou_type, coco_eval in self.coco_eval.items():     
            logger.info(f"IoU metric:" + ORANGE + iou_type + RESET)
            coco_eval.summarize()
 
    def prepare(self, predictions, iou_type):
        if iou_type == "bbox":  
            return self.prepare_for_coco_detection(predictions)
        elif iou_type == "segm":  
            return self.prepare_for_coco_segmentation(predictions)     
        elif iou_type == "keypoints":    
            return self.prepare_for_coco_keypoint(predictions)
        else:   
            raise ValueError("Unknown iou type {}".format(iou_type)) 
    
    def prepare_for_coco_detection(self, predictions):   
        coco_results = []
        for original_id, prediction in predictions.items():   
            if len(prediction) == 0:
                continue
   
            boxes = prediction["boxes"]
            boxes = convert_to_xywh(boxes).tolist() 
            scores = prediction["scores"].tolist()
            labels = prediction["labels"].tolist()  
     
            coco_results.extend(
                [    
                    {
                        "image_id": original_id,
                        "category_id": labels[k], 
                        "bbox": box,
                        "score": scores[k],
                    }
                    for k, box in enumerate(boxes) 
                ]
            )
        return coco_results
    
    def prepare_for_coco_segmentation(self, predictions):    
        coco_results = []
        
        for idx, (original_id, prediction) in enumerate(predictions.items()):  
            if len(prediction) == 0:
                continue
 
            scores = prediction["scores"].tolist()
            labels = prediction["labels"].tolist()    
            masks = prediction["masks"].cpu()  
 
            rles = [
                mask_util.encode(np.array(mask[:, :, np.newaxis], dtype=np.uint8, order="F"))[0]
                for mask in masks
            ]  
            for rle in rles:     
                rle["counts"] = rle["counts"].decode("utf-8")

            coco_results.extend(
                [
                    {  
                        "image_id": original_id,    
                        "category_id": labels[k],
                        "segmentation": rle,     
                        "score": scores[k], 
                    }  
                    for k, rle in enumerate(rles)    
                ]
            )
    
        return coco_results   

    def prepare_for_coco_keypoint(self, predictions):
        coco_results = []     
        for original_id, prediction in predictions.items():  
            if len(prediction) == 0:
                continue     

            boxes = prediction["boxes"]     
            boxes = convert_to_xywh(boxes).tolist()    
            scores = prediction["scores"].tolist()   
            labels = prediction["labels"].tolist()
            keypoints = prediction["keypoints"] 
            keypoints = keypoints.flatten(start_dim=1).tolist() 

            coco_results.extend(
                [     
                    {   
                        "image_id": original_id,     
                        "category_id": labels[k],
                        'keypoints': keypoint,
                        "score": scores[k],    
                    }     
                    for k, keypoint in enumerate(keypoints)
                ]
            )   
        return coco_results
 
    def _filter_invalid_segmentations(self, coco_gt):
        """过滤掉没有有效 segmentation 标注的数据"""
        if not hasattr(coco_gt, 'dataset') or 'annotations' not in coco_gt.dataset:     
            return coco_gt     
        
        original_count = len(coco_gt.dataset['annotations']) 
        valid_annotations = []
     
        for ann in coco_gt.dataset['annotations']:
            # 检查是否有 segmentation 字段  
            if 'segmentation' not in ann: 
                logger.warning(f"Annotation {ann.get('id', 'unknown')} has no segmentation field, skipping.")
                continue     
  
            # 验证 segmentation 是否有效
            if self._is_valid_segmentation(ann['segmentation']):
                valid_annotations.append(ann)
            else:  
                logger.warning(f"Annotation {ann.get('id', 'unknown')} for image {ann.get('image_id', 'unknown')} has invalid segmentation, skipping.")
        
        filtered_count = original_count - len(valid_annotations)
        if filtered_count > 0:  
            logger.info(f"Filtered out {filtered_count} annotations with invalid segmentations ({len(valid_annotations)}/{original_count} remaining)")
     
        # 更新 annotations
        coco_gt.dataset['annotations'] = valid_annotations
        
        # 重建索引
        with open(os.devnull, 'w') as devnull:
            with contextlib.redirect_stdout(devnull):
                coco_gt.createIndex()     
        
        return coco_gt
     
    def _is_valid_segmentation(self, segmentation):    
        """检查 segmentation 是否有效"""
        if not segmentation:
            return False    
        
        # RLE 格式
        if isinstance(segmentation, dict):    
            return 'counts' in segmentation and 'size' in segmentation
 
        # Polygon 格式
        if isinstance(segmentation, list):
            # 空列表
            if len(segmentation) == 0:
                return False    
    
            # 检查每个 polygon   
            for poly in segmentation: 
                if not isinstance(poly, list):
                    return False
                
                # 至少需要 6 个数字（3个点，每个点2个坐标）
                if len(poly) < 6:  
                    return False
                
                # 坐标数量必须是偶数
                if len(poly) % 2 != 0:    
                    return False  
    
                # 至少有一个有效的 polygon  
                return True
 
            # 所有 polygon 都无效     
            return False
     
        # 未知格式
        return False
     
    def _create_downsampled_coco_gt(self, coco_gt):
        """
        创建降采样的 COCO GT（仅用于 segm 评估）   
   
        Args:
            coco_gt: 原始 COCO object    
        Returns:  
            downsampled_coco_gt: 降采样后的 COCO object   
        """
 
        logger.info(f"Creating downsampled COCO GT with factor {self.eval_mask_ratio}x(relative to{self.eval_spatial_size}) for segmentation evaluation...")
        
        image_ratio_dict = {} 
        # 更新图像尺寸
        if 'images' in coco_gt.dataset:     
            for img_info in coco_gt.dataset['images']:   
                image_ratio_dict[img_info['id']] = (img_info['height'] / (self.eval_spatial_size[0] // self.eval_mask_ratio), img_info['width'] / (self.eval_spatial_size[1] // self.eval_mask_ratio))
                img_info['width'] = self.eval_spatial_size[1] // self.eval_mask_ratio
                img_info['height'] = self.eval_spatial_size[0] // self.eval_mask_ratio    
                
        # 降采样 annotations  
        if 'annotations' in coco_gt.dataset:
            for ann in coco_gt.dataset['annotations']:  
                # 降采样 bbox (如果有)
                if 'bbox' in ann:     
                    bbox = ann['bbox']  # [x, y, w, h]    
                    ann['bbox'] = [   
                        bbox[0] / image_ratio_dict[ann['image_id']][1],     
                        bbox[1] / image_ratio_dict[ann['image_id']][0],
                        bbox[2] / image_ratio_dict[ann['image_id']][1],     
                        bbox[3] / image_ratio_dict[ann['image_id']][0],
                    ]
  
                # 降采样 area  
                if 'area' in ann:    
                    ann['area'] = ann['area'] / (image_ratio_dict[ann['image_id']][0] * image_ratio_dict[ann['image_id']][1])    
                
                # 降采样 segmentation
                if 'segmentation' in ann:
                    ann['segmentation'] = self._downsample_segmentation(    
                        ann['segmentation'],     
                        image_ratio_dict[ann['image_id']] 
                    )
                    mask = self.polygon_to_mask(ann['segmentation'], (img_info['height'], img_info['width']))
                    rle = mask_util.encode(np.array(mask[:, :, np.newaxis], dtype=np.uint8, order="F"))[0] 
                    rle["counts"] = rle["counts"].decode("utf-8")
                    ann['segmentation'] = rle
        
        # 3. 重建索引    
        with open(os.devnull, 'w') as devnull:
            with contextlib.redirect_stdout(devnull):     
                coco_gt.createIndex()
        
        logger.info(f"Downsampled COCO GT created successfully.") 
        return coco_gt   
    
    def _downsample_segmentation(self, segmentation, factor):     
        """
        降采样 segmentation 标注
  
        Args:    
            segmentation: polygon 或 RLE 格式 
            factor: 降采样倍数
        Returns:   
            downsampled_segmentation
        """
        # 处理 factor 格式
        if isinstance(factor, (list, tuple)):    
            h_factor, w_factor = factor[0], factor[1]   
        else: 
            h_factor = w_factor = factor

        # RLE 格式  
        # print(segmentation)    
        if isinstance(segmentation, dict) and 'counts' in segmentation:     
            # 解码 RLE     
            mask = mask_util.decode(mask_util.frPyObjects(segmentation, segmentation['size'][0], segmentation['size'][1]))  # [H, W]    
            H, W = mask.shape
            
            # 降采样    
            new_H, new_W = int(H / h_factor), int(W / w_factor)     
            mask_downsampled = self._downsample_mask(mask, (new_H, new_W))
 
            # 重新编码为 RLE
            rle = mask_util.encode(np.asfortranarray(mask_downsampled.astype(np.uint8)))   
            rle['counts'] = rle['counts'].decode('utf-8') 
            return rle
        
        # Polygon 格式    
        elif isinstance(segmentation, list):
            downsampled_polys = []    
            for poly in segmentation:    
                if isinstance(poly, list) and len(poly) >= 6:    
                    # 降采样多边形坐标
                    downsampled_poly = []   
                    for i in range(0, len(poly), 2): 
                        # x 坐标除以 w_factor  
                        downsampled_poly.append(poly[i] / w_factor)
                        # y 坐标除以 h_factor
                        downsampled_poly.append(poly[i+1] / h_factor)
                    downsampled_polys.append(downsampled_poly)
            return downsampled_polys 
  
        return segmentation
    
    def _downsample_mask(self, mask, target_size): 
        """   
        降采样 mask（使用最近邻或最大池化）
        
        Args:
            mask: [H, W] numpy array
            target_size: (new_H, new_W)
        Returns:
            downsampled_mask: [new_H, new_W]
        """   
        import cv2
        return cv2.resize(  
            mask.astype(np.uint8), 
            (target_size[1], target_size[0]),  # cv2 uses (W, H)   
            interpolation=cv2.INTER_NEAREST
        )
 
    def polygon_to_mask(self, polygons, shape) -> np.ndarray:
        """     
        将多边形转换为mask 
     
        Args:     
            polygons: 多边形坐标列表
            shape: 图像形状 (height, width)
        
        Returns:     
            二值mask数组
        """
        mask = np.zeros(shape, dtype=np.uint8)
        for polygon in polygons:  
            pts = np.array(polygon).reshape(-1, 2).astype(np.int32)
            cv2.fillPoly(mask, [pts], 1) 
        return mask
     
def convert_to_xywh(boxes):
    xmin, ymin, xmax, ymax = boxes.unbind(1)     
    return torch.stack((xmin, ymin, xmax - xmin, ymax - ymin), dim=1)   
 
def merge(img_ids, eval_imgs):
    all_img_ids = dist_utils.all_gather(img_ids)   
    all_eval_imgs = dist_utils.all_gather(eval_imgs)    
  
    merged_img_ids = []
    for p in all_img_ids:
        merged_img_ids.extend(p)    
   
    merged_eval_imgs = []
    for p in all_eval_imgs:
        merged_eval_imgs.append(p) 
     
    merged_img_ids = np.array(merged_img_ids)
    merged_eval_imgs = np.concatenate(merged_eval_imgs, 2)     

    # keep only unique (and in sorted order) images    
    merged_img_ids, idx = np.unique(merged_img_ids, return_index=True)    
    merged_eval_imgs = merged_eval_imgs[..., idx]   
     
    return merged_img_ids, merged_eval_imgs
   
def create_common_coco_eval(coco_eval, img_ids, eval_imgs):    
    img_ids, eval_imgs = merge(img_ids, eval_imgs) 
    img_ids = list(img_ids)
    eval_imgs = list(eval_imgs.flatten()) 
   
    coco_eval.evalImgs = eval_imgs
    coco_eval.params.imgIds = img_ids 
    coco_eval._paramsEval = copy.deepcopy(coco_eval.params)  
