from collections import Counter


def convert_dict(items):
    hashmap = {}
    for item in items:
        if item not in hashmap.keys():
            hashmap[item] = 1
        else:
            hashmap[item] += 1
    return hashmap


class DiffEngine:
    initial_items: dict
    current_items: dict
    surgery_status = 2

    def set_initial_items(self, items):
        self.initial_items = convert_dict(items)

    def set_current_items(self, items):
        self.current_items = convert_dict(items)

    def compare(self):
        diff = {}
        for k in self.initial_items:
            if k not in self.current_items:
                diff[k] = self.initial_items[k]
            else:
                d = self.initial_items[k] - self.current_items[k]
                if d > 0:
                    diff[k] = d
        return diff
