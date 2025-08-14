import click
import os
import json

def build_dataset(path):
    path2uml = os.path.join(path, "UML")
    dataset = []
    specs = []
    
    with open(os.path.join(path, "specifications.json"), 'r') as j:
        specs = json.loads(j.read())
    if not len(specs) == 15:
        return ""
    
    for domain_name, dcontent in specs.items():

        domain_path = os.path.join(path2uml, domain_name)
        if os.path.isdir(domain_path):
            print("processing folder:", domain_name)
            
            domain_node = {
                "domain_name": domain_name,
                "domain_context": None,
                "plantuml_model": None,
                "nl_model": None,
                "constraints": []
            }

            # Populate domain_context
            spec_file = os.path.join(domain_path, "spec.txt")
            if os.path.isfile(spec_file):
                with open(spec_file, 'r') as file:
                    domain_node["domain_context"] = file.read().strip()

            # Populate PlantUML model
            plantuml_file = os.path.join(domain_path, domain_name+".puml")
            if os.path.isfile(plantuml_file):
                with open(plantuml_file, 'r') as file:
                    domain_node["plantuml_model"] = file.read().strip()
            
            # Populate NL model
            nlmodel_file = os.path.join(domain_path, domain_name+".txt")
            if os.path.isfile(nlmodel_file):
                with open(nlmodel_file, 'r') as file:
                    domain_node["nl_model"] = file.read().strip()

            # Populate constraints
            specifications = []
            for key, value in dcontent["specifications"].items():
                # Only INVARIANTS with OCL solution are allowed
                if value!="NA" and (" inv " in value or " inv:" in value):
                    specifications.append({"ocl": value, "specification": key})
            domain_node["constraints"] = specifications

            # Add to the dataset
            dataset.append(domain_node)

    return dataset

@click.command()
@click.argument('path', type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True), 
                metavar='<path>')
@click.argument('output_file', type=click.Path(file_okay=True, dir_okay=False, writable=True), 
                metavar='<output_file>')
def main(path, output_file):
    """Build a hierarchical dataset in JSON format from the given dataset folder."""
    dataset = build_dataset(path)

    # Write the dataset to the output file
    with open(output_file, 'w') as file:
        json.dump(dataset, file, indent=4)

    print(f"Dataset successfully written to {output_file}")

if __name__ == "__main__":
    main()