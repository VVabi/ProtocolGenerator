import StructField
import StructDescription
import re
import sys
import getopt

from language_specific.rust_generator import generate_rust
from language_specific.python_generator import generate_python
from output import *


def parse(inputfile):

    starttag = "structdef "
    endtag = "endstructdef"
    definitions = open(inputfile, "r")

    lines = definitions.readlines()
    startpattern = re.compile(starttag+".*")
    endpattern   = re.compile(endtag+".*")


    enumpattern = re.compile("enumdef.*")
    enumendpattern = re.compile("endenumdef.*")
    parsedStructs = list()
    currentStruct = StructDescription
    parsingStruct = False
    parsingEnum   = False
    isvector = False

    parsedEnums = dict()
    while len(lines) > 0:
        nextLine = lines.pop(0)
        if nextLine == "\n":
            continue

        if enumpattern.match(nextLine):
            current_enum    = dict()
            enum_name       = nextLine[8:].rstrip()
            parsingEnum     = True
            continue

        if enumendpattern.match(nextLine):
            parsedEnums[enum_name] = current_enum
            parsingEnum     = False
            continue

        if parsingEnum:
            data = nextLine.split(':')
            current_enum[data[0]] = data[1].rstrip()
            continue


        if startpattern.match(nextLine):
            if parsingStruct:
                raise ValueError("new struct def found before previous struct ended")
            parsingStruct = True
            name = re.sub(starttag, "", nextLine)
            topic = lines.pop(0).rstrip()
            name = name.rstrip()
            currentStruct = StructDescription.StructDescription(name, topic)
            continue

        if endpattern.match(nextLine):
            if not parsingStruct:
                raise ValueError("endstruct before start detected")
            parsingStruct = False
            parsedStructs.append(currentStruct)
            continue

        if not parsingStruct:
            raise ValueError("Trying to parse fields before struct start")

        fielddescriptor = nextLine.split(' ')

        if len(fielddescriptor) != 2:
            raise ValueError("endstruct before start detected")

        fieldname = fielddescriptor[1].rstrip()
        fieldtype = fielddescriptor[0].rstrip()

        vectorpattern = re.compile("vector:.*")
        if vectorpattern.match(fieldtype):
            isvector=True
            fieldtype = re.sub("vector:", "", fieldtype)
        else:
            isvector=False

        currentStruct.addfield(StructField.StructField(fieldname, fieldtype, isvector))
    return parsedStructs, parsedEnums


def parse_definitions(inputfile, outputfile, language):
    parsedStructs, parsedEnums = parse(inputfile)

    if language == "python":
        output = generate_python(parsedStructs, parsedEnums)
    elif language == "rust":
        output = generate_rust(parsedStructs, parsedEnums)

    with open(outputfile, "w+") as fh:
        fh.write(output)

if __name__ == "__main__":
    argv = sys.argv[1:]
    inputfile = ""
    outputfile = ""
    language = ""
    try:
        opts, args = getopt.getopt(argv, "l:d:o:")
    except getopt.GetoptError:
        print('parser.py -l <language:cpp or rust> -d <definitionfile> -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('parser.py -l <language:cpp or rust> -d <definitionfile> -o <outputfile>')
            sys.exit()
        elif opt in ("-d"):
            inputfile = arg
        elif opt in ("-o"):
            outputfile = arg
        elif opt in ("-l"):
            language = arg


    #if len(inputfile) == 0 or len(outputfile) == 0 or len(language) == 0:
        #print('Usage: parser.py -l <language:cpp or rust> -d <definitionfile> -o <outputfile>')
        #sys.exit()

    inputfile = "test_definitions.txt"
    language  = "python"
    outputfile = "output.py"

    print(inputfile)
    print(outputfile)
    print(language)

    parse_definitions(inputfile, outputfile, language)