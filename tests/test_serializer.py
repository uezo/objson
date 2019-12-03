import pytest
from pytz import timezone
from datetime import datetime
from copy import deepcopy

from objson import (
    date_to_str,
    str_to_date,
    dumpd,
    loadd,
    dumps,
    loads,
    Serializable
)


class PlainClass:
    def __init__(self, strvalue=None, intvalue=None, dtvalue=None,
                 listvalue=None, dictvalue=None, objvalue=None):
        self.strvalue = strvalue
        self.intvalue = intvalue
        self.dtvalue = dtvalue
        self.listvalue = listvalue
        self.dictvalue = dictvalue
        self.objvalue = objvalue


class SerializableClass(Serializable):
    def __init__(self, strvalue=None, intvalue=None, dtvalue=None,
                 listvalue=None, dictvalue=None, objvalue=None):
        self.strvalue = strvalue
        self.intvalue = intvalue
        self.dtvalue = dtvalue
        self.listvalue = listvalue
        self.dictvalue = dictvalue
        self.objvalue = objvalue

    @classmethod
    def _types(cls):
        return {
            "objvalue": cls
        }


@pytest.fixture
def date_with_tz():
    return timezone("Asia/Tokyo").localize(datetime(2019, 8, 11, 6, 10, 24))


@pytest.fixture
def p_obj(date_with_tz):
    gch = PlainClass(
        strvalue="instance of grand child class",
        intvalue=3,
        dtvalue=date_with_tz,
        listvalue=["list_str_3", 3],
        dictvalue={"key1": "value3", "key2": 3})

    ch = PlainClass(
        strvalue="instance of child class",
        intvalue=2,
        dtvalue=date_with_tz,
        listvalue=["list_str_2", 2, gch],
        dictvalue={"key1": "value2", "key2": 2})

    return PlainClass(
        strvalue="instance of plain class",
        intvalue=1,
        dtvalue=date_with_tz,
        listvalue=["list_str_1", 1, date_with_tz, ch],
        dictvalue={"key1": "value1", "key2": 1},
        objvalue=ch)


@pytest.fixture
def s_obj(date_with_tz):
    gch = SerializableClass(
        strvalue="instance of grand child class",
        intvalue=3,
        dtvalue=date_with_tz,
        listvalue=["list_str_3", 3],
        dictvalue={"key1": "value3", "key2": 3})

    ch = SerializableClass(
        strvalue="instance of child class",
        intvalue=2,
        dtvalue=date_with_tz,
        listvalue=["list_str_2", 2],
        dictvalue={"key1": "value2", "key2": 2},
        objvalue=gch)

    return SerializableClass(
        strvalue="instance of serializable class",
        intvalue=1,
        dtvalue=date_with_tz,
        listvalue=["list_str_1", 1, ch],
        dictvalue={"key1": "value1", "key2": 1, "key3": ch},
        objvalue=ch)


def test_date_to_str():
    dt = datetime(2019, 8, 11, 6, 10, 24)
    assert date_to_str(dt) == "2019-08-11T06:10:24.000000"
    dt_tz = timezone("Asia/Tokyo").localize(dt)
    assert date_to_str(dt_tz) == "2019-08-11T06:10:24.000000"
    assert date_to_str(dt_tz, True) == "2019-08-11T06:10:24.000000+09:00"


def test_str_to_date():
    dtstr = "2019-08-11T06:10:24"
    assert str_to_date(dtstr) == datetime(2019, 8, 11, 6, 10, 24)
    dtstr_tz = "2019-08-11T06:10:24+09:00"
    assert str_to_date(dtstr_tz) == \
        timezone("Asia/Tokyo").localize(datetime(2019, 8, 11, 6, 10, 24))


def test_dumpd_plain(date_with_tz, p_obj):
    d = dumpd(p_obj)
    assert d["strvalue"] == "instance of plain class"
    assert d["intvalue"] == 1
    assert d["dtvalue"] == date_with_tz
    assert d["listvalue"] == ["list_str_1", 1, date_with_tz, d["objvalue"]]
    assert d["dictvalue"]["key1"] == "value1"
    assert d["dictvalue"]["key2"] == 1
    assert d["objvalue"]["strvalue"] == "instance of child class"
    assert d["objvalue"]["listvalue"][2]["strvalue"] == \
        "instance of grand child class"
    d2 = dumpd(d)
    assert d == d2


def test_dumps_plain(date_with_tz, p_obj):
    d = dumps(p_obj)
    assert isinstance(d, str)
    assert "instance of plain class" in d
    assert "2019-08-11T06:10:24.000000+09:00" in d


def test_dumps_plain_none():
    s = dumps(None)
    assert s == ""


