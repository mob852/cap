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

def biao_dian(yuan, img):
    """
    从二值图像中提取轮廓，找到面积最大的四边形，并修正顶点顺序。
    """
    contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    max_area = 0
    approx = None  # 用于存储近似多边形的点

    for a in range(len(contours)):
        peri = cv2.arcLength(contours[a], True)  # 计算轮廓的周长
        approx_poly = cv2.approxPolyDP(contours[a], 0.02 * peri, True)  # 近似多边形
        area = cv2.contourArea(approx_poly)

        if area > max_area and len(approx_poly) == 4:  # 筛选面积最大且是四边形的轮廓
            max_area = area
            approx = approx_poly

    if approx is None:  # 如果没有找到合适的四边形
        print("No valid quadrilateral found.")
        return yuan  # 返回原图，不进行任何操作

    # 打印近似的四边形点
    print("Approximation points:", approx)

    # 转换为普通的点列表
    jisuandian = [point[0] for point in approx]
    print("Original points:", jisuandian)

    # 调用修正点的函数
    jieguo = xiuzhengdian(jisuandian)
    print("Corrected points:", jieguo)

    # 示例：透视变换（根据修正后的点进行变换）
    width, height = 500, 500  # 目标图像大小
    dst_points = np.array([[0, 0], [width - 1, 0], [0, height - 1], [width - 1, height - 1]], dtype="float32")
    M = cv2.getPerspectiveTransform(np.array(jieguo, dtype="float32"), dst_points)
    img_warp = cv2.warpPerspective(yuan, M, (width, height))

    return img_warp

def main():
    # 加载测试图像
    img = cv2.imread("test_image.jpg")  # 替换为你的图像路径
    if img is None:
        print("Failed to load image.")
        return

    # 转换为灰度图并二值化
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, img_erzhi = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY)

    # 处理图像，找到并修正顶点
    img_warp = biao_dian(img, img_erzhi)

    # 显示结果
    cv2.imshow("Original", img)
    cv2.imshow("Warped", img_warp)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
