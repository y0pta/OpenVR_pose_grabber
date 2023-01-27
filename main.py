import numpy as np
import openvr
import time
from vr_utilities import *
import sys, threading, json

start_event = threading.Event()
stop_event = threading.Event()


def poll_keyboard():
    print("Press ENTER key to start, q to stop")
    while True:
        input = sys.stdin.read(1)
        if input == '\n' and not start_event.is_set():
            start_event.set()
            print('Program started capturing.')

        if input.rstrip() == 'q' and not stop_event.is_set():
            stop_event.set()
            print('Capturing stopped. Exiting.')


def save_poses_json(poses, path):
    reformat = []
    for pose in poses:
        reformat.append(pose.__dict__)

    with open(path, 'w') as f:
        JSON_STR = json.dumps(reformat, indent=4)
        f.write(JSON_STR)
        print(json.loads(JSON_STR))


class Pose:
    def __init__(self, t: float, poses):
        self.t = t
        if not poses[openvr.k_unTrackedDeviceIndex_Hmd].bPoseIsValid:
            print(f"Caught invalid pose for time {t}.")
        hdm = list(convert_matrix(poses[openvr.k_unTrackedDeviceIndex_Hmd].mDeviceToAbsoluteTracking))
        self.hmd_pose = list(map(lambda x: x.tolist(), hdm))
        self.controller_poses = {}
        for i in get_controller_idxs(poses):
            p = list(convert_matrix(poses[i].mDeviceToAbsoluteTracking))
            self.controller_poses[i] = list(map(lambda x: x.tolist(), p))


JSON_WRITE_PATH = "poses.json"
FREQUENCY = 20
TIME = 5

if __name__ == "__main__":
    # Poll keyboard for start and stop in separate thread
    threading.Thread(target=poll_keyboard, daemon=True).start()

    openvr.init(openvr.VRApplication_Scene)
    poses = []

    start_t = time.time()
    while True:
        # Wait for start data capturing event(hardware init claims some time)
        if not start_event.is_set():
            time.sleep(0.25)
            continue

        # Catch keyboard interruption
        if stop_event.is_set():
            break

        poses_vr = []
        poses_vr, _ = openvr.VRCompositor().waitGetPoses(poses_vr, None)

        t = round(time.time() - start_t, 3)
        pose = Pose(t, poses_vr)
        poses.append(pose)

        sys.stdout.flush()
        time.sleep(1.0/FREQUENCY)

    # Process posses
    save_poses_json(poses, JSON_WRITE_PATH)
    print(f"{len(poses)} poses are saved in: {JSON_WRITE_PATH}")


openvr.shutdown()
