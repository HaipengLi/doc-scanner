from transform import four_point_transform
from skimage.filters import threshold_local
import argparse
import cv2
import imutils


def transform(orig, ratio, screen_cnt):
    warped = four_point_transform(orig, screen_cnt.reshape(4, 2) * ratio)

    # convert the warped image to grayscale, then threshold it
    # to give it that 'black and white' paper effect
    warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
    T = threshold_local(warped, 11, offset=10, method="gaussian")
    warped = (warped > T).astype("uint8") * 255

    # show the original and scanned images
    print("STEP 3: Apply perspective transform")
    cv2.imshow("Original", imutils.resize(orig, height=650))
    cv2.imshow("Scanned", imutils.resize(warped, height=650))
    cv2.waitKey(0)


def find_contours(ori_img, edged_img):
    cnts = cv2.findContours(edged_img.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if imutils.is_cv2() else cnts[1]
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:5]

    # loop over the contours
    for c in cnts:
        # approximate the contour
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)

        # if our approximated contour has four points, then we
        # can assume that we have found our screen
        if len(approx) == 4:
            screen_cnt = approx
            break

    # show the contour (outline) of the piece of paper
    print("STEP 2: Find contours of paper")
    cv2.drawContours(ori_img, [screen_cnt], -1, (0, 255, 0), 2)
    cv2.imshow("Outline", ori_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return screen_cnt


def detect_edge(img):
    # orig = img.copy()
    # img = imutils.resize(img, height=500)

    # convert the image to grayscale, blur it, and find edges
    # in the image
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray_blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(gray_blurred, 75, 200)

    # show the original image and the edge detected image
    print("STEP 1: Edge Detection")
    cv2.imshow("Image", img)
    cv2.imshow("Edged", edged)
    cv2.imshow("Gray Blurred", gray_blurred)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return edged


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image", required=True,
                    help="Path to the image to be scanned")
    args = vars(ap.parse_args())
    img = cv2.imread(args["image"])
    ratio = img.shape[0] / 500.0
    resized_img = imutils.resize(img, height=500)
    edged_img = detect_edge(resized_img)
    screen_cnt = find_contours(resized_img, edged_img)
    transform(img, ratio, screen_cnt)


if __name__ == '__main__':
    main()