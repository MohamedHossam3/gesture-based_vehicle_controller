import cv2
import mediapipe as mp
import numpy as np
import carla
import time

# Initialize MediaPipe Face Mesh
mp_face = mp.solutions.face_mesh
face = mp_face.FaceMesh(refine_landmarks=True)
mp_draw = mp.solutions.drawing_utils

# Connect to CARLA
client = carla.Client("localhost", 2000)
client.set_timeout(10.0)        
world = client.get_world()
world.unload_map_layer(carla.MapLayer.Buildings)
world.unload_map_layer(carla.MapLayer.Decals)
world.unload_map_layer(carla.MapLayer.Foliage)
world.unload_map_layer(carla.MapLayer.ParkedVehicles)
world.unload_map_layer(carla.MapLayer.Particles)
world.unload_map_layer(carla.MapLayer.Props)
world.unload_map_layer(carla.MapLayer.Walls)

blueprint_library = world.get_blueprint_library()

spawn_point = world.get_map().get_spawn_points()[75]

vehicle_bp = blueprint_library.filter('vehicle.mercedes.coupe_2020')[0]
vehicle = world.try_spawn_actor(vehicle_bp, spawn_point)
# Helper function to calculate Euclidean distance
def distance(p1, p2):
    return np.linalg.norm(np.array(p1) - np.array(p2))

# Facial landmark indices
MOUTH_TOP = 13
MOUTH_BOTTOM = 14
NOSE_TIP = 1
LEFT_CHEEK = 234
RIGHT_CHEEK = 454
LEFT_EYE = 159
RIGHT_EYE = 386
LEFT_BROW = 65
RIGHT_BROW = 295

# Webcam setup
cap = cv2.VideoCapture(0)

# Control flags
gear = 1
prev_nose_y = None
prev_nod_time = time.time()

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face.process(frame_rgb)

        control = carla.VehicleControl()

        spectator = world.get_spectator()
        transform = carla.Transform(vehicle.get_transform().transform(carla.Location(x=-6,z=2)),vehicle.get_transform().rotation)
        spectator.set_transform(transform)


        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0].landmark

            ih, iw, _ = frame.shape
            get_point = lambda idx: (int(landmarks[idx].x * iw), int(landmarks[idx].y * ih))

            # Gesture detection
            mouth_open = distance(get_point(MOUTH_TOP), get_point(MOUTH_BOTTOM)) > 20

            # Frown detection: brow down relative to eyes
            left_frown = get_point(LEFT_BROW)[1] > get_point(LEFT_EYE)[1] - 5
            right_frown = get_point(RIGHT_BROW)[1] > get_point(RIGHT_EYE)[1] - 5
            frowning = left_frown and right_frown

            # Head tilt: difference in cheek height
            left_cheek_y = get_point(LEFT_CHEEK)[1]
            right_cheek_y = get_point(RIGHT_CHEEK)[1]
            head_tilt_delta = right_cheek_y - left_cheek_y
            head_tilt_thresh = 10

            # Nodding detection for gear shift
            nose_y = get_point(NOSE_TIP)[1]
            nodding_up = False
            nodding_down = False
            now = time.time()

            if prev_nose_y is not None and now - prev_nod_time > 1.0:
                delta_y = nose_y - prev_nose_y
                if delta_y < -15:
                    nodding_up = True
                    gear = min(5, gear + 1)
                    prev_nod_time = now
                elif delta_y > 15:
                    nodding_down = True
                    gear = max(-1, gear - 1)
                    prev_nod_time = now
            prev_nose_y = nose_y

            # Apply gesture mappings
            control.throttle = 0.6 if mouth_open else 0.0
            control.brake = 0.8 if frowning else 0.0
            control.steer = -0.5 if head_tilt_delta > head_tilt_thresh else (0.5 if head_tilt_delta < -head_tilt_thresh else 0.0)
            control.gear = gear if gear >= 0 else 0
            control.reverse = gear < 0

            vehicle.apply_control(control)

            # Draw overlay
            cv2.putText(frame, f"Throttle: {control.throttle}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Brake: {control.brake}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.putText(frame, f"Steer: {control.steer:.2f}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            cv2.putText(frame, f"Gear: {gear}", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)

        cv2.imshow('Facial Control', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    cap.release()
    cv2.destroyAllWindows()
    print("Exited safely.")