

class StructDescription:
    name=""
    fields = list()
    topic = ""

    def __init__(self):
        self.name=""
        self.fields=list()

    def __init__(self, nm, topic):
        self.name   = nm
        self.fields = list()
        self.topic  = topic

    def addfield(self, field):
        self.fields.append(field)

    def output(self):
        print("Struct "+self.name)
        for field in self.fields:
            field.output()

    def makecppconstructors(self):
        ret = "    "+self.name+"() {\n"
        ret = ret+"        unique_id = protocol::"+self.name+"_unique_id;\n"
        for field in self.fields:
            ret = ret + field.todefaultconstructorpart()

        ret = ret+"    }\n"
        ret = ret + "\n"
        if (len(self.fields) > 0):
            ret = ret+"    "+self.name+"("

            for field in self.fields:
                printtype = field.getprinttype()

                if(field.isvector):
                    printtype = "std::vector<"+printtype+">"
                ret = ret+printtype+ " constr_"+field.name+","

            ret = ret[:-1]

            ret = ret+") {\n"
            ret = ret+"        unique_id = protocol::"+self.name+"_unique_id;\n"
            for field in self.fields:
                ret = ret + field.tovalueconstructorpart()

            ret = ret+"    }\n"
            ret = ret + "\n"


        ret = ret+"    " + self.name + "(const Json::Value& root) {\n"
        ret = ret + "        unique_id = protocol::" + self.name + "_unique_id;\n"
        for field in self.fields:
            ret = ret+field.toconstructorpart()

        ret = ret+"    }\n"
        return ret

    def toCppstruct(self):
        ret = "struct "+self.name+":public protocol::message {\n"
        for field in self.fields:
            ret = ret+field.tocppdeclaration()
        ret = ret+"     constexpr static int get_struct_unique_id() { return protocol::"+self.name+"_unique_id; }\n"
        ret = ret+"\n"
        ret = ret+"    Json::Value toJsonValue() {\n"
        ret = ret+"        Json::Value root;\n"

        for field in self.fields:
            ret = ret+field.makecppjsonoutput()
        ret = ret + "        return root;\n"
        ret = ret + "    }\n"
        ret = ret + "\n"
        ret = ret+self.makecppconstructors()
        ret = ret+"};\n"
        return ret

    def toKotlinstruct(self):
        ret = "data class "+self.name+"("

        for field in self.fields:
            printType = field.getkotlinprinttype()
            ret = ret+"var "+field.name+": "+printType+", "
        if (len(self.fields)) > 0:
            ret  = ret[:-2]
        ret  =ret+"): ProtocolMessage(ProtocolUniqueId."+self.name.upper()+")\n"
        return ret

    def toRustStruct(self):
        ret = "#[derive(Serialize, Deserialize)]\n"
        ret += "pub struct "+self.name+" {\n"
        for field in self.fields:
            printType = field.getrustprinttype()
            ret = ret+"    pub "+field.name+": "+printType+",\n"
        if (len(self.fields)) > 0:
            ret  = ret[:-2]

        ret += "\n}\n"
        return ret
