# objson

objson is a object serializer that enables you to convert object <-> json/dict

# Installation

```
$ pip install objson-py
```

Or, simply put `serializer.py` into your project.

# Quick Start

You can use `dumps` and `loads` like `json` library not only for `dict` but also for your custom objects.

```python
import objson

class MyClass:
    def __init__(self, foo=None, bar=None):
        self.foo = foo
        self.bar = bar

obj = MyClass(foo="hoge", bar="fuga")

# object to json
s = objson.dumps(obj)
print(s, type(s))
# -> {"foo": "hoge", "bar": "fuga"} <class 'str'>

# json to object
o = objson.loads(obj, MyClass)
print(o.foo, o.bar, type(o))
# -> hoge fuga <class '__main__.MyClass'>

# json to dict
d = objson.loads(s)
print(d, type(d))
# -> {'foo': 'hoge', 'bar': 'fuga'} <class 'dict'>

# dict to json
s = objson.dumps(d)
print(s, type(s))
# -> {"foo": "hoge", "bar": "fuga"} <class 'str'>
```

You can also use `dumpd` and `loadd` to encode to/decode from `dict`.

```python
# object to dict
d = objson.dumpd(obj)
print(d, type(d))
# -> {'foo': 'hoge', 'bar': 'fuga'} <class 'dict'>

# dict to object
o = objson.loadd(d, MyClass)
print(o, type(o))
# -> <__main__.MyClass object at 0x106e7ce48> <class '__main__.MyClass'>
```

# Serializable base class

`Serializable` provides `to_json()`, `from_json()`, `to_dict()` and `from_dict()`.

```python
import objson

class MySerializable(objson.Serializable):
    def __init__(self, foo=None, bar=None):
        self.foo = foo
        self.bar = bar

obj = MySerializable(foo="hoge", bar="fuga")

# object to json
s = obj.to_json()
print(s, type(s))
# -> {"foo": "hoge", "bar": "fuga"} <class 'str'>

# json to object
o = MySerializable.from_json(s)
print(o.foo, o.bar, type(o))
# -> hoge fuga <class '__main__.MySerializable'>

# object to dict
d = obj.to_dict()
print(d, type(d))
# -> {'foo': 'hoge', 'bar': 'fuga'} <class 'dict'>

# dict to object
o = MySerializable.from_dict(d)
print(o, type(o))
# -> <MySerializable at 0x109f67160>
# {
#   "foo": "hoge",
#   "bar": "fuga"
# } <class '__main__.MySerializable'>
```

# Auto convert datetime to ISO 8601 format string

`datetime` members will be automatically converted to ISO 8601 formatted string.

```python
import objson
from datetime import datetime

dt = datetime(2019, 8, 11, 12, 1, 30)
d = {"dt": dt}
s = objson.dumps(d)
print(s)
# -> {"dt": "2019-08-11T12:01:30.000000"}

d = objson.loads(s)
print(d, type(d["dt"]))
# -> {'dt': datetime.datetime(2019, 8, 11, 12, 1, 30)} <class 'datetime.datetime'>
```

# Auto convert member objects

Each members will be automatically converted to proper objects by implementing `_types()`.

```python
import objson

class Location:
    def __init__(self, name=None, school=None):
        self.name = name
        self.school = school

class Character:
    def __init__(self, name=None, actor=None):
        self.name = name
        self.actor = actor

class IdolGroup(objson.Serializable):
    def __init__(self, name=None, location=None, members=None):
        self.name = name
        self.location = location
        self.members = members

    # `_types` provides the type to deserialize each members
    @classmethod
    def _types(cls):
        return {
            "location": Location,
            "members": Character
        }

idol_group = IdolGroup(
    name="μ’s",
    location=Location("Akihabara", "Otonokizaka High"),
    members=[Character("Honoka Kosaka", "Emi Nitta"),
             Character("Umi Sonoda", "Suzuko Mimori"),
             Character("Kotori Minami", "Aya Uchida")])

# encode to json
s = idol_group.to_json(indent=2, ensure_ascii=False)
print(s)
# -> {
#   "name": "μ’s",
#   "location": {
#     "name": "Akihabara",
#     "school": "Otonokizaka High"
#   },
#   "members": [
#     {
#       "name": "Honoka Kosaka",
#       "actor": "Emi Nitta"
#     },
#     {
#       "name": "Umi Sonoda",
#       "actor": "Suzuko Mimori"
#     },
#     {
#       "name": "Kotori Minami",
#       "actor": "Aya Uchida"
#     }
#   ]
# }

# decode to object with members also decoded
obj = IdolGroup.from_json(s)
print(type(obj.location), type(obj.members[0]))
# -> <class '__main__.Location'> <class '__main__.Character'>
```

If you want to pass the argument to constructor of the class, implement class method named `create_object`.

```python
class IdolGroup(objson.Serializable):
    def __init__(self, name, location=None, members=None):
        self.name = name
        self.location = location
        self.members = members

    @classmethod
    def create_object(cls, d):
        # create object with argument(s)
        obj = cls(d["name"])
        # delete before return to avoid resetting the value
        del d["name"]
        return obj

    # `_types` provides the type to deserialize each members
    @classmethod
    def _types(cls):
        return {
            "location": Location,
            "members": Character
        }
```

# Contributions are welcome

Please feel free to send pull requests and post issues!

