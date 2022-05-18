import pytest

from tests import example, example_assign


def test_exports():
    assert example.foo() == 42
    with pytest.raises(AttributeError):
        example.baz
    assert example.bar == "hello"
    assert example.god == "blessed"
    assert example.a == 123
    assert example.b == 456
    assert example.__all__ == ["foo", "bar", "god", "a", "b"]


def test_exports_assign():
    assert example_assign.foo() == 42
    assert example_assign.a == 123
    assert example_assign.b == 456
    assert example_assign.__all__ == ["a", "b", "foo"]


def test_duplicate_export():
    from modul import exports

    exports.test_foo = 1
    with pytest.raises(ValueError, match="test_foo has already been exported"):
        exports.test_foo = 2


class Foo:
    pass


@pytest.mark.parametrize("value", (1, "hello", Foo(), {1: "hello"}))
def test_illegal_export_argument(value):
    from modul import exports

    with pytest.raises(TypeError):
        exports(value)


def test_dict_like_interface():
    from modul import exports

    exports.clear()
    assert len(exports) == 0
    exports["foo"] = 1
    exports.update({"a": 123, "b": 456})
    assert list(exports) == ["foo", "a", "b"]
    assert dict(exports) == {"foo": 1, "a": 123, "b": 456}
    assert exports.pop("foo") == 1
    assert "foo" not in exports
