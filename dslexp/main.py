import click
import os
import json
import re
import pandas as pd
from explib import Experiment
from validation.well_formedness import CheckForWellFormedness
from validation.correctness import CheckForCorrectness
from coderepair.well_formedness import WFCodeRepair
from coderepair.correctness import CorrectnessCodeRepair

@click.command()
@click.option('--k', default=1, help='Number of instances, pass@k')
@click.option('--step', default=None, type=int, help='Peform only this step. Cannot be used with --start')
@click.option('--start', default=0, type=int, help='Start form this step. Cannot be use with --step')
@click.option('--end', default=99, type=int, help='End experiment afther this step. Cannot be use with --step')
@click.option('--template', default=None, type=int, help='Run the experiment using only one prompt template: the one specified with this option.')
@click.option('--domain', default=None, type=str, help='To select a specific domain')
@click.option('--language', default=None, type=str, help='Use only this language.')
@click.option('--option', default=None, type=int, help='Use only this option.')
@click.argument('dataset')
def main(dataset, k, step, start, end, template, domain, language, option):
    result_f = "_results"
    codegen_f = os.path.join(result_f,"1_code_generation")
    wf_1_f = os.path.join(result_f,"2_wf_1")
    wf_code_repair_f = os.path.join(result_f,"3_wf_code_repair")
    wf_2_f = os.path.join(result_f,"4_wf_2")
    correctness_1_f = os.path.join(result_f,"5_corr_1")
    corr_code_repair_f = os.path.join(result_f,"6_corr_code_repair")
    correctness_2_f = os.path.join(result_f,"7_corr_2")
    final_f = os.path.join(result_f,"final")

    steps = []
    if not step==None:
        steps = [step]
    else:
        steps = range(start, end)

    print("[START] Experiment")
    print("pass@k=",k)
    print("start",start)
    print("end",end)
    print("step",step)
    print("template",template)
    print("resulting steps involved",steps)

    df = pd.read_json(dataset, encoding="utf-8")

    languages = ["ALLOY","OCL","PYTHON"]
    options = [1, 3]

    if not language == None:
        languages = [language]
    if not option == None:
        options = [option]        
    if not domain == None:
        print("domain",domain)
        df = df[df["domain_name"] == domain]
    else:
        # Bad idea to do this, because we cannot paralelize anything
        print("domain","ALL")

    print("languages", languages)

    for index, row in df.iterrows():
        domain_name = row["domain_name"]
        domain_context = row["domain_context"]
        coding_tasks = [item["specification"] for item in row["constraints"]]
        class_diagram_puml = row["plantuml_model"]
        class_diagram_nl = row["nl_model"]

        if not len(coding_tasks) > 0:
            print(f"[ERROR]: There are no constraints defined in the dataset for the domain: {domain_name}")
            return False

        judging_model = "gpt-4o-mini"
        # code_repair_model = "gpt-4o-mini"
        code_repair_model = "deepseek-coder:6.7b"
        results = []
        # models = ["gpt-4o-mini","gpt-4o"]
        models = ["deepseek-coder:6.7b"]
        
        
        if 1 in steps:
        # step1: Code Generation (pass@k)
            print("\n\n\nStep (1): Code Generation (pass@k)")
            for i in range(0, k):
                for model in models:
                    for option in options:
                        for lang in languages:
                            print("\n\nPASS@K=",i+1)
                            print("domain_name: ", domain_name)
                            print("model:", model)
                            print("option: ", option)                            
                            print("language: ", lang)
                            filename = f"""{domain_name}_{model}-{lang}_op{option}_pass@{k}_instance{i+1}.csv"""
                            if template is None:
                                pass
                            else:
                                print("template: ", template)
                                filename = f"""{domain_name}_{model}-{lang}-{template}_op{option}_pass@{k}_instance{i+1}.csv"""
                            path = os.path.join(codegen_f, filename)
                            experiment = Experiment(domain_context=domain_context, 
                                                    coding_tasks=coding_tasks, 
                                                    class_diagram_puml=class_diagram_puml, 
                                                    class_diagram_nl=class_diagram_nl,
                                                    languages=[lang],
                                                    model=model,
                                                    file_name=path,
                                                    constraints_explanation=True)
                            
                            # To be able to resume interrupted code generation
                            if not os.path.exists(path):
                                if template is None:
                                    experiment.run_experiment(option=option)
                                else:
                                    experiment.run_template(template=template, option=option)
                            else:
                                print("ALREADY GENERATED!")
                            # results.append(filename)

        # if len(results) == 0:
        csv = [file for file in os.listdir(codegen_f) if file.endswith('.csv')]
        for filename in csv:
            match2 = re.search(r'^(.+?)_', filename)
            if match2 and match2.group(1) == domain_name:
                results.append(filename)                

        if 2 in steps:
            # step2: Check for well-formedness
            print("\n\n\nStep (2): Check for well-formedness")
            for filename in results:
                val = CheckForWellFormedness(filename=filename, filepath=codegen_f, targetpath=wf_1_f)
                val.run()

        if 3 in steps:
            # step3: Code repair (W.F.)
            print("\n\n\nStep (3): Code repair (W.F.)")
            for filename in results:
                val = WFCodeRepair(filename=filename, filepath=wf_1_f, targetpath=wf_code_repair_f, domain_context=domain_context, coding_tasks=coding_tasks, model=code_repair_model)
                val.run()

        if 4 in steps:
            # step4: Check for well-formedness (second pass)
            print("\n\n\nStep (4): Check for well-formedness (second pass)")
            for filename in results:
                val = CheckForWellFormedness(filename=filename, filepath=wf_code_repair_f, targetpath=wf_2_f)
                val.run_second_pass()   

        if 5 in steps:
            # step5: Check for Correctness
            print("\n\n\nStep (5): Check for Correctness")
            for filename in results:
                val = CheckForCorrectness(filename=filename, filepath=wf_2_f, targetpath=correctness_1_f, domain_context=domain_context, coding_tasks=coding_tasks, model=judging_model)
                val.run()

        if 6 in steps:
            # step6: Code repair (Correctness)
            print("\n\n\nStep (6): Code repair (Correctness)")
            for filename in results:
                val = CorrectnessCodeRepair(filename=filename, filepath=correctness_1_f, targetpath=corr_code_repair_f, domain_context=domain_context, coding_tasks=coding_tasks, model=code_repair_model)
                val.run()
        
        if 7 in steps:
            # step7: Check for correctness (second pass)
            print("\n\n\nStep (7): Check for correctness (second pass)")
            for filename in results:
                val = CheckForCorrectness(filename=filename, filepath=corr_code_repair_f, targetpath=correctness_2_f, domain_context=domain_context, coding_tasks=coding_tasks, model=judging_model)
                val.run_second_pass()
        
        if 8 in steps:
            # step8: Keep only the necessary fields from the datasets
            # just enough for the analysis. Everything else, 
            # which is auxiliary and meant for historical analysis
            # remains in the different versions of the files
            print("\n\n\nStep (FINAL): Generate final datasets")
            for filename in results:
                ds = pd.read_csv(os.path.join(correctness_2_f,filename))
                ds.reset_index()
                ds["INSTANCE"] = -1
                ds["PASS@K"] = k
                ds["DATASET"] = dataset
                ds["DOMAIN_NAME"] = ""
                ds["OPTION"] = -1

                match1 = re.search(r'instance(\d+)\.csv$', filename)
                if match1:
                    ds["INSTANCE"] = int(match1.group(1))                   
                match2 = re.search(r'^(.+?)_', filename)
                if match2:
                    ds["DOMAIN_NAME"] = match2.group(1)
                match3 = re.search(r'_op(\d+)_', filename)
                if match3:
                    ds["OPTION"] = int(match3.group(1))                     

                ds = ds[["INSTANCE","PASS@K","OPTION","DATASET","MODEL","DOMAIN_NAME","LANGUAGE","PS","TASK","RESULT","W.F.","W.F.FEEDBACK","W.F.C.R.","CORRECTNESS","C.FEEDBACK","C.C.R."]]

                fp = os.path.join(final_f, filename)
                print("Saving FINAL file '"+fp+"' to disk")
                ds.to_csv(fp, index=False)            

    print("\n\n[END] Experiment")

if __name__ == "__main__":
    main()