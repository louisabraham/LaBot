from pathlib import Path
import re
import pickle

from pprint import pprint

class_pattern =\
    r"\s*public class (?P<name>\w+) (?:extends (?P<parent>\w+) )?implements (?P<interface>\w+)\n"
id_pattern =\
    r"\s*public static const protocolId:uint = (?P<id>\d+);\n"
public_var_pattern =\
    r"\s*public var (?P<name>\w+):(?P<type>\S*)( = (?P<init>.*))?;\n"
vector_type_pattern =\
    r"Vector\.<(?P<type>\w+)>"

attr_assign_pattern_of_name =\
    r"\s*this\.%s = (?:\w*)\.read(?P<type>\w*)\(\);\n"
vector_attr_write_pattern_of_name =\
    r"\s*(?:\w*)\.write(?P<type>\w*)\(this\.%s\[(?:\w+)\]\);\n"
vector_len_write_pattern_of_name =\
    r"\s*(?:\w*)\.write(?P<type>\w*)\(this\.%s\.length\);\n"
vector_const_len_pattern_of_name_and_type =\
    r"\s*this\.%s = new Vector\.<%s>\((?P<size>\d+),true\);\n"
dynamic_type_pattern_of_type =\
    r"\s*(?:this\.)?\w+ = ProtocolTypeManager\.getInstance\(%s,\w*\);\n"


def load_from_path(path):
    if isinstance(path, str):
        path = Path(path)
    for p in path.glob('**/*.as'):
        name = p.name[:-3]
        new = dict(name=name, path=p)
        types[name] = new


def lines(t):
    with t['path'].open() as f:
        yield from f


def parseVar(name, typename, lines):
    if typename in ['Boolean', 'ByteArray']:
        return dict(name=name, length=None, type=typename)
    if typename in types:
        type = typename

    m = re.fullmatch(vector_type_pattern, typename)
    if m:
        return parseVectorVar(name, m.group('type'), lines)

    attr_assign_pattern = attr_assign_pattern_of_name % name
    dynamic_type_pattern = dynamic_type_pattern_of_type % typename

    for line in lines:
        m = re.fullmatch(attr_assign_pattern, line)
        if m:
            type = m.group('type')

        m = re.fullmatch(dynamic_type_pattern, line)
        if m:
            type = False

    return dict(name=name, length=None, type=type)


def parseVectorVar(name, typename, lines):
    if typename in types:
        type = typename

    vector_attr_write_pattern = vector_attr_write_pattern_of_name % name
    vector_len_write_pattern = vector_len_write_pattern_of_name % name
    vector_const_len_pattern = (
        vector_const_len_pattern_of_name_and_type
        % (name, typename)
    )
    dynamic_type_pattern = dynamic_type_pattern_of_type % typename

    for line in lines:
        m = re.fullmatch(vector_attr_write_pattern, line)
        if m:
            type = m.group('type')

        m = re.fullmatch(dynamic_type_pattern, line)
        if m:
            type = False

        m = re.fullmatch(vector_len_write_pattern, line)
        if m:
            length = m.group('type')

        m = re.fullmatch(vector_const_len_pattern, line)
        if m:
            length = int(m.group('size'))

    return dict(name=name, length=length, type=type)


def parse(t):
    vars = []

    for line in lines(t):

        m = re.fullmatch(class_pattern, line)
        if m:
            assert m.group('name') == t['name']
            parent = m.group('parent')
            if not parent in types:
                parent = None
            t['parent'] = parent

        m = re.fullmatch(id_pattern, line)
        if m:
            protocolId = int(m.group('id'))

        m = re.fullmatch(public_var_pattern, line)
        if m:
            var = parseVar(m.group('name'), m.group('type'), lines(t))
            vars.append(var)

    t['protocolId'] = protocolId

    if 'messages' in str(t['path']):
        assert protocolId not in msg_from_id
        msg_from_id[protocolId] = t
    elif 'types' in str(t['path']):
        assert protocolId not in types_from_id
        types_from_id[protocolId] = t

    if sum(var['type'] == 'Boolean' for var in vars) > 1:
        boolVars = [var for var in vars if var['type'] == 'Boolean']
        vars = [var for var in vars if var['type'] != 'Boolean']
    else:
        boolVars = []

    t['vars'] = vars
    t['boolVars'] = boolVars


def build():
    for t in types.values():
        parse(t)


filepath = Path(__file__).parent

if __name__ == '__main__':

    types = {}
    msg_from_id = {}
    types_from_id = {}

    paths = [
        filepath.parent.joinpath(
            'sources/scripts/com/ankamagames/dofus/network/types'
        ),
        filepath.parent.joinpath(
            'sources/scripts/com/ankamagames/dofus/network/messages'
        )
    ]

    for p in paths:
        load_from_path(p)

    build()

    primitives = {
        v['type']
        for t in types.values()
        for v in t['vars']
        if v['type'] and not v['type'] in types
    }

    with filepath.joinpath('protocol.pk').open('wb') as f:
        pickle.dump(types, f)
        pickle.dump(msg_from_id, f)
        pickle.dump(types_from_id, f)
        pickle.dump(primitives, f)

else:
    with filepath.joinpath('protocol.pk').open('rb') as f:
        types = pickle.load(f)
        msg_from_id = pickle.load(f)
        types_from_id = pickle.load(f)
        primitives = pickle.load(f)
