INDENT = "    "
LINEBREAK = "\n"
EMTPY_LINE = ""

def remove_prefix(full_name):
    return full_name.split(":")[1]

def get_python_header():
    ret = []
    ret.append("import enum")
    return ret

def generate_python_enum(name, enum_def):
    ret = []
    ret.append(f"class {name}(enum.Enum):")

    for entry_name, entry_def in enum_def.items():
        ret.append(f"{INDENT}{entry_name} = {entry_def}")

    return ret

def generate_python_struct_code(parsed_struct):
    ret = []
    ret.append(f"class {parsed_struct.name}:")

    field_names = [field.name for field in parsed_struct.fields]
    
    constructor_str = f"{INDENT}def __init__(self"
    for name in field_names:
        constructor_str += f", {name}"

    constructor_str += "):"
    ret.append(constructor_str)

    for field in parsed_struct.fields:
        comment = f"{field.type}"
        if field.isvector:
            comment = f"list:{field.type}"
        ret.append(f"{INDENT}{INDENT}self.{field.name} = {field.name} #{comment}")

    if len(field_names) == 0:
        ret.append(f"{INDENT}{INDENT}pass")
    ret.append(EMTPY_LINE)

    ret.append(f"{INDENT}def to_dict(self):")
    ret.append(f"{INDENT}{INDENT}ret = dict()")
    for field in parsed_struct.fields:
        if field.isstruct() and not field.isvector:
            ret.append(f"{INDENT}{INDENT}ret['{field.name}'] = self.{field.name}.to_dict()")
        elif field.isvector:
            ret.append(f"{INDENT}{INDENT}ret['{field.name}'] = []")
            is_base_type = field.type in field.core_names
            ret.append(f"{INDENT}{INDENT}for data_point in self.{field.name}:")
            if is_base_type:
                ret.append(f"{INDENT}{INDENT}{INDENT}ret['{field.name}'].append(data_point)")
            else:
                ret.append(f"{INDENT}{INDENT}{INDENT}ret['{field.name}'].append(data_point.to_dict())")
        elif field.isEnum():
            ret.append(f"{INDENT}{INDENT}ret['{field.name}'] = self.{field.name}.name")
        else:
            ret.append(f"{INDENT}{INDENT}ret['{field.name}'] = self.{field.name}")

    ret.append(f"{INDENT}{INDENT}return ret")
    ret.append(EMTPY_LINE)
    ret.append(f"{INDENT}def get_topic(self):")
    ret.append(f"{INDENT}{INDENT}return '{parsed_struct.topic}'")
    ret.append(EMTPY_LINE)
    ret.append(f"{INDENT}def get_topic_static():")
    ret.append(f"{INDENT}{INDENT}return '{parsed_struct.topic}'")
    ret.append(EMTPY_LINE)
    ret.append(f"{INDENT}def from_dict(input_dict):")
    
    for field in parsed_struct.fields:
        if field.isstruct() and not field.isvector:
            ret.append(f"{INDENT}{INDENT}{field.name} = {remove_prefix(field.type)}.from_dict(input_dict['{field.name}'])")
        elif field.isvector:
            ret.append(f"{INDENT}{INDENT}{field.name} = []")
            is_base_type = field.type in field.core_names
            ret.append(f"{INDENT}{INDENT}for data_point in input_dict['{field.name}']:")
            if is_base_type:
                ret.append(f"{INDENT}{INDENT}{INDENT}{field.name}.append(data_point)")
            else:
                ret.append(f"{INDENT}{INDENT}{INDENT}{field.name}.append({remove_prefix(field.type)}.from_dict(data_point))")
        elif field.isEnum():
            ret.append(f"{INDENT}{INDENT}{field.name} = {remove_prefix(field.type)}[input_dict['{field.name}']]")
        else:
            ret.append(f"{INDENT}{INDENT}{field.name} = input_dict['{field.name}']")
    ret.append(f"{INDENT}{INDENT}return {parsed_struct.name}(")
    for field in parsed_struct.fields:
        ret.append(f"{INDENT}{INDENT}{INDENT}{field.name},")
    ret.append(f"{INDENT}{INDENT})")
    return ret

def generate_python(parsed_structs, parsed_enums):
    ret = get_python_header()

    for (name, parsed_enum) in parsed_enums.items():
        ret.extend(generate_python_enum(name, parsed_enum))
        ret.append(EMTPY_LINE)

    for parsed_struct in parsed_structs:
        ret.extend(generate_python_struct_code(parsed_struct))
        ret.append(EMTPY_LINE)

    ret_str = ""
    for line in ret:
        ret_str += line
        ret_str += "\n"
    
    return ret_str