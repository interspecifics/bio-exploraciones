import numpy as np
import cv2
from tracker import CentroidTracker

# trackeo
ct = CentroidTracker()
(H, W) = (640, 480)

# cámara
cap = cv2.VideoCapture(2)
kernel = np.ones((2,2),np.uint8)

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()
   
    # Our operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (7, 7), 0)
    gray= cv2.medianBlur(gray, 3)   #to remove salt and paper noise
    gray = 255-gray
    #to binary
    ret,thresh = cv2.threshold(gray,128,255,0)  #to detect white objects
    #to get outer boundery only     
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_GRADIENT, kernel)
    #to strength week pixels
    thresh = cv2.dilate(thresh,kernel,iterations = 5)

    #
    contours,hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    #contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    for k,c in enumerate(contours):
        rect = cv2.boundingRect(c)
    #    if rect[2] < 100 or rect[3] < 100: continue
    #    #print cv2.contourArea(c)
        x,y,w,h = rect
        cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,255),1)
    #    cv2.putText(frame,'{}'.format(k),(x+w+10,y+h),0,0.3,(0,255,0))

    rects = [cv2.boundingRect(c) for c in contours]
    objects = ct.update(rects)

	# loop over the tracked objects
    for (objectID, centroid) in objects.items():
		# draw both the ID of the object and the centroid of the
		# object on the output frame
        text = "ID {}".format(objectID)
        cv2.putText(frame, text, (centroid[0] - 10, centroid[1] - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.circle(frame, (centroid[0], centroid[1]),2, (0, 255, 0), -1)



    # Display the resulting frame
    cv2.imshow('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()