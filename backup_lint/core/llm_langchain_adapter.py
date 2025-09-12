# core/llm_langchain_adapter.py
from typing import Any, Dict, List, Optional, Tuple
import json

from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import (
    BaseMessage, AIMessage, HumanMessage, SystemMessage, 
    FunctionMessage, ToolMessage, ToolCall, AIMessageChunk
)
from langchain_core.outputs import (
    ChatResult, ChatGeneration, Generation, 
    LLMResult, ChatGenerationChunk
)

from core.llm_adapter import OpenAILLMAdapter

class CustomLangChainLLM(BaseChatModel):
    llm_adapter: OpenAILLMAdapter

    def __init__(self, llm_adapter: OpenAILLMAdapter, **kwargs: Any):
        super().__init__(llm_adapter=llm_adapter, **kwargs)

    @property
    def _llm_type(self) -> str:
        return "custom_openai_llm"

    def _generate(self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        openai_messages = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                openai_messages.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                if msg.tool_calls:
                    processed_tool_calls = []
                    for tc in msg.tool_calls:
                        tc_dict = tc if isinstance(tc, dict) else tc.dict()
                        # Estrutura correta para a API da OpenAI
                        api_tool_call = {
                            "id": tc_dict.get("id"),
                            "type": "function",
                            "function": {
                                "name": tc_dict.get("name"),
                                "arguments": json.dumps(tc_dict.get("args", {}))
                            }
                        }
                        processed_tool_calls.append(api_tool_call)
                    openai_messages.append({"role": "assistant", "content": msg.content, "tool_calls": processed_tool_calls})
                else:
                    openai_messages.append({"role": "assistant", "content": msg.content})
            elif isinstance(msg, SystemMessage):
                openai_messages.append({"role": "system", "content": msg.content})
            elif isinstance(msg, FunctionMessage):
                openai_messages.append({"role": "function", "name": msg.name, "content": msg.content})
            elif isinstance(msg, ToolMessage):
                tool_message_to_send = {
                    "role": "tool",
                    "tool_call_id": msg.tool_call_id,
                    "content": str(msg.content)
                }
                openai_messages.append(tool_message_to_send)
            else:
                raise ValueError(f"Unsupported message type: {type(msg)}")

        tools = kwargs.get("tools")
        if tools:
            pass

        llm_response = self.llm_adapter.get_completion(messages=openai_messages, tools=tools)

        if "error" in llm_response:
            raise Exception(f"LLM Adapter Error: {llm_response['error']}")

        content = llm_response.get("content") or "" # Ensure content is a string
        tool_calls_data = llm_response.get("tool_calls")

        lc_tool_calls = []
        if tool_calls_data:
            for tc_data in tool_calls_data:
                try:
                    args = json.loads(tc_data.function.arguments)
                except (json.JSONDecodeError, TypeError):
                    args = {"error": "Argumentos em formato JSON inválido", "received": tc_data.function.arguments}
                
                lc_tool_calls.append(ToolCall(
                    name=tc_data.function.name, 
                    args=args, 
                    id=tc_data.id
                ))

        ai_message = AIMessage(content=content, tool_calls=lc_tool_calls)

        return ChatResult(generations=[ChatGeneration(message=ai_message)])

    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        raise NotImplementedError("CustomLangChainLLM does not support async generation yet.")

    def _stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        chat_result = self._generate(messages, stop, run_manager, **kwargs)
        generation = chat_result.generations[0]
        ai_message = generation.message
        
        message_chunk = AIMessageChunk(
            content=ai_message.content,
            tool_calls=ai_message.tool_calls
        )

        yield ChatGenerationChunk(message=message_chunk)
