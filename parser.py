import StructField
import StructDescription
import re
import sys
import getopt

def generateRust(parsedStructs, parsedEnums):
    indent = "    "
    rust = "extern crate serde_json;\n"
    rust += "extern crate serde;\n"
    rust += "use std::error::Error;\n"
    rust += "use serde::{Deserialize, Serialize};\n\n"


    for enum in parsedEnums:
        rust += "#[derive(Debug, Serialize, Deserialize, Copy, Clone)]\npub enum "+enum+"{\n"
        data = parsedEnums[enum]

        for t in data:
            rust += ("    " + t + "=" + data[t]+",\n")

        rust += "}\n\n"

        rust += "pub fn translate_" + enum.lower() + "_from_int(input: u32) -> Result<"+enum+", Box<dyn Error>> {\n"

        rust += indent+"match input {\n"
        
        for t in data:
            rust += indent + indent + data[t] + "=> Ok("+enum+"::"+t+"),\n"

        rust += indent + indent + "_ => return Err(Box::new(std::io::Error::new(std::io::ErrorKind::NotFound, \"Unknown" + enum +"\")))\n"

        rust += indent+"}\n}\n\n"



    rust += "#[derive(Debug)]\npub enum MessageUniqueId {\n"

    for struct in parsedStructs:
        rust += "    " + struct.name+"UniqueId,\n"
    rust += "}\n\n"

    rust += "pub trait Message {\n"+indent+"fn get_unique_id_dyn(&self) -> MessageUniqueId;\n"+ indent+"fn to_json(&self) -> std::result::Result<std::string::String, serde_json::Error>;\n"+indent+"fn get_topic_dyn(&self) -> std::string::String;\n}\n\n"

    rust += "pub trait StaticMessageInfo {\n"+indent+"fn get_unique_id() -> MessageUniqueId;\n"+ indent+"fn get_topic() -> std::string::String;\n}\n\n"

    for struct in parsedStructs:
        rust = rust+struct.toRustStruct()
        rust += "\n"
        rust += "impl Message for "+struct.name+" {\n"
        rust += "    #[inline]\n"
        rust += "    fn get_unique_id_dyn(&self) -> MessageUniqueId {\n"
        rust += "        MessageUniqueId::"+struct.name+"UniqueId\n"
        rust += "    }\n"
        rust += "    fn to_json(&self) -> std::result::Result<std::string::String, serde_json::Error> {\n"
        rust += "        serde_json::to_string(&self)\n"
        rust += "    }\n"
        rust += "    fn get_topic_dyn(&self) -> std::string::String {\n"
        rust += "        return \""+struct.topic+"\".to_string();\n"
        rust += "    }\n"
        rust += "}\n"
        rust += "\n"
        rust += "impl StaticMessageInfo for " + struct.name + " {\n"
        rust += "    #[inline]\n"
        rust += "    fn get_unique_id() -> MessageUniqueId {\n"
        rust += "        MessageUniqueId::" + struct.name + "UniqueId\n"
        rust += "    }\n"
        rust += "    fn get_topic() -> std::string::String {\n"
        rust += "        return \"" + struct.topic + "\".to_string();\n"
        rust += "    }\n"
        rust += "}\n"
        rust += "\n"

    return rust

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


if len(inputfile) == 0 or len(outputfile) == 0 or len(language) == 0:
    print('Usage: parser.py -l <language:cpp or rust> -d <definitionfile> -o <outputfile>')
    sys.exit()

print(inputfile)
print(outputfile)
print(language)

parsedStructs, parsedEnums = parse(inputfile)

rust = generateRust(parsedStructs, parsedEnums)

print(rust)

sys.exit()





