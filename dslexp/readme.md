# Experiment

## To execute the experiment

To execute the complete experiement with a given dataset `dataset.json` and pass@k with `k = 1`:
```shell 
python main.py dataset.json --k 1 
```

You can execute one single step. For example, considering the example below, we can execute only the first step:
```shell 
python main.py dataset.json --k 1 --step 1
```

Also, it is possible to execute a subset of steps. For example, executing only from step 1 to 4:
```shell 
python main.py dataset.json --k 1 --start 1 --end 4
```


To be able to paralelize, you need to split by domains:
```shell 
python main.py dataset.json --k 1 --step 1 --domain DOMAIN_NAME
```


## To keep a log of the whole experiment run

```shell 
python main.py dataset.json --k 1 > experiment.log 2>&1
```
Note: It won't print any error message and it will store everything in the output.file.