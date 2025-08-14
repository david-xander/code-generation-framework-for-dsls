import sys
sys.path.append('../')
import os
import pandas as pd
from parsers.grammars.ocl.validate import Validation as OclValidation
from parsers.grammars.alloy.validate import Validation as AlloyValidation
from parsers.grammars.python.validate import Validation as PythonValidation

class CheckForWellFormedness():
    def __init__(self, filename, filepath, targetpath):
        self.filename = filename
        self.filepath = filepath
        self.targetpath = targetpath
        self.ds = pd.read_csv(os.path.join(filepath,filename))
        self.ds.reset_index()

    def run(self):
        print("Starting Well-formedness checking of file... ")
        OclValidator = OclValidation()
        AlloyValidator = AlloyValidation()
        PythonValidator = PythonValidation()

        def run_validation(x):
            x["W.F."] = 0
            x["W.F.FEEDBACK"] = ""

            if not x["TASK"] == -1:
                if x["LANGUAGE"] == "OCL":
                    res = OclValidator.validate(x["RESULT"])
                    x["W.F."] = res["result"]
                    x["W.F.FEEDBACK"] = res["desc"]
                elif x["LANGUAGE"] == "ALLOY":
                    res = AlloyValidator.validate(x["RESULT"])
                    x["W.F."] = res["result"]
                    x["W.F.FEEDBACK"] = res["desc"]
                elif x["LANGUAGE"] == "PYTHON":
                    res = PythonValidator.validate(x["RESULT"])
                    x["W.F."] = res["result"]
                    x["W.F.FEEDBACK"] = res["desc"]                    
            return x
    
        self.ds = self.ds.apply(run_validation, axis=1)
        self.ds = self.ds[["MODEL","LANGUAGE","PS","TASK","RESULT","W.F.","W.F.FEEDBACK"]]
        self.save_to_disk()

    def run_second_pass(self):
        print("Starting Well-formedness checking of file... ")

        OclValidator = OclValidation()
        AlloyValidator = AlloyValidation()
        PythonValidator = PythonValidation()

        def run_validation(x):
            x["W.F.Old"] = ""
            x["W.F.FEEDBACK.Old"] = ""

            if not x["TASK"] == -1 and int(x["W.F."]) <= 0:
                x["W.F.Old"] = x["W.F."]
                x["W.F.FEEDBACK.Old"] = x["W.F.FEEDBACK"]

                if x["LANGUAGE"] == "OCL":
                    res = OclValidator.validate(x["RESULT"])
                    x["W.F."] = res["result"]
                    x["W.F.FEEDBACK"] = res["desc"]
                elif x["LANGUAGE"] == "ALLOY":
                    res = AlloyValidator.validate(x["RESULT"])
                    x["W.F."] = res["result"]
                    x["W.F.FEEDBACK"] = res["desc"]
                elif x["LANGUAGE"] == "PYTHON":
                    res = PythonValidator.validate(x["RESULT"])
                    x["W.F."] = res["result"]
                    x["W.F.FEEDBACK"] = res["desc"]                 
            return x
    
        self.ds = self.ds.apply(run_validation, axis=1)      
        self.save_to_disk()
        
    def save_to_disk(self):
        fp = os.path.join(self.targetpath, self.filename)
        print("Saving file '"+fp+"' to disk")
        self.ds.to_csv(fp, index=False)
