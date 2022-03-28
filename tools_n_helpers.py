import cv2
from datetime import datetime

def curDateTime():
    now = datetime.now()
    return now.strftime("%Y_%m.%d.%H.%M.%S.%f")

def putTexts(img, texts, org, v_step, h_shep, clr, scale):
    n_org = org
    for text in texts:
        if n_org[0] >= img.shape[1] or n_org[1] >= img.shape[0]:
            break
        cv2.putText(
            img,
            text,
            n_org,
            cv2.FONT_HERSHEY_PLAIN,
            scale,
            clr,
            2
        )
        n_org = (n_org[0] + h_shep, n_org[1] + v_step)
    return n_org