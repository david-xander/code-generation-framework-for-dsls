import pandas as pd
import re

def extract_ocl_code(response):
    # Define a regex pattern for OCL code blocks
    pattern = re.compile(r"```ocl\n(?P<code>.*?)```", re.DOTALL)
    
    # Find all matches
    matches = pattern.finditer(response)
    
    # Extract code blocks in order
    ocl_listings = []
    for idx, match in enumerate(matches, start=1):
        ocl_listings.append({
            "id": f"Task {idx}",
            "code": match.group("code").strip()
        })
    
    return ocl_listings

def extract_ocl_code2(response):
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

def extract_facts_from_alloy(response):
    # Extract the content of the code block
    code_block_match = re.search(r"```alloy\n(.*?)\n```", response, re.DOTALL)
    if not code_block_match:
        return []

    alloy_code = code_block_match.group(1)

    # Find all facts in the Alloy code
    fact_matches = list(re.finditer(r"fact\s+(\w+)\s*\{.*?\}", alloy_code, re.DOTALL))

    # Build the result list
    facts = []
    for idx, match in enumerate(fact_matches):
        fact_code = match.group(0)
        facts.append({"id": idx, "code": fact_code})

    return facts    

def extract_functions_from_python(response):
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


text = """ 
```ocl
context Product
inv UniqueIdentifier:
    self.identifier->isUnique()

context ManufacturingOrder
inv QuotingState:
    self.state = 'quoting' implies self.quote.approved = false

context ProductionOrder
inv ApprovedDesign:
    self.product.designs->select(d | d.approved = true)->size() = 1

context SublimationCalender
inv TemperatureSetting:
    self.temperature = 
        if Environment.temperature > 30 then 
            self.fabric.temperature - 5 
        else if Environment.temperature < 8 then 
            self.fabric.temperature + 3 
        else 
            self.fabric.temperature 
        endif

context ProductionOrder
inv SingleRoute:
    self.route->size() = 1

context ProductionOrder
inv MandatoryPreparation:
    self.route.last().name = 'Preparation'

context ProductionOrder
inv AtLeastOneProcessBeforePreparation:
    self.route->select(p | p.name = 'Sublimation' or p.name = 'Sewing')->size() >= 1

context ProductionOrder
inv PrintedAndCutBeforeSublimation:
    self.isPrinted and self.isCut implies self.isSublimated

context ManufacturingOrder
inv AtLeastOneProductionOrder:
    self.productionOrders->size() >= 1

context ProductionOrder
inv AtLeastOneLine:
    self.productionOrderLines->size() >= 1

context Quote
inv ThreadsInQuote:
    self.materials->exists(m | m.name = 'threads')

context ManufacturingOrder
inv MaxProductionOrders:
    ManufacturingOrder.allInstances()->select(m | m.state = 'in production')->size() <= 100

context ManufacturingOrder
inv PrintingRequiresSublimation:
    self.route->exists(p | p.name = 'Printing') implies self.route->exists(p | p.name = 'Sublimation')
```

"""


print(len(extract_ocl_code2(text)))