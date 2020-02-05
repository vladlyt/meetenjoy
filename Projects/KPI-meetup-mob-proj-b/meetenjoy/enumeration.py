class Enumeration:
    def __init__(self, enum_list):
        def aux(t):
            if len(t) > 2:
                return t
            else:
                return t[0], t[1], t[1]

        def check_for_unique(t):
            # indexes_count = len(set([i[0] for i in t]))
            # assert indexes_count == len(t)
            if len(t) > 2:
                human_readable_indexes_count = len(set([i[1] for i in t]))
                assert human_readable_indexes_count == len(t)

        check_for_unique(enum_list)
        self.full_enum_list = enum_list
        enum_list = [aux(i) for i in enum_list]
        self.enum_list = [(item[0], item[2]) for item in enum_list]
        self.enum_dict = {}
        for item in enum_list:
            self.enum_dict[item[1]] = (item[0], item[2])

    def __contains__(self, v):
        return v in self.enum_list

    def __len__(self):
        return len(self.enum_list)

    def __getitem__(self, v):
        if isinstance(v, str):
            return self.enum_dict[v][0]
        elif isinstance(v, int):
            return self.enum_list[v]

    def __getattr__(self, name):
        return self.enum_dict[name][0]

    def __iter__(self):
        return self.enum_list.__iter__()

    def __add__(self, other):
        assert isinstance(other, Enumeration)
        new_enum_list = self.full_enum_list + other.full_enum_list
        return Enumeration(new_enum_list)

    def __deepcopy__(self, name):
        # HACK: for filters; but from another point of view enum it's a singleton
        return self

    def get_tuple(self):
        return tuple(self.enum_list)

    def get_name_by_value(self, v):
        for value, name in self.enum_list:
            if v == value:
                return name
        raise KeyError("No such value")

    def get_value_by_name(self, code, default=None):
        for name, (value, description) in self.enum_dict.items():
            if code == value:
                return name
        return default

    def all_except(self, *names):
        # maybe can be a better solution
        return tuple(v[0] for k, v in self.enum_dict.items() if k not in names)

    def enum_only(self, *names):
        # checks that all names present
        for n in names:
            assert n in self.enum_dict.keys()
        return [v for k, v in self.enum_dict.items() if k in names]

    @property
    def values_list(self):
        return [el[0] for el in self.enum_list]

    @property
    def to_dict(self):
        return {k: v[0] for k, v in self.enum_dict.items()}

    def exclude(self, *args):
        keys = self.all_except(*args)
        return Enumeration([t for t in self.full_enum_list if t[0] in keys])
