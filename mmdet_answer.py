from mmdet.apis import init_detector, inference_detector
import numpy as np
mmdet_model = init_detector('./full_config.py', './epoch_12.pth', device='cuda:0')
image_path = '1.png'
result = inference_detector(mmdet_model, image_path)
thresholdedResult = np.array(list(filter(lambda x : x[-1] > 0 , result[0][0])))  
final_result = non_max_suppression_fast(thresholdedResult, .4) 
print(result[0][0].tolist() )
