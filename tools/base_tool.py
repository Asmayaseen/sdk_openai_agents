from abc import ABC, abstractmethod
from typing import Optional, Type, Dict, Any, Generic, TypeVar
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
import logging
from ..context import UserSessionContext

# Set up logging
logger = logging.getLogger(__name__)

# Type variables for input/output schemas
InputSchema = TypeVar('InputSchema', bound=BaseModel)
OutputSchema = TypeVar('OutputSchema', bound=BaseModel)

class ToolOutput(BaseModel):
    """Standardized output format for all tools"""
    tool_call_id: str = Field(default="", description="Unique identifier for tool execution")
    output: Dict[str, Any] = Field(..., description="Tool execution results")
    execution_time: float = Field(default=0.0, description="Execution duration in seconds")
    success: bool = Field(default=True, description="Whether execution succeeded")
    timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="When execution completed"
    )

class BaseTool(ABC, Generic[InputSchema, OutputSchema]):
    """
    Abstract base class for all Health & Wellness Planner tools.
    """

    @classmethod
    @abstractmethod
    def name(cls) -> str:
        pass

    @classmethod
    @abstractmethod
    def description(cls) -> str:
        pass

    @classmethod
    def input_schema(cls) -> Optional[Type[InputSchema]]:
        return None

    @classmethod
    def output_schema(cls) -> Optional[Type[OutputSchema]]:
        return None

    @classmethod
    def validate_input(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        if schema := cls.input_schema():
            validated = schema(**input_data)
            return validated.model_dump()
        return input_data

    @classmethod
    def validate_output(cls, output_data: Dict[str, Any]) -> Dict[str, Any]:
        if schema := cls.output_schema():
            validated = schema(**output_data)
            return validated.model_dump()
        return output_data

    @abstractmethod
    async def execute(
        self,
        validated_input: Dict[str, Any],
        context: Optional[UserSessionContext] = None
    ) -> Dict[str, Any]:
        pass

    async def __call__(
        self,
        input_data: Dict[str, Any],
        context: Optional[UserSessionContext] = None
    ) -> ToolOutput:
        start_time = datetime.now()
        tool_call_id = input_data.get("tool_call_id", "")

        try:
            validated_input = self.validate_input(input_data)
            logger.info(f"Executing {self.name()} with input: {validated_input}")
            result = await self.execute(validated_input, context)
            validated_output = self.validate_output(result)
            return ToolOutput(
                tool_call_id=tool_call_id,
                output=validated_output,
                execution_time=(datetime.now() - start_time).total_seconds(),
                success=True
            )

        except Exception as e:
            logger.error(f"Tool {self.name()} failed: {str(e)}", exc_info=True)
            return ToolOutput(
                tool_call_id=tool_call_id,
                output={"error": str(e)},
                execution_time=(datetime.now() - start_time).total_seconds(),
                success=False
            )

# Example tool implementation
class ExampleHealthTool(BaseTool):

    @classmethod
    def name(cls) -> str:
        return "example_health_tool"

    @classmethod
    def description(cls) -> str:
        return "Analyzes a health metric and gives progress feedback"

    class InputModel(BaseModel):
        metric_name: str = Field(..., description="Metric to track")
        current_value: float = Field(..., description="Current measurement")
        target_value: float = Field(..., description="Goal value")

        @field_validator('current_value', 'target_value')
        @classmethod
        def check_positive(cls, v):
            if v <= 0:
                raise ValueError("Value must be greater than 0")
            return v

    class OutputModel(BaseModel):
        analysis: str
        progress_percentage: float = Field(..., ge=0, le=100)
        recommendation: str

    @classmethod
    def input_schema(cls) -> Type[InputModel]:
        return cls.InputModel

    @classmethod
    def output_schema(cls) -> Type[OutputModel]:
        return cls.OutputModel

    async def execute(
        self,
        validated_input: Dict[str, Any],
        context: Optional[UserSessionContext] = None
    ) -> Dict[str, Any]:

        current = validated_input['current_value']
        target = validated_input['target_value']
        metric = validated_input['metric_name']

        progress = ((target - current) / target) * 100
        recommendation = (
            "Great job! Maintain your routine."
            if progress >= 0 else
            "Consider modifying your plan for better results."
        )

        return {
            "analysis": f"You are tracking {metric}.",
            "progress_percentage": abs(progress),
            "recommendation": recommendation
        }


