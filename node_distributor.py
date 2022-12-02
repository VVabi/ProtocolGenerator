import toml
import os
from protocol_parser import parse_definitions

config_dict = toml.load("node_config.toml")

node_definitions = config_dict["definitions"]

nodes = config_dict["nodes"]
base_path = config_dict["path"]["base_path"]

file_extensions = {"python": ".py", "rust": ".rs"}

for (node_name, node) in nodes.items():
    language = node["language"]
    target_path = os.path.join(base_path, node["target_path"])

    print(f"Creating definitions for node {node_name}")
    for dependency in node["dependencies"]:
        definitions_file = os.path.join(base_path, node_definitions[dependency]["path"])
        print(f"Creating messages for {definitions_file} in {target_path} for language {language}")
        output_file_name = os.path.splitext(os.path.basename(definitions_file))[0]+file_extensions[language]
        parse_definitions(definitions_file, os.path.join(target_path, output_file_name), language)