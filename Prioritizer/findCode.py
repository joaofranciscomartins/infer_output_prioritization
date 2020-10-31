import re
import codecs
import glob
import os
import html2text
import csv


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
    text = text.replace("_", " ")
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


##############################################################################################


myData = [["text", "label"],]

# read the file into a list of lines
with open('bugs.txt','r') as f:
    lines = f.read().split("\n")

null_der = 'error: NULL_DEREFERENCE'
res_leak = 'error: RESOURCE_LEAK'
bug_null_lines =[]
bug_leak_lines =[]

for line in lines:
    if null_der in line: # or word in line.split() to search for full words
        bug_null_lines.append(line)
    elif res_leak in line:
        bug_leak_lines.append(line)

null_file_names = []
null_file_lines = []
leak_file_names = []
leak_file_lines = []

for line in bug_null_lines:
    if 'test' in line:
        continue;
    else :
        string = re.search("\w+\.java", line).group()
        null_file_names.append(string)
        string = re.search("\d+", line).group()
        null_file_lines.append(string)

for line in bug_leak_lines:
    if 'test' in line:
        continue;
    else :
        string = re.search("\w+\.java", line).group()
        leak_file_names.append(string)
        string = re.search("\d+", line).group()
        leak_file_lines.append(string)

###### NULL DEREFERENCE BUGS ######
for x in range(0,len(null_file_names)):

    path = glob.glob(null_file_names[x] + '.' + '*/') # We can later add infer-out/captured/*

    if(len(path) > 0):
        os.chdir(path[0])
        for file in glob.glob("*.html"): #check all the method HTML's
            with codecs.open(file, 'r') as f:
                text = f.read()
                if "Null Dereference" in text and (null_file_lines[x] in text): # If a method contains the error and desired line we analyze it
                    lines = text.split("\n")
                    print(file)
                    for line in lines: # Search the file for node and session numbers
                        if "Null Dereference" in line:
                            string = re.search("node\d+#session\d+", line).group() 
                            break

                    split = string.split("#")
                    node_name = file.replace(".html", "") + "_" + split[0] + ".html"  # node file where the bug is recorded

                    with codecs.open('nodes/' + node_name,'r') as data:         
                        #node = html2text.html2text(data.read()).split("\n")
                        text_to_analize = []
                        text_organized = []

                        # Skips text before the beginning of the interesting session:
                        for line in data:
                            if string in line:  # node\d+#session\d+
                                break

                        for line in data:
                            if 'Processing prop' in line:  # node\d+#session\d+
                                break

                        # Reads text until the end of the desired portion:
                        for line in data:  
                            if 'Failure of symbolic execution:' in line:
                                text_to_analize.append(line)
                                break
                            text_to_analize.append(line)


                        for line in reversed(text_to_analize):
                            if 'Processing prop' in line:
                                text_organized.append(html2text.html2text(line))
                                break
                            text_organized.append(html2text.html2text(line))

                    text = ''.join(text_organized[::-1])
                    normalized_text = normalizer(text)
                    myData.append([normalized_text,bug_null_lines[x]])
                    break
        os.chdir("..")



###### RESOURCE_LEAK BUGS ######

for x in range(0,len(leak_file_names)):
    path = glob.glob(leak_file_names[x] + '*/') # We can later add infer-out/captured/*
    if(len(path) > 0):
        os.chdir(path[0])
        for file in glob.glob("*.html"): #check all the method HTMLs
            with codecs.open(file, 'r') as f:
                text = f.read()
                if ("Resource Leak" in text) and (leak_file_lines[x] in text): # If a method contains the error and desired line we analyze it
                    lines = text.split("\n")
                    print(file)
                    for line in lines: # Search the file for node and session numbers
                        if "Resource Leak" in line:
                            string = re.search("node\d+#session\d+", line).group() 
                            break

                    split = string.split("#")
                    node_name = file.replace(".html", "") + "_" + split[0] + ".html"  # node file where the bug is recorded

                    with codecs.open('nodes/' + node_name,'r') as data:       
                        text_to_analize = []

                        # Skips text before the beginning of the interesting session:
                        for line in data:
                            if string in line:  # node\d+#session\d+
                                break

                        # We don't want the props and instructions part
                        for line in data:
                            if 'Processing prop' in line:  
                                break

                        # Reads text until the end of the desired portion:
                        for line in data:  
                            if '.... After Symbolic Execution ....' in line:
                                break
                            text_to_analize.append(html2text.html2text(line))
                    
                    text = ''.join(text_to_analize)
                    normalized_text = normalizer(text)
                    myData.append([normalized_text,bug_leak_lines[x]])
                    break
        os.chdir("..")


with open('data.csv', 'w') as myFile:
   writer = csv.writer(myFile)
   writer.writerows(myData)
