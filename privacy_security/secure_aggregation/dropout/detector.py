from ..models import DropoutInformation
def detect(expected: set[str], received: set[str], threshold: int) -> DropoutInformation:
    return DropoutInformation(frozenset(expected), frozenset(received), frozenset(expected-received), len(received)>=threshold)
