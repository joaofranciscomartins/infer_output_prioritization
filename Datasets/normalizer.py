import re
import codecs
import glob
import os
import html2text
import csv
import sys

##### Functions Normalizer ####

def variables(text):                  
    x = re.findall("STRING \w+ = | STRING PTR \w+ = | INT \w+ = | INT PTR \w+ = " , text)
    variables = 1
    for string in x:
        if(string.find("THIS = ") > 0):
            break;
        elif(string.find("STRING PTR = | INT PTR =") > 0):
            break;
        else:
            var = re.search(" \w+ =", string).group()
            var = var.replace("=", "")
            text = text.replace(var," VAR " + str(variables) +" ")
            variables = variables + 1
    return text

def find_int_literals(text):                    # TODO scientific notation still missing
    x = re.findall("INT \w+ = \d+ | = \d+ | \d+ < | \d+ ALLOC" , text)

    for string in x:
        number = re.findall("\d+",string)[0]
        positive = 1 if (int(number) >= 0) else 0
        length = len(number)
        
        if(length == 1):                    
            number = " I1 "
        elif (length == 2):
            number = " I2 "
        elif (length == 3):
            number = " I3 "
        else:
            number = " I4\+ "
        if(positive):
            var = re.sub("\d+", number, string)
            text = re.sub(string,var,text)
        else:
            var = re.sub("\d+", "NEG" + number, string)
            text = re.sub(string,var,text)
    return text
 
def find_string_literals(text):                
    x = re.findall("STRING \w+ = \w+ | STRING PTR \w+ = \w+" , text)
    literals = 1

    for string in x:
        if(string.find(" = PTR") > 0):
            break;
        else:
            clean = re.sub("= \w+", "= STR " + str(literals) + " ", string)
            text = text.replace(string,clean)
            literals = literals + 1
    return text


# Function to convert   
def listToString(s):  
        
    # initialize an empty string 
    str1 = " " 

    return (str1.join(s))

def normalizer(text):

    text = re.sub("([a-z])([A-Z])","\g<1> \g<2>",text) #split camel case words

    text = text.upper() #everything to upper case

    #Clean text a bit
    text = text.replace(".", " ")
    text = text.replace(":", " ")
    text = text.replace(";", "")
    text = text.replace("@", "")
    text = text.replace("[", "")
    text = text.replace("]", "")
    text = text.replace("()", "")
    text = text.replace("(", " ( ")
    text = text.replace(")", " ) ")
    text = text.replace("_", " ") #removing snake_case
    text = text.replace(",", " ")
    text = text.replace("{", " { ")
    text = text.replace("}", " } ")
    text = text.replace("#", " ")
    text = text.replace('""', "STR") #replacing "" with string notation


    #Language
    text = text.replace("&", " ADDR ") #address
    text = text.replace("*", " PTR ") #pointer

    text = ' '.join(text.split())


    #Resolve spacing and deleting line numbers
    text = re.sub("LINE\s\d+", "", text) #fix line numbers
    text = re.sub("INITIAL", " INITIAL ", text) #fix spacing
    text = re.sub("NULLIFY", " NULLIFY ", text) #fix spacing
    text = re.sub("UPDATE", " UPDATE ", text) #fix spacing
    text = re.sub("FOOTPRINT", " FOOTPRINT ", text) #fix spacing
    text = re.sub("FORMAL", " FORMAL ", text) #fix spacing
    text = re.sub("NONE", " NONE ", text) #fix spacing
    text = text.replace("REARRANGE", " REARRANGE ") #
    text = text.replace("|->", " POINTS ") #POINTS TO
    text = text.replace("|", " ") #remove "|"
    text = text.replace("!=", " DIFFERENT ") #DIFFERENT
    text = text.replace("=", " EQUALS ") #EQUALS
    text = text.replace("( Z )", " Z ")
    text = text.replace("( SUB )", " SUB ")
    text = text.replace("<", " SMALLER ")
    text = text.replace(">", " BIGGER ")
    text = text.replace("{", " LBRACKET ")
    text = text.replace("}", " RBRACKET ")
    text = text.replace("(", " LPARENTHESES ")
    text = text.replace(")", " RPARENTHESES ")
    text = text.replace("ALLOC", " ALLOC ")
    text = text.replace("INSTRUCTION", " INSTRUCTION ")
    text = text.replace("PROP", " PROP ")



    text = text.replace("/", " ")

    text = text.replace("::", ":")

    # Treating number and string literals
    text = find_int_literals(text) #replacing int literals in the code
    text = find_string_literals(text) #replacing string literals in the code
    text = variables(text) #replacing variables in the code

    text = re.sub(" \d+ ", " ", text) #replaces alone line numbers
    text = text.replace("$", " ")
    text = text.replace("KEY", " KEY ")
    text = text.replace("VAR", " VAR ")
    text = text.replace("IN ", " IN ")
    text = text.replace("PATH", " PATH ")
    text = ' '.join(text.split())

    #SPLIT LITERALS
    numbers = re.findall("\d+",text)
    for number in numbers:
        separate = listToString([(n) for n in number])
        text = text.replace(number, separate)

    return text

myData = [["text", "label"],]

csv.field_size_limit(sys.maxsize)

with open('data.csv', 'r') as dataFile:
    data = csv.DictReader(dataFile)
    for row in data:
        text_raw = row['text']
        label = row['label']
        myText = normalizer(text_raw)
        myData.append([myText,label])

with open('normalized.csv', 'w') as normFile:
   writer = csv.writer(normFile)
   writer.writerows(myData)