def test_dumpd_serializable(date_with_tz, s_obj):
    d = dumpd(s_obj)
    assert d["strvalue"] == "instance of serializable class"
    assert d["intvalue"] == 1
    assert d["dtvalue"] == date_with_tz
    assert d["listvalue"] == ["list_str_1", 1, d["objvalue"]]
    assert d["listvalue"][2]["strvalue"] == "instance of child class"
    assert d["listvalue"][2]["objvalue"]["strvalue"] == \
        "instance of grand child class"
    assert d["dictvalue"]["key1"] == "value1"
    assert d["dictvalue"]["key2"] == 1
    assert d["dictvalue"]["key3"]["strvalue"] == "instance of child class"
    assert d["dictvalue"]["key3"]["objvalue"]["strvalue"] == \
        "instance of grand child class"
    assert d["objvalue"]["strvalue"] == "instance of child class"
    assert d["objvalue"]["objvalue"]["strvalue"] == \
        "instance of grand child class"


def test_dumps_serializable(date_with_tz, s_obj):
    d = dumps(s_obj)
    assert isinstance(d, str)
    assert "instance of serializable class" in d
    assert "instance of child class" in d
    assert "instance of grand child class" in d
    assert "2019-08-11T06:10:24.000000+09:00" in d


def test_loadd_plain(date_with_tz, p_obj):
    d = dumpd(p_obj)
    obj = loadd(d, PlainClass)
    assert obj.strvalue == "instance of plain class"
    assert obj.intvalue == 1
    assert obj.dtvalue == date_with_tz
    assert obj.listvalue == [
        "list_str_1", 1, date_with_tz, dumpd(obj.objvalue)]
    assert obj.dictvalue["key1"] == "value1"
    assert obj.dictvalue["key2"] == 1
    assert obj.objvalue["strvalue"] == "instance of child class"


def test_loadd_with_initargs(date_with_tz):
    class MyClass:
        def __init__(self, foo):
            self.foo = foo
            self.bar = None

        @classmethod
        def create_object(cls, d):
            obj = cls(d["foo"])
            del d["foo"]
            return obj

    obj = loadd({"foo": "foo1", "bar": "bar2"}, MyClass)
    assert obj.foo == "foo1"    # set at __init__
    assert obj.bar == "bar2"    # set by dict value


def test_loads_plain(date_with_tz, p_obj):
    d = dumps(p_obj)
    obj = loads(d, PlainClass)
    assert obj.strvalue == "instance of plain class"
    assert obj.intvalue == 1
    assert obj.dtvalue == date_with_tz
    assert obj.listvalue == [
        "list_str_1", 1, date_with_tz, dumpd(p_obj.listvalue[3])]
    assert obj.dictvalue["key1"] == "value1"
    assert obj.dictvalue["key2"] == 1
    assert obj.objvalue["strvalue"] == "instance of child class"


def test_loads_plain_to_dict(date_with_tz, p_obj):
    s = dumps(p_obj)
    d = loads(s)
    assert d["strvalue"] == "instance of plain class"
    assert d["intvalue"] == 1
    assert d["dtvalue"] == date_with_tz
    assert d["listvalue"] == [
        "list_str_1", 1, date_with_tz, dumpd(p_obj.listvalue[3])]
    assert d["dictvalue"]["key1"] == "value1"
    assert d["dictvalue"]["key2"] == 1
    assert d["objvalue"]["strvalue"] == "instance of child class"


def test_loads_plain_none():
    obj = loads("")
    assert obj is None
    obj = loads(None)
    assert obj is None


def test_loads_with_initargs(date_with_tz):
    class MyClass:
        def __init__(self, foo):
            self.foo = foo
            self.bar = None

        @classmethod
        def create_object(cls, d):
            obj = cls(d["foo"])
            del d["foo"]
            return obj

    obj = loads('{"foo": "foo1", "bar": "bar2"}', MyClass)
    assert obj.foo == "foo1"    # set at __init__
    assert obj.bar == "bar2"    # set by dict value


def test_loadd_serializable(date_with_tz, s_obj):
    d = dumpd(s_obj)
    obj = loadd(d, SerializableClass)
    assert obj.strvalue == "instance of serializable class"
    assert obj.intvalue == 1
    assert obj.dtvalue == date_with_tz
    assert obj.listvalue == ["list_str_1", 1, s_obj.listvalue[2].to_dict()]
    assert obj.dictvalue["key1"] == "value1"
    assert obj.dictvalue["key2"] == 1
    assert obj.dictvalue["key3"] == s_obj.listvalue[2].to_dict()
    assert obj.objvalue.to_dict() == s_obj.objvalue.to_dict()


