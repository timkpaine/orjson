# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import datetime
import inspect
import json
import re

import pytest

import xorjson

SIMPLE_TYPES = (1, 1.0, -1, None, "str", True, False)


def default(obj):
    return str(obj)


class TestApi:
    def test_loads_trailing(self):
        """
        loads() handles trailing whitespace
        """
        assert xorjson.loads("{}\n\t ") == {}

    def test_loads_trailing_invalid(self):
        """
        loads() handles trailing invalid
        """
        pytest.raises(xorjson.JSONDecodeError, xorjson.loads, "{}\n\t a")

    def test_simple_json(self):
        """
        dumps() equivalent to json on simple types
        """
        for obj in SIMPLE_TYPES:
            assert xorjson.dumps(obj) == json.dumps(obj).encode("utf-8")

    def test_simple_round_trip(self):
        """
        dumps(), loads() round trip on simple types
        """
        for obj in SIMPLE_TYPES:
            assert xorjson.loads(xorjson.dumps(obj)) == obj

    def test_loads_type(self):
        """
        loads() invalid type
        """
        for val in (1, 3.14, [], {}, None):
            pytest.raises(xorjson.JSONDecodeError, xorjson.loads, val)

    def test_loads_recursion(self):
        """
        loads() recursion limit
        """
        pytest.raises(xorjson.JSONDecodeError, xorjson.loads, "[" * (1024 * 1024))

    def test_version(self):
        """
        __version__
        """
        assert re.match(r"^\d+\.\d+(\.\d+)?$", xorjson.__version__)

    def test_valueerror(self):
        """
        xorjson.JSONDecodeError is a subclass of ValueError
        """
        pytest.raises(xorjson.JSONDecodeError, xorjson.loads, "{")
        pytest.raises(ValueError, xorjson.loads, "{")

    def test_optional_none(self):
        """
        dumps() option, default None
        """
        assert xorjson.dumps([], option=None) == b"[]"
        assert xorjson.dumps([], default=None) == b"[]"
        assert xorjson.dumps([], option=None, default=None) == b"[]"
        assert xorjson.dumps([], None, None) == b"[]"

    def test_option_not_int(self):
        """
        dumps() option not int or None
        """
        with pytest.raises(xorjson.JSONEncodeError):
            xorjson.dumps(True, option=True)

    def test_option_invalid_int(self):
        """
        dumps() option invalid 64-bit number
        """
        with pytest.raises(xorjson.JSONEncodeError):
            xorjson.dumps(True, option=9223372036854775809)

    def test_option_range_low(self):
        """
        dumps() option out of range low
        """
        with pytest.raises(xorjson.JSONEncodeError):
            xorjson.dumps(True, option=-1)

    def test_option_range_high(self):
        """
        dumps() option out of range high
        """
        with pytest.raises(xorjson.JSONEncodeError):
            xorjson.dumps(True, option=1 << 12)

    def test_opts_multiple(self):
        """
        dumps() multiple option
        """
        assert (
            xorjson.dumps(
                [1, datetime.datetime(2000, 1, 1, 2, 3, 4)],
                option=xorjson.OPT_STRICT_INTEGER | xorjson.OPT_NAIVE_UTC,
            )
            == b'[1,"2000-01-01T02:03:04+00:00"]'
        )

    def test_default_positional(self):
        """
        dumps() positional arg
        """
        with pytest.raises(TypeError):
            xorjson.dumps(__obj={})  # type: ignore
        with pytest.raises(TypeError):
            xorjson.dumps(zxc={})  # type: ignore

    def test_default_unknown_kwarg(self):
        """
        dumps() unknown kwarg
        """
        with pytest.raises(TypeError):
            xorjson.dumps({}, zxc=default)  # type: ignore

    def test_default_empty_kwarg(self):
        """
        dumps() empty kwarg
        """
        assert xorjson.dumps(None, **{}) == b"null"

    def test_default_twice(self):
        """
        dumps() default twice
        """
        with pytest.raises(TypeError):
            xorjson.dumps({}, default, default=default)  # type: ignore

    def test_option_twice(self):
        """
        dumps() option twice
        """
        with pytest.raises(TypeError):
            xorjson.dumps({}, None, xorjson.OPT_NAIVE_UTC, option=xorjson.OPT_NAIVE_UTC)  # type: ignore

    def test_option_mixed(self):
        """
        dumps() option one arg, one kwarg
        """

        class Custom:
            def __str__(self):
                return "zxc"

        assert (
            xorjson.dumps(
                [Custom(), datetime.datetime(2000, 1, 1, 2, 3, 4)],
                default,
                option=xorjson.OPT_NAIVE_UTC,
            )
            == b'["zxc","2000-01-01T02:03:04+00:00"]'
        )

    def test_dumps_signature(self):
        """
        dumps() valid __text_signature__
        """
        assert (
            str(inspect.signature(xorjson.dumps))
            == "(obj, /, default=None, option=None)"
        )
        inspect.signature(xorjson.dumps).bind("str")
        inspect.signature(xorjson.dumps).bind("str", default=default, option=1)
        inspect.signature(xorjson.dumps).bind("str", default=None, option=None)

    def test_loads_signature(self):
        """
        loads() valid __text_signature__
        """
        assert str(inspect.signature(xorjson.loads)), "(obj == /)"
        inspect.signature(xorjson.loads).bind("[]")

    def test_dumps_module_str(self):
        """
        xorjson.dumps.__module__ is a str
        """
        assert xorjson.dumps.__module__ == "xorjson"

    def test_loads_module_str(self):
        """
        xorjson.loads.__module__ is a str
        """
        assert xorjson.loads.__module__ == "xorjson"

    def test_bytes_buffer(self):
        """
        dumps() trigger buffer growing where length is greater than growth
        """
        a = "a" * 900
        b = "b" * 4096
        c = "c" * 4096 * 4096
        assert xorjson.dumps([a, b, c]) == f'["{a}","{b}","{c}"]'.encode("utf-8")

    def test_bytes_null_terminated(self):
        """
        dumps() PyBytesObject buffer is null-terminated
        """
        # would raise ValueError: invalid literal for int() with base 10: b'1596728892'
        int(xorjson.dumps(1596728892))
