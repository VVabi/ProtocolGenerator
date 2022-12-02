import re

class StructField:
    name=""
    type=""
    isvector=False

    cppnames = {"uint32": "uint32_t", "int32": "int32_t", "double": "double", "bool":"bool", "uint8": "uint8_t", "int8": "int8_t"}
    kotlinnames = {"uint32": "Int", "int32": "Int", "double": "Double", "bool": "bool", "uint8": "Byte", "int8": "Byte"}
    jsonfunctions = {"uint32": "asUInt()", "int32": "asInt()", "double": "asDouble()", "bool":"asBool", "uint8": "asByte()", "int8": "asByte()"}
    rustNames  = {"uint32": "u32", "int32": "i32", "double": "f64", "bool": "bool", "uint8": "u8", "int8": "i8"}

    core_names = set(["uint32", "int32", "double", "bool", "uint8", "int8", "string"])

    def __init__(self, nm, tp, isvector):
        self.name = nm
        self.type = tp
        self.isvector = isvector

    def output(self):
        print("Field: Type "+self.type+" Name "+self.name)

    def isstruct(self):
        structpattern = re.compile("struct:.*")
        return structpattern.match(self.type)

    def isEnum(self):
        structpattern = re.compile("enum:.*")
        return structpattern.match(self.type)

    def getkotlinprinttype(self):
        if self.isstruct():
            printType = re.sub("struct:", "", self.type)
            if self.isvector:
                printType = "ArrayList<"+printType+">"
        elif self.isvector:
            printType = "ArrayList<"+self.kotlinnames[self.type]+">"
        else:
            printType = self.kotlinnames[self.type]
        return printType

    def getrustprinttype(self):
        if self.isstruct():
            printType = re.sub("struct:", "", self.type)
            if self.isvector:
                printType = "Vec<"+printType+">"
        elif self.isvector:
            printType = "Vec<"+self.rustNames[self.type]+">"
        elif self.isEnum():
            printType = self.type[5:]    
        else:
            printType = self.rustNames[self.type]
        return printType


    def getprinttype(self):
        if self.isstruct():
            printType = re.sub("struct:", "", self.type)
        else:
            printType = self.cppnames[self.type]
        return printType

    def tocppdeclaration(self):
        printType = self.getprinttype()

        if self.isvector:
            ret = "    std::vector<" + printType + "> " + self.name + ";\n"
        else:
            ret = "    "+printType+" "+self.name+";\n"
        return ret

    def makecppjsonoutput(self):
        printType = self.getprinttype()
        ret = ""
        if (not self.isvector) and (not self.isstruct()):
            ret = ret+"        root[\""+self.name+"\"] = "+self.name+";\n"
        elif not self.isstruct():
            tmp_struct_name = "tmp_" + self.name
            ret = ret+"        Json::Value "+tmp_struct_name+"(Json::arrayValue);\n"
            ret = ret+"        for (std::vector<"+printType+">::iterator it = "+self.name+".begin() ; it != "+self.name+".end(); ++it) {\n            "+tmp_struct_name+".append(*it);\n        }\n"
            ret = ret+"        root[\""+self.name+"\"] = "+tmp_struct_name+";\n"
        elif not self.isvector:
            ret = ret+"        root[\""+self.name+"\"] = "+self.name+".toJsonValue();\n"

        else:
            tmp_struct_name = "tmp_" + self.name
            ret = ret + "        Json::Value "+tmp_struct_name+"(Json::arrayValue);\n"
            ret = ret+"        for (std::vector<"+printType+">::iterator it = "+self.name+".begin() ; it != "+self.name+".end(); ++it) {\n            "+tmp_struct_name+".append(it->toJsonValue());\n        }\n"
            ret = ret+"        root[\""+self.name+"\"] = "+tmp_struct_name+";\n"

        return ret

    def toconstructorpart(self):
        printtype = self.getprinttype()
        ret = ""
        if (not self.isvector) and (not self.isstruct()):
            ret = ret+"        "+self.name+" = root[\""+self.name+"\"]."+self.jsonfunctions[self.type]+";\n"
        elif not self.isstruct():
            tmp_struct_name = "tmp_" + self.name
            ret = ret+"        Json::Value "+tmp_struct_name+" = root[\""+self.name+"\"];\n"
            ret = ret+"        for (Json::Value::ArrayIndex i = 0; i < "+tmp_struct_name+".size(); i++) {\n"
            ret = ret+"            "+self.name+".push_back("+tmp_struct_name+"[i]."+self.jsonfunctions[self.type]+");\n"
            ret = ret+"        }\n"
        elif not self.isvector:
            ret = ret+"        "+self.name+" = "+printtype+"(root[\""+self.name+"\"]);\n"
        else:
            tmp_struct_name = "tmp_"+self.name
            ret = ret + "        Json::Value "+tmp_struct_name+" = root[\"" + self.name + "\"];\n"
            ret = ret + "        for (Json::Value::ArrayIndex i = 0; i < "+tmp_struct_name+".size(); i++) {\n"
            ret = ret + "            " + self.name + ".push_back("+printtype+"("+tmp_struct_name+"[i]));\n"
            ret = ret + "        }\n"
        return ret

    def todefaultconstructorpart(self):
        printtype = self.getprinttype()
        ret = ""
        if (not self.isvector) and (not self.isstruct()):
            ret = ret + "        " + self.name + " = 0;\n"
        return ret

    def tovalueconstructorpart(self):
        printtype = self.getprinttype()
        ret = ""
        ret = ret + "        " + self.name + " = constr_"+self.name+";\n"
        return ret