def test_loadd_serializable_notserializable(p_obj):
    class MyClass(Serializable):
        def __init__(self):
            self.strvalue = "my_class"
            self.objvalue = p_obj
            self.listvalue = [p_obj, p_obj]
            self.dictvalue = {"k1": p_obj, "k2": p_obj}

        @classmethod
        def _types(cls):
            return {
                "objvalue": PlainClass
            }

    o = MyClass()
    d = dumpd(o)
    assert isinstance(d["objvalue"], dict)
    assert isinstance(d["listvalue"][0], dict)
    assert isinstance(d["listvalue"][0]["objvalue"], dict)
    assert isinstance(d["dictvalue"]["k1"], dict)
    assert isinstance(d["dictvalue"]["k1"]["objvalue"], dict)
    obj = loadd(d, MyClass)
    assert isinstance(obj, MyClass)
    assert isinstance(obj.objvalue, PlainClass)
    assert obj.objvalue.strvalue == p_obj.strvalue
    assert obj.objvalue.objvalue["strvalue"] == "instance of child class"
    assert obj.objvalue.listvalue[3]["strvalue"] == "instance of child class"


def test_loads_serializable(date_with_tz, s_obj):
    d = dumps(s_obj)
    obj = loads(d, SerializableClass)
    assert obj.strvalue == "instance of serializable class"
    assert obj.intvalue == 1
    assert obj.dtvalue == date_with_tz
    assert obj.listvalue[0:2] == ["list_str_1", 1]
    # when a item of list, object is not restored
    obj.listvalue[2] = SerializableClass.from_dict(obj.listvalue[2])
    assert obj.listvalue[2].to_dict() == s_obj.listvalue[2].to_dict()
    assert obj.dictvalue["key1"] == "value1"
    assert obj.dictvalue["key2"] == 1
    # when a item of dict, object is not restored
    obj.dictvalue["key3"] = SerializableClass.from_dict(obj.dictvalue["key3"])
    assert obj.dictvalue["key3"].to_dict() == s_obj.listvalue[2].to_dict()
    # top level member is restored to object by configure `_types`
    assert obj.objvalue.to_dict() == s_obj.objvalue.to_dict()


def test_to_dict(s_obj, date_with_tz):
    d = s_obj.to_dict()
    assert d["strvalue"] == "instance of serializable class"
    assert d["intvalue"] == 1
    assert d["dtvalue"] == date_with_tz
    assert d["listvalue"] == ["list_str_1", 1, d["objvalue"]]
    assert d["listvalue"][2]["strvalue"] == "instance of child class"
    assert d["listvalue"][2]["objvalue"]["strvalue"] == \
        "instance of grand child class"
    assert d["dictvalue"]["key1"] == "value1"
    assert d["dictvalue"]["key2"] == 1
    assert d["dictvalue"]["key3"]["strvalue"] == "instance of child class"
    assert d["dictvalue"]["key3"]["objvalue"]["strvalue"] == \
        "instance of grand child class"
    assert d["objvalue"]["strvalue"] == "instance of child class"
    assert d["objvalue"]["objvalue"]["strvalue"] == \
        "instance of grand child class"


def test_to_json(date_with_tz, s_obj):
    d = s_obj.to_json()
    assert isinstance(d, str)
    assert "instance of serializable class" in d
    assert "instance of child class" in d
    assert "instance of grand child class" in d
    assert "2019-08-11T06:10:24.000000+09:00" in d


def test_from_dict(date_with_tz, s_obj):
    d = s_obj.to_dict()
    obj = SerializableClass.from_dict(d)
    assert obj.strvalue == "instance of serializable class"
    assert obj.intvalue == 1
    assert obj.dtvalue == date_with_tz
    assert obj.listvalue == ["list_str_1", 1, s_obj.listvalue[2].to_dict()]
    assert obj.dictvalue["key1"] == "value1"
    assert obj.dictvalue["key2"] == 1
    assert obj.dictvalue["key3"] == s_obj.listvalue[2].to_dict()
    assert obj.objvalue.to_dict() == s_obj.objvalue.to_dict()


def test_from_dict_dict(date_with_tz, s_obj):
    obj0 = deepcopy(s_obj)
    obj0.strvalue = "object 0"
    obj1 = deepcopy(s_obj)
    obj1.strvalue = "object 1"
    obj2 = deepcopy(s_obj)
    obj2.strvalue = "object 2"
    d = {
        "obj0": obj0.to_dict(),
        "obj1": obj1.to_dict(),
        "obj2": obj2.to_dict()
    }
    obj_list = SerializableClass.from_dict_dict(d)
    obj = obj_list["obj0"]
    assert obj.strvalue == "object 0"
    assert obj.intvalue == 1
    assert obj.dtvalue == date_with_tz
    assert obj.listvalue == ["list_str_1", 1, s_obj.listvalue[2].to_dict()]
    assert obj.dictvalue["key1"] == "value1"
    assert obj.dictvalue["key2"] == 1
    assert obj.dictvalue["key3"] == s_obj.listvalue[2].to_dict()
    assert obj.objvalue.to_dict() == s_obj.objvalue.to_dict()
    assert obj_list["obj1"].strvalue == "object 1"
    assert obj_list["obj2"].strvalue == "object 2"


