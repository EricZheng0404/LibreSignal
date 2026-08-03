"""
All your implementation code for the bank system simulation goes here.
"""
class InMemoryDatabase:
    def __init__(self):
        self.files = {}
        self.backup = {}
        pass
    # ========== Level 1 Operations ==========
    def set(self,key, field, value):
        if key not in self.files :
            self.files[key] = {}
            # add to object if its not there
        self.files[key][field] = (value, None)
            # (value, expiry) - None means never expires
        return ""

    def get(self,key, field):
        if key not in self.files or field not in self.files[key]:
            return ""
        return self.files[key][field][0]

    def delete(self,key, field):
        if key not in self.files or field not in self.files[key]:
            return "false"
        del self.files[key][field]
        return "true"

    # ========== Level 2 Operations ==========
    def scan(self, key):
        if key not in self.files:
            return ""
        result = ""
        sortedfiles = sorted(self.files[key])
        for field in sortedfiles:
            result += f"{field}({self.files[key][field][0]}), "
            # add each value
        result = result[:-2] # strip last 2 characters ", "
        return result

    def scan_by_prefix(self, key, prefix):
        if key not in self.files:
            return ""
        result = ""
        sortedfiles = sorted(self.files[key])
        for field in sortedfiles:
            if field.startswith(prefix):
                result += f"{field}({self.files[key][field][0]}), "
        result = result[:-2]
        return result

    # ========== Level 3 Operations ==========
    # easies tif we make a helper about being alie, cause we'll do it  alot
    # check if it exits first, and the field exists
    # if no timestamp on the thing, it is defintiely alive
    # last chekc, we see if timestamp is before o after its thing
    def isAlive(self, key, field, timestamp):
        if key not in self.files or field not in self.files[key] :
            print(f"Does not exist so isn't alive")
            return False
        if self.files[key][field][1] is None:
            print(f"Does not have expiry so it's alive")
            return True 
        print(f"timestamp is {timestamp} and expiry is {self.files[key][field][1]}")
        alive = (timestamp < self.files[key][field][1])
        return alive

    def set_at(self, key, field, value, timestamp):
        if key not in self.files :
            self.files[key] = {}
            # add to object if its not there
        self.files[key][field] = (value, None)
            # add new field. expiry doesnt matter yet
        return ""

    def set_at_with_ttl(self, key, field, value, timestamp, ttl):
        if key not in self.files :
            self.files[key] = {}
            # add to object if its not there
        self.files[key][field] = (value, timestamp + ttl)
            # add new field. expiry is the timestamp +ttl 
        return ""

    def delete_at(self, key, field, timestamp):
        if key not in self.files or field not in self.files[key]:
            return "false"
        if not self.isAlive(key, field, timestamp):
            return "false"
        del self.files[key][field]
        return "true"

    def get_at(self, key, field, timestamp):
        if key not in self.files or field not in self.files[key]:
            return ""
        if not self.isAlive(key, field, timestamp):
            return ""    
        return self.files[key][field][0]

    def scan_at(self, key, timestamp):
        if key not in self.files:
            return ""
        result = ""
        sortedfiles = sorted(self.files[key])
        for field in sortedfiles:
            if self.isAlive(key, field, timestamp):
                result += f"{field}({self.files[key][field][0]}), "
                # add each value
        result = result[:-2] # strip last 2 characters ", "
        return result

    def scan_by_prefix_at(self, key, prefix, timestamp):
        if key not in self.files:
            return ""
        result = ""
        sortedfiles = sorted(self.files[key])
        for field in sortedfiles:
            if field.startswith(prefix) and self.isAlive(key, field, timestamp):
                result += f"{field}({self.files[key][field][0]}), "
        result = result[:-2]
        return result

    # ========== Level 4 Operations ==========
    def backup(self, timestamp):
        # make a duplicate copy of the database, at the diciontary, with key as timestamp
        # expiry is already in database at this time. 
        # if we backup, at a timestamp, expiry is already set per value. doesn't matter
        # return 
        pass

    def restore(self, timestamp, timestampToRestore):
        return ""