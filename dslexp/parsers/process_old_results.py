import pandas as pd
import re
import os


class ProcessOld():
    def __init__(self, file_path):
        self.file_path = file_path

    def process(self):
        new_ds = []

        ds = pd.read_excel(self.file_path)
        ds = ds[ds["TASK"]=="T1"]
        
        for index, x in ds.iterrows():
            response = x["RAW RESULT"]
            number_of_tasks = 14
            tasks_code = []

            if x["LANGUAGE"] == "OCL":
                tasks_code = self.extract_ocl_code(response)
                if len(tasks_code) != number_of_tasks:
                    tasks_code = self.extract_ocl_code2(response)
            elif x["LANGUAGE"] == "ALLOY":
                tasks_code = self.extract_facts_from_alloy(response)
            elif x["LANGUAGE"] == "PYTHON":
                tasks_code = self.extract_functions_from_python(response)
            


            if len(tasks_code) == number_of_tasks:
                for i, item in enumerate(tasks_code):
                    item = {
                        "MODEL": x["MODEL"], 
                        "LANGUAGE": x["LANGUAGE"],
                        "PS": x["PS"],
                        "TASK": "T"+str(i+1),
                        "RESULT": item["code"]
                    }
                    new_ds.append(item)
            else:
                test = {
                    "MODEL": x["MODEL"], 
                    "LANGUAGE": x["LANGUAGE"],
                    "PS": x["PS"],
                }
                print(test, len(tasks_code), number_of_tasks)                
                print("Number of tasks unmatch tasks identified in the code!")  
                item = {
                    "MODEL": x["MODEL"], 
                    "LANGUAGE": x["LANGUAGE"],
                    "PS": x["PS"],
                    "TASK": "T-ERROR",
                    "RESULT": "ERROR"
                }
                new_ds.append(item)                    

        self.save_to_disk(pd.DataFrame(new_ds), "FUNCTIONS_EXTRACTED", path)


    def extract_ocl_code(self,response):
        # Define a regex pattern for OCL code blocks
        pattern = re.compile(r"```ocl\n(?P<code>.*?)```", re.DOTALL)
        
        # Find all matches
        matches = pattern.finditer(response)
        
        # Extract code blocks in order
        ocl_listings = []
        for idx, match in enumerate(matches, start=1):
            ocl_listings.append({
                "id": idx,
                "code": match.group("code").strip()
            })
        
        return ocl_listings

    def extract_facts_from_alloy(self,response):
        # Extract the content of the code block
        code_block_match = re.search(r"```alloy\n(.*?)\n```", response, re.DOTALL)
        if not code_block_match:
            return []

        alloy_code = code_block_match.group(1)

        # Find all facts in the Alloy code
        fact_pattern = r"fact\s+\w+\s*\{(\{[^{}]*\}|[^{}])*?\}"        
        fact_matches = list(re.finditer(fact_pattern, alloy_code, re.DOTALL))

        # Build the result list
        facts = []
        for idx, match in enumerate(fact_matches):
            fact_code = match.group(0)
            facts.append({"id": idx, "code": fact_code})

        return facts        

    def extract_functions_from_python(self,response):
        # Extract the content of the code block
        code_block_match = re.search(r"```python\n(.*?)\n```", response, re.DOTALL)
        if not code_block_match:
            return []

        python_code = code_block_match.group(1)

        # Find all function definitions in the Python code
        function_matches = list(re.finditer(r"def\s+\w+\s*\(.*?\):.*?(?=\n\S|\Z)", python_code, re.DOTALL))

        # Build the result list
        functions = []
        for idx, match in enumerate(function_matches):
            function_code = match.group(0)
            functions.append({"id": idx, "code": function_code})
        
        return functions

    def extract_ocl_code2(self,response):
        # Extract the content of the code block
        code_block_match = re.search(r"```ocl\n(.*?)\n```", response, re.DOTALL)
        if not code_block_match:
            return []

        text = code_block_match.group(1)

        pattern = re.compile(r"context\s+\w+\b.*?(?=\ncontext\s+\w+\b|\Z)", re.DOTALL)

        # Find all matches
        matches = pattern.findall(text)

        # Build the result list
        res = []
        for idx, match in enumerate(matches):
            code = match.strip()
            res.append({"id": idx, "code": code})

        return res

    def save_to_disk(self,nds, suffix, file_path):
        filename, file_extension = os.path.splitext(file_path)
        fp = filename + "_" + suffix +".csv"
        print("Saving file '"+fp+"' to disk")
        nds.to_csv(fp, index=False)




# From gpt-4o-mini: I can't extract the Python code (previous to the Python specific prompt)
# From gpt-4o: I've got errors with ALLOY with prompting templates (P8 and P11

paths = ["/Users/david/My Drive/DOCTORADO/Researching my Thesis topic/experiment/dslexp/_results/exp02_gpt-4o-python2.xlsx", "/Users/david/My Drive/DOCTORADO/Researching my Thesis topic/experiment/dslexp/_results/exp02_gpt-4o.xlsx", "/Users/david/My Drive/DOCTORADO/Researching my Thesis topic/experiment/dslexp/_results/exp02_gpt-4o-mini.xlsx"]

for path in paths:
    p = ProcessOld(path)
    p.process()
