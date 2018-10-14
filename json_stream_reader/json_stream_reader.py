# -*- coding: utf-8 -*-
"""
Given a byte stream of {}-bracketed objects, generate one object-string at a
time.

Roadmap:
    - Allow any amount of whitespace characters between objects, without
      slowing down the parser.

"""

from typing import Generator, IO


def reader(stream: IO[bytes], chunk_size=1000) -> Generator:
    """
    >>> import io
    >>> stream = io.BytesIO()
    >>> stream.write(b'{"value":1}{"value":2}{"value":3}')
    33
    >>> stream.seek(0)
    0
    >>> items = reader(stream)
    >>> import json
    >>> [json.loads(x.decode()) for x in items] == [{"value":1}, {"value":2},
    ...   {"value":3}]
    True
    >>> stream.seek(0)
    0
    >>> items = reader(stream, 1)
    >>> import json
    >>> [json.loads(x.decode()) for x in items] == [{"value":1}, {"value":2},
    ...   {"value":3}]
    True
    """
    size_to_read = chunk_size
    buffer = stream.read(size_to_read)
    assert buffer.startswith(b'{')
    while buffer:
        cursor = None
        begin = 0
        while not cursor:
            try:
                cursor = buffer.index(b'}{', begin)
            except ValueError:
                # No end/begin pair found.
                more = stream.read(size_to_read)
                if more:
                    # Subtract 1 because we may need to catch the trailing }
                    # again.
                    begin += len(buffer) - 1 if begin is 0 else (
                            size_to_read - 1)
                    buffer += more
                elif buffer.endswith(b'}'):
                    yield buffer
                    return None
                else:
                    raise Exception('Stream ends with incomplete JSON object.')
                size_to_read = size_to_read + chunk_size

        line = buffer[:cursor+1]
        yield line
        buffer = buffer[cursor+1:] + stream.read(size_to_read)
