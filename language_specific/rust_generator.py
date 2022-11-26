def generate_rust(parsedStructs, parsedEnums):
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