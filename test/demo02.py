import cv2
import numpy as np

def xiuzhengdian(dian):
    """
    修正点的位置顺序，确保点按左上、右上、左下、右下排列。
    """
    if len(dian) != 4:
        raise ValueError("Expected 4 points, got {}".format(len(dian)))

    # 按 y 坐标排序，y 相同按 x 坐标排序
    dian = sorted(dian, key=lambda x: (x[1], x[0]))
    if dian[0][0] > dian[1][0]:  # 左上和右上交换
        dian[0], dian[1] = dian[1], dian[0]
    if dian[2][0] > dian[3][0]:  # 左下和右下交换
        dian[2], dian[3] = dian[3], dian[2]
    return dian

def biao_dian(frame, img):
    """
    从二值图像中提取轮廓，找到面积最大的四边形，并修正顶点顺序。
    """
    contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    max_area = 0
    approx = None

    for contour in contours:
        peri = cv2.arcLength(contour, True)
        approx_poly = cv2.approxPolyDP(contour, 0.02 * peri, True)
        area = cv2.contourArea(approx_poly)

        if area > max_area and len(approx_poly) == 4:
            max_area = area
            approx = approx_poly

    if approx is None:
        return frame  # 如果没有找到四边形，直接返回原始帧

    # 转换为普通点列表
    jisuandian = [point[0] for point in approx]
    print("Original points:", jisuandian)

    try:
        jieguo = xiuzhengdian(jisuandian)
    except ValueError as e:
        print(e)
        return frame

    print("Corrected points:", jieguo)

    # 透视变换
    width, height = 500, 500
    dst_points = np.array([[0, 0], [width - 1, 0], [0, height - 1], [width - 1, height - 1]], dtype="float32")
    M = cv2.getPerspectiveTransform(np.array(jieguo, dtype="float32"), dst_points)
    img_warp = cv2.warpPerspective(frame, M, (width, height))

    return img_warp

def main():
    cap = cv2.VideoCapture(0)  # 打开摄像头
    if not cap.isOpened():
        print("Failed to open camera.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read frame.")
            break

        # 转换为灰度图并二值化
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, img_erzhi = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY)

        # 处理帧
        img_warp = biao_dian(frame, img_erzhi)

        # 显示结果
        cv2.imshow("Original", frame)
        cv2.imshow("Warped", img_warp)

        # 按 'q' 退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
