"""
All your implementation code for the bank system simulation goes here.
"""
import copy
class InMemoryDatabase:
    def __init__(self):
        self.files = {}
        self.backups = {}
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
        snapshot = {}
        # make a duplicate copy of the database. But instead of recording expiry, 
        # we record the TTL. TTL is expiry - timestamp. if no expiry, no TTL
        for key in self.files :
            print(f"key: {key}")
            for field in self.files[key]:
                # we only want to take alive fields, so check first
                if self.isAlive(key, field, timestamp):
                    # og data structure of a field is value, expiry.
                    # we can safely assign the value. expiry is none, or the TTL
                    value, expiry = self.files[key][field]
                    # i would need to remember that a key can have multkple fields. so we add an empty dict
                    if key not in snapshot:
                        snapshot[key]= {}
                    # and now we populate the key with the fields
                    # value is value. remaining lifespan is expiry - timestamp
                    # it is none if no expiry. else its a subtration
                    remainingttl = None if expiry is None else expiry - timestamp
                    snapshot[key][field] = value, remainingttl
        self.backups[timestamp] = snapshot
        print(f"backups made: {self.backups[timestamp]}")
        return str(len(snapshot))

    def restore(self, timestamp, timestampToRestore):
        # find the most recent valid backup, that timestamp is BEFORE timestampttorestoe
        print(f"Restore timestamp {timestampToRestore}, timestamp now is {timestamp}. backups before restore : {self.backups}")
        targetBackup = None
        for target in reversed(list(self.backups.keys())):
            if target <= timestampToRestore:
                targetBackup = target
                print(f"Restore target is: {target} with backup: {self.backups[target]}")
                break
                # find target and set to timestamp
        # then we need to set files to the backup
        self.files = copy.deepcopy(self.backups[target])
        print(f"backup made. files are: {self.files}")
        # now we need to update expiry, cause rn they're all TTL's, adn we have timestamp
        for key in self.files :
            print(f"key: {key}")
            for field in self.files[key]:
                # og data structure of a field is value, expiry.
                # we can safely assign the value. expiry is none, or the TTL
                value, expiry = self.files[key][field]
                # and now we populate the key with the fields
                # value is value. new expiry is timestamp + TTL
                # it is none if no expiry. 
                newExpiry = None if expiry is None else expiry + timestamp
                self.files[key][field] = value, newExpiry
        return ""

    def runExpiration(self, timestamp):
        # run through each key. 
        # check if each field is NOT still alive
        # then delete it
        for key in list(self.files.keys()):
            for field in list(self.files[key].keys()):
                print(f"Checking expiration at {timestamp}. Key = {key} field = {field}")
                if not self.isAlive(key, field, timestamp):
                    self.delete_at(key, field, timestamp)
                    print(f"Deleting expired field: {self.files[key]}")