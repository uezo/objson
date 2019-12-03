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

# decode to object with members also decoded
obj = IdolGroup.from_json(s)
print(type(obj.location), type(obj.members[2]))
