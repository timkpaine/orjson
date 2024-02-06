import xorjson


class C:
    c: "C"

    def __del__(self):
        xorjson.loads('"' + "a" * 10000 + '"')


def test_reentrant():
    c = C()
    c.c = c
    del c

    xorjson.loads("[" + "[]," * 1000 + "[]]")
