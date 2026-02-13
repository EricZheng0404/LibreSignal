import copy
import collections

class InMemoryDatabase:
    def __init__(self):
        self.map = {}
        # level 3
        self.map_ts = {}
        self.ts = 0
        # level 4
        self.backup_map = collections.defaultdict(dict)
        self.backup_map_ts = collections.defaultdict(dict)

    def set(self,key, field, value):
        if key not in self.map:
            self.map[key] = {field : value}
        else:
            self.map[key][field] = value
        return ''
    
    def set_at(self, key, field, value, ts):
        ''' 
            key : field,value 
            {'A' : {'BD,C' : '15'} }
        '''
        self.ts = ts
        if key not in self.map:
            self.map[key] = {field : value}
            self.map_ts[key] = {field + ',' + value : 'INF'}
        else:
            # update map_ts with updated key value 
            if field in self.map[key] and value != self.map[key][field]:
                items = self.map_ts[key].items()
                for k, v in items:
                    if k.split(',') == field:
                        del self.map_ts[key][k]
                        self.map_ts[key][field + ',' + value] = 'INF' 
            elif field not in self.map[key]:
                self.map_ts[key][field + ',' + value] = 'INF'

            self.map[key][field] = value
        return ''
    
    def set_at_with_ttl(self, key, field, value, ts, ttl):
        self.ts = ts
        if key not in self.map:
            self.map[key] = {field : value}
            self.map_ts[key] = {field + ',' + value : int(ts) + int(ttl)}
            return ''
        
        if field in self.map[key] and value != self.map[key][field]:
            items = self.map_ts[key].items()
            for k, v in items:
                if k.split(',') == field:
                    del self.map_ts[key][k]
                    self.map_ts[key][field + ',' + value] = int(ts) + int(ttl)
        elif field not in self.map[key]:
            self.map_ts[key][field + ',' + value] = int(ts) + int(ttl)

        self.map[key][field] = value
        # always update because ttl can change and we can't track ttl exactly here 
        self.map_ts[key][field + ',' + value] = int(ts) + int(ttl)
        
        return ''    
    
    def get(self,key, field):
        if key not in self.map or field not in self.map[key]:
            return ''
        return self.map[key][field]
    
    def get_at(self, key, field, ts):
        self.ts = ts
        if key not in self.map or field not in self.map[key]:
            return ''
        # check ttl
        val = self.map[key][field]
        expire_ts = self.map_ts[key][field + ',' + val]
        if expire_ts == 'INF':
            return self.map[key][field]
        if expire_ts <= int(ts):
            return ''
        return self.map[key][field]

    def delete(self,key, field):
        if key not in self.map or field not in self.map[key]:
            return 'false'
        del self.map[key][field]
        return 'true'
    
    def delete_at(self, key, field, ts):
        self.ts = ts
        if key not in self.map or field not in self.map[key]:
            return 'false'
        val = self.map[key][field]
        search = field + ',' + val
        if self.map_ts[key][search] <= int(ts):
            # since already expired due to timestamp
            del self.map_ts[key][search]
            del self.map[key][field]
            return 'false'
        
        del self.map_ts[key][search]
        del self.map[key][field]
        return 'true'

    def scan(self, key):
        if key not in self.map:
            return ''
        arr = []
        nested_map = self.map[key]
        for field in sorted(nested_map):
            temp = field + '(' + nested_map[field] + ')'
            arr.append(temp)
        return ', '.join(arr)
    
    def scan_at(self, key, ts):
        self.ts = ts
        if key not in self.map:
            return ''
        nested_map = self.map[key]
        items = nested_map.items()
        # cleanup first
        map_ts_delete = []
        map_delete = []
        for k, v in items:
            search  = k + ',' + v
            if self.map_ts[key][search] <= int(ts):
                map_ts_delete.append(search)
                map_delete.append(k)
        for map_ts_key in map_ts_delete:
            del self.map_ts[key][map_ts_key]
        for field in map_delete:
            del self.map[key][field]

        items = sorted(nested_map.items())
        arr = []
        for k, v in items:
            arr.append(k + '(' + v + ')')
        if len(arr) == 0:
            return ''
        return ', '.join(arr)

    def scan_by_prefix(self, key, prefix):
        if key not in self.map:
            return ''
        fields = self.map[key].items()
        arr = []
        for k, v in fields:
            if k.startswith(prefix):
                arr.append(k)
        if len(arr) == 0:
            return ''
        # sort fields lexico
        arr.sort()
        res = []
        for field in arr:
            temp = field + '('+ self.map[key][field] + ')'
            res.append(temp)
        return ', '.join(res)
    
    def scan_by_prefix_at(self, key, prefix, ts):
        self.ts = ts
        if key not in self.map:
            return ''
        nested_map = self.map[key]
        items = nested_map.items()
        # cleanup first
        map_ts_delete = []
        map_delete = []
        for k, v in items:
            search  = k + ',' + v
            if self.map_ts[key][search] <= int(ts):
                map_ts_delete.append(search)
                map_delete.append(k)
        for map_ts_key in map_ts_delete:
            del self.map_ts[key][map_ts_key]
        for field in map_delete:
            del self.map[key][field]

        return self.scan_by_prefix(key, prefix)
    

    def backup(self, ts):
        # cleanup first
        map_ts_delete = []
        map_delete = []
        for key in self.map_ts:
            items = self.map_ts[key].items()
            for field_val, expire_time in items:
                field = field_val.split(',')[0]
                if expire_time <= int(ts):
                    map_ts_delete.append(field_val)
                    map_delete.append(field)

        for map_ts_key in map_ts_delete:
            del self.map_ts[key][map_ts_key]
        for field in map_delete:
            del self.map[key][field]       


        # deep copy
        self.backup_map[ts] = copy.deepcopy(self.map)
        self.backup_map_ts[ts] = copy.deepcopy(self.map_ts)
        # set timestamp
        self.ts = ts

        cnt = 0
        for key in self.map:
            cnt += len(self.map[key])
        return str(cnt)
    
    def restore(self, ts, ts_to_restore):
        self.ts = ts
        ts_val = '-1'
        for i in range(int(ts_to_restore), -1, -1):
            if str(i) in self.backup_map:
                ts_val = str(i)
                break

        self.map = copy.deepcopy(self.backup_map[ts_val])
        self.map_ts = copy.deepcopy(self.backup_map_ts[ts_val])
        return ''