def test_from_dict_list(date_with_tz, s_obj):
    obj0 = deepcopy(s_obj)
    obj0.strvalue = "object 0"
    obj1 = deepcopy(s_obj)
    obj1.strvalue = "object 1"
    obj2 = deepcopy(s_obj)
    obj2.strvalue = "object 2"
    d = [obj0.to_dict(), obj1.to_dict(), obj2.to_dict()]
    obj_list = SerializableClass.from_dict(d)
    obj = obj_list[0]
    assert obj.strvalue == "object 0"
    assert obj.intvalue == 1
    assert obj.dtvalue == date_with_tz
    assert obj.listvalue == ["list_str_1", 1, s_obj.listvalue[2].to_dict()]
    assert obj.dictvalue["key1"] == "value1"
    assert obj.dictvalue["key2"] == 1
    assert obj.dictvalue["key3"] == s_obj.listvalue[2].to_dict()
    assert obj.objvalue.to_dict() == s_obj.objvalue.to_dict()
    assert obj_list[1].strvalue == "object 1"
    assert obj_list[2].strvalue == "object 2"


def test_from_json(date_with_tz, s_obj):
    d = s_obj.to_json()
    obj = SerializableClass.from_json(d)
    assert obj.strvalue == "instance of serializable class"
    assert obj.intvalue == 1
    assert obj.dtvalue == date_with_tz
    assert obj.listvalue[0:2] == ["list_str_1", 1]
    # when a item of list, object and datetime are not restored
    obj.listvalue[2] = SerializableClass.from_dict(obj.listvalue[2])
    assert obj.listvalue[2].to_dict() == s_obj.listvalue[2].to_dict()
    assert obj.dictvalue["key1"] == "value1"
    assert obj.dictvalue["key2"] == 1
    # when a item of dict, object and datetime are not restored
    obj.dictvalue["key3"] = SerializableClass.from_dict(obj.dictvalue["key3"])
    assert obj.dictvalue["key3"].to_dict() == s_obj.listvalue[2].to_dict()
    # top level member is restored to object by configure `_types`
    assert obj.objvalue.to_dict() == s_obj.objvalue.to_dict()


def test_from_json_list(date_with_tz, s_obj):
    o0 = deepcopy(s_obj)
    o0.strvalue = "instance of serializable class 0"
    o1 = deepcopy(s_obj)
    o1.strvalue = "instance of serializable class 1"
    o2 = deepcopy(s_obj)
    o2.strvalue = "instance of serializable class 2"
    d = dumps([o0, o1, o2])
    obj = SerializableClass.from_json(d)[1]
    assert obj.strvalue == "instance of serializable class 1"
    assert obj.intvalue == 1
    assert obj.dtvalue == date_with_tz
    assert obj.listvalue[0:2] == ["list_str_1", 1]
    # when a item of list, object and datetime are not restored
    obj.listvalue[2] = SerializableClass.from_dict(obj.listvalue[2])
    assert obj.listvalue[2].to_dict() == s_obj.listvalue[2].to_dict()
    assert obj.dictvalue["key1"] == "value1"
    assert obj.dictvalue["key2"] == 1
    # when a item of dict, object and datetime are not restored
    obj.dictvalue["key3"] = SerializableClass.from_dict(obj.dictvalue["key3"])
    assert obj.dictvalue["key3"].to_dict() == s_obj.listvalue[2].to_dict()
    # top level member is restored to object by configure `_types`
    assert obj.objvalue.to_dict() == s_obj.objvalue.to_dict()


def test_repr(s_obj):
    print(s_obj)


def test_property():
    class PropClass:
        def __init__(self):
            self._foo = None
            self._bar = None

        @property
        def foo(self):
            return self._foo

        @foo.setter
        def foo(self, val):
            self._foo = val

        @property
        def bar(self):
            return self._bar

        @bar.setter
        def bar(self, val):
            self._bar = val

    obj = loadd({"foo": "foo1", "bar": "bar2"}, PropClass)
    assert obj.foo == "foo1"
    assert obj.bar == "bar2"


def test_example():
    class Location:
        def __init__(self, name=None, school=None):
            self.name = name
            self.school = school

    class Character:
        def __init__(self, name=None, actor=None):
            self.name = name
            self.actor = actor

    class IdolGroup(Serializable):
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

    # decode to object with members also decoded
    obj = IdolGroup.from_json(s)
    assert obj.name == "μ’s"
    assert obj.location.name == "Akihabara"
    assert obj.location.school == "Otonokizaka High"
    assert obj.members[2].name == "Kotori Minami"

    clist = loads(dumps(idol_group.members), Character)
    assert clist[1].name == "Umi Sonoda"
