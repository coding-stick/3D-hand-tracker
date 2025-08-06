# 🧊 Hand-Controlled 3D Cube (Tony Stark-Style Interface)
# Mediapipe works on Python 3.11 or before, not 3.12!!
This project uses **Python**, **OpenCV**, and **MediaPipe** to read hand gestures from a webcam and control a **3D cube** rendered with **PyOpenGL**. Inspired by Tony Stark's futuristic interface, the user can rotate, zoom, and orbit the camera around a 3D object using just hand movement.

https://user-images.githubusercontent.com/your_video_here.gif  
*(Optional: Replace this with a demo GIF or YouTube short)*

---

## RUNNING
- Install these libraries: pygame, pyopengl, opencv-python, numpy, mediapipe
- Just run three.py file

---

## ✨ Features

- 🖐️ **Hand Tracking** via MediaPipe
- 🔄 **Rotate**, **zoom**, and **orbit** the camera around a 3D cube
- 🧭 Colored axis and grid lines for reference
- 🧱 Loads `.obj` mesh files (optionally with texture support)
- ⚙️ Wireframe and solid rendering modes
- 🎮 Keyboard navigation (WASDQE keys to move camera)

---

## 🧰 Tech Stack

- `Python`
- `OpenCV`
- `MediaPipe`
- `PyOpenGL`
- `Pygame` (used to create the OpenGL window)

---

## 🎮 Controls

| Action        | Input        |
|---------------|--------------|
| Orbit Left/Right | `A` / `D` |
| Orbit Up/Down | `W` / `S`    |
| Toggle Wireframe | `M`       |

---

## 🖐️ Hand Gestures (via MediaPipe)

You can map gestures like:
- **Pinch (thumb + index) right hand**: for zoom
- **Point (index and thumn) left hand**: for rotation

Currently, OpenCV and MediaPipe identify hands using `.multi_handedness`, which you can parse to differentiate gestures from left/right hand.


