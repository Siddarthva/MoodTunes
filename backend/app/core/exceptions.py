class MoodTunesException(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class NoFaceDetectedException(MoodTunesException):
    def __init__(self, message: str = "No face could be detected. Please face the camera directly."):
        super().__init__(code="NO_FACE_DETECTED", message=message, status_code=422)

class InvalidImageException(MoodTunesException):
    def __init__(self, message: str = "Provided file could not be decoded as a valid image."):
        super().__init__(code="CORRUPT_IMAGE", message=message, status_code=422)

class ModelNotReadyException(MoodTunesException):
    def __init__(self, message: str = "Emotion recognition model is currently unavailable."):
        super().__init__(code="MODEL_NOT_READY", message=message, status_code=503)

class MusicProviderException(MoodTunesException):
    def __init__(self, message: str = "Unable to fetch music recommendations at this time."):
        super().__init__(code="MUSIC_PROVIDER_ERROR", message=message, status_code=503)

class NoRecommendationsException(MoodTunesException):
    def __init__(self, message: str = "No playable music recommendations could be found."):
        super().__init__(code="NO_RECOMMENDATIONS", message=message, status_code=404)

