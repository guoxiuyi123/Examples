""" 
Copied from RT-DETR (https://github.com/lyuwenyu/RT-DETR)
Copyright(c) 2023 lyuwenyu. All Rights Reserved.
"""    
 
import torch
import torch.nn as nn

import torchvision
import torchvision.transforms.v2 as T 
import torchvision.transforms.v2.functional as F   
from torchvision.transforms.v2 import InterpolationMode  
   
import PIL
import PIL.Image 
 
from typing import Any, Dict, List, Optional, Union, Tuple

from .._misc import convert_to_tv_tensor, _boxes_keys
from .._misc import Image, Video, Mask, BoundingBoxes
from .._misc import SanitizeBoundingBoxes  

from ...core import register
torchvision.disable_beta_transforms_warning()  
   
from ...logger_module import get_logger    
    
RandomPhotometricDistort = register()(T.RandomPhotometricDistort) 
RandomZoomOut = register()(T.RandomZoomOut)
RandomHorizontalFlip = register()(T.RandomHorizontalFlip)
Resize = register()(T.Resize)
# ToImageTensor = register()(T.ToImageTensor) 
# ConvertDtype = register()(T.ConvertDtype) 
# PILToTensor = register()(T.PILToTensor)
SanitizeBoundingBoxes = register(name='SanitizeBoundingBoxes')(SanitizeBoundingBoxes)   
RandomCrop = register()(T.RandomCrop)
Normalize = register()(T.Normalize) 

logger = get_logger(__name__)
   
@register()
class EmptyTransform(T.Transform):  
    def __init__(self, ) -> None:
        super().__init__()    

    def forward(self, *inputs): 
        inputs = inputs if len(inputs) > 1 else inputs[0]
        return inputs     
 
@register()   
class ResizeLongestEdge(T.Transform):   
    """
    将最长边缩放到指定大小，保持宽高比   
     
    支持:
        - PIL.Image
        - torch.Tensor    
        - torchvision.tv_tensors (Image, Video, Mask, BoundingBoxes)     
   
    Args:     
        size (int): 最长边的目标尺寸
        interpolation (InterpolationMode): 插值模式，默认 BILINEAR
        max_size (int, optional): 最短边的最大值限制 
        antialias (bool): 是否抗锯齿，默认 True     
    
    Examples:     
        >>> transform = ResizeLongestEdge(size=640)
        >>> img = Image.new('RGB', (1920, 1080)) 
        >>> out = transform(img)    
        >>> print(out.size)  # (640, 360)
  
        >>> # 配合其他变换
        >>> transform = T.Compose([    
        ...     ResizeLongestEdge(640),     
        ...     T.ConvertImageDtype(torch.float32),
        ...     T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]) 
        ... ])  
    """
 
    _transformed_types = (  
        PIL.Image.Image,  
        Image, 
        Video, 
        Mask,
        BoundingBoxes,
    )     
    
    def __init__(
        self,
        size: int,
        interpolation: InterpolationMode = InterpolationMode.BILINEAR,   
        max_size: int = None,
        antialias: bool = True    
    ):
        super().__init__()    
        self.size = size
        self.interpolation = interpolation
        self.max_size = max_size     
        self.antialias = antialias
    
    def _get_spatial_size(self, inpt: Any) -> Tuple[int, int]:
        """  
        获取空间尺寸 (height, width)  
        兼容多版本 torchvision
        """
        # 尝试使用 torchvision 的函数 
        if hasattr(F, 'get_size'):   
            return F.get_size(inpt) 
        elif hasattr(F, 'get_spatial_size'):
            return F.get_spatial_size(inpt)     
        
        # 手动处理
        if isinstance(inpt, PIL.Image.Image):
            w, h = inpt.size   
            return (h, w)   
        elif isinstance(inpt, torch.Tensor): 
            return tuple(inpt.shape[-2:])
        elif hasattr(inpt, 'shape'):   
            return tuple(inpt.shape[-2:])
        else:
            raise TypeError(f"Cannot get spatial size from {type(inpt)}") 
    
    def _get_params(self, flat_inputs: List[Any]) -> Dict[str, Any]:
        """计算缩放后的尺寸""" 
        orig_h, orig_w = self._get_spatial_size(flat_inputs[0])
        
        # 找到最长边   
        longest_edge = max(orig_h, orig_w)     
   
        # 计算缩放比例
        scale = self.size / longest_edge
     
        # 计算新尺寸    
        new_h = int(orig_h * scale) 
        new_w = int(orig_w * scale)   
        
        # 如果设置了 max_size，限制最短边     
        if self.max_size is not None: 
            shortest_edge = min(new_h, new_w)     
            if shortest_edge > self.max_size:
                scale = self.max_size / min(orig_h, orig_w)
                new_h = int(orig_h * scale)
                new_w = int(orig_w * scale)
        
        return {     
            'size': (new_h, new_w),
            'scale': scale   
        }     
 
    def _transform(self, inpt: Any, params: Dict[str, Any]) -> Any:
        """应用缩放变换"""    
        size = params['size'] 
    
        # 对不同类型使用不同的插值模式
        if isinstance(inpt, (BoundingBoxes, Mask)):     
            # BoundingBoxes 和 Mask 使用最近邻插值
            return F.resize(
                inpt,
                size=size,  
                interpolation=InterpolationMode.NEAREST    
            )
        else:  
            # 图像使用指定的插值模式 
            return F.resize(
                inpt,
                size=size,
                interpolation=self.interpolation,    
                antialias=self.antialias  
            )    
    
    def __repr__(self) -> str:    
        return ( 
            f"{self.__class__.__name__}("
            f"size={self.size}, "
            f"interpolation={self.interpolation}, "    
            f"max_size={self.max_size}, " 
            f"antialias={self.antialias})"     
        )

