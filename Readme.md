# Facial Gesture-Based Vehicle Controller for CARLA Simulator

## Overview

This project implements a real-time facial gesture-based vehicle control system for the [CARLA driving simulator](https://carla.org/). The system uses a webcam to detect facial movements using **MediaPipe Face Mesh**, and maps specific gestures to control commands such as throttle, brake, steering, and gear shifting.

## Features

- Control a CARLA vehicle using facial gestures:
  - **Mouth open** → Accelerate
  - **Frown** → Brake
  - **Head tilt left/right** → Steer left/right (with two levels of sensitivity)
  - **Nod up** → Shift gear up
  - **Nod down** → Shift gear down
- Logs gesture detection and vehicle control states in a CSV file.
- Automatically positions the spectator camera behind the vehicle for a third-person view.

## Gesture Detection Details

Facial landmarks are extracted using MediaPipe’s Face Mesh solution, which provides 468 points on the face in real-time. Gesture recognition is implemented based on distances or relative positions of key facial features:

- **Mouth Open**: Measured as the distance between upper and lower lip landmarks.
- **Frown**: Detected by checking the distance between eyebrows and eyes; a shorter distance indicates a frown.
- **Head Tilt**: Determined by comparing the vertical position (Y-axis) difference between the left and right cheeks.
- **Nodding**: Tracked via changes in the nose tip’s vertical position over time.

## Vehicle Control Mapping

The detected gestures are mapped to vehicle control inputs using CARLA's Python API:

| Gesture         | Action                           |
| --------------- | -------------------------------- |
| Mouth Open      | `control.throttle = 0.6`         |
| Frown           | `control.brake = 1.0`            |
| Head Tilt Left  | `control.steer = -0.1` to `-0.3` |
| Head Tilt Right | `control.steer = 0.1` to `0.3`   |
| Nod Up          | `gear += 1`                      |
| Nod Down        | `gear -= 1`                      |

The vehicle gear ranges from -1 (reverse) to 5 (forward), and the reverse flag is automatically toggled based on gear value.

## Logging

Gesture states and vehicle control values are logged to a file called `gesture_vehicle_log.csv`. Each row contains:

- Timestamp
- Gesture states: MouthOpen, Frowning, NoddingUp, NoddingDown
- Vehicle control states: Throttle, Brake, Steer, Gear

## Requirements

- Python 3.8+
- [CARLA Simulator](https://carla.org/) 0.9.14+
- Dependencies:
  - `opencv-python`
  - `mediapipe`
  - `numpy`
  - `carla` (CARLA Python API)

Install dependencies:

```bash
pip install opencv-python mediapipe numpy
```

## Usage

1. Make sure the CARLA simulator is running (`./CarlaUE4.sh -opengl`).
2. Run the main script:

```bash
python facial_control.py
```

3. Use your webcam and facial gestures to control the car.
4. Press `q` to quit.

## Demo

A short video demo can be added here to show the system in action.

## License

MIT License

---

Contributions welcome! Feel free to fork and build upon this project.
```

