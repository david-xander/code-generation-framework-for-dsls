import os
import pandas as pd
import json
import re
from llm_factory import PromptingServiceFactory
from pydantic import BaseModel

class StoreData():
    def __init__(self, columns):
        self.data = []
        self.columns = columns

    def add(self, content):
        self.data.append( content )

    def save_to_csv(self, filename):
        df = pd.DataFrame(self.data, columns=self.columns)
        df.to_csv(filename, index=False)
        print(f"Data saved to {filename}")

class PromptingDataBuilder():
    def __init__(self,domain_context, coding_tasks, class_diagram_puml, class_diagram_nl):
        self.domain_context = domain_context
        self.coding_tasks = coding_tasks
        self.class_diagram_puml = class_diagram_puml
        self.class_diagram_nl = class_diagram_nl
        self.language = "PYTHON"

    def set_language(self, language):
        self.language = language

    def get_nl_context(self):
        res = "Consider the context description of the domain:\n" + self.domain_context
        return res

    def get_class_diagram_puml(self):
        res = "Below is the domain model described in PlantUML:\n" + self.class_diagram_puml
        return res
    
    def get_class_diagram_nl(self):
        res = "Below is the domain model described in natural language:\n" + self.class_diagram_nl
        return res
    
    def get_coding_task(self, coding_task):
        res = f"Code this constraint in {self.language}:\n{coding_task}"
        if self.language == "ALLOY":
            res = f"Code this constraint in {self.language}, ensuring that it is represented as a single 'fact':\n{coding_task}"
        elif self.language == "PYTHON":
            res = f"Code this constraint in {self.language}, ensuring that it is represented as a single 'def':\n{coding_task}"
        
        res += """
        Format the output as a JSON object with the following structure:
        {
            "code": "generated code for the constraint"
        }


        Do not include explanations, examples, or usage demonstrations. Only provide the JSON array.
        """
        return res
    
    def get_explain_it_in_nl(self):
        res = "Explain it in natural language"
        return res
    
    def get_code_domain_model_in_nl(self):
        res = "Create the Domain Model of the context in natural language"
        return res
    
    def get_code_domain_model_in_puml(self):
        res = "Create the Domain Model of the context in PLANTUML"
        return res  
    
    def get_code_all(self):
        res = f"Code the following constraints in {self.language}, ensuring each is represented distinctly:"
        if self.language == "ALLOY":
            res = f"Code the following constraints in {self.language}, ensuring each is represented as a separate 'fact':"
        elif self.language == "PYTHON":
            res = f"Code the following constraints in {self.language}, ensuring each is represented as a separate 'def':"
        
        for i, task in enumerate(self.coding_tasks):
            res = res + f"\n{i+1}. {task}"
        
        res += """
        Format the output as a JSON array with the following structure:
        {
            "tasks": [
                {
                    "id": "constraint number from the list",
                    "code": "generated code for the constraint"
                }
            ]
        }
        Do not include explanations, examples, or usage demonstrations. Only provide the JSON array.
        """
        return res
    
    def get_constraints_explanation(self):
        res = None
        if self.language == "PYTHON":
            res = "Think of a constraint test as a boolean function. You don't need to program an entire application, assume the application already exists. Your task is to create a function that evaluates the properties described in the coding task and returns 'True' or 'False' based on whether the constraint is satisfied. Assume that system entities are represented as data structures like lists, tuples, or dictionaries. Your job is to check if all instances within a specific context comply with the given constraint."
        elif self.language == "ALLOY":
            res = "Keep each constraint as a separate 'fact'. Do not combine multiple constraints into a single 'fact'."
        return res

class ExperimentOption3Response(BaseModel):
    code: str

class ExperimentCodingTaskResponse(BaseModel):
    id: int
    code: str

class ExperimentOption1Response(BaseModel):
    tasks: list[ExperimentCodingTaskResponse]

