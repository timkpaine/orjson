# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import dataclasses
import datetime
import uuid

import pytest

import xorjson

try:
    import pytz
except ImportError:
    pytz = None  # type: ignore

try:
    import numpy
except ImportError:
    numpy = None  # type: ignore


class SubStr(str):
    pass


class TestNonStrKeyTests:
    def test_dict_keys_duplicate(self):
        """
        OPT_NON_STR_KEYS serializes duplicate keys
        """
        assert (
            xorjson.dumps({"1": True, 1: False}, option=xorjson.OPT_NON_STR_KEYS)
            == b'{"1":true,"1":false}'
        )

    def test_dict_keys_int(self):
        assert (
            xorjson.dumps({1: True, 2: False}, option=xorjson.OPT_NON_STR_KEYS)
            == b'{"1":true,"2":false}'
        )

    def test_dict_keys_substr(self):
        assert (
            xorjson.dumps({SubStr("aaa"): True}, option=xorjson.OPT_NON_STR_KEYS)
            == b'{"aaa":true}'
        )

    def test_dict_keys_substr_passthrough(self):
        """
        OPT_PASSTHROUGH_SUBCLASS does not affect OPT_NON_STR_KEYS
        """
        assert (
            xorjson.dumps(
                {SubStr("aaa"): True},
                option=xorjson.OPT_NON_STR_KEYS | xorjson.OPT_PASSTHROUGH_SUBCLASS,
            )
            == b'{"aaa":true}'
        )

    def test_dict_keys_substr_invalid(self):
        with pytest.raises(xorjson.JSONEncodeError):
            xorjson.dumps({SubStr("\ud800"): True}, option=xorjson.OPT_NON_STR_KEYS)

    def test_dict_keys_strict(self):
        """
        OPT_NON_STR_KEYS does not respect OPT_STRICT_INTEGER
        """
        assert (
            xorjson.dumps(
                {9223372036854775807: True},
                option=xorjson.OPT_NON_STR_KEYS | xorjson.OPT_STRICT_INTEGER,
            )
            == b'{"9223372036854775807":true}'
        )

    def test_dict_keys_int_range_valid_i64(self):
        """
        OPT_NON_STR_KEYS has a i64 range for int, valid
        """
        assert (
            xorjson.dumps(
                {9223372036854775807: True},
                option=xorjson.OPT_NON_STR_KEYS | xorjson.OPT_STRICT_INTEGER,
            )
            == b'{"9223372036854775807":true}'
        )
        assert (
            xorjson.dumps(
                {-9223372036854775807: True},
                option=xorjson.OPT_NON_STR_KEYS | xorjson.OPT_STRICT_INTEGER,
            )
            == b'{"-9223372036854775807":true}'
        )
        assert (
            xorjson.dumps(
                {9223372036854775809: True},
                option=xorjson.OPT_NON_STR_KEYS | xorjson.OPT_STRICT_INTEGER,
            )
            == b'{"9223372036854775809":true}'
        )

    def test_dict_keys_int_range_valid_u64(self):
        """
        OPT_NON_STR_KEYS has a u64 range for int, valid
        """
        assert (
            xorjson.dumps(
                {0: True},
                option=xorjson.OPT_NON_STR_KEYS | xorjson.OPT_STRICT_INTEGER,
            )
            == b'{"0":true}'
        )
        assert (
            xorjson.dumps(
                {18446744073709551615: True},
                option=xorjson.OPT_NON_STR_KEYS | xorjson.OPT_STRICT_INTEGER,
            )
            == b'{"18446744073709551615":true}'
        )

    def test_dict_keys_int_range_invalid(self):
        """
        OPT_NON_STR_KEYS has a range of i64::MIN to u64::MAX
        """
        with pytest.raises(xorjson.JSONEncodeError):
            xorjson.dumps({-9223372036854775809: True}, option=xorjson.OPT_NON_STR_KEYS)
        with pytest.raises(xorjson.JSONEncodeError):
            xorjson.dumps({18446744073709551616: True}, option=xorjson.OPT_NON_STR_KEYS)

    def test_dict_keys_float(self):
        assert (
            xorjson.dumps({1.1: True, 2.2: False}, option=xorjson.OPT_NON_STR_KEYS)
            == b'{"1.1":true,"2.2":false}'
        )

    def test_dict_keys_inf(self):
        assert (
            xorjson.dumps({float("Infinity"): True}, option=xorjson.OPT_NON_STR_KEYS)
            == b'{"null":true}'
        )
        assert (
            xorjson.dumps({float("-Infinity"): True}, option=xorjson.OPT_NON_STR_KEYS)
            == b'{"null":true}'
        )

    def test_dict_keys_nan(self):
        assert (
            xorjson.dumps({float("NaN"): True}, option=xorjson.OPT_NON_STR_KEYS)
            == b'{"null":true}'
        )

    def test_dict_keys_bool(self):
        assert (
            xorjson.dumps({True: True, False: False}, option=xorjson.OPT_NON_STR_KEYS)
            == b'{"true":true,"false":false}'
        )

    def test_dict_keys_datetime(self):
        assert (
            xorjson.dumps(
                {datetime.datetime(2000, 1, 1, 2, 3, 4, 123): True},
                option=xorjson.OPT_NON_STR_KEYS,
            )
            == b'{"2000-01-01T02:03:04.000123":true}'
        )

    def test_dict_keys_datetime_opt(self):
        assert (
            xorjson.dumps(
                {datetime.datetime(2000, 1, 1, 2, 3, 4, 123): True},
                option=xorjson.OPT_NON_STR_KEYS
                | xorjson.OPT_OMIT_MICROSECONDS
                | xorjson.OPT_NAIVE_UTC
                | xorjson.OPT_UTC_Z,
            )
            == b'{"2000-01-01T02:03:04Z":true}'
        )

    def test_dict_keys_datetime_passthrough(self):
        """
        OPT_PASSTHROUGH_DATETIME does not affect OPT_NON_STR_KEYS
        """
        assert (
            xorjson.dumps(
                {datetime.datetime(2000, 1, 1, 2, 3, 4, 123): True},
                option=xorjson.OPT_NON_STR_KEYS | xorjson.OPT_PASSTHROUGH_DATETIME,
            )
            == b'{"2000-01-01T02:03:04.000123":true}'
        )

    def test_dict_keys_uuid(self):
        """
        OPT_NON_STR_KEYS always serializes UUID as keys
        """
        assert (
            xorjson.dumps(
                {uuid.UUID("7202d115-7ff3-4c81-a7c1-2a1f067b1ece"): True},
                option=xorjson.OPT_NON_STR_KEYS,
            )
            == b'{"7202d115-7ff3-4c81-a7c1-2a1f067b1ece":true}'
        )

    def test_dict_keys_date(self):
        assert (
            xorjson.dumps(
                {datetime.date(1970, 1, 1): True}, option=xorjson.OPT_NON_STR_KEYS
            )
            == b'{"1970-01-01":true}'
        )

    def test_dict_keys_time(self):
        assert (
            xorjson.dumps(
                {datetime.time(12, 15, 59, 111): True},
                option=xorjson.OPT_NON_STR_KEYS,
            )
            == b'{"12:15:59.000111":true}'
        )

    def test_dict_non_str_and_sort_keys(self):
        assert (
            xorjson.dumps(
                {
                    "other": 1,
                    datetime.date(1970, 1, 5): 2,
                    datetime.date(1970, 1, 3): 3,
                },
                option=xorjson.OPT_NON_STR_KEYS | xorjson.OPT_SORT_KEYS,
            )
            == b'{"1970-01-03":3,"1970-01-05":2,"other":1}'
        )

    @pytest.mark.skipif(pytz is None, reason="pytz optional")
    def test_dict_keys_time_err(self):
        """
        OPT_NON_STR_KEYS propagates errors in types
        """
        val = datetime.time(12, 15, 59, 111, tzinfo=pytz.timezone("Asia/Shanghai"))
        with pytest.raises(xorjson.JSONEncodeError):
            xorjson.dumps({val: True}, option=xorjson.OPT_NON_STR_KEYS)

    def test_dict_keys_str(self):
        assert (
            xorjson.dumps({"1": True}, option=xorjson.OPT_NON_STR_KEYS) == b'{"1":true}'
        )

    def test_dict_keys_type(self):
        class Obj:
            a: str

        val = Obj()
        with pytest.raises(xorjson.JSONEncodeError):
            xorjson.dumps({val: True}, option=xorjson.OPT_NON_STR_KEYS)

    @pytest.mark.skipif(numpy is None, reason="numpy is not installed")
    def test_dict_keys_array(self):
        with pytest.raises(TypeError):
            {numpy.array([1, 2]): True}

    def test_dict_keys_dataclass(self):
        @dataclasses.dataclass
        class Dataclass:
            a: str

        with pytest.raises(TypeError):
            {Dataclass("a"): True}

    def test_dict_keys_dataclass_hash(self):
        @dataclasses.dataclass
        class Dataclass:
            a: str

            def __hash__(self):
                return 1

        obj = {Dataclass("a"): True}
        with pytest.raises(xorjson.JSONEncodeError):
            xorjson.dumps(obj, option=xorjson.OPT_NON_STR_KEYS)

    def test_dict_keys_list(self):
        with pytest.raises(TypeError):
            {[]: True}

    def test_dict_keys_dict(self):
        with pytest.raises(TypeError):
            {{}: True}

    def test_dict_keys_tuple(self):
        obj = {(): True}
        with pytest.raises(xorjson.JSONEncodeError):
            xorjson.dumps(obj, option=xorjson.OPT_NON_STR_KEYS)

    def test_dict_keys_unknown(self):
        with pytest.raises(xorjson.JSONEncodeError):
            xorjson.dumps({frozenset(): True}, option=xorjson.OPT_NON_STR_KEYS)

    def test_dict_keys_no_str_call(self):
        class Obj:
            a: str

            def __str__(self):
                return "Obj"

        val = Obj()
        with pytest.raises(xorjson.JSONEncodeError):
            xorjson.dumps({val: True}, option=xorjson.OPT_NON_STR_KEYS)
