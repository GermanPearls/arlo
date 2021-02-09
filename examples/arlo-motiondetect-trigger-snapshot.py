import sys, os
currentDir = os.getcwd()
parentDir = os.path.dirname(currentDir)
upTwoDir = os.path.dirname(parentDir)
sys.path.insert(0,upTwoDir)
sys.path.insert(0,parentDir)
from arlo import Arlo
from arlocreds import USERNAME, PASSWORD

try:

    # Instantiating the Arlo object automatically calls Login(), which returns an oAuth token that gets cached.
    # Subsequent successful calls to login will update the oAuth token.
    arlo = Arlo(USERNAME, PASSWORD)
    # At this point you're logged into Arlo.

    # Get the list of devices and filter on device type to only get the basestation.
    # This will return an array which includes all of the basestation's associated metadata.
    basestations = arlo.GetDevices('basestation')
    cameras = arlo.GetDevices('camera')
    camerasById = {}
    camerasByIndex = []
    cameraIndex = 0
    cameraName = ''
    cameraObj = {}

    # setup a hash where each camera deviceId is assocaited with its name for lookup later
    for camera in cameras:
        camerasById[camera['deviceId']] = camera['deviceName']
        camerasByIndex.append(camera['deviceId'])

    # Define a callback function that will get called once for each motion event.
    def callback(arlo, event):
        # Here you will have access to self, basestation_id, xcloud_id, and the event schema.
        cameraId = event['resource'][len('cameras/'):]
        cameraName = camerasById[cameraId]
        cameraIndex = camerasByIndex.index(cameraId)

        # Trigger the snapshot. Motion will trigger streaming so need to access stream to take snapshot.
        streamURL = arlo.StartStream(basestations[0], cameras[int(cameraIndex)])
        #print(streamURL)
        url = arlo.TriggerStreamSnapshot(basestations[0], cameras[int(cameraIndex)])
        #print(url)
        
        # Download snapshot.
        arlo.DownloadSnapshot(url, 'snapshot.jpg')
        stopStream = arlo.StopStream(basestations[0], cameras[int(cameraIndex)])
        
        print('motion event detected on camera ' + cameraId + ' which is the ' + cameraName + ' camera, index ' + str(cameraIndex))
        #print(event)
        #print(arlo)
        #print(basestations)
        arlo.Logout()

    # Subscribe to motion events. This method blocks until the event stream is closed. (You can close the event stream in the callback if you no longer want to listen for events.)
    arlo.SubscribeToMotionEvents(basestations[0], callback)
except Exception as e:
    print(e)
