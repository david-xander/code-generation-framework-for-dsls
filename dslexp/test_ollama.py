from llm_factory import PromptingServiceFactory
from pydantic import BaseModel
from ollama import Client as OLlamaClient
import re


class ExperimentSingleCodeTask(BaseModel):
    code: str

class ExperimentCodeTask(BaseModel):
    id: int
    code: str

class ExperimentResponse(BaseModel):
    tasks: list[ExperimentCodeTask]

# deepseek-r1:14b
# llama3.1:latest
# mistral:latest

# codellama:7b
# deepseek-coder:6.7b
# qwen2.5-coder:7b
# granite-code:8b


def test_with_prompting_servicing(model):
    prompting = PromptingServiceFactory.get_instance(model)

    # prompting.add_to_context("Generate code these constraints in OCL: 1. Each truck must have a batch number. 2. Only five trucks are allowed in the parking A")
    prompting.add_to_context("Generate the code for the following constraint in OCL: Each truck must have a batch number.")

    print(ExperimentSingleCodeTask.model_json_schema())
    print("#####################################")

    response = prompting.run_and_get_result(add_response_to_context=True, format=ExperimentSingleCodeTask.model_json_schema())

    # Print the response
    print(response)
    print("#####################################")
    print(prompting.get_context())

def test_plain(model):

    prompt = [{"role": "user", "content": "Consider the context description of the domain:We want to capture how a car rental company works who's involved, what cars we have, and how the rentals are managed.We've got people both employees and customers. Everyone's just a person at the base, with basic info like first name, last name, age, and whether they're married. Customers have an address, and employees have a salary. Employees work at branches, and some of them manage those branches. Each branch has a location, and can have a numerous employees and a manager.We also have cars, and we don't just track individual vehicles we organize them into car groups, like compact, intermediate, and luxury. Car groups can even be ranked, this is, one group being higher than another, maybe for pricing or upgrade purposes.A rental is tied to a customer and usually to a branch. Sometimes the rental is for a specific car, and other times it's just for a group of cars. Each rental has a start and end date. A customer can have multiple rentals, and cars might go through different rentals over time.There's also this idea of a service depot basically just a location, probably where cars get maintained or stored. And there's also a \"check\", which contains a description maybe that's for inspections or service reports.Finally, customers can't exist in isolation they're linked to rentals, which are linked to cars, which are linked to branches.\n\nCode this constraint in OCL:A car group must not be the higher group of its own higher group, and it must not be the lower group of its own lower group.        Format the output as a JSON object with the following structure:        {            \"code\": \"generated code for the constraint\"        }        Do not include explanations, examples, or usage demonstrations. Only provide the JSON array."}]

    client = OLlamaClient(host="http://ollama.:11434")
    options =  {"temperature": 0.3}
    chat_completion = client.chat(
        model=model, 
        stream=False, 
        messages=prompt,
        options=options,
    )    

    response = chat_completion.message.content

    # the following is to remove the thinking from DeepSeek models
    response = re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL).strip()

    print(response)

test_plain("codellama:7b")