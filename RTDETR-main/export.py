import warnings
warnings.filterwarnings('ignore')
from ultralytics import RTDETR

# onnx onnxsim onnxruntime onnxruntime-gpu

# 导出参数官方详解链接：https://docs.ultralytics.com/modes/export/#usage-examples

if __name__ == '__main__':
    model = RTDETR('rtdetr-weight-path')
    model.export(format='onnx', simplify=True)
    # 导出tensorrt模型，本项目的detect.py不支持用tensorrt导出的模型测试，如需测试请去官方Ultralytics中使用，使用方法也是一样
    # model.export(format='engine', simplify=True) 