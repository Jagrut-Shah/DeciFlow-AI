
"""
DeciFlow AI — BaseAgent
=======================
Minimal, extensible base class for all agents in the DeciFlow AI
multi-agent decision intelligence pipeline.

Every agent in the pipeline (DataAgent, InsightAgent, PredictionAgent,
DecisionAgent) must inherit from this class and override `run()`.

Chaining pattern:
    output = AgentA().execute(input_dict)
    output = AgentB().execute(output)   # output flows directly as input
"""

import traceback
from datetime import datetime


class BaseAgent:
    """
    Abstract base class for all DeciFlow AI agents.

    Subclasses MUST override `run(input_data: dict) -> dict`.
    Always call `execute()` — never `run()` directly — to get safe,
    validated execution with logging and error handling included.

    Attributes:
        name (str): Agent identifier used in logs and error responses.
                    Defaults to the subclass class name.

    Example:
        class DataAgent(BaseAgent):
            def run(self, input_data: dict) -> dict:
                # your logic here
                return {"status": "ok", "data": [...]}

        result = DataAgent().execute({"source": "csv", "payload": [...]})
    """

    def __init__(self, name: str = None):
        self.name = name or self.__class__.__name__

    # ------------------------------------------------------------------
    # Public interface — always call this
    # ------------------------------------------------------------------

    async def execute(self, input_data: dict) -> dict:
        """
        Safe entry point for running any agent.

        Validates input, delegates to `run()`, and catches all exceptions
        so a single agent failure never crashes the pipeline.

        Args:
            input_data (dict): Payload passed to this agent.

        Returns:
            dict: Agent output, or a structured error dict on failure.
        """
        validation_error = self._validate_input(input_data)
        if validation_error:
            return validation_error

        self._log("started")
        try:
            result = await self.run(input_data)
        except NotImplementedError:
            return self._error(
                "run() is not implemented. Override it in your agent subclass."
            )
        except Exception as exc:
            return self._error(str(exc), detail=traceback.format_exc())
        finally:
            self._log("finished")

        if not isinstance(result, dict):
            return self._error(
                f"run() must return a dict, got {type(result).__name__} instead."
            )

        return result

    # ------------------------------------------------------------------
    # Override this in every subclass
    # ------------------------------------------------------------------

    async def run(self, input_data: dict) -> dict:
        """
        Core agent logic. Must be overridden by every subclass.

        Args:
            input_data (dict): Validated input payload.

        Returns:
            dict: Agent output payload.

        Raises:
            NotImplementedError: Always, until overridden.
        """
        raise NotImplementedError(
            f"{self.name}.run() is not implemented. "
            "Override this method in your subclass."
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _validate_input(self, input_data) -> dict | None:
        """
        Checks that input_data is a dict.

        Returns:
            None if valid; a structured error dict if not.
        """
        if not isinstance(input_data, dict):
            return self._error(
                f"input_data must be a dict, got {type(input_data).__name__} instead."
            )
        return None

    def _error(self, message: str, detail: str = None) -> dict:
        """
        Builds a consistent error response.

        Args:
            message (str): Short, human-readable description of the error.
            detail  (str): Optional traceback or extended context.

        Returns:
            dict: Structured error payload with "status", "agent", and "error" keys.
        """
        payload = {
            "status": "error",
            "agent": self.name,
            "error": message,
        }
        if detail:
            payload["detail"] = detail
        return payload

    def _log(self, event: str) -> None:
        """Minimal stdout logging — no external dependencies."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{self.name}] {event}")