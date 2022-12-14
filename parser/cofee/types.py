from enum import Enum,auto

class HintAction(Enum):
    DELETE=0
    REPLACE= 1
    REPLACEALL= 2
    PREPEND=3
    APPEND=4
    REPLACEWITHMESSAGE=5

class ErrorResult(Enum):
    ERROR = 1
    WARNING = 2
    SUCCESS = 3
    FAILED = 0

class ErrorType(Enum):
    ERROR = auto()
    UNITTEST = auto()
    RAW = auto()

