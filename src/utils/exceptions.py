class ResourceNotFoundException(Exception):

    def __init__(self, message:str):
        super().__init__(message)
        self.message = message

class AppBusinessException(Exception):

    def __init__(self, message:str):
        super().__init__(message)
        self.message = message