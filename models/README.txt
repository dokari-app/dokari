tennis_v8_player_racket_ball.onnx - YOLOv8 export, classes: Player, Racket, Tennis Ball (640x640). Source: github.com/Hey-Salad/Tennis_Detection_Model (best.onnx).
License AGPL-3.0 (Ultralytics): fine for internal factory experiments; do NOT ship in the app. For the product, train our own detector (the factory can label frames).
Used by sphere/ball.py (Detector auto-detects YOLOv8 vs YOLOX exports). Generic person detector used for the player box: YOLOX-m ONNX (Apache-2.0),
github.com/Megvii-BaseDetection/YOLOX/releases/download/0.1.1rc0/yolox_m.onnx
