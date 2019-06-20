import numpy as np
import cv2 as cv


oldx, oldy = -1, -1


def on_mouse(event, x, y, flags, _):
    global oldx, oldy

    if event == cv.EVENT_LBUTTONDOWN:
        oldx, oldy = x, y

    elif event == cv.EVENT_LBUTTONUP:
        oldx, oldy = -1, -1

    elif event == cv.EVENT_MOUSEMOVE:
        if flags & cv.EVENT_FLAG_LBUTTON:
            cv.line(img, (oldx, oldy), (x, y), (255, 255, 255), 40, cv.LINE_AA)
            oldx, oldy = x, y
            cv.imshow('img', img)


# Generate training samples and labels

digits = cv.imread('digits.png', cv.IMREAD_GRAYSCALE)

if digits is None:
    print('Image load failed!')
    exit()

h, w = digits.shape[:2]
hog = cv.HOGDescriptor((20, 20), (10, 10), (5, 5), (5, 5), 9)

cells = [np.hsplit(row, w//20) for row in np.vsplit(digits, h//20)]
cells = np.array(cells)
cells = cells.reshape(-1, 20, 20)

desc = []
for img in cells:
    dd = hog.compute(img)
    desc.append(dd)

train_desc = np.array(desc).squeeze().astype(np.float32)
train_labels = np.repeat(np.arange(10), len(train_desc)/10)

# Training SVM

svm = cv.ml.SVM_create()
svm.setType(cv.ml.SVM_C_SVC)
svm.setKernel(cv.ml.SVM_RBF)
svm.setC(2.5)
svm.setGamma(0.50625)
svm.train(train_desc, cv.ml.ROW_SAMPLE, train_labels)

# Tests

img = np.zeros((400, 400), np.uint8)

cv.imshow('img', img)
cv.setMouseCallback('img', on_mouse)

while True:
    c = cv.waitKey()

    if c == 27:
        break
    elif c == ord(' '):
        img_resize = cv.resize(img, (20, 20), interpolation=cv.INTER_AREA)

        desc = hog.compute(img_resize)
        test_desc = np.array(desc).astype(np.float32)

        _, res = svm.predict(test_desc.T)
        print(int(res[0, 0]))

        img.fill(0)
        cv.imshow('img', img)

cv.destroyAllWindows()
