"""
Model Context Protocol schema definitions.

Provides schema classes for MCP communication.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union
from enum import Enum
import json
from datetime import datetime


class MessageRole(Enum):
    """Roles for messages."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class ContentType(Enum):
    """Types of content in messages."""
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"


@dataclass
class TextContent:
    """Text content in a message."""
    type: str = "text"
    text: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {"type": self.type, "text": self.text}


@dataclass
class ImageContent:
    """Image content in a message."""
    type: str = "image"
    source: str = ""  # URL or base64
    media_type: str = "image/png"
    alt_text: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "type": self.type,
            "source": self.source,
            "media_type": self.media_type,
        }
        if self.alt_text:
            result["alt_text"] = self.alt_text
        return result


@dataclass
class FileContent:
    """File content in a message."""
    type: str = "file"
    name: str = ""
    path: str = ""
    mime_type: str = ""
    size: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "type": self.type,
            "name": self.name,
            "path": self.path,
            "mime_type": self.mime_type,
        }
        if self.size:
            result["size"] = self.size
        return result


@dataclass
class ToolParameter:
    """A parameter for a tool."""
    name: str
    param_type: str  # string, number, boolean, array, object
    description: str
    required: bool = True
    default: Any = None
    enum: Optional[List[Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "name": self.name,
            "type": self.param_type,
            "description": self.description,
            "required": self.required,
        }
        if self.default is not None:
            result["default"] = self.default
        if self.enum:
            result["enum"] = self.enum
        return result
    
    def to_json_schema(self) -> Dict[str, Any]:
        """Convert to JSON Schema format."""
        schema = {
            "type": self.param_type,
            "description": self.description,
        }
        if self.enum:
            schema["enum"] = self.enum
        return schema


@dataclass
class Tool:
    """Definition of a tool that can be called."""
    name: str
    description: str
    parameters: List[ToolParameter] = field(default_factory=list)
    returns: Optional[str] = None
    version: str = "1.0.0"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": [p.to_dict() for p in self.parameters],
            "returns": self.returns,
            "version": self.version,
        }
    
    def to_openai_format(self) -> Dict[str, Any]:
        """Convert to OpenAI function calling format."""
        properties = {}
        required = []
        
        for param in self.parameters:
            properties[param.name] = param.to_json_schema()
            if param.required:
                required.append(param.name)
        
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        }


@dataclass
class ToolCall:
    """A call to a tool."""
    id: str
    name: str
    arguments: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "tool_call",
            "id": self.id,
            "name": self.name,
            "arguments": self.arguments,
        }


@dataclass
class ToolResult:
    """Result of a tool call."""
    tool_call_id: str
    content: Any
    is_error: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "tool_result",
            "tool_call_id": self.tool_call_id,
            "content": self.content,
            "is_error": self.is_error,
        }


@dataclass
class Message:
    """A message in the conversation."""
    role: MessageRole
    content: List[Union[TextContent, ImageContent, FileContent, ToolCall, ToolResult]]
    name: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "role": self.role.value,
            "content": [c.to_dict() for c in self.content],
        }
        if self.name:
            result["name"] = self.name
        if self.metadata:
            result["metadata"] = self.metadata
        return result
    
    @classmethod
    def from_text(cls, role: MessageRole, text: str) -> 'Message':
        """Create a simple text message."""
        return cls(
            role=role,
            content=[TextContent(text=text)],
        )
    
    def get_text(self) -> str:
        """Extract text content from the message."""
        texts = []
        for c in self.content:
            if isinstance(c, TextContent):
                texts.append(c.text)
        return "\n".join(texts)


@dataclass
class Conversation:
    """A conversation context."""
    id: str
    messages: List[Message] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def add_message(self, message: Message) -> None:
        """Add a message to the conversation."""
        self.messages.append(message)
    
    def add_user_message(self, text: str) -> None:
        """Add a user text message."""
        self.messages.append(Message.from_text(MessageRole.USER, text))
    
    def add_assistant_message(self, text: str) -> None:
        """Add an assistant text message."""
        self.messages.append(Message.from_text(MessageRole.ASSISTANT, text))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "messages": [m.to_dict() for m in self.messages],
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }
    
    def to_json(self) -> str:
        """Serialize to JSON."""
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class Request:
    """A request to the model."""
    conversation: Conversation
    tools: List[Tool] = field(default_factory=list)
    model: str = ""
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    stop_sequences: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "conversation": self.conversation.to_dict(),
            "tools": [t.to_dict() for t in self.tools],
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stop_sequences": self.stop_sequences,
        }


@dataclass
class Response:
    """A response from the model."""
    message: Message
    finish_reason: str = "stop"  # stop, tool_call, length, error
    usage: Dict[str, int] = field(default_factory=dict)
    model: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "message": self.message.to_dict(),
            "finish_reason": self.finish_reason,
            "usage": self.usage,
            "model": self.model,
        }


def create_tool(
    name: str,
    description: str,
    parameters: Optional[Dict[str, Dict[str, Any]]] = None,
) -> Tool:
    """Create a tool from a simplified format."""
    params = []
    
    if parameters:
        for param_name, param_config in parameters.items():
            params.append(ToolParameter(
                name=param_name,
                param_type=param_config.get("type", "string"),
                description=param_config.get("description", ""),
                required=param_config.get("required", True),
                default=param_config.get("default"),
                enum=param_config.get("enum"),
            ))
    
    return Tool(name=name, description=description, parameters=params)


__all__ = [
    "MessageRole",
    "ContentType",
    "TextContent",
    "ImageContent",
    "FileContent",
    "ToolParameter",
    "Tool",
    "ToolCall",
    "ToolResult",
    "Message",
    "Conversation",
    "Request",
    "Response",
    "create_tool",
]
