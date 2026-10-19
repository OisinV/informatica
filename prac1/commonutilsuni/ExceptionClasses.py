import warnings # type:ignore

class NotInsideWorldError(Exception):
    pass

class NotOnGridError(Exception):
    pass

class CannotBeNegative(UserWarning):
    """This number cannot be negative.
    Stay positive folks! If you do not, our glorious country will keelhaul you!
    Disclaimer: This is a joke, please capitalist, communist or whatever do not keelhaul me."""

class RecommendedTooBig(UserWarning):
    """It is recommended to make this number smaller."""
