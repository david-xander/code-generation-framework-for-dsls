# Build the dataset
The dataset is based on https://huggingface.co/datasets/fpan/text-to-ocl-from-ecore/tree/main/models. 

It has been manually checked.

The build.py script builds a hierarchical dataset in JSON format from the given dataset folder.

To build it run:
```bash
python build_Pan_dataset.py Pan DS1.json
python build_Abukhalaf_dataset.py Abukhalaf DS2.json
```
