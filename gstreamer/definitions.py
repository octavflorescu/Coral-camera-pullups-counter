
class CONSTANTS:
    # number of seconds that need to pass after which the video recording is stopped and the video saved to disk
    NO_FACE_THRESHOLD_SEC = 5  # seconds
    # number of seconds that need to pass for a pullup to be considered valid
    # scope: false positive counts removal
    MIN_SEC_PER_PULLUP = 1.0

    class RECORD_STATUS:
        OFF, JUST_STARTED, ON, JUST_STOPPED, *_ = range(10)
        POSITIVE_STATS = [JUST_STARTED, ON]
        NEGATIVE_STATS = [JUST_STOPPED, OFF]

    class PullupsHistoryColumns:
        WHEN, WHO, COUNT, EVIDENCE = "WHEN, WHO, COUNT, EVIDENCE".split(', ')
        all_ordered = [WHEN, WHO, COUNT, EVIDENCE]

    db_path = "/home/mendel/db.csv"
    font_path = "/home/mendel/mnt/cameraSamples/examples-camera/gstreamer/OpenSans.ttf"
