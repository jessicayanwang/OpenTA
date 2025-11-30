"""
Multi-Agent System for OpenTA
"""
from .base_agent import BaseAgent, AgentCapability
from .orchestrator import OrchestratorAgent

# Professor-side agents
from .professor_orchestrator import ProfessorOrchestrator
from .clustering_agent import ClusteringAgent
from .canonical_answer_agent import CanonicalAnswerAgent
from .unresolved_queue_agent import UnresolvedQueueAgent
from .dashboard_agent import DashboardAgent
from .guardrail_settings_agent import GuardrailSettingsAgent

__all__ = [
    'BaseAgent', 
    'AgentCapability', 
    'OrchestratorAgent',
    # Professor-side
    'ProfessorOrchestrator',
    'ClusteringAgent',
    'CanonicalAnswerAgent',
    'UnresolvedQueueAgent',
    'DashboardAgent',
    'GuardrailSettingsAgent',
]