if False:
    parsed = "/*-----------------------------------------*/\n"
    parsed = parsed + "/*THIS FILE IS AUTOGENERATED-DO NOT CHANGE!*/\n"
    parsed = parsed + "/*-----------------------------------------*/\n"
    parsed = parsed + "#ifndef PROTOCOL_MESSAGES_DEFINED\n"
    parsed = parsed + "#define PROTOCOL_MESSAGES_DEFINED\n"
    parsed = parsed + "#include \"json/json.h\"\n"
    parsed = parsed + "#include <stdint.h>\n\n"

    parsed = parsed + "namespace protocol {\n"
    enum = "enum message_unique_id {"
    for struct in parsedStructs:
        enum = enum+struct.name+"_unique_id, "

    enum = enum+ "};\n\n"

    parsed = parsed+enum
    parsed = parsed+"class message{\n"
    parsed = parsed+"protected:\n"
    parsed = parsed+"    message_unique_id unique_id;\n"
    parsed = parsed+"public:\n"
    parsed = parsed+"    message_unique_id get_unique_id() {\n"
    parsed = parsed+"                 return unique_id;\n";
    parsed = parsed+"    }\n"
    parsed = parsed+"    virtual Json::Value toJsonValue() = 0;\n"
    parsed = parsed+"    virtual ~message(){};\n"
    parsed = parsed+"};\n"

    factory = "#include \"gen/messages.hpp\"\n"
    factory = factory+"#include <memory>\n"
    factory = factory+"#include \"json/json.h\"\n\n"

    factory = factory + "std::unique_ptr<protocol::message> message_factory(Json::Value& root, protocol::message_unique_id id) {\n"
    factory = factory + "    switch (id) {\n"
    for struct in parsedStructs:
        #struct.output()
        parsed  = parsed + struct.toCppstruct()+"\n"
        factory = factory + "        case protocol::"+struct.name+"_unique_id: {\n"
        factory = factory + "            return std::unique_ptr<protocol::"+struct.name+">(new protocol::" + struct.name + "(root));\n"
        factory = factory + "            break;\n"
        factory = factory + "        }\n"
    factory = factory+"    }\n"
    factory = factory + "    return std::move(std::unique_ptr<protocol::message>(nullptr));\n"
    factory = factory+"}\n"
    parsed = parsed+"};\n\n"
    parsed = parsed+"#endif\n"

    spec = "#include <stdint.h>\n#include <string>\n#include <map>\n#include \"decoupling/decoupling_private.hpp\"\n\nnamespace decoupling {\n"

    spec = spec + "   mqtt_topic_id_pair mqtt_spec[] = {\n"
    for struct in parsedStructs:
        spec = spec + "     { protocol::"+struct.name+"_unique_id, \""+struct.topic+"\"},\n"


    spec = spec + "  };\n"


    spec = spec+"void init_mqqt_mappings(std::map<protocol::message_unique_id, std::string>& output_map, std::map<std::string, protocol::message_unique_id>& input_map) {\n"
    spec = spec+"     for (uint16_t ind = 0; ind < sizeof(mqtt_spec)/sizeof(mqtt_topic_id_pair); ind++) {\n"
    spec = spec+"           output_map[mqtt_spec[ind].id] = mqtt_spec[ind].topic;\n"
    spec = spec+"           input_map[mqtt_spec[ind].topic] = mqtt_spec[ind].id;\n"
    spec = spec+"    }\n"
    spec = spec+"}\n"
    spec = spec+"}\n\n"

    kotlin = "//THIS FILE IS AUTOGENERATED! DO NOT CHANGE! \n\npackage robotconnector \n\nimport com.google.gson.Gson \n\nenum class ProtocolUniqueId { \n"
    for struct in parsedStructs:
        kotlin = kotlin+struct.name.upper()+", "

    kotlin = kotlin+" INVALID"


    kotlin = kotlin+"\n}\n\n"

    kotlin = kotlin+"open class ProtocolMessage(unique_id: ProtocolUniqueId) {\n     val id = unique_id \n } \n\n"

    for struct in parsedStructs:
        kotlin = kotlin+struct.toKotlinstruct()


    kotlin = kotlin+"\nfun getTopicById(id: ProtocolUniqueId): String {\n     when(id) {\n"

    for struct in parsedStructs:
        kotlin = kotlin+"       ProtocolUniqueId."+struct.name.upper() +" -> return \""+struct.topic+"\"\n"

    kotlin = kotlin+"       ProtocolUniqueId.INVALID                    -> throw(Exception(\"Invalid unique id\"))\n"
    kotlin = kotlin+"   }\n"
    kotlin = kotlin+"}\n\n"

    kotlin = kotlin+"fun getIdByTopic(topic: String): ProtocolUniqueId{\n    when(topic) {\n"

    for struct in parsedStructs:
        kotlin = kotlin+"       \""+struct.topic+"\" -> return ProtocolUniqueId."+struct.name.upper() + "\n"


    kotlin = kotlin+"   }\n"
    kotlin = kotlin+"        return ProtocolUniqueId.INVALID\n"
    kotlin = kotlin+"}\n\n"

    kotlin = kotlin+"fun getMessageFromJson(json:String,  id: ProtocolUniqueId, gson: Gson): ProtocolMessage {\n    when(id) {\n"

    for struct in parsedStructs:
        kotlin = kotlin+"       ProtocolUniqueId."+struct.name.upper() +" -> return gson.fromJson(json, " + struct.name + "::class.java)\n"


    kotlin = kotlin+"       ProtocolUniqueId.INVALID                    -> throw(Exception(\"Invalid unique id\"))\n"
    kotlin = kotlin+"    }\n"
    kotlin = kotlin+"}\n\n"




print(rust)

#print(parsed)
#print(factory)
#print(kotlin)
#print(spec)
#outputfile = open(sys.argv[1]+"/ev3/src/gen/messages.hpp", "w")

#outputfile.write(parsed)

#outputfile = open(sys.argv[1]+"/ev3/src/gen/factory.cpp", "w")

#outputfile.write(factory)

#outputfile = open(sys.argv[1]+"/ev3/src/gen/mqtt_specification.cpp", "w")

#outputfile.write(spec)

#outputfile = open(sys.argv[1]+"/Nodes/LowLevelBehavior/src/gen/mqtt_specification.cpp", "w")

#outputfile.write(spec)

#outputfile = open(sys.argv[1]+"/Nodes/LowLevelBehavior/src/gen/messages.hpp", "w")

#outputfile.write(parsed)

#outputfile = open(sys.argv[1]+"/Nodes/LowLevelBehavior/src/gen/factory.cpp", "w")

#outputfile.write(factory)



#outputfile = open(sys.argv[1]+"/kotlin-sdk/src/robotconnector/ProtocolMessage.kt", "w")

#outputfile.write(kotlin)

#outputfile = open(sys.argv[1]+"/rust_sdk/src/protocol/messages.rs", "w")
#outputfile.write(rust)
#outputfile.close()