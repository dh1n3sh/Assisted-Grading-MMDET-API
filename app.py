import uvicorn
from fastapi import FastAPI, File, UploadFile
from mmdet.apis import init_detector, inference_detector
import numpy as np
from tempfile import NamedTemporaryFile
from pathlib import Path
import shutil

app = FastAPI()
model_path = './model/epoch_12.pth'
config_path = './model/full_config.py'
mmdet_model = init_detector(config_path, model_path, device='cuda:0')

'''
Function that preforms NMS for the given bounding boxes and threshold
'''
def non_max_suppression_fast(boxes, overlapThresh):
	# if there are no boxes, return an empty list
	if len(boxes) == 0:
		return []
	# if the bounding boxes integers, convert them to floats --
	# this is important since we'll be doing a bunch of divisions
	if boxes.dtype.kind == "i":
		boxes = boxes.astype("float")
	# initialize the list of picked indexes	
	pick = []
	# grab the coordinates of the bounding boxes
	x1 = boxes[:,0]
	y1 = boxes[:,1]
	x2 = boxes[:,2]
	y2 = boxes[:,3]
	# compute the area of the bounding boxes and sort the bounding
	# boxes by the bottom-right y-coordinate of the bounding box
	area = (x2 - x1 + 1) * (y2 - y1 + 1)
	idxs = np.argsort(y2)
	# keep looping while some indexes still remain in the indexes
	# list
	while len(idxs) > 0:
		# grab the last index in the indexes list and add the
		# index value to the list of picked indexes
		last = len(idxs) - 1
		i = idxs[last]
		pick.append(i)
		# find the largest (x, y) coordinates for the start of
		# the bounding box and the smallest (x, y) coordinates
		# for the end of the bounding box
		xx1 = np.maximum(x1[i], x1[idxs[:last]])
		yy1 = np.maximum(y1[i], y1[idxs[:last]])
		xx2 = np.minimum(x2[i], x2[idxs[:last]])
		yy2 = np.minimum(y2[i], y2[idxs[:last]])
		# compute the width and height of the bounding box
		w = np.maximum(0, xx2 - xx1 + 1)
		h = np.maximum(0, yy2 - yy1 + 1)
		# compute the ratio of overlap
		overlap = (w * h) / area[idxs[:last]]
		# delete all indexes from the index list that have
		idxs = np.delete(idxs, np.concatenate(([last],
			np.where(overlap > overlapThresh)[0])))
	# return only the bounding boxes that were picked using the
	# integer data type
	return boxes[pick].astype("int")

@app.post('/detect/')
async def create_file(answer_image: UploadFile = File(...)):
	'''
	Endpoint to run answer script segmentation
	'''
	result = 'failure'
	try:
		suffix = Path(answer_image.filename).suffix
		with NamedTemporaryFile(delete=True, suffix=suffix) as tmp:
			shutil.copyfileobj(answer_image.file, tmp)
			tmp_path = Path(tmp.name)
			result = inference_detector(mmdet_model, tmp_path)
			thresholdedResult = np.array(list(filter(lambda x : x[-1] > 0.4 , result[0][0])))  
			final_result = non_max_suppression_fast(thresholdedResult, .4)  
			if(final_result!=[]):
				final_result = final_result.tolist()
			print(answer_image.filename,final_result)
	finally:
		answer_image.file.close()

	return {"answer_bboxes": final_result}


if __name__ == '__main__':
	uvicorn.run(app, host='127.0.0.1', port=8008)