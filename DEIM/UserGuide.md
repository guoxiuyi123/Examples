# DEIM使用指导 创作人：BiliBili魔傀面具

### 环境安装

1. 新建conda环境
    conda create -n torch_2_3_0_py310 python=3.10 anaconda
2. 新建环境后需要激活新安装的环境才能继续后面的装包或者运行工作
   查看当前有哪里环境: conda env list
   激活上述安装的环境: conda activate torch_2_3_0_py310
3. 安装torch
    pip install torch==2.3.0 torchvision==0.18.0 torchaudio==2.3.0 --index-url https://download.pytorch.org/whl/cu121
4. 安装额外的包
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
5. 可以运行check_torch_gpu.py查看安装是否成功、gpu是否调用成功
6. 需要编译的模块可以先看下[YOLO｜DETR｜DEIM｜使用DCNV3、DCNV4、KAN、Mamba相关改进必定涉及到的编译频繁报错？我们来看看最常见的CUDA相关报错注意点！](https://www.bilibili.com/video/BV1vhVfzVEdv/)

### 训练、测试教程

1. [CVPR2025-DEIM｜新一代目标检测SOTA｜2025发高区论文必备的baseline｜手把手调试带你跑通DEIM的训练阶段](https://www.bilibili.com/video/BV1yX9VYpEPL/)
2. [CVPR2025-DEIM｜新一代目标检测SOTA｜2025发高区论文必备的baseline｜手把手调试带你跑通DEIM的测试阶段](https://www.bilibili.com/video/BV1uf9GY8E1h/)
3. [CVPR2025-DEIM｜新一代目标检测SOTA｜2025发高区论文必备的baseline｜手把手调试带你跑通DEIM的推理阶段](https://www.bilibili.com/video/BV1UwLNznEy5/)

### 基础课程(基础很重要，这些视频都需要过一下)

B站链接：https://space.bilibili.com/286900343/lists/4909499  
1. 基础较差的同学建议先看完B站的基础课程再来看进阶教程  
2. 基础一般或以上的同学可以自行跳着基础视频来看，如果会的跳过就行

### 训练命令

##### nohup<主要用于linux后台训练> 必看视频-深度学习炼丹小技巧:https://www.bilibili.com/video/BV1q3SZYsExc/
nohup xxx > logs/xxx.log 2>&1 & tail -f logs/xxx.log
###### 示例
CUDA_VISIBLE_DEVICES=0 nohup python train.py -c configs/deim/deim_hgnetv2_n_custom.yml --seed=0 > train.log 2>&1 & tail -f train.log  
CUDA_VISIBLE_DEVICES=0,1,2,3 nohup python -m torch.distributed.run --nproc_per_node 4 train.py -c configs/deim/deim_hgnetv2_n_custom.yml --seed=0 > train.log 2>&1 & tail -f train.log

##### 普通训练命令

单卡用法： CUDA_VISIBLE_DEVICES=<显卡id> python train.py -c <yml的路径> --seed=0  
单卡例子： CUDA_VISIBLE_DEVICES=0 python train.py -c configs/deim/deim_hgnetv2_n_custom.yml --seed=0  

多卡用法： CUDA_VISIBLE_DEVICES=<显卡id> python -m torch.distributed.run --nproc_per_node <选用的显卡数量> train.py -c <yml的路径> --seed=0  
多卡例子： CUDA_VISIBLE_DEVICES=0,1,2,3 python -m torch.distributed.run --nproc_per_node 4 train.py -c configs/deim/deim_hgnetv2_n_custom.yml --seed=0  
Windows多卡是不支持CUDA_VISIBLE_DEVICES=0,1,2,3指定的，要换一种方法，具体在train.py顶部有标注

### 测试命令

说明： test-only状态下会输出FPS、模型权重大小、计算量、参数量指标、TIDE指标、保存预测结果的coco-json文件。
用法： python train.py -c <yml的路径> --test-only -r <权重的路径> ｜ 请注意，yml和权重的结构必须一致，不然会报载入失败的问题  
例子： python train.py -c configs/test/dfine_hgnetv2_n_visdrone.yml --test-only -r /home/waas/best_stg2.pth  

### 推理命令(字体和框的大小请看tools/inference/<torch_inf.py,onnx_inf.py,trt_inf.py>的draw函数注释)

##### torch模型推理命令
用法： python tools/inference/torch_inf.py -c <yml的路径> -r <权重的路径> --input <需要检测的路径，支持单张图片、单个视频、一个文件夹>  --output <保存路径> -t <置信度,默认为0.2>  
例子： python tools/inference/torch_inf.py -c configs/dfine/dfine_hgnetv2_n_custom.yml -r /home/waas/best_stg2.pth --input image.png --output inference_results/exp -t 0.2

##### onnx模型推理命令
用法： python tools/inference/onnx_inf.py -p <onnx权重的路径> --input <需要检测的路径，支持单张图片、单个视频、一个文件夹>  --output <保存路径> -t <置信度,默认为0.2>  
例子： python tools/inference/onnx_inf.py -p model.onnx --input image.png --output inference_results/exp -t 0.2 

##### tensorrt模型推理命令
用法： python tools/inference/trt_inf.py -p <tensorrt权重的路径> --input <需要检测的路径，支持单张图片、单个视频、一个文件夹>  --output <保存路径> -t <置信度,默认为0.2>  
例子： python tools/inference/trt_inf.py -p model.engine --input image.png --output inference_results/exp -t 0.2 

### 计算yml的参数量和计算量功能
用法： python tools/benchmark/get_info.py -c <yml的路径>  
例子： python tools/benchmark/get_info.py -c configs/dfine/dfine_hgnetv2_n_custom.yml

### 输出yml的全部参数
用法： python show_yml_param.py -c <yml的路径>   
例子： python show_yml_param.py -c configs/dfine/dfine_hgnetv2_n_custom.yml

### 输出热力图
用法：看VideoBaiduYun.txt中的heatmap脚本使用教程

### 输出特征图
用法：看VideoBaiduYun.txt中的featuremap脚本使用教程

### COCO格式数据集信息输出脚本(输出类别数和类别id、输出每个类别的实例数量)
用法：python dataset/coco_analyzer.py <json标签的路径>
例子：python dataset/coco_analyzer.py dataset/train/annotations/data.json

### 分析检测结果的TP、FP、FN
用法：看VideoBaiduYun.txt中的tp_fp_fn_analysis脚本使用教程

### 改进模块(对应的论文链接均在py文件头部,模块结构图和简介在engine/extre_module/module_images)

- engine/extre_module/custom_nn/attention 

    1. engine/extre_module/custom_nn/attention/SEAM.py
    2. CVPR2021|engine/extre_module/custom_nn/attention/ca.py
    3. ICASSP2023|engine/extre_module/custom_nn/attention/ema.py
    4. ICML2021|engine/extre_module/custom_nn/attention/simam.py
    5. ICCV2023|engine/extre_module/custom_nn/attention/lsk.py
    6. WACV2024|engine/extre_module/custom_nn/attention/DeformableLKA.py
    7. engine/extre_module/custom_nn/attention/mlca.py
    8. BIBM2024|engine/extre_module/custom_nn/attention/FSA.py
    9. AAAI2025|engine/extre_module/custom_nn/attention/CDFA.py
    10. engine/extre_module/custom_nn/attention/GLSA.py
    11. TGRS2025|engine/extre_module/custom_nn/attention/MCA.py
    12. CVPR2025|engine/extre_module/custom_nn/attention/CASAB.py 
    13. NN2025|engine/extre_module/custom_nn/attention/KSFA.py

- engine/extre_module/custom_nn/block

    1. engine/extre_module/custom_nn/block/RepHMS.py
    2. 自研模块|engine/extre_module/custom_nn/block/rgcspelan.py
    3. TPAMI2025|engine/extre_module/custom_nn/block/MANet.py

- engine/extre_module/custom_nn/conv_module

    1. CVPR2021|engine/extre_module/custom_nn/conv_module/dbb.py
    2. IEEETIP2024|engine/extre_module/custom_nn/conv_module/deconv.py
    3. ICCV2023|engine/extre_module/custom_nn/conv_module/dynamic_snake_conv.py
    4. CVPR2023|engine/extre_module/custom_nn/conv_module/pconv.py
    5. AAAI2025|engine/extre_module/custom_nn/conv_module/psconv.py
    6. CVPR2025|engine/extre_module/custom_nn/conv_module/ShiftwiseConv.py
    7. engine/extre_module/custom_nn/conv_module/wdbb.py
    8. engine/extre_module/custom_nn/conv_module/deepdbb.py
    9. ECCV2024|engine/extre_module/custom_nn/conv_module/wtconv2d.py
    10. CVPR2023|engine/extre_module/custom_nn/conv_module/ScConv.py
    11. engine/extre_module/custom_nn/conv_module/dcnv2.py
    12. CVPR2024|engine/extre_module/custom_nn/conv_module/DilatedReparamConv.py
    13. engine/extre_module/custom_nn/conv_module/gConv.py
    14. CVPR2024|engine/extre_module/custom_nn/conv_module/IDWC.py
    15. engine/extre_module/custom_nn/conv_module/DSA.py
    16. CVPR2025|engine/extre_module/custom_nn/conv_module/FDConv.py
    17. CVPR2023|engine/extre_module/custom_nn/conv_module/dcnv3.py
    18. CVPR2024|engine/extre_module/custom_nn/conv_module/dcnv4.py
    19. CVPR2024|engine/extre_module/custom_nn/conv_module/DynamicConv.py
    20. CVPR2024|engine/extre_module/custom_nn/conv_module/FADC.py
    21. CVPR2023|engine/extre_module/custom_nn/conv_module/SMPConv.py
    22. MIA2025|engine/extre_module/custom_nn/conv_module/FourierConv.py
    23. CVPR2024|engine/extre_module/custom_nn/conv_module/SFSConv.py
    24. ICCV2025|engine/extre_module/custom_nn/conv_module/MBRConv.py
    25. ICCV2025|engine/extre_module/custom_nn/conv_module/ConvAttn.py
    26. ICCV2025|engine/extre_module/custom_nn/conv_module/Converse2D.py
    27. CVPR2025|engine/extre_module/custom_nn/conv_module/gcconv.py
    28. ACCV2024|engine/extre_module/custom_nn/conv_module/RMBC.py

- engine/extre_module/custom_nn/upsample

    1. CVPR2024|engine/extre_module/custom_nn/upsample/eucb.py
    2. CVPR2024|engine/extre_module/custom_nn/upsample/eucb_sc.py
    3. engine/extre_module/custom_nn/upsample/WaveletUnPool.py
    4. ICCV2019|engine/extre_module/custom_nn/upsample/CARAFE.py
    5. ICCV2023|engine/extre_module/custom_nn/upsample/DySample.py
    6. ICCV2025|engine/extre_module/custom_nn/upsample/Converse2D_Up.py
    7. CVPR2025|engine/extre_module/custom_nn/upsample/DSUB.py

- engine/extre_module/custom_nn/downsample

    1. IEEETIP2020|engine/extre_module/custom_nn/downsample/gcnet.py
    2. 自研模块|engine/extre_module/custom_nn/downsample/lawds.py 
    3. engine/extre_module/custom_nn/downsample/WaveletPool.py
    4. engine/extre_module/custom_nn/downsample/ADown.py
    5. engine/extre_module/custom_nn/downsample/YOLOV7Down.py
    6. engine/extre_module/custom_nn/downsample/SPDConv.py
    7. engine/extre_module/custom_nn/downsample/HWD.py
    8. engine/extre_module/custom_nn/downsample/DRFD.py

- engine/extre_module/custom_nn/stem

    1. engine/extre_module/custom_nn/stem/SRFD.py
    2. engine/extre_module/custom_nn/stem/LoG.py
    3. ICCV2023|engine/extre_module/custom_nn/stem/RepStem.py

- engine/extre_module/custom_nn/featurefusion

    1. 自研模块|engine/extre_module/custom_nn/featurefusion/cgfm.py
    2. BMVC2024|engine/extre_module/custom_nn/featurefusion/msga.py
    3. CVPR2024|engine/extre_module/custom_nn/featurefusion/mfm.py
    4. IEEETIP2023|engine/extre_module/custom_nn/featurefusion/CSFCN.py
    5. BIBM2024|engine/extre_module/custom_nn/featurefusion/mpca.py
    6. ACMMM2024|engine/extre_module/custom_nn/featurefusion/wfu.py
    7. CVPR2025|engine/extre_module/custom_nn/featurefusion/GDSAFusion.py
    8. engine/extre_module/custom_nn/featurefusion/PST.py
    9. TGRS2025|engine/extre_module/custom_nn/featurefusion/MSAM.py
    10. INFFUS2025|engine/extre_module/custom_nn/featurefusion/DPCF.py
    11. CVRP2025|engine/extre_module/custom_nn/featurefusion/LCA.py
    12. TGRS2025|engine/extre_module/custom_nn/featurefusion/HFFE.py

- engine/extre_module/custom_nn/module

    1. AAAI2025|engine/extre_module/custom_nn/module/APBottleneck.py
    2. CVPR2025|engine/extre_module/custom_nn/module/efficientVIM.py
    3. CVPR2023|engine/extre_module/custom_nn/module/fasterblock.py
    4. CVPR2024|engine/extre_module/custom_nn/module/starblock.py
    5. engine/extre_module/custom_nn/module/DWR.py
    6. CVPR2024|engine/extre_module/custom_nn/module/UniRepLKBlock.py
    7. CVPR2025|engine/extre_module/custom_nn/module/mambaout.py
    8. AAAI2024|engine/extre_module/custom_nn/module/DynamicFilter.py
    9. engine/extre_module/custom_nn/module/StripBlock.py
    10. TGRS2024|engine/extre_module/custom_nn/module/elgca.py
    11. CVPR2024|engine/extre_module/custom_nn/module/LEGM.py
    12. ICCV2023|engine/extre_module/custom_nn/module/iRMB.py
    13. TPAMI2025|engine/extre_module/custom_nn/module/MSBlock.py
    14. ICLR2024|engine/extre_module/custom_nn/module/FATBlock.py
    15. CVPR2024|engine/extre_module/custom_nn/module/MSCB.py
    16. engine/extre_module/custom_nn/module/LEGBlock.py
    17. CVPR2025|engine/extre_module/custom_nn/module/RCB.py
    18. ECCV2024|engine/extre_module/custom_nn/module/JDPM.py
    19. CVPR2025|engine/extre_module/custom_nn/module/vHeat.py
    20. CVPR2025|engine/extre_module/custom_nn/module/EBlock.py
    21. CVPR2025|engine/extre_module/custom_nn/module/DBlock.py
    22. ECCV2024|engine/extre_module/custom_nn/module/FMB.py
    23. CVPR2024|engine/extre_module/custom_nn/module/IDWB.py
    24. ECCV2022|engine/extre_module/custom_nn/module/LFE.py
    25. AAAI2025|engine/extre_module/custom_nn/module/FCM.py
    26. CVPR2024|engine/extre_module/custom_nn/module/RepViTBlock.py
    27. CVPR2024|engine/extre_module/custom_nn/module/PKIModule.py
    28. CVPR2024|engine/extre_module/custom_nn/module/camixer.py
    29. ICCV2025|engine/extre_module/custom_nn/module/ESC.py
    30. CVPR2025|engine/extre_module/custom_nn/module/nnWNet.py
    31. TGRS2025|engine/extre_module/custom_nn/module/ARF.py
    32. AAAI2024|engine/extre_module/custom_nn/module/CFBlock.py
    33. IJCV2024|engine/extre_module/custom_nn/module/FMA.py
    34. engine/extre_module/custom_nn/module/LWGA.py
    35. TGRS2025|engine/extre_module/custom_nn/module/CSSC.py
    35. TGRS2025|engine/extre_module/custom_nn/module/CNCM.py
    36. ICCV2025|engine/extre_module/custom_nn/module/HFRB.py
    37. ICIP2025|engine/extre_module/custom_nn/module/EVA.py
    38. CVPR2025|engine/extre_module/custom_nn/module/IEL.py

- engine/extre_module/custom_nn/neck

    1. 自研模块|engine/extre_module/custom_nn/neck/FDPN.py

- engine/extre_module/custom_nn/neck_module

    1. TPAMI2025|engine/extre_module/custom_nn/neck_module/HyperCompute.py
    2. engine/extre_module/custom_nn/neck_module/HyperACE.py
    3. engine/extre_module/custom_nn/neck_module/GoldYOLO.py
    4. AAAI2025|engine/extre_module/custom_nn/neck_module/HS_FPN.py

- engine/extre_module/custom_nn/norm

    1. ICML2024|engine/extre_module/custom_nn/transformer/repbn.py
    2. CVPR2025|engine/extre_module/custom_nn/transformer/dyt.py

- engine/extre_module/custom_nn/transformer

    1. ICLR2025|engine/extre_module/custom_nn/transformer/PolaLinearAttention.py
    2. CVPR2023|engine/extre_module/custom_nn/transformer/biformer.py
    3. CVPR2023|engine/extre_module/custom_nn/transformer/CascadedGroupAttention.py
    4. CVPR2022|engine/extre_module/custom_nn/transformer/DAttention.py
    5. ICLR2022|engine/extre_module/custom_nn/transformer/DPBAttention.py
    6. CVPR2024|engine/extre_module/custom_nn/transformer/AdaptiveSparseSA.py
    7. engine/extre_module/custom_nn/transformer/GSA.py
    8. engine/extre_module/custom_nn/transformer/RSA.py
    9. ECCV2024|engine/extre_module/custom_nn/transformer/FSSA.py
    10. AAAI2025|engine/extre_module/custom_nn/transformer/DilatedGCSA.py
    11. AAAI2025|engine/extre_module/custom_nn/transformer/DilatedMWSA.py
    12. CVPR2024|engine/extre_module/custom_nn/transformer/SHSA.py
    13. IJCAI2024|engine/extre_module/custom_nn/transformer/CTA.py
    13. IJCAI2024|engine/extre_module/custom_nn/transformer/SFA.py
    14. engine/extre_module/custom_nn/transformer/MSLA.py
    15. ACMMM2025|engine/extre_module/custom_nn/transformer/CPIA_SA.py
    16. NN2025|engine/extre_module/custom_nn/transformer/TokenSelectAttention.py
    17. CVPR2025|engine/extre_module/custom_nn/transformer/TAB.py
    19. TPAMI2025|engine/extre_module/custom_nn/transformer/LRSA.py
    20. ICCV2025|engine/extre_module/custom_nn/transformer/MALA.py
    21. ICML2023|engine/extre_module/custom_nn/transformer/MUA.py
    22. ACMMM2025|engine/extre_module/custom_nn/transformer/EGSA.py
    23. ACMMM2025|engine/extre_module/custom_nn/transformer/SWSA.py

- engine/extre_module/custom_nn/mlp

    1. CVPR2024|engine/extre_module/custom_nn/mlp/ConvolutionalGLU.py
    2. IJCAI2024|engine/extre_module/custom_nn/mlp/DFFN.py
    3. ICLR2024|engine/extre_module/custom_nn/mlp/FMFFN.py
    4. CVPR2024|engine/extre_module/custom_nn/mlp/FRFN.py
    5. ECCV2024|engine/extre_module/custom_nn/mlp/EFFN.py 
    6. WACV2025|engine/extre_module/custom_nn/mlp/SEFN.py
    7. ICLR2025|engine/extre_module/custom_nn/mlp/KAN.py
    8. CVPR2025|engine/extre_module/custom_nn/mlp/EDFFN.py
    9. ICVJ2024|engine/extre_module/custom_nn/mlp/DML.py

- engine/extre_module/custom_nn/mamba

    1. AAAI2025|engine/extre_module/custom_nn/mamba/SS2D.py
    2. CVPR2025|engine/extre_module/custom_nn/mamba/ASSM.py
    3. CVPR2025|engine/extre_module/custom_nn/mamba/SAVSS.py
    4. CVPR2025|engine/extre_module/custom_nn/mamba/MobileMamba/mobilemamba.py
    5. CVPR2025|engine/extre_module/custom_nn/mamba/MaIR.py
    6. TGRS2025|engine/extre_module/custom_nn/mamba/GLVSS.py
    7. ICCV2025|engine/extre_module/custom_nn/mamba/VSSD.py
    8. ICCV2025|engine/extre_module/custom_nn/mamba/TinyViM.py
    9. INFFUS2025|engine/extre_module/custom_nn/mamba/CSI.py
    10. TIP2025|engine/extre_module/custom_nn/mamba/SFMB.py

- engine/extre_module/custom_nn/moe

    1. engine/extre_module/custom_nn/moe/moe_module.py

- 积木模块,示例教程engine/extre_module/custom_nn/module/example.py

    1. YOLOV5|C3
    2. YOLOV8|C2f
    3. YOLO11|C3k2
    4. TPAMI2025|MANet
    5. TPAMI2024|MetaFormer_Block
    6. TPAMI2024+CVPR2025|MetaFormer_Mona
    7. TPAMI2024+CVPR2025+WACV2025|MetaFormer_SEFN
    8. TPAMI2024+CVPR2025+WACV2025|MetaFormer_Mona_SEFN

- 创新课程代码<标识着是那个课程中的代码，详细可以去看对应的课程视频>

    1. 顶会中的Partial创新思想课程|engine/extre_module/innovate/CVPR2020_GhostConv.py
    2. 顶会中的Partial创新思想课程|engine/extre_module/innovate/CVPR2023_PartialConv.py
    3. CVPR2025-MobileMamba中的Long-Range WTB-Mamba二次创新|engine/extre_module/innovate/CVPR2025_MobileMamba.py
    4. TGRS2025-HighFrequencyDirectionInjection创新思想课程|engine/extre_module/innovate/TGRS2025_HFDI.py

## 项目内yml一些额外参数说明

1. configs/runtime.yml <plot_train_batch_freq>

    这个参数是控制间隔多少个epcoh保存一次数据增强的图，例如原始设置的12，每隔12个epoch就会把第一个batch的图存下来到output_dir上.

2. configs/runtime.yml <verbose_type>

    这个参数是控制训练阶段的输出是以默认的方式输出还是以进度条的方式输出。参数设置为'origin'就是官方的输出方法，'progress'就是进度条输出方法。

3. configs/runtime.yml <ram_cache>、<cache_imgsz>

    ram_cache设置为True的话会把训练集和验证集的读取数据在开始训练之前载入到内存Ram中，这样能缓解哪些由于读取图片的速度慢导致训练速度慢的问题，但需要注意一点就是这个对内存有一定要求，如果发现设置为True会爆内存就不能用了。
    cache_imgsz就是当ram_cache的参数设置为True的时候，会把数据读取到内存并等比例缩放到cache_imgsz数值的尺寸，除非你需要改输入尺寸，否则这个参数就不用动了，如果你把模型的输入尺寸改成1024，那这个参数也建议改成1024。
    更详细的说明可以看B视频：https://www.bilibili.com/video/BV1r5jnzHEjG/

4. configs/runtime.yml <yolo_metrice>

    设置为True后，训练的每个epoch或者test-only的状态下都会多输出YOLO指标。  
    202512更新后，会在test-only的状态下输出混淆矩阵。

5. configs/test/dfine_hgnetv2_m_pcb.yml <no_weight_vfl_epoch>

    前多少个epoch关闭vfl/mal中的weight分配。详细作用可以看这期视频：https://www.bilibili.com/video/BV1bihCziEZf/

6. configs/test/visdrone2019.yml <using_tiny_metrice>

    设置为True后，COCO指标会多一个tiny目标的精度。

    默认：
    | 类别 | 面积范围（像素²） | 边长范围（像素） | 说明 |
    |------|------------------|-----------------|------|
    | **small** | 0 ~ 1,024 | 0 ~ 32 | 小目标：边长小于 32 像素的目标 |
    | **medium** | 1,024 ~ 9,216 | 32 ~ 96 | 中等目标：边长在 32-96 像素之间 |
    | **large** | 9,216+ | 96+ | 大目标：边长大于 96 像素的目标 |

    使用using_tiny_metrice后：
    | 类别 | 面积范围（像素²） | 边长范围（像素） | 说明 |
    |------|------------------|-----------------|------|
    | **tiny** | 0 ~ 256 | 0 ~ 16 | 微小目标：边长小于 16 像素 |
    | **small** | 256 ~ 1,024 | 16 ~ 32 | 小目标：边长在 16-32 像素之间 |
    | **medium** | 1,024 ~ 9,216 | 32 ~ 96 | 中等目标：边长在 32-96 像素之间 |
    | **large** | 9,216+ | 96+ | 大目标：边长大于 96 像素 |

7. configs/test/visdrone2019.yml <max_dets>

    每张图像中最多考虑的检测框数量，默认为100，对于复杂的场景或者多目标的场景可以设置更大，例如300。

## 训练策略建议方案

1. 基准模型的选择。

    - nsmlx版本选择  
        统一建议选择n，因为训练成本最低，也意味着更快出结果。
    - baseline的选择  
        建议DEIM、DFine、DFine-MAL，如果你觉得DEIM的数据增强火力全开阶段太慢的话，就建议DFine或者DFine-MAL，这两个就看哪个效果好就选那个。  

2. AMP是否使用？

    非常不建议使用，DETR类模型在fp16下训练会比较容易出NAN，就算基准模型没出现也不代表后续改进不会遇到。

3. 预训练权重是否使用？

    非常不建议使用，有很多朋友反映去掉预训练后效果差非常多，结合这边我自己训练的经验给出大家一些建议，先分别跑一遍带主干预训练权重和不带主干预训练权重，然后分以下几种情况。  
    1. 带主干预训练权重和不带主干预训练权重差距在3个点内，这种情况建议就直接忽略，直接用不带主干预训练权重的即可，也不需要加训练次数和调整学习率。
    2. 带主干预训练权重和不带主干预训练权重差距在3-10个点内，这种情况一般可以通过tensorboard可视化看精度曲线的上升程度，一般来说差距这么大的话，曲线还是很明显往上涨的话，那就增加训练次数去实验。
    3. 不带预训练权重直接很难收敛或者差距几十个点，建议统一batchsize设置为4，然后学习率统一设置为0.0001，训练次数设置300去实验，一般来说这样跑精度差距就会少很多。

4. 是否一定要训练到精度曲线完全收敛？

    对于我个人的意见，如果你是上述第三点的第一小点的情况，我建议就不用管了，如果是上述第三点的其他情况，也不一定要说完全收敛，但是建议按照上述的建议尽量降低与使用了预训练权重的精度差距就行。

5. 一般来说小模型训练的次数要比大模型训练的次数要多，因为参数少，训练难度大，所以对于部分比较难收敛的，可以考虑换更大尺寸的模型，这个具体就要训练看看，究竟那个尺寸的模型综合性能较好(训练时间+精度的衡量)。

6. 建议关闭多尺度训练，不然有些模块可能不支持使用，因为有些模块要求输入的特征图尺寸是固定的，多尺度的话不满足此条件，如何关闭多尺度训练请看下方常见问题及解决方案第五点。

7. 如果没有预训练权重按照上述的方案调整还是效果非常不理想的话，可以看[CVPR2025-DEIM|新一代目标检测SOTA|基础课程二十-按照基础课程十六操作后训练精度还是不理想，那可不可以在带预训练的基础上尽可能改动主干？](https://www.bilibili.com/video/BV1SRjMzvE2b/)

8. 如何按照上述的还是很不理想、甚至精度一直为0附近之类的问题，可以看这期视频[CVPR2025-DEIM|新一代目标检测SOTA|基础课程二十一-模型一直训练不好，精度一直都是0，学习率一些基础的参数都调过了，怎么办？](https://www.bilibili.com/video/BV1bihCziEZf/) 

9. 如果精度还是很异常的话，可以按照B站CVPR2025-DEIM基础课程十六中的示例<示例文档在群文件中的重要文件文件夹中>整理好数据私聊发我，我会给你一些训练意见。

## 常见问题及解决方案

1. windows用户会出现：CUDA_VISIBLE_DEVICES 命令不存在的问题

    统一到train.py顶部的os.environ["CUDA_VISIBLE_DEVICES"]进行设置，然后命令就不需要前面的CUDA_VISIBLE_DEVICES=xxx了。

2. OverflowError: Python integer -x out of bounds for uint8

    例如我的报错信息如下：
    [rank0]:   File "/home/user/anaconda3/envs/torch_2_3_0_py310/lib/python3.10/site-packages/torchvision/transforms/_functional_pil.py", line 114, in adjust_hue
    [rank0]:     np_h += np.uint8(hue_factor * 255)
    [rank0]: OverflowError: Python integer -3 out of bounds for uint8

    我们需要找到/home/user/anaconda3/envs/torch_2_3_0_py310/lib/python3.10/site-packages/torchvision/transforms/_functional_pil.py这个文件中的第114行 把对应 np_h += np.uint8(hue_factor * 255) 代码改为 np_h += np.clip(hue_factor * 255, 0, 255).astype(np.uint8)

    有些同学也反应把numpy降到1.x版本就可以解决，也可以试试这个。

3. assert (boxes1[:, 2:] >= boxes1[:, :2]).all()

    File "/root/DEIM/engine/deim/box_ops.py", line 53, in generalized_box_iou
        assert (boxes1[:, 2:] >= boxes1[:, :2]).all()
    AssertionError

    解决方案：关闭AMP,如果没开AMP还是出现的话降低BatchSize,最好是4或者8.

4. 刚开始训练就出现以下大面积的这种错

    ../aten/src/ATen/native/cuda/IndexKernel.cu:92: operator(): block: [102,0,0], thread: [102,0,0] Assertion `-sizes[i] <= index && index < sizes[i] && "index out of bounds"` failed.
    ../aten/src/ATen/native/cuda/IndexKernel.cu:92: operator(): block: [102,0,0], thread: [104,0,0] Assertion `-sizes[i] <= index && index < sizes[i] && "index out of bounds"` failed.
    ../aten/src/ATen/native/cuda/IndexKernel.cu:92: operator(): block: [102,0,0], thread: [111,0,0] Assertion `-sizes[i] <= index && index < sizes[i] && "index out of bounds"` failed.

    数据集的yml中的类别数没设置好，跟真实数据集中的类别数目不一样。<例如数据集中标签是从1开始的，这个情况可以修改下标签的生成代码，修改为从0开始>

5. 如何关闭多尺度训练？

    在yml中添加以下参数：
    '''
    train_dataloader:
        collate_fn:
            base_size_repeat: ~ # 这个就是关闭多尺度训练的关键
    '''

6. 训练不小心中断了，怎么进行断点续训？

    假设我正常的训练命令是：CUDA_VISIBLE_DEVICES=0 torchrun --master_port=7777 --nproc_per_node=1 train.py -c configs/dfine/dfine_hgnetv2_n_custom.yml --seed=0  
    断点续训的命令是：CUDA_VISIBLE_DEVICES=0 torchrun --master_port=7777 --nproc_per_node=1 train.py -c configs/dfine/dfine_hgnetv2_n_custom.yml --seed=0 -r outputs/dfine_hgnetv2_n_custom/last.pth  
    简单来说就是在原先的命令上加上"-r last.pth"

7. 部分模块的py中输出的计算量需要去修改一下calflops库的代码，不修改只是影响单独运行对应的py文件会报错，不影响整体训练和使用。

    控制台输入:conda env list可以找到对应虚拟环境的位置，例如我的输出是：  

        # conda environments:
        #
        base                     /opt/miniconda
        pytorch_2_2_2_py39    *  /root/code/conda/env/pytorch_2_2_2_py39
    
    1. 在对应我的目录下找到/root/code/conda/env/pytorch_2_2_2_py39/lib/python3.9/site-packages/calflops/flops_counter.py(对于你们的环境应该是conda显示的环境后面接上lib/python3.9/site-packages/calflops/flops_counter.py)，然后在群文件中的重要文件文件夹中找到flops_counter.py这个文件把里面的函数覆盖到上述的文件对应的函数即可，注意不是文件替换，是函数替换！

    2. 在对应我的目录下找到/root/code/conda/env/pytorch_2_2_2_py39/lib/python3.9/site-packages/calflops/pytorch_ops.py(对于你们的环境应该是conda显示的环境后面接上lib/python3.9/site-packages/calflops/pytorch_ops.py)，然后在群文件中的重要文件文件夹中找到pytorch_ops.py这个文件把里面的函数覆盖到上述的文件对应的函数即可，注意不是文件替换，是函数替换！

8. 训练的时候出现以下报错

    labels = [category2label[obj["category_id"]] for obj in anno]
    KeyError: x

    数据集的yml配置文件设置 remap_mscoco_category:False

9. 如何关闭预训练权重？

    可以在项目内全局搜索pretrained的参数，会发现这个参数在yml的backbone部分会存在，在自己最外层的yml对应的主干部分设定pretrained: False即可，具体可以参考：configs/base/dfine_hgnetv2.yml 这个配置文件。

10. 这个项目中的best模型是根据什么来判断的？

    根据ap50-95来判断，详细代码在：engine/solver/det_solver.py 159行附近。

11. [rank0]: RuntimeError: Expected to have finished reduction in the prior iteration before starting a new one. This error indicates that your module has parameters that were not used in producing loss. You can enable unused parameter detection by passing the keyword argument `find_unused_parameters=True` to `torch.nn.parallel.DistributedDataParallel`, and by 
[rank0]: making sure all `forward` function outputs participate in calculating loss.

    在configs/runtime.yml这个文件里面把find_unused_parameters设置为True。

12. configs里的deim、deimv2、deim_dfine、deim_rtdetrv2、dfine、rtdetrv2、cfg、cfg-improve、yaml的文件夹代表什么意思？

    首先deim的论文提出了一种训练策略+损失函数，所以deim是不会改变网络结构的。<这里指的是cvpr2025-deim，可以理解为deimv1>
    deim文件夹里面是deim_dfine的配置文件，代表在dfine的基础上用上了deim提出的训练策略+mal损失函数。
    deimv2文件夹是deimv2版本的配置文件。
    deim_dfine是官方自带的，里面包含deim_dfine和dfine。
    deim_rtdetrv2文件夹里面就是rtdetrv2的基础上用上了deim提出的训练策略+mal损失函数。
    dfine文件夹里面就是普通的dfine配置文件。
    rtdetrv2文件夹里面就是普通的rtdetrv2配置文件。
    cfg、cfg-improve、yaml文件夹都是Ultralytics版本的配置文件，详细看VideoBaiduYun.txt中的视频链接。

13. best_stg1.pth和best_stg2.pth的相关问题

    在B站的基础课程就说过最后no_aug阶段为stg2，如果同时出现stg1和stg2，最终测试的时候用stg2，如果没有stg2只有stg1，那就代表stg2的情况没有比stg1更好，所以没有best_stg2.pth，这个时候就用stg1进行测试。

14. DINOV3相关预训练权重链接

    https://pan.baidu.com/s/1mWPPRdDKqM8GMleHcDB33Q?pwd=esp5

15. 如何修改训练的图像尺寸(示例可以去参考configs/deimv2/deimv2_hgnetv2_femto_coco.yml)

    1. 在yml配置文件部分train_dataloader,val_dataloader中修改Resize的参数，修改成你自己需要的分辨率。
    2. 在yml配置文件部分添加eval_spatial_size参数，比如你改为[416, 416]，那么就是eval_spatial_size: [416, 416]。  

### 更新日志

- 20250330

    1. 初版项目发布.

- 20250413

    1. 新增多个改进模块并新增模块简介，位置在engine/extre_module/module_images内。
    2. 新增训练和测试阶段的进度条显示。
    3. 优化tensorboard中的精度名称显示。
    4. 优化输出，把重要信息换颜色显示。
    5. 新增plot_train_batch_freq参数，用于控制间隔多少epoch保存第一个batch中的数据增强后的图像，默认为12。
    6. 新增保存当前参数信息，会自动保存到output_dir中的args.json文件内。
    7. 优化output_dir保存逻辑，当判断output_dir路径存在的时候，会自动在后缀加1，避免覆盖原先代码。

- 20250419

    1. 新增verbose_type参数，用于控制使用默认还是进度条输出，默认为官方默认输出形式。
    2. 新增thop计算模型计算量方式，避免calflops对于部分算子出现不支持报错的操作。
    3. 完善每个模块的py文件，增加输出计算量和参数量等数值，方便用户后续调试。
    4. 给DataLoader中添加pin_memory参数为True，可以在训练时候如果是数据加载成为瓶颈，可以提高速度。
    5. 修复用户反馈的已知问题。
    6. 新增多个改进模块。

- 20250422

    1. 新增train.py在test-only的状态下输出模型权重大小、计算量、参数量指标、TIDE指标、保存预测结果的coco-json文件。
    2. 完善tools/inference/torch_inf.py功能，支持指定单张图片、单个视频、完整文件夹推理，支持指定输出路径，支持指定置信度。
    3. 新增热力图脚本、特征图脚本。
    4. 修复用户反馈的已知问题。
    5. 新增多个改进模块。

- 20250429

    1. 修复engine/extre_module/custom_nn/attention/SEAM.py模块，应该是MutilSEAM。
    2. 新增一些进阶课程的视频。
    3. 新增多个改进模块。
    4. 修复用户反馈的已知问题。
    5. 修复续训时候会新增一个保存路径的问题。
    6. 修复多卡训练Stage2的时候会出现部分进程找不到权重文件的问题。

- 20250514

    1. 新增一些进阶课程的视频。
    2. 新增多个改进模块。
    3. 修复用户反馈的已知问题。

- 20250526

    1. 新增一些进阶课程的视频。
    2. 新增多个改进模块。
    3. 新增cache_ram参数，详细可以看userguide。
    4. 修复在torch2.7.0下出现的NotImplementedError问题。

- 20250609

    1. 修复新增了cache_ram功能后训练COCO数据集精度不正常的问题。
    2. 修复在训练COCO数据集中数据增强的绘制BUG。
    3. 新增多个改进模块。
    4. 新增一些进阶课程的视频。
    5. 修复用户反馈的已知问题。

- 20250614

    1. 新增Ultralytics的配置文件方式，大大降低改进难度。
    2. 新增一些<Ultralytics的配置文件方式>进阶课程的视频。
    3. 新增多个改进模块。

- 20250617

    1. 修复配置文件中层序号有误的问题。

- 20250619

    1. 修复配置文件中层序号有误的问题。
    2. 新增多个改进模块。
    3. 新增一些<Ultralytics的配置文件方式>进阶课程的视频。

- 20250625

    1. 修复best_stg2保存异常的问题。
    2. 新增YOLOV13中的HyperACE模块。
    3. 新增多个关于<Ultralytics的配置文件方式>进阶课程的视频。

- 20250705

    1. 新增多个改进模块。
    2. 新增多个关于<Ultralytics的配置文件方式>进阶课程的视频。
    3. 新增20250704基础疑问解答直播回放链接。

- 20250714

    1. 新增多个改进模块。
    2. 新增多个关于<Ultralytics的配置文件方式>进阶课程的视频。
    3. 新增小目标检测网络架构专题一群课题直播回放。

- 20250726

    1. 新增在test-only的状态下输出每个类别的'mAP', 'mAP_50', 'mAP_75', 'mAP_s', 'mAP_m', 'mAP_l'。
    2. 新增多个改进模块。
    3. 修复用户反馈的已知问题。
    4. 新增一个JSON格式数据集脚本。(输出类别数和类别id、输出每个类别的实例数量)

- 20250817

    1. 新增支持蒸馏学习，蒸馏学习支持断点续训使用方法跟正常训练一样。
    2. 蒸馏学习支持特征蒸馏、逻辑蒸馏、特征+逻辑蒸馏 这三种方式。
    3. 无论是Ultralytics配置文件方式、还是原始的代码方式都支持相互蒸馏。
    4. 蒸馏学习支持控制epoch，例如只有前50epoch进行蒸馏学习，后50epoch关闭蒸馏学习。
    5. 更多细节请看关于<知识蒸馏教学视频>的进阶课程。
    6. 支持输出YOLO指标(Precision、Recall、F1-Score、mAP50、mAP75、mAP50-95)，详细请看userguide。
    7. 新增多个改进模块。
    8. 新增小目标检测网络架构专题二链接。

- 20250823

    1. 修复YOLO指标在一些图片没真实标签的时候报错的bug。
    2. 开放逻辑蒸馏，在项目内有对应的课程。
    3. 新增多个改进模块。
    4. 新增<知识蒸馏教学视频>的进阶课程。

- 20250907

    1. 新增多个改进模块。
    2. 修复蒸馏学习中教师信息输出错误的问题。

- 20250920

    1. 新增导出脚本(export.py)，支持导出onnx、tensorrt模型。
    2. 重构大部分输出，增加输出对应的时间、文件、函数、行数，以便用户快速定位。
    3. 新增20250910直播回放链接。
    4. 修复一些已知BUG。
    5. 完善onnx、tensorrt模型推理脚本。
    6. 支持在train.py test-only状态下中使用onnx、tensorrt模型进行验证。
    7. 新增<模型导出>相关教程视频。
    8. 新增多个改进模块。
    9. 支持DINOV3(ConvNext、ViT)作为主干进行微调。<教程在百度云创新课题的第五点>

- 20251012

    1. 移植DEIMV2到本项目，暂只支持原始的代码修改方式。
    2. 更新UserGuide。
    3. 新增<DEIMV2说明视频>。
    4. 修复一些已知问题。

- 20251025

    1. 新增DQ-DETR的模块。
    2. 新增多个改进模块。
    3. 新增<DQ-DETR改进点>的相关教程视频。
    4. 修复一些已知问题。

- 20251102

    1. 新增<DQ-DETR改进点>的相关教程视频。
    2. 修复一些已知问题。

- 20251115

    1. 新增以DensityMap为主导的创新课程[DFINE with Density-aware Query Selection]。
    2. 修复一些已知问题。

- 20251207

    1. 新增在test-only状态下，yolo-metrice支持保存混淆矩阵。
    2. 新增DFine、DEIM实例分割的实现，使用相关请看进阶教程实例分割部分。
    3. 更新dataset/coco_analyzer.py脚本，支持输出数据集中更多的内容，以便分析数据集的特点。
    4. 新增tools/visualization/tp_fp_fn_analysis.py脚本，用于分析检测结果中的tp、fp、fn。
    5. 新增多个改进模块。
    6. 修复一些已知问题。
    7. 新增<TGRS2025-HighFrequencyDirectionInjection创新思想课程>。
    8. 新增基于ByteTrack的目标跟踪，教程请看进阶教程内的<目标跟踪ByteTrack的使用教程>。

- 20251213

    1. 参考CVPR2022-MaskDINO重构实例分割检测头代码。
    2. 修复在ram_cache状态下实例分割数据集部分存在的BUG。
    3. 重新录制实例分割部分的进阶视频。

- 20251224

    1. 新增多个改进模块。
    2. 修复实例分割部分已知的问题。
    3. 新增以DensityMap为主导的实例分割检测头内容[DFINESeg with Density-aware Query Selection]。
    4. 新增[DFINESeg with Density-aware Query Selection]的使用视频教程。
    5. 更新实例分割实现讲解。

- 20251226

    1. 修复一些已知问题。
    2. 新增基于COCO-Tiny指标，并支持输出每类COCO-Tiny指标，详细请看UserGuide.md中的<项目内yml一些额外参数说明>。

- 20260109

    1. 修复一些已知问题。
    2. 新增<ES-MoE>动态路由网络模块。
    3. 更新视频链接。

- 20260128

    1. 修复一些已知问题。
    2. 新增多个改进模块。
    3. 新增<ES-MoE>动态路由网络教程视频。
    4. 新增<TPAMI2025 YOLO-MS>的MSBlock和GQL的教程视频。

### 魔鬼面具专属调试链接

python train.py -c configs/test/dfine_1.yml --seed=0
CUDA_VISIBLE_DEVICES=0 python train.py -c configs/dfine/dfine_hgnetv2_n_custom.yml --seed=0
CUDA_VISIBLE_DEVICES=0 python train.py -c configs/dfine/dfine_hgnetv2_n_custom.yml --seed=0 -r outputs/dfine_hgnetv2_n_custom/last.pth
CUDA_VISIBLE_DEVICES=0 python train.py -c configs/dfine/dfine_hgnetv2_n_custom.yml --test-only -r outputs/dfine_hgnetv2_n_custom/last.pth
CUDA_VISIBLE_DEVICES=0 python train.py -c configs/test/dfine_hgnetv2_n_visdrone.yml --seed=0
CUDA_VISIBLE_DEVICES=0 python train.py -c configs/test/deim_hgnetv2_s_visdrone.yml --test-only -r ../best_stg2.pth
python tools/inference/torch_inf.py -c configs/test/deim_hgnetv2_s_visdrone.yml -r ../best_stg2.pth --input /home/dataset/dataset_visdrone/VisDrone2019-DET-test-dev/images/9999938_00000_d_0000380.jpg -o inference_result/exp -t 0.5
python tools/inference/torch_inf.py -c configs/test/deim_hgnetv2_s_visdrone.yml -r ../best_stg2.pth --input /home/dataset/dataset_visdrone/VisDrone2019-DET-test-dev/images -o inference_result/exp -t 0.4
python distill.py -sc configs/test/deim_hgnetv2_s_visdrone_distill.yml -tc configs/test/deim_hgnetv2_s_visdrone.yml -tw ../best_stg2.pth
python distill.py -sc configs/test/deim_hgnetv2_s_visdrone_distill.yml -tc configs/test/dfine_hgnetv2_n_visdrone.yml -tw ../best_stg2.pth
python distill.py -sc configs/test/dfine_hgnetv2_n_visdrone_distill.yml -tc configs/test/dfine_hgnetv2_n_visdrone.yml -tw ../best_stg2.pth
python distill.py -sc configs/test/deim_hgnetv2_s_visdrone_distill.yml -tc configs/test/dfine_hgnetv2_test.yml -tw ../best_stg1.pth
python distill.py -sc configs/test/deim_hgnetv2_s_visdrone_distill.yml -tc configs/test/dfine_hgnetv2_test.yml -tw ../best_stg1.pth -r outputs/deim_hgnetv2_s_custom/last.pth

python distill.py -sc configs/test/dfine_hgnetv2_n_test.yaml -tc configs/test/dfine_hgnetv2_test.yml -tw outputs/dfine-s-mg/last.pth
python distill.py -sc configs/test/dfine_hgnetv2_n_test.yaml -tc configs/test/deim_hgnetv2_s_visdrone.yml -tw outputs/deim_hgnetv2_s_custom/last.pth
python distill.py -sc configs/test/dfine_hgnetv2_n_visdrone_distill.yml -tc configs/test/deim_hgnetv2_s_visdrone.yml -tw outputs/deim_hgnetv2_s_custom/last.pth

python export.py -c configs/test/dfine_hgnetv2_n_visdrone.yml -r best_stg2.pth
python tools/inference/torch_inf.py -c configs/test/dfine_hgnetv2_n_visdrone.yml -r best_stg2.pth -i /root/dataset/dataset_visdrone/VisDrone2019-DET-test-challenge/images
python tools/inference/onnx_inf.py -p best_stg2.onnx -i /root/dataset/dataset_visdrone/VisDrone2019-DET-test-challenge/images
python tools/inference/trt_inf.py -p best_stg2.engine -i /root/dataset/dataset_visdrone/VisDrone2019-DET-test-challenge/images

python train.py -c configs/test/dfine_hgnetv2_test.yml -p outputs/dfine-s-mg/best_stg1.onnx --test-only

python tools/inference/torch_inf.py -c configs/test/dqs_dfine_dinov3_s_visdrone.yml -r outputs/dqs_dfine_dinov3_s_visdrone6/best_stg2.pth -i /root/dataset/dataset_visdrone/VisDrone2019-DET-train/images/9999940_00000_d_0000024.jpg

python export.py -c configs/test/dfine_hgnetv2_n_seg.yml -r outputs/dfine_hgnetv2_n_car/best_stg1.pth --format engine
python train.py -c configs/test/dfine_hgnetv2_n_seg.yml -r outputs/dfine_hgnetv2_n_car/best_stg1.pth --test-only
python train.py -c configs/test/dfine_hgnetv2_n_seg.yml -p outputs/dfine_hgnetv2_n_car/best_stg1.engine -m mask --test-only
python tools/inference/segment/trt_inf.py -p outputs/dfine_hgnetv2_n_car/best_stg1.engine -i /root/code/project/dataset_seg/valid
python tools/inference/segment/onnx_inf.py -p outputs/dfine_hgnetv2_n_car/best_stg1.onnx -i /root/code/project/dataset_seg/valid

python tools/inference/segment/torch_inf.py -c configs/test/dfine_hgnetv2_s_seg.yml -r outputs/dfine_hgnetv2_s_seg/best_stg1.pth -i /root/dataset/cococutmark/images
python train.py -c configs/test/dfine_hgnetv2_s_seg.yml -r outputs/dfine_hgnetv2_s_seg/best_stg2.pth --test-only