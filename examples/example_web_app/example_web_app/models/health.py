from enum import Enum


class HealthStatus(Enum):
    """
    Health API Status Values

    Inspired by: https://tools.ietf.org/id/draft-inadarei-api-health-check-01.html
    """
    Pass = "pass"
    Fail = "fail"
    Warn = "warn"

