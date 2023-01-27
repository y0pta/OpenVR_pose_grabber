import numpy as np
import openvr
import time

# Openvr documentation is not very good implemented. Here will be some notes
# https://skarredghost.com/2018/03/15/introduction-to-openvr-101-series-what-is-openvr-and-how-to-get-started-with-its-apis/
# TrackedDevicePose_t
#     ("mDeviceToAbsoluteTracking", HmdMatrix34_t),
#     ("vVelocity", HmdVector3_t),
#     ("vAngularVelocity", HmdVector3_t),
#     ("eTrackingResult", ETrackingResult),
#     ("bPoseIsValid", openvr_bool),
#     ("bDeviceIsConnected", openvr_bool),


def get_controller_idxs(poses) -> list:
    """
    For each pose:TrackedDevicePose_t check if it is controller
    :param poses: array of TrackedDevicePose_t, retrieved from openvr.VRCompositor().waitGetPoses
    :return:
    list of indexes in poses
    """
    idxs = []
    for i in range(1, len(poses)):
        pose = poses[i]
        if not pose.bDeviceIsConnected:
            continue
        if not pose.bPoseIsValid:
            continue
        device_class = openvr.VRSystem().getTrackedDeviceClass(i)  # TODO: getControllerRoleForTrackedDeviceIndex
        if not device_class == openvr.TrackedDeviceClass_Controller:
            continue
        idxs.append(i)
    return idxs


def convert_matrix(mat) -> (np.array, np.array):
    """
    Converts HmdMatrix34_t into rotation matrix and translation vector
    :param mat: HmdMatrix34_t
    :return: tuple (translation vector, rotation matrix )
    """
    t = np.array([mat[0][3], mat[1][3], mat[2][3]])
    rot = np.array([[mat[0][0], mat[0][1], mat[0][2]],
                    [mat[1][0], mat[1][1], mat[1][2]],
                    [mat[2][0], mat[2][1], mat[2][2]]])
    return t, rot

if __name__ == "__main__":
    FREQUENCY = 40
    openvr.init(openvr.VRApplication_Scene)
    for i in range(4000000):

        last_poses_vr = []
        last_poses_vr, undefined = openvr.VRCompositor().getLastPoses(last_poses_vr, None)
        poses_vr = []
        poses_vr, undefined = openvr.VRCompositor().waitGetPoses(poses_vr, None)

        pose_last = convert_matrix(last_poses_vr[openvr.k_unTrackedDeviceIndex_Hmd].mDeviceToAbsoluteTracking)[0]
        pose = convert_matrix(poses_vr[openvr.k_unTrackedDeviceIndex_Hmd].mDeviceToAbsoluteTracking)[0]
        if np.sum(pose_last - pose) > 0.00000001:
            print("Poses differ!")

        timing = openvr.Compositor_FrameTiming()
        result, timing_info = openvr.VRCompositor().getFrameTiming(0)
        #if result:
        #    print(f"{timing_info.m_nSize}: DataValid")

        time.sleep(1.0/FREQUENCY)


# class Compositor_FrameTiming(Structure):
#     """Provides a single frame's timing information to the app"""
#
#     _fields_ = [
#         ("m_nSize", c_uint32),
#         ("m_nFrameIndex", c_uint32),
#         ("m_nNumFramePresents", c_uint32),
#         ("m_nNumMisPresented", c_uint32),
#         ("m_nNumDroppedFrames", c_uint32),
#         ("m_nReprojectionFlags", c_uint32),
#         ("m_flSystemTimeInSeconds", c_double),
#         ("m_flPreSubmitGpuMs", c_float),
#         ("m_flPostSubmitGpuMs", c_float),
#         ("m_flTotalRenderGpuMs", c_float),
#         ("m_flCompositorRenderGpuMs", c_float),
#         ("m_flCompositorRenderCpuMs", c_float),
#         ("m_flCompositorIdleCpuMs", c_float),
#         ("m_flClientFrameIntervalMs", c_float),
#         ("m_flPresentCallCpuMs", c_float),
#         ("m_flWaitForPresentCpuMs", c_float),
#         ("m_flSubmitFrameMs", c_float),
#         ("m_flWaitGetPosesCalledMs", c_float),
#         ("m_flNewPosesReadyMs", c_float),
#         ("m_flNewFrameReadyMs", c_float),
#         ("m_flCompositorUpdateStartMs", c_float),
#         ("m_flCompositorUpdateEndMs", c_float),
#         ("m_flCompositorRenderStartMs", c_float),
#         ("m_HmdPose", TrackedDevicePose_t),
#         ("m_nNumVSyncsReadyForUse", c_uint32),
#         ("m_nNumVSyncsToFirstView", c_uint32),
#     ]