class Experiment():
    # P1	Given NL context: 1) Code restrictions
    # P2	Given a class diagram in PlantUML: Code restrictions 
    # P3	Given a class diagram in NL: Code restrictions 
    # P4	Given a class diagram in PlantUML: 1) Explain code in NL, 2) Code restrictions 
    # P5	Given a class diagram in NL: 1) Explain code in NL, 2) Code restrictions 
    # P6	Given NL context: 1) Code the domain model diagram in NL, 2) Code restrictions
    # P7	Given NL context: 1) Code the domain model diagram in PlantUML, 2) Code restrictions
    # P8	Given NL context and a class diagram in PlantUML: Code restrictions
    # P9	Given NL context and a class diagram in NL: Code restrictions

    # OP1: All requirements are requested in a single prompt. A single response is obtained with all the requirements coded in the requested language.
    # OP2: All requirements are requested one by one in different prompts. As responses are obtained, they are stored in the context. Thus, the last requirement has the context of the questions and answers for all previous requirements. This is how ChatGPT functions unless a new chat is created for each question.
    # OP3: All requirements are requested one by one in different prompts. A common session is not maintained. Therefore, while crafting any prompt, there is no knowledge of any other constraints aside from the one being requested.

    def __init__(self, domain_context, coding_tasks, class_diagram_puml, class_diagram_nl, languages, model, file_name, constraints_explanation=False):
        self.languages = languages
        self.model = model
        self.file_name = file_name
        self.coding_tasks = coding_tasks
        self.number_of_tasks = len(self.coding_tasks)
        self.constraints_explanation = constraints_explanation
        self.data = PromptingDataBuilder(domain_context, self.coding_tasks, class_diagram_puml, class_diagram_nl)
        self.storage = StoreData(["MODEL","LANGUAGE", "PS", "TASK", "RESULT", "RAW RESULT", "PROMPT"])
        self.prompting = PromptingServiceFactory.get_instance(self.model)

    def persist(self, prompt_style, prompt_option, language, response, rawres, task=None):
        prompt_context = json.dumps( self.prompting.get_context(), indent=2 )
        if prompt_option == 1:
            print(f"Persisting {self.model} {prompt_style}-{prompt_option} in {language}: ALL TASKS")

            tasks_code = self.extract_code_list_from_llm_response(response)
            if isinstance(tasks_code, int):
                print("[ERROR] JSON format. ErrorCode:", tasks_code)
            elif not isinstance(tasks_code, list):
                print("[ERROR] Not able to obtain a list of tasks from response!")
            elif not len(tasks_code) == self.number_of_tasks:
                print("[ERROR] Number of tasks and split tasks don't match!", "target->", self.number_of_tasks, "| returned->", len(tasks_code))                
            
            if isinstance(tasks_code, list) and len(tasks_code) == self.number_of_tasks:
                for i, item in enumerate(tasks_code):
                    raw_result = ""
                    if i == 0: raw_result = rawres
                    self.storage.add([self.model, 
                                    language, 
                                    prompt_style, 
                                    (i+1), 
                                    item,
                                    raw_result, 
                                    prompt_context])
            else:
                self.storage.add([self.model, 
                                language, 
                                prompt_style, 
                                -1, 
                                "[ERROR] SPLITING CODE IN CODE TASKS",
                                rawres, 
                                prompt_context])
            
        elif prompt_option == 3:
            print(f"Persisting {self.model} {prompt_style}-{prompt_option} in {language}: T{str(task+1)}")

            cleaned_resp = self.extract_code_from_llm_response(response)
            if isinstance(cleaned_resp, int):
                print("[ERROR] JSON format. ErrorCode:", cleaned_resp)
            if not isinstance(cleaned_resp, str):
                print("[ERROR] Not able to obtain a string with the code from response!")
            if cleaned_resp == "":
                print("[ERROR] Empty code response!")

            task_number = task
            if isinstance(cleaned_resp, str) and not cleaned_resp == "":
                self.storage.add([  self.model,
                                    language, 
                                    prompt_style, 
                                    (task_number+1), 
                                    cleaned_resp, 
                                    rawres, 
                                    prompt_context])
            else:
                self.storage.add([  self.model, 
                                    language, 
                                    prompt_style,
                                    -1, 
                                    "[ERROR] OBTAINING CODE FROM RESPONSE",
                                    rawres, 
                                    prompt_context])                
            
        else:
            pass

    def extract_code_from_llm_response(self, raw_response):
        try:
            cleaned_response = raw_response.strip().strip('```').strip('json').strip()
            parsed_response = json.loads(cleaned_response)
            
            # check that the necessary keys exist
            if "code" in parsed_response:
                return parsed_response["code"]
            else:
                return -2 # Missing required key 'code'
        except json.JSONDecodeError:
            return -1 # Invalid JSON FORMAT
        
    def extract_code_list_from_llm_response(self, raw_response):
        try:
            cleaned_response = raw_response.strip().strip('```').strip('json').strip()
            parsed_response = json.loads(cleaned_response)
            
            if not "tasks" in parsed_response:
                return -2 # Missing required key 'code'            

            # Check if the parsed response is a list
            if not isinstance(parsed_response["tasks"], list):
                return -3  # Expected a JSON array


            # Ensure each object in the list contains "id" and "code" keys
            code_list = []
            for item in parsed_response["tasks"]:
                if not isinstance(item, dict) or "id" not in item or "code" not in item:
                    return -4 # Missing required key 'code'
                code_list.append(item["code"])  # Collect the "code" value

            return code_list
        except json.JSONDecodeError:
            return -1 # Invalid JSON FORMAT

    def save_to_csv(self):
        self.storage.save_to_csv(self.file_name)

    def run_template(self, template, option):
        if template == 1:
            self.run_p1(option=option)
        elif template == 2:
            self.run_p2(option=option)
        elif template == 3:
            self.run_p3(option=option)
        elif template == 4:
            self.run_p4(option=option)
        elif template == 5:
            self.run_p5(option=option)
        elif template == 6:
            self.run_p6(option=option)
        elif template == 7:
            self.run_p7(option=option)
        elif template == 8:
            self.run_p8(option=option)
        elif template == 9:
            self.run_p9(option=option)
        else:
            self.run_p1(option=option)
        
        self.save_to_csv()
    
    def run_experiment(self, option):
        self.run_p1(option=option)
        self.run_p2(option=option)
        self.run_p3(option=option)
        self.run_p4(option=option)
        self.run_p5(option=option)
        self.run_p6(option=option)
        self.run_p7(option=option)
        self.run_p8(option=option)
        self.run_p9(option=option)

        self.save_to_csv()

    def run_p1(self, option):
        for language in self.languages:
            self.data.set_language(language)
            self.prompting.clear_context()
            self.prompting.add_to_context( self.data.get_nl_context() )

            expl = self.data.get_constraints_explanation()
            if self.constraints_explanation and not expl==None:
                self.prompting.add_to_context( expl )

            if option == 1:
                self.prompting.add_to_context( self.data.get_code_all() )
                response = self.prompting.run_and_get_result(add_response_to_context=True, format=ExperimentOption1Response.model_json_schema())
                self.persist(1, option, language, response, response)                
            elif option == 3:
                for task_number, task in enumerate(self.coding_tasks):
                    self.prompting.add_to_context( self.data.get_coding_task(task) )
                    response = self.prompting.run_and_get_result(add_response_to_context=False, format=ExperimentOption3Response.model_json_schema())
                    self.persist(1, option, language, response, response, task_number)
                    # print( self.prompting.get_context() )
                    self.prompting.delete_last_prompt_from_context()
            else:
                pass

    def run_p2(self, option):
        for language in self.languages:
            self.data.set_language(language)
            self.prompting.clear_context()
            self.prompting.add_to_context( self.data.get_class_diagram_puml() )

            expl = self.data.get_constraints_explanation()
            if self.constraints_explanation and not expl==None:
                self.prompting.add_to_context( expl )

            if option == 1:
                self.prompting.add_to_context( self.data.get_code_all() )
                response = self.prompting.run_and_get_result(add_response_to_context=True, format=ExperimentOption1Response.model_json_schema())
                self.persist(2, option, language, response, response)                
            elif option == 3:
                for task_number, task in enumerate(self.coding_tasks):
                    self.prompting.add_to_context( self.data.get_coding_task(task) )
                    response = self.prompting.run_and_get_result(add_response_to_context=False, format=ExperimentOption3Response.model_json_schema())
                    self.persist(2, option, language, response, response, task_number)
                    # print( self.prompting.get_context() )
                    self.prompting.delete_last_prompt_from_context()
            else:
                pass                          

    def run_p3(self, option):
        for language in self.languages:
            self.data.set_language(language)
            self.prompting.clear_context()
            self.prompting.add_to_context( self.data.get_class_diagram_nl() )

            expl = self.data.get_constraints_explanation()
            if self.constraints_explanation and not expl==None:
                self.prompting.add_to_context( expl )

            if option == 1:
                self.prompting.add_to_context( self.data.get_code_all() )
                response = self.prompting.run_and_get_result(add_response_to_context=True, format=ExperimentOption1Response.model_json_schema())
                self.persist(3, option, language, response, response)                
            elif option == 3:
                for task_number, task in enumerate(self.coding_tasks):
                    self.prompting.add_to_context( self.data.get_coding_task(task) )
                    response = self.prompting.run_and_get_result(add_response_to_context=False, format=ExperimentOption3Response.model_json_schema())
                    self.persist(3, option, language, response, response, task_number)
                    # print( self.prompting.get_context() )
                    self.prompting.delete_last_prompt_from_context()
            else:
                pass                     
    
    def run_p4(self, option):
        for language in self.languages:
            self.data.set_language(language)
            self.prompting.clear_context()
            self.prompting.add_to_context( self.data.get_class_diagram_puml() )
            self.prompting.add_to_context( self.data.get_explain_it_in_nl() )
            response1 = self.prompting.run_and_get_result()

            expl = self.data.get_constraints_explanation()
            if self.constraints_explanation and not expl==None:
                self.prompting.add_to_context( expl )

            if option == 1:
                self.prompting.add_to_context( self.data.get_code_all() )
                response2 = self.prompting.run_and_get_result(add_response_to_context=True, format=ExperimentOption1Response.model_json_schema())
                self.persist(4, option, language, response2, response1+"\n\n"+response2)                
            elif option == 3:
                for task_number, task in enumerate(self.coding_tasks):
                    self.prompting.add_to_context( self.data.get_coding_task(task) )
                    response2 = self.prompting.run_and_get_result(add_response_to_context=False, format=ExperimentOption3Response.model_json_schema())
                    self.persist(4, option, language, response2, response2, task_number)
                    # print( self.prompting.get_context() )
                    self.prompting.delete_last_prompt_from_context()
            else:
                pass                  

    def run_p5(self, option):
        for language in self.languages:
            self.data.set_language(language)
            self.prompting.clear_context()
            self.prompting.add_to_context( self.data.get_class_diagram_nl() )
            self.prompting.add_to_context( self.data.get_explain_it_in_nl() )
            response1 = self.prompting.run_and_get_result()

            expl = self.data.get_constraints_explanation()
            if self.constraints_explanation and not expl==None:
                self.prompting.add_to_context( expl )

            if option == 1:
                self.prompting.add_to_context( self.data.get_code_all() )
                response2 = self.prompting.run_and_get_result(add_response_to_context=True, format=ExperimentOption1Response.model_json_schema())
                self.persist(5, option, language, response2, response1+"\n\n"+response2)                
            elif option == 3:
                for task_number, task in enumerate(self.coding_tasks):
                    self.prompting.add_to_context( self.data.get_coding_task(task) )
                    response2 = self.prompting.run_and_get_result(add_response_to_context=False, format=ExperimentOption3Response.model_json_schema())
                    self.persist(5, option, language, response2, response2, task_number)
                    # print( self.prompting.get_context() )
                    self.prompting.delete_last_prompt_from_context()
            else:
                pass  

    def run_p6(self, option):
        for language in self.languages:
            self.data.set_language(language)
            self.prompting.clear_context()
            self.prompting.add_to_context( self.data.get_nl_context() )
            self.prompting.add_to_context( self.data.get_code_domain_model_in_nl() )
            response1 = self.prompting.run_and_get_result()

            expl = self.data.get_constraints_explanation()
            if self.constraints_explanation and not expl==None:
                self.prompting.add_to_context( expl )

            if option == 1:
                self.prompting.add_to_context( self.data.get_code_all() )
                response2 = self.prompting.run_and_get_result(add_response_to_context=True, format=ExperimentOption1Response.model_json_schema())
                self.persist(6, option, language, response2, response1+"\n\n"+response2)                
            elif option == 3:
                for task_number, task in enumerate(self.coding_tasks):
                    self.prompting.add_to_context( self.data.get_coding_task(task) )
                    response2 = self.prompting.run_and_get_result(add_response_to_context=False, format=ExperimentOption3Response.model_json_schema())
                    self.persist(6, option, language, response2, response2, task_number)
                    # print( self.prompting.get_context() )
                    self.prompting.delete_last_prompt_from_context()
            else:
                pass  

    def run_p7(self, option):
        for language in self.languages:
            self.data.set_language(language)
            self.prompting.clear_context()
            self.prompting.add_to_context( self.data.get_nl_context() )
            self.prompting.add_to_context( self.data.get_code_domain_model_in_puml() )
            response1 = self.prompting.run_and_get_result()

            expl = self.data.get_constraints_explanation()
            if self.constraints_explanation and not expl==None:
                self.prompting.add_to_context( expl )

            if option == 1:
                self.prompting.add_to_context( self.data.get_code_all() )
                response2 = self.prompting.run_and_get_result(add_response_to_context=True, format=ExperimentOption1Response.model_json_schema())
                self.persist(7, option, language, response2, response1+"\n\n"+response2)                
            elif option == 3:
                for task_number, task in enumerate(self.coding_tasks):
                    self.prompting.add_to_context( self.data.get_coding_task(task) )
                    response2 = self.prompting.run_and_get_result(add_response_to_context=False, format=ExperimentOption3Response.model_json_schema())
                    self.persist(7, option, language, response2, response2, task_number)
                    # print( self.prompting.get_context() )
                    self.prompting.delete_last_prompt_from_context()
            else:
                pass              

    def run_p8(self, option):
        for language in self.languages:
            self.data.set_language(language)
            self.prompting.clear_context()
            self.prompting.add_to_context( self.data.get_nl_context() )
            self.prompting.add_to_context( self.data.get_class_diagram_puml() )

            expl = self.data.get_constraints_explanation()
            if self.constraints_explanation and not expl==None:
                self.prompting.add_to_context( expl )

            if option == 1:
                self.prompting.add_to_context( self.data.get_code_all() )
                response = self.prompting.run_and_get_result(add_response_to_context=True, format=ExperimentOption1Response.model_json_schema())
                self.persist(8, option, language, response, response)                
            elif option == 3:
                for task_number, task in enumerate(self.coding_tasks):
                    self.prompting.add_to_context( self.data.get_coding_task(task) )
                    response = self.prompting.run_and_get_result(add_response_to_context=False, format=ExperimentOption3Response.model_json_schema())
                    self.persist(8, option, language, response, response, task_number)
                    # print( self.prompting.get_context() )
                    self.prompting.delete_last_prompt_from_context()
            else:
                pass               
                 
    def run_p9(self, option):
        for language in self.languages:
            self.data.set_language(language)
            self.prompting.clear_context()
            self.prompting.add_to_context( self.data.get_nl_context() )
            self.prompting.add_to_context( self.data.get_class_diagram_nl() )

            expl = self.data.get_constraints_explanation()
            if self.constraints_explanation and not expl==None:
                self.prompting.add_to_context( expl )

            if option == 1:
                self.prompting.add_to_context( self.data.get_code_all() )
                response = self.prompting.run_and_get_result(add_response_to_context=True, format=ExperimentOption1Response.model_json_schema())
                self.persist(9, option, language, response, response)                
            elif option == 3:
                for task_number, task in enumerate(self.coding_tasks):
                    self.prompting.add_to_context( self.data.get_coding_task(task) )
                    response = self.prompting.run_and_get_result(add_response_to_context=False, format=ExperimentOption3Response.model_json_schema())
                    self.persist(9, option, language, response, response, task_number)
                    # print( self.prompting.get_context() )
                    self.prompting.delete_last_prompt_from_context()
            else:
                pass               
