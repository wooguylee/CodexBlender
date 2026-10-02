"""Public, provider-independent contracts for request and future subtask routing."""
from dataclasses import asdict, dataclass, field
from typing import Literal

ModelTier = Literal['luna', 'sol', 'astra']
MODEL_TIERS = ('luna', 'sol', 'astra')


@dataclass
class RoutingContext:
    model_mode: str = 'auto'
    expected_tool_calls: int = 0
    step_count: int = 0
    python_generation: bool | None = None
    geometry_nodes: bool | None = None
    shader_nodes: bool | None = None
    rigging: bool | None = None
    animation: bool | None = None
    modifiers: bool | None = None
    scene_analysis: bool | None = None
    visual_review: bool | None = None
    complex_math: bool | None = None
    whole_scene: bool | None = None
    debugging: bool | None = None
    high_difficulty: bool | None = None
    simple_repeat: bool | None = None
    simple: bool | None = None
    previous_failures: int = 0
    sol_failures: int = 0
    mcp_error: bool = False
    tool_call_count: int = 0


@dataclass
class RoutingDecision:
    model: ModelTier
    model_id: str
    reasoning_effort: str | None
    score: int
    reasons: list[str]
    simple: bool = False
    astra_eligible: bool = False
    manual: bool = False

    def to_dict(self):
        return asdict(self)


@dataclass
class TaskExecutionState:
    task_id: str
    selected_model: str
    original_model: str
    attempt_count: int = 0
    failure_count: int = 0
    tool_call_count: int = 0
    model_call_count: int = 0
    previous_errors: list[str] = field(default_factory=list)
    escalated: bool = False
    escalation_history: list[dict] = field(default_factory=list)
    failures_by_model: dict = field(default_factory=lambda: {tier: 0 for tier in MODEL_TIERS})
    substantive_failures: dict = field(default_factory=lambda: {tier: 0 for tier in MODEL_TIERS})
    status: str = 'running'


@dataclass
class ExecutionResult:
    ok: bool
    state: TaskExecutionState
    decision: RoutingDecision
    message: str = ''
    error: str | None = None
    pending_result: dict | None = None
    statistics: dict = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)
