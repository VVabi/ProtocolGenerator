INDENT = "    "
LINEBREAK = "\n"

def get_python_header():
    ret = []
    ret.append("import enum")
    return ret

def generate_python_enum(name, enum_def):
    ret = []
    ret.append(f"class {name}(enum):")

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

    for name in field_names:
        ret.append(f"{INDENT}{INDENT}self.{name} = {name}")

    ret.append(LINEBREAK)

    ret.append(f"{INDENT}def to_dict(self):")
    ret.append(f"{INDENT}{INDENT}ret = dict()")
    for field in parsed_struct.fields:
        if field.isstruct():
            ret.append(f"{INDENT}{INDENT}ret['{field.name}'] = self.{name}.to_dict()")
        elif field.isEnum():
            ret.append(f"{INDENT}{INDENT}ret['{field.name}'] = self.{name}.name")
        else:
            ret.append(f"{INDENT}{INDENT}ret['{field.name}'] = self.{name}")

    ret.append(f"{INDENT}return ret")
    return ret

def generate_python(parsed_structs, parsed_enums):
    ret = get_python_header()

    for (name, parsed_enum) in parsed_enums.items():
        ret.extend(generate_python_enum(name, parsed_enum))
        ret.append(LINEBREAK)

    for parsed_struct in parsed_structs:
        ret.extend(generate_python_struct_code(parsed_struct))
        ret.append(LINEBREAK)

    ret_str = ""
    for line in ret:
        ret_str += line
        ret_str += "\n"
    
    return ret_str