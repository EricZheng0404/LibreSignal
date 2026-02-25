class InMemoryDatabase:
    def __init__(self):
        # key: {field: value}
        self.database = {}

    def set(self, key, field, value):
        if key not in self.database:
            self.database[key] = {}
        self.database[key][field] = value
        return ""
    
    def get(self, key, field):
        if key not in self.database or field not in self.database[key]:
            return ""
        return self.database[key][field]

    def delete(self, key, field):
        if key not in self.database or field not in self.database[key]:
            return "false"
        del self.database[key][field]
        return "true"

    def scan(self, key):
        if key not in self.database:
            return ""
        items = list(self.database[key].items())
        print("items:", items)
        items.sort()  # Sort by field name
        return ", ".join(f"{field}({value})" for field, value in items)