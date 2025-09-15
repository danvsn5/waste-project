from typing import List, Dict, Any

def bbox_iou(boxA, boxB):
    # boxA and boxB: [x, y, width, height]
    xA = max(boxA[0] - boxA[2]/2, boxB[0] - boxB[2]/2)
    yA = max(boxA[1] - boxA[3]/2, boxB[1] - boxB[3]/2)
    xB = min(boxA[0] + boxA[2]/2, boxB[0] + boxB[2]/2)
    yB = min(boxA[1] + boxA[3]/2, boxB[1] + boxB[3]/2)

    interArea = max(0, xB - xA) * max(0, yB - yA)
    boxAArea = boxA[2] * boxA[3]
    boxBArea = boxB[2] * boxB[3]
    if boxAArea + boxBArea - interArea == 0:
        return 0
    iou = interArea / float(boxAArea + boxBArea - interArea)
    return iou

def is_same_object(new_det, existing_det, iou_threshold=0.5):
    boxA = [new_det["x"], new_det["y"], new_det["width"], new_det["height"]]
    boxB = [existing_det["x"], existing_det["y"], existing_det["width"], existing_det["height"]]
    return bbox_iou(boxA, boxB) > iou_threshold and new_det["class"] == existing_det["class"]

def process_detections(detections: List[Dict[str, Any]], bin_state: List[Dict[str, Any]], iou_threshold=0.5):
    new_objects = []
    for detection in detections:
        is_duplicate = False
        for existing in bin_state:
            if is_same_object(detection, existing, iou_threshold):
                is_duplicate = True
                break
        if not is_duplicate:
            bin_state.append(detection)
            new_objects.append(detection)
    return new_objects