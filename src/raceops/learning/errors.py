"""Domain conflicts for the Session decision and execution workflow."""


class PriorityScopeConflictError(RuntimeError):
    """A main-priority rank is unavailable or the scope already has three."""


class InvalidDecisionContextError(RuntimeError):
    """A target, motivation, recipient, or assignee combination is invalid."""


class InvalidActionStatusTransitionError(RuntimeError):
    """The requested Action execution transition is not allowed."""


class InvalidActionOutcomeError(RuntimeError):
    """An Outcome would violate execution, target, or conclusion rules."""


class ActionOutcomeConflictError(RuntimeError):
    """The Action already has its single P0 Outcome."""
