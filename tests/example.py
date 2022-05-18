from exports import exports


@exports
def foo():
    return 42


baz = "unexported"
bar = "hello"

exports.bar = bar
exports["god"] = "blessed"
exports({"a": 123, "b": 456})
