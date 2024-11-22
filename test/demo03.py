import cv2
import numpy as np
import glob

# 1. 定义棋盘格参数
CHESSBOARD_SIZE = (9, 6)  # 棋盘格内角点数量（列数 - 1, 行数 - 1）
SQUARE_SIZE = 0.02  # 每个方块的实际尺寸（单位：米，例如 20mm = 0.02m）

# 2. 准备真实世界的 3D 坐标
objp = np.zeros((CHESSBOARD_SIZE[0] * CHESSBOARD_SIZE[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:CHESSBOARD_SIZE[0], 0:CHESSBOARD_SIZE[1]].T.reshape(-1, 2)
objp *= SQUARE_SIZE  # 转换为真实尺寸

# 用于存储 3D 和 2D 点的数组
objpoints = []  # 真实世界的 3D 点
imgpoints = []  # 图像平面的 2D 点

# 3. 读取标定图像
images = glob.glob("img/*.png")  # 替换为你的标定图片路径
if not images:
    print("未找到任何标定图片，请检查路径和文件格式！")
    exit()

for fname in images:
    img = cv2.imread(fname)
    if img is None:
        print(f"无法加载图片: {fname}")
        continue

    # 转为灰度图
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 查找棋盘格的角点
    ret, corners = cv2.findChessboardCorners(gray, CHESSBOARD_SIZE, None)

    if ret:
        objpoints.append(objp)
        imgpoints.append(corners)

        # 可视化角点
        cv2.drawChessboardCorners(img, CHESSBOARD_SIZE, corners, ret)
        cv2.imshow('Chessboard', img)
        cv2.waitKey(500)
    else:
        print(f"未找到角点: {fname}")

cv2.destroyAllWindows()

# 4. 执行摄像头标定
if len(objpoints) == 0 or len(imgpoints) == 0:
    print("未成功检测到足够的角点，无法完成标定！")
    exit()

ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

if ret:
    print("标定成功!")
    print("相机内参矩阵:\n", mtx)
    print("畸变系数:\n", dist)

    # 保存标定结果
    np.savez("calibration_data.npz", mtx=mtx, dist=dist)
else:
    print("标定失败！")
    exit()

# 5. 使用标定结果矫正摄像头画面
cap = cv2.VideoCapture(0)  # 摄像头索引
if not cap.isOpened():
    print("无法打开摄像头！")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("无法读取摄像头画面")
        break

    # 矫正图像
    h, w = frame.shape[:2]
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))
    dst = cv2.undistort(frame, mtx, dist, None, newcameramtx)

    # 裁剪矫正后的图像（可选）
    x, y, w, h = roi
    dst = dst[y:y + h, x:x + w]

    # 显示矫正后的画面
    cv2.imshow('Original', frame)
    cv2.imshow('Undistorted', dst)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
