class DependencyError(Exception):
    def __init__(self, reason):
        self.reason = reason

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self.reason)


    # def get_method(self, name):
    #     state = 0
    #     for line in self.lines():
    #         if state == 0:
    #             m = re.fullmatch(parser.method_def_pattern, line)
    #             if m and m.group('name') == name:
    #                 name, args, type = m.groups()
    #                 ans = Method(name)
    #                 state = 1
    #             else:
    #                 continue
    #         elif state == 1:
    #             begin = re.fullmatch(parser.block_begin_pattern, line)
    #             assert begin
    #             block_end_pattern = parser.make_block_end_pattern(
    #                 begin.group())
    #             state = 2
    #         elif state == 2:
    #             m = re.fullmatch(block_end_pattern, line)
    #             if m:
    #                 state = 3
    #         elif state == 3:
    #             break
    #         ans.code.append(line)
    #     return ans

    # def serialize(self):
    #     return self.get_method('serializeAs_' + self.name)
    #
    # def deserialize(self):
    #     return self.get_method('deserializeAs_' + self.name)

    @classmethod
    def parse_all(cls):
        """
        Parse all messages
        """
        # queue = deque()
        # msgiter = iter(messages)
        #
        # def task_iter():
        #     if bases:
        #         yield queue.popleft()
        #     else:
        #         yield next(msgiter)
        #
        # def add_task(msg):
        #     queue.appendright(msg)

        for msg in cls.messages.values():
            # try:
            msg.parse()
            # except DependencyError as d:
            #     add_task(d.reason)
            #     add_task(msg)

    # def code(self):
    #     with self.path.open() as f:
    #         return f.read()
