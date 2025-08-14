import sys
sys.path.append('../')
import os
import json
import pandas as pd
from dslexp.llm_factory import PromptingServiceFactory
from datetime import datetime
from pydantic import BaseModel

class PromptingDataBuilder():
    def __init__(self, domain_context, coding_tasks):
        self.domain_context = domain_context
        self.coding_tasks = coding_tasks
        self.language = "PYTHON"
        self.code = ""
        self.task = ""
        self.error = ""
    
    def set_language(self, language):
        self.language = language

    def set_task(self, task):
        self.task = self.get_task_description(task)

    def set_code(self, code):
        self.code = code

    def set_error(self, error):
        self.error = error

    def get_code_repair_task(self):
        res = f"""Given a task description, the code in {self.language} and the error feedback from the parser. 
        First: Reason about why this error is happening.  Second: Fix the code accordingly. 
        The output should be in JSON format, with "result" providing the fixed code, and "desc" to provide a short explanation of why the error was happening."""
        return res

    def get_error_feedback(self):
        res = f"Error feedback:\n{self.error}"
        return res
    
    def get_task_to_check(self):
        res = f"Task description:\n{self.task}" 
        return res
    
    def get_code_to_check(self):
        msg = f"Code in {self.language}:\n"
        res = msg + self.code
        return res
    
    def get_output_format(self):
        res = """Output format:\n{\n\t"result": "fixed code",\n\t"desc": "Short explanation"}\nPlease repair the code and return the JSON response."""
        return res

    def get_task_description(self, task_number):
        return self.coding_tasks[task_number]

class CheckResponse(BaseModel):
    result: str
    desc: str

class WFCodeRepair():
    def __init__(self, filename, filepath, targetpath, domain_context, coding_tasks, model):
        self.filename = filename
        self.filepath = filepath
        self.targetpath = targetpath
        self.ds = pd.read_csv(os.path.join(filepath,filename))
        self.ds.reset_index()

        self.model = model
        self.data = PromptingDataBuilder(domain_context, coding_tasks)
        self.prompting = PromptingServiceFactory.get_instance(self.model)

    def code_repair(self, task, code, language, error):
        self.data.set_language(language)
        self.data.set_task(task)
        self.data.set_code(code)
        self.data.set_error(error)

        self.prompting.clear_context()
        self.prompting.add_to_context( self.data.
        get_code_repair_task() )
        self.prompting.add_to_context( self.data.get_task_to_check() )
        self.prompting.add_to_context( self.data.get_code_to_check() )
        self.prompting.add_to_context( self.data.get_error_feedback() )
        self.prompting.add_to_context( self.data.get_output_format() )

        response = self.prompting.run_and_get_result(add_response_to_context=False, format=CheckResponse.model_json_schema())
        prompt_context = json.dumps( self.prompting.get_context(), indent=2 )

        res = self.process_llm_response(response, prompt_context)

        return res

    def process_llm_response(self, raw_response, cprompt):
        try:
            cleaned_response = raw_response.strip().strip('```').strip('json').strip()
            parsed_response = json.loads(cleaned_response)
            
            # check that the necessary keys exist
            if "result" in parsed_response and "desc" in parsed_response:
                return {"result": parsed_response["result"], "desc": parsed_response["desc"], "cprompt":cprompt, "crawresp": raw_response}
            else:
                return {"error": "Missing required keys 'result' or 'desc'"}
        except json.JSONDecodeError:
            return {"result": "UNKNOWN", "desc": "ERROR PROCESSING LLM OUTPUT: Invalid JSON FORMAT", "cprompt":cprompt, "crawresp": raw_response}


    def run(self):
        print("Starting Code-Repair of file... ")

        log = []
        def run_validation(x):
            x["W.F.C.R."] = 0
            x["RESULT.Old"] = ""
            x["W.F.C.R.Explanation"] = ""
            x["W.F.C.R.PROMPT"] = ""
            x["W.F.C.R.RAWRESP"] = "" 

            print(x["LANGUAGE"], x["TASK"])            

            if not x["TASK"] == -1 and int(x["W.F."]) <= 0:
                task = self.convert_task_string_to_int(x["TASK"])
                code = x["RESULT"]
                language = x["LANGUAGE"]
                error = x["W.F.FEEDBACK"]
                res = self.code_repair(task, code, language, error)
                x["W.F.C.R."] = 1
                x["RESULT.Old"] = x["RESULT"]
                x["RESULT"] = res["result"]
                x["W.F.C.R.Explanation"] = res["desc"]
                x["W.F.C.R.PROMPT"] = res["cprompt"]
                x["W.F.C.R.RAWRESP"] = res["crawresp"]
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
        fp = os.path.join("logs", f"{filename}_wf_cr_{timestamp}.log")
        with open(fp, 'w') as f:
            for line in log:
                f.write(f"{line}\n")

