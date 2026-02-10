class InMemoryDatabase:
    def __init__(self):
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

