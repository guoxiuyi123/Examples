"""   
# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved    
https://github.com/facebookresearch/detr/blob/main/util/box_ops.py
""" 

import numpy as np
import torch
from torch import Tensor    
from torchvision.ops.boxes import box_area
     

def box_cxcywh_to_xyxy(x):   
    x_c, y_c, w, h = x.unbind(-1)
    b = [(x_c - 0.5 * w.clamp(min=0.0)), (y_c - 0.5 * h.clamp(min=0.0)),
         (x_c + 0.5 * w.clamp(min=0.0)), (y_c + 0.5 * h.clamp(min=0.0))]
    return torch.stack(b, dim=-1)


def box_xyxy_to_cxcywh(x: Tensor) -> Tensor: 
    x0, y0, x1, y1 = x.unbind(-1)
    b = [(x0 + x1) / 2, (y0 + y1) / 2, 
         (x1 - x0), (y1 - y0)]
    return torch.stack(b, dim=-1)

 
# modified from torchvision to also return the union  
def box_iou(boxes1: Tensor, boxes2: Tensor):     
    area1 = box_area(boxes1)
    area2 = box_area(boxes2) 

    lt = torch.max(boxes1[:, None, :2], boxes2[:, :2])  # [N,M,2]   
    rb = torch.min(boxes1[:, None, 2:], boxes2[:, 2:])  # [N,M,2]

    wh = (rb - lt).clamp(min=0)  # [N,M,2]
    inter = wh[:, :, 0] * wh[:, :, 1]  # [N,M]     
   
    union = area1[:, None] + area2 - inter 

    iou = inter / union
    return iou, union   
  
def shrink_boxes(boxes, ratio=1.5): 
    """  
    按比例缩小边界框（保持中心点不变）   
    
    Args:
        boxes (torch.Tensor | np.ndarray): 边界框坐标，形状为 [n, 4]，格式为 (x1, y1, x2, y2) 
        ratio (float): 缩放比例，默认 0.7 表示缩小到原来的 70% 
    
    Returns:
        torch.Tensor | np.ndarray: 缩小后的边界框，形状为 [n, 4]，格式为 (x1, y1, x2, y2)  
    
    Example:
        >>> boxes = torch.tensor([[10, 20, 50, 60], [100, 100, 200, 200]])
        >>> shrunk = shrink_boxes(boxes, ratio=0.5) 
        >>> print(shrunk)  
        tensor([[ 20.,  30.,  40.,  50.],
                [125., 125., 175., 175.]])  
    """     
    assert boxes.shape[-1] == 4, f"Expected last dimension to be 4, but got shape {boxes.shape}"
    
    # 计算中心点坐标    
    cx = (boxes[..., 0] + boxes[..., 2]) / 2  # x center  
    cy = (boxes[..., 1] + boxes[..., 3]) / 2  # y center    
  
    # 计算宽高     
    w = boxes[..., 2] - boxes[..., 0]  # width
    h = boxes[..., 3] - boxes[..., 1]  # height   
    
    # 计算缩小后的宽高
    new_w = w * ratio
    new_h = h * ratio
    
    # 计算缩小后的边界框坐标（保持中心不变）
    if isinstance(boxes, torch.Tensor):    
        shrunk_boxes = torch.empty_like(boxes)
    else:
        shrunk_boxes = np.empty_like(boxes)
    
    shrunk_boxes[..., 0] = cx - new_w / 2  # x1
    shrunk_boxes[..., 1] = cy - new_h / 2  # y1     
    shrunk_boxes[..., 2] = cx + new_w / 2  # x2
    shrunk_boxes[..., 3] = cy + new_h / 2  # y2
    
    return shrunk_boxes

def generalized_box_iou(boxes1, boxes2): 
    """  
    Generalized IoU from https://giou.stanford.edu/    

    The boxes should be in [x0, y0, x1, y1] format 

    Returns a [N, M] pairwise matrix, where N = len(boxes1)
    and M = len(boxes2)  
    """
    # degenerate boxes gives inf / nan results 
    # so do an early check  
    # assert (boxes1[:, 2:] >= boxes1[:, :2]).all() 
    # assert (boxes2[:, 2:] >= boxes2[:, :2]).all()
    iou, union = box_iou(boxes1, boxes2)     
  
    lt = torch.min(boxes1[:, None, :2], boxes2[:, :2])
    rb = torch.max(boxes1[:, None, 2:], boxes2[:, 2:])    

    wh = (rb - lt).clamp(min=0)  # [N,M,2]
    area = wh[:, :, 0] * wh[:, :, 1]    

    return iou - (area - union) / area     

def generalized_box_inner_iou(boxes1, boxes2, ratio=2.0):
    """    
    Generalized IoU from https://giou.stanford.edu/    

    The boxes should be in [x0, y0, x1, y1] format

    Returns a [N, M] pairwise matrix, where N = len(boxes1)
    and M = len(boxes2)
    """    
    # degenerate boxes gives inf / nan results   
    # so do an early check
    # assert (boxes1[:, 2:] >= boxes1[:, :2]).all()    
    # assert (boxes2[:, 2:] >= boxes2[:, :2]).all()
    # boxes1 = shrink_boxes(boxes1, ratio)
    boxes2 = shrink_boxes(boxes2, ratio)
   
    iou, union = box_iou(boxes1, boxes2)
  
    lt = torch.min(boxes1[:, None, :2], boxes2[:, :2])
    rb = torch.max(boxes1[:, None, 2:], boxes2[:, 2:])     
     
    wh = (rb - lt).clamp(min=0)  # [N,M,2]    
    area = wh[:, :, 0] * wh[:, :, 1]

    return iou - (area - union) / area

def masks_to_boxes(masks):
    """Compute the bounding boxes around the provided masks
    
    The masks should be in format [N, H, W] where N is the number of masks, (H, W) are the spatial dimensions.
 
    Returns a [N, 4] tensors, with the boxes in xyxy format
    """  
    if masks.numel() == 0:     
        return torch.zeros((0, 4), device=masks.device)

    h, w = masks.shape[-2:] 

    y = torch.arange(0, h, dtype=torch.float)
    x = torch.arange(0, w, dtype=torch.float)  
    y, x = torch.meshgrid(y, x)
     
    x_mask = (masks * x.unsqueeze(0))
    x_max = x_mask.flatten(1).max(-1)[0]  
    x_min = x_mask.masked_fill(~(masks.bool()), 1e8).flatten(1).min(-1)[0]

    y_mask = (masks * y.unsqueeze(0))  
    y_max = y_mask.flatten(1).max(-1)[0]
    y_min = y_mask.masked_fill(~(masks.bool()), 1e8).flatten(1).min(-1)[0] 

    return torch.stack([x_min, y_min, x_max, y_max], 1)