from typing import List, Dict, Any, Optional
import logging
from core.llm_base import BaseLLMAdapter
from core.config.config import Config
from openai import OpenAI, APITimeoutError, APIConnectionError, RateLimitError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

class OpenAILLMAdapter(BaseLLMAdapter):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.client = OpenAI(
            api_key=Config().OPENAI_API_KEY,
            timeout=30.0,  # Adiciona um timeout de 30 segundos
        )

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        retry=retry_if_exception_type((APITimeoutError, APIConnectionError, RateLimitError)),
        reraise=True # Reraise the exception if all retries fail
    )
    def get_completion(self, messages: List[Dict[str, str]], tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        try:
            # Prepare arguments for the API call
            api_args = {
                "model": Config().LLM_MODEL_NAME,
                "messages": messages,
                "temperature": 0, # Set temperature to 0 for more deterministic output
            }
            if tools:
                api_args["tools"] = tools
                api_args["tool_choice"] = "auto" # Let the model decide whether to call a tool

            self.logger.info("Making OpenAI API call...")
            response = self.client.chat.completions.create(**api_args)
            self.logger.info("OpenAI API call finished.")

            # Extract message content
            message_content = response.choices[0].message.content
            tool_calls = response.choices[0].message.tool_calls

            result = {"content": message_content}
            if tool_calls:
                result["tool_calls"] = tool_calls
            
            return result

        except (APITimeoutError, APIConnectionError, RateLimitError) as e:
            self.logger.warning(f"A retriable error occurred: {e}")
            raise # Reraise the exception to trigger tenacity's retry mechanism
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during OpenAI API call: {e}", exc_info=True)
            return {"error": f"An unexpected error occurred while getting completion from OpenAI: {e}"}

