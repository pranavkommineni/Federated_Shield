class SecureAggregationError(Exception): pass
class InvalidParticipantError(SecureAggregationError): pass
class InvalidRoundError(SecureAggregationError): pass
class DuplicateSubmissionError(SecureAggregationError): pass
class InvalidUpdateError(SecureAggregationError): pass
class InsufficientParticipantsError(SecureAggregationError): pass
class ProtocolStateError(SecureAggregationError): pass
class DropoutRecoveryError(SecureAggregationError): pass
