from enum import Enum


class MemberRole(str, Enum):
    Collector = "Collector"
    Supervisor = "Supervisor"
    Admin = "Admin"

class DatasetType(str, Enum):
    Training = "Training"
    Validation = "Validation"
    Testing = "Testing"