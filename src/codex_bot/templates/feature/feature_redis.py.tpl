def create_orchestrator(container):
    """
    Factory for creating the {class_name} feature orchestrator (Redis).
    """
    from .logic.orchestrator import {class_name}Orchestrator
    return {class_name}Orchestrator()
