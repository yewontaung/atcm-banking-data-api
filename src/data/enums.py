from enum import Enum


class MemberRole(str, Enum):
    Collector = "Collector"
    Supervisor = "Supervisor"
    Admin = "Admin"
