import modul


def foo():
    return 42


modul.exports = {
    "a": 123,
    "b": 456,
    "foo": foo,
}
