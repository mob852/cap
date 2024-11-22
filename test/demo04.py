import cv2
import numpy as np

# 棋盘格设置
CHESSBOARD_SIZE = (9, 6)

# 摄像头预览和角点检测
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("无法打开摄像头")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("无法读取摄像头画面")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    ret, corners = cv2.findChessboardCorners(gray, CHESSBOARD_SIZE, None)

    if ret:
        print("成功找到角点")
        cv2.drawChessboardCorners(frame, CHESSBOARD_SIZE, corners, ret)

    cv2.imshow('Corners Detection', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
