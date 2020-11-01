# Prioritizing Facebook's Infer Static Analysis Tool Warnings

## Datasets

All the datasets used to train the model can be found under the folder "Datasets". These are sorted according to the type of studied scenario, whitin-program warning classification and cross-program warnings classification.
As well as that, this folder contains the Python programs that create, train and evaluate the models.



## Output Prioritization Application

The Output Prioritization Application can be found under the folder "Pioritization"

This solution is consisted of 4 parts:

* The pre-trained machine learning model.
* The tokenizer used to train the model.
* A program whose function is to capture and preprocess all the information related with the output warnings.
* A program which takes the preprocessed information and evaluates it using the pre-trained model.

In order to sucessfully prioritize infer warnings the following steps have to be performed:

1. Run infer on the program to be analysed with the flag `--debug`.
2. Run `findCode.py` in the folder `infer-out/captured`, that generates a "Data.csv" with the processed information.
3. Run `prioritize.py` using the previosuly generated "Data.csv" file, the tokenizer and the model.
4. Open file Prioritized.txt.