@register()     
class PadToSize(T.Pad):
    _transformed_types = (  
        PIL.Image.Image,
        Image,   
        Video,   
        Mask,
        BoundingBoxes,
    )
    def _get_params(self, flat_inputs: List[Any]) -> Dict[str, Any]:    
        if hasattr(F, 'get_size'):
            sp = F.get_size(flat_inputs[0])     
        elif hasattr(F, 'get_spatial_size'): 
            sp = F.get_spatial_size(flat_inputs[0])
        else:    
            if isinstance(flat_inputs[0], PIL.Image.Image):
                w, h = flat_inputs[0].size
                sp = (h, w)
        print(sp)
        h, w = self.size[1] - sp[0], self.size[0] - sp[1] 
        self.padding = [0, 0, w, h]
        return dict(padding=self.padding)
  
    def __init__(self, size, fill=0, padding_mode='constant') -> None:
        if isinstance(size, int):
            size = (size, size)
        self.size = size
        super().__init__(0, fill, padding_mode) 

    def _transform(self, inpt: Any, params: Dict[str, Any]) -> Any:
        padding = params['padding']     
        return F.pad(inpt, padding=padding, fill=self.fill, padding_mode=self.padding_mode)  # type: ignore[arg-type] 
 
    def transform(self, inpt: Any, params: Dict[str, Any]) -> Any:
        return self._transform(inpt, params) 

    def __call__(self, *inputs: Any) -> Any:     
        outputs = super().forward(*inputs)  
        if len(outputs) > 1 and isinstance(outputs[1], dict):
            outputs[1]['padding'] = torch.tensor(self.padding)   
        return outputs


@register()
class RandomIoUCrop(T.RandomIoUCrop):   
    def __init__(self, min_scale: float = 0.3, max_scale: float = 1, min_aspect_ratio: float = 0.5, max_aspect_ratio: float = 2, sampler_options: Optional[List[float]] = None, trials: int = 40, p: float = 1.0):  
        super().__init__(min_scale, max_scale, min_aspect_ratio, max_aspect_ratio, sampler_options, trials)
        self.p = p

    def __call__(self, *inputs: Any) -> Any:
        if torch.rand(1) >= self.p:    
            return inputs if len(inputs) > 1 else inputs[0] 
   
        return super().forward(*inputs)     
     
  
@register()
class ConvertBoxes(T.Transform):   
    _transformed_types = (
        BoundingBoxes, 
    )
    def __init__(self, fmt='', normalize=False) -> None:
        super().__init__()     
        self.fmt = fmt
        self.normalize = normalize
     
    def _transform(self, inpt: Any, params: Dict[str, Any]) -> Any:
        spatial_size = getattr(inpt, _boxes_keys[1])     
        if self.fmt:  
            in_fmt = inpt.format.value.lower()    
            inpt = torchvision.ops.box_convert(inpt, in_fmt=in_fmt, out_fmt=self.fmt.lower()) 
            inpt = convert_to_tv_tensor(inpt, key='boxes', box_format=self.fmt.upper(), spatial_size=spatial_size)

        if self.normalize: 
            inpt = inpt / torch.tensor(spatial_size[::-1]).tile(2)[None]

        return inpt   

    def transform(self, inpt: Any, params: Dict[str, Any]) -> Any:
        return self._transform(inpt, params)
 

@register()
class ConvertPILImage(T.Transform):
    _transformed_types = (
        PIL.Image.Image, 
    )
    def __init__(self, dtype='float32', scale=True, dinov3_norm=False) -> None:  
        super().__init__()
        self.dtype = dtype
        self.scale = scale
        self.dinov3_norm = dinov3_norm
        
        self.dinov3_normalize = T.Normalize(
            mean=(0.485, 0.456, 0.406),
            std=(0.229, 0.224, 0.225),  
        ) 

        if self.dinov3_norm:
            logger.info(f'Using Dinov3 Normalize:{self.dinov3_normalize}')
   
    def _transform(self, inpt: Any, params: Dict[str, Any]) -> Any:
        inpt = F.pil_to_tensor(inpt)
        if self.dtype == 'float32':  
            inpt = inpt.float() 
        
        if self.scale:    
            inpt = inpt / 255.     
            if self.dinov3_norm: 
                inpt = self.dinov3_normalize(inpt)  

        inpt = Image(inpt)
  
        return inpt   
    
    def transform(self, inpt: Any, params: Dict[str, Any]) -> Any: 
        return self._transform(inpt, params)
