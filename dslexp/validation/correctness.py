import sys
sys.path.append('../')
import os
import json
import pandas as pd
from dslexp.llm_factory import PromptingServiceFactory
from datetime import datetime

class PromptingDataBuilder():
    def __init__(self,domain_context, coding_tasks):
        self.domain_context = domain_context
        self.coding_tasks = coding_tasks
        self.language = "PYTHON"
        self.code = ""
        self.task = ""
    
    def set_language(self, language):
        self.language = language

    def set_task(self, task):
        self.task = self.get_task_description(task)

    def set_code(self, code):
        self.code = code

    def get_validation_task_instructions(self):
        res = f"""Validate the correctness of the given code in {self.language} with the provided task description. The output should be in JSON format, with "result" indicating whether the code is correct (1 for correct, 0 for incorrect) and "desc" providing a short explanation of why the code does not work."""
        return res

    def get_nl_context(self):
        res = "Domain context:\n" + self.domain_context
        return res
    
    def get_task_to_validate(self):
        res = "Task description:\n" + self.task
        return res
    
    def get_code_to_validate(self):
        msg = "Code in "+self.language+":\n"
        res = msg + self.code
        return res
    
    def get_output_format(self):
        res = """Output format:\n{\n\t"result": 1 or 0,\n\t"desc": "Short explanation"}\nPlease evaluate the code and return the JSON response."""
        return res

    def get_task_description(self, task_number):
        return self.coding_tasks[task_number]


class CheckForCorrectness():
    def __init__(self, filename, filepath, targetpath, domain_context,coding_tasks,model):
        self.filename = filename
        self.filepath = filepath
        self.targetpath = targetpath    
        self.ds = pd.read_csv(os.path.join(filepath,filename))
        self.ds.reset_index()            
        self.model = model
        self.data = PromptingDataBuilder(domain_context, coding_tasks)
        self.prompting = PromptingServiceFactory.get_instance(self.model)

    def validate_correctness(self, task, code, language):
        self.data.set_language(language)
        self.data.set_task(task)
        self.data.set_code(code)

        self.prompting.clear_context()
        self.prompting.add_to_context( self.data.
        get_validation_task_instructions() )
        self.prompting.add_to_context( self.data.get_task_to_validate() )
        self.prompting.add_to_context( self.data.get_code_to_validate() )
        self.prompting.add_to_context( self.data.get_nl_context() )
        self.prompting.add_to_context( self.data.get_output_format() )

        response = self.prompting.run_and_get_result()
        prompt_context = json.dumps( self.prompting.get_context(), indent=2 )

        res = self.process_llm_response(response, prompt_context)

        return res

    def process_llm_response(self, raw_response, cprompt):
        try:
            cleaned_response = raw_response.strip().strip('```').strip('json').strip()
            parsed_response = json.loads(cleaned_response)
            
            # Validate that the necessary keys exist
            if "result" in parsed_response and "desc" in parsed_response:
                return {"result": parsed_response["result"], "desc": parsed_response["desc"], "cprompt":cprompt, "crawresp": raw_response}
            else:
                return {"error": "Missing required keys 'result' or 'desc'"}
        except json.JSONDecodeError:
            return {"result": "UNKNOWN", "desc": "ERROR PROCESSING LLM OUTPUT: Invalid JSON FORMAT", "cprompt":cprompt, "crawresp": raw_response}


    def run(self):
        print("Starting Correctness validation of file... ")

        log = []
        def run_validation(x):
            x["CORRECTNESS"] = 0
            x["C.FEEDBACK"] = ""
            x["C.PROMPT"] = ""
            x["C.RAWRESP"] = "" 

            print(x["LANGUAGE"], x["TASK"])

            if not x["TASK"] == -1 and int(x["W.F."]) > 0:
                task = self.convert_task_string_to_int(x["TASK"])
                code = x["RESULT"]
                language = x["LANGUAGE"]
                res = self.validate_correctness(task, code, language)

                res_int = res["result"]
                if isinstance(res["result"], list) and len(res["result"]) == 1:
                    res_int = res["result"][0]

                x["CORRECTNESS"] = res_int
                x["C.FEEDBACK"] = res["desc"]
                x["C.PROMPT"] = res["cprompt"]
                x["C.RAWRESP"] = res["crawresp"]
                reg = "Result prompting "+str(x["PS"])+": "+str(x["TASK"])+" in "+x["LANGUAGE"]+" returns: "+str(res["result"])
                log.append(reg)
            else:
                language = x["LANGUAGE"]
                reg = "Skipping task "+str(x["TASK"])+" from "+str(x["PS"])+" in language "+x["LANGUAGE"]
                log.append(reg)
            
            return x
    
        self.ds = self.ds.apply(run_validation, axis=1)
        self.ds = self.ds[["MODEL","LANGUAGE","PS","TASK","RESULT","W.F.","W.F.FEEDBACK","W.F.C.R.","CORRECTNESS","C.FEEDBACK","C.PROMPT", "C.RAWRESP"]]          
        self.save_to_disk()
        self.save_log(log)
        

    def run_second_pass(self):
        print("Starting Correctness validation of file... ")

        log = []
        def run_validation(x):
            x["CORRECTNESS.Old"] = ""
            x["C.FEEDBACK.Old"] = ""
            x["C.PROMPT.Old"] = ""
            x["C.RAWRESP.Old"] = "" 

            if not x["TASK"] == -1 and int(x["W.F."]) > 0 and int(x["CORRECTNESS"]) == 0:
                x["CORRECTNESS.Old"] = x["CORRECTNESS"]
                x["C.FEEDBACK.Old"] = x["C.FEEDBACK"]
                x["C.PROMPT.Old"] = x["C.PROMPT"]
                x["C.RAWRESP.Old"] = x["C.RAWRESP"]

                task = self.convert_task_string_to_int(x["TASK"])
                code = x["RESULT"]
                language = x["LANGUAGE"]
                res = self.validate_correctness(task, code, language)

                res_int = res["result"]
                if isinstance(res["result"], list) and len(res["result"]) == 1:
                    res_int = res["result"][0]

                x["CORRECTNESS"] = res_int
                x["C.FEEDBACK"] = res["desc"]
                x["C.PROMPT"] = res["cprompt"]
                x["C.RAWRESP"] = res["crawresp"]
                reg = "Result prompting "+str(x["PS"])+": "+str(x["TASK"])+" in "+x["LANGUAGE"]+" returns: "+str(res["result"])
                log.append(reg)
            else:
                language = x["LANGUAGE"]
                reg = "Skipping task "+str(x["TASK"])+" from "+str(x["PS"])+" in language "+x["LANGUAGE"]
                log.append(reg)
            
            return x
    
        self.ds = self.ds.apply(run_validation, axis=1)
        self.save_to_disk()
        self.save_log(log)

    def convert_task_string_to_int(self, task_string):
        return int(task_string) - 1

    def save_to_disk(self):
        fp = os.path.join(self.targetpath, self.filename)
        print("Saving file '"+fp+"' to disk")
        self.ds.to_csv(fp, index=False)

    def save_log(self, log):
        filename, _ = os.path.splitext(self.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        fp = os.path.join("logs", f"{filename}_correctness_{timestamp}.log")
        with open(fp, 'w') as f:
            for line in log:
                f.write(f"{line}\n")                
