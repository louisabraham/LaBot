#
#
# def get_id(line):
#     s = re.fullmatch(id_pattern, line)
#     if not s:
#         return s
#     return int(s.group(1))
#
#
# method_def_pattern = r"\s*(?:override )?public function (?P<name>\w+)\((?P<args>[^)]+)\) : (?P<type>.*)\n"
# block_begin_pattern = r"\s*{\n"
#
#
# def make_block_end_pattern(begin): return begin[:-2] + '}\n'
#
#
