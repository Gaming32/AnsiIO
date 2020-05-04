import sys
import io, string

from typing import List, Union, Tuple


ESCAPE_CHAR  = '\u001b'
ESCAPE_START = '['

SUPPORT_CHARS = '=' + string.digits + ';'


class Escape:
    def __init__(self, type, args):
        self.type = type
        self.args = args
    @classmethod
    def parse(cls, data:str):
        escape_type = ''
        result = ['']
        for char in data:
            if char == '=':
                escape_type += '='
                continue
            elif char == ';' or char in string.ascii_letters:
                result[-1] = int(result[-1])
                if char in string.ascii_letters:
                    escape_type += char
                    break
                else: result.append('')
            else:
                result[-1] += char
        return cls(escape_type, result)
    def __str__(self):
        if len(self.type) >= 2:
            pretype = self.type[0]
            type = self.type[1]
        else:
            pretype = ''
            type = self.type
        return ESCAPE_CHAR + ESCAPE_START + pretype + ';'.join(str(arg) for arg in self.args) + type
    def __repr__(self):
        return '%s(%r, %r)' % (self.__class__.__qualname__, self.type, self.args)


def parse_string(data:str) -> List[Union[str, Escape]]:
    wait_for_start = False
    in_ansi = False

    result = ['']
    ansi_result = ''

    for char in data:
        if in_ansi:
            if char in SUPPORT_CHARS:
                ansi_result += char
            elif char in string.ascii_letters:
                result.append(Escape.parse(ansi_result + char))
                result.append('')
                in_ansi = False
            else:
                result[-1] += ansi_result
                in_ansi = False
            continue

        if char == ESCAPE_CHAR:
            wait_for_start = True
        elif wait_for_start:
            wait_for_start = False
            if char == ESCAPE_START:
                ansi_result = ''
                in_ansi = True
            else:
                result += ESCAPE_CHAR
        if not (wait_for_start or in_ansi): result[-1] += char
    
    if result[0] == '': del result[0]
    if result[-1] == '': del result[-1]
    return result


class AnsiStream(io.TextIOBase):
    def __init__(self, wrapped:io.TextIOBase=sys.stdout):
        self.wrapped = wrapped

    def writable(self):
        return True

    def use_ansi_escape(self, escape:Escape) -> None:
        pass

    def write(self, data:str, forget_result=False) -> Union[int, None]:
        """Writes the string parts of data to `self.wrapped` and calls
`self.use_ansi_escape(escape_type, escape_args)` for every ansi escape

Parameters
----------
data : str
    The data to comb for ansi and write to `self.wrapped`
forget_result : bool
    Whether to keep track of the raw string data written to `self.wrapped` and return its length

Returns
-------
The length of the written string if `forget_result` is `False`, otherwise it returns None"""

        if not forget_result: result = ''

        for value in parse_string(data):
            if isinstance(value, str):
                self.wrapped.write(value)
                result += value
            else:
                self.use_ansi_escape(value)

        return None if forget_result else len(result)

    def flush(self):
        return self.wrapped.flush()

    def readable(self):
        return False

    def close(self):
        return self.wrapped.close()

    @property
    def closed(self):
        return self.wrapped.closed


class StreamReplacer:
    class _ReplaceWrite(io.TextIOBase):
        def __init__(self, wrapped):
            self.save_write = wrapped.write
            self.wrapped = wrapped
        def write(self, s):
            return self.save_write(s)
        def __getattr__(self, attr):
            return getattr(self.wrapped, attr)

    def __init__(self, stream=sys.stdout, replace_class=AnsiStream):
        self.stream = stream
        self.save_write = stream.write
        self.replaced = replace_class(StreamReplacer._ReplaceWrite(stream))

    def activate(self):
        self.stream.write = self.replaced.write
    def deactivate(self):
        self.stream.write = self.save_write

    def __enter__(self):
        self.activate()
        return self
    def __exit__(self, *exc_info):
        self.deactivate()


del List, Union, Tuple


if __name__ == '__main__':
    data = parse_string('Hello \u001b[36m World!')
    print(data)
    data2 = parse_string('Hello, World!')
    print(data2)

    print()
    stream = AnsiStream()
    stream.write('Hello \u001b[36mWorld!\n')
    stream.write('Hello, World!\n')
    stream.writelines(['Hello\n', '\u001b[33m', 'World\n'])

    print()
    with StreamReplacer():
        print('Hello \u001b[33m World \u001b[0m')
    print('Hello \u001b[36m World \u001b[0m')