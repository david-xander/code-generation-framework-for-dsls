from llm_prompting import OpenAIPrompting, OLlamaPrompting

class PromptingServiceFactory:

    @staticmethod
    def get_instance(model: str):
        if model.startswith("gpt-"):
            return OpenAIPrompting(model)
        else:
            return OLlamaPrompting(model)
        # else:
        #     raise ValueError(f"Unsupported model: {model}")