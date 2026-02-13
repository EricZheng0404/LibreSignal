import pytest
from simulation_solution import InMemoryDatabase
from simulation import Simulation
class TestLevel1:
    def test_set_and_get(self):
        db = InMemoryDatabase()
        assert db.set("user1", "name", "Alice") == ""
        assert db.set("user1", "age", "30") == ""
        assert db.get("user1", "name") == "Alice"
        assert db.get("user1", "age") == "30"

    def test_set_overwrite(self):
        db = InMemoryDatabase()
        assert db.set("user1", "name", "Alice") == ""
        assert db.set("user1", "name", "Bob") == ""
        assert db.get("user1", "name") == "Bob"

    def test_get_non_existent(self):
        db = InMemoryDatabase()
        assert db.get("user1", "field") == ""
        assert db.set("user1", "name", "Alice") == ""
        assert db.get("user1", "non_existent") == ""

    def test_delete(self):
        db = InMemoryDatabase()
        assert db.set("user1", "name", "Alice") == ""
        assert db.delete("user1", "name") == "true"
        assert db.get("user1", "name") == ""
        assert db.delete("user1", "name") == "false"
        assert db.delete("non_existent", "field") == "false"

class TestLevel2:
    def test_scan(self):
        db = InMemoryDatabase()
        assert db.set('A', 'BC', 'E') == ''
        assert db.set('A', 'BD', 'F') == ''
        assert db.set('A', 'C', 'G') == ''
        assert db.scan('A') == 'BC(E), BD(F), C(G)'
        assert db.scan('B') == ''
    
    def test_scan_by_prefix(self):
        db = InMemoryDatabase()
        assert db.set('A', 'BC', 'E') == ''
        assert db.set('A', 'BD', 'F') == ''
        assert db.set('A', 'C', 'G') == ''
        assert db.scan_by_prefix('A', 'B') == 'BC(E), BD(F)'
        assert db.scan_by_prefix('B', 'B') == ''
        assert db.scan_by_prefix('A', 'D') == ''
        assert db.scan_by_prefix('A', 'C') == 'C(G)'

class TestLevel3:
    def test_no_timestamp_get_at(self):
        db = InMemoryDatabase()
        assert db.set_at('A', 'BC', 'D', '1') == ''
        assert db.set_at('A', 'EF', 'G', '2') == ''
        assert db.get_at('A', 'BC', '15') == 'D'
        assert db.get_at('B', "BC", '17') == ''
        assert db.get_at('A', 'EF', '10000') == 'G'

    def test_yes_timestamp_get_at(self):
        db = InMemoryDatabase()
        # expire at 16
        assert db.set_at_with_ttl('A', 'BC', 'D', '1', '15') == ''
        # expire at 22
        assert db.set_at_with_ttl('A', 'EF', 'G', '2', '20') == ''
        assert db.get_at('A', 'BC', '3') == 'D'
        assert db.get_at('B', 'BC', '4') == ''
        assert db.get_at('A', 'BC', '16') == ''
        assert db.get_at('A', 'EF', '20') == 'G'
        assert db.get_at('A', 'EF', '22') == ''
    
    def test_set_at_with_ttl_override(self):
        db = InMemoryDatabase()
        # expire at 16
        assert db.set_at_with_ttl('A', 'BC', 'D', '1', '15') == ''
        # expire at 22
        assert db.set_at_with_ttl('A', 'EF', 'G', '2', '20') == ''
        # expire at 18
        assert db.set_at_with_ttl('A', 'BC', 'D', '3', '15') == ''
        assert db.get_at('A', 'BC', '16') == 'D'
        # override value this time with ttl
        assert db.set_at_with_ttl('A', 'BC', 'CHG', '17', '23') == ''
        assert db.get_at('A', 'BC', '19') == 'CHG'

    def test_delete_at(self):
        db = InMemoryDatabase()
        # expire at 16
        assert db.set_at_with_ttl('A', 'BC', 'D', '1', '15') == ''
        # expire at 22
        assert db.set_at_with_ttl('A', 'EF', 'G', '2', '20') == ''
        # expire at 33
        assert db.set_at_with_ttl('A', 'BD', 'E', '3', '30') == ''
        assert db.delete_at('A', 'BC', '3') == 'true'
        assert db.delete_at('A', 'EF', '22') == 'false'
        assert db.delete_at('A', 'BD', '31') == 'true'
    
    def test_scan_at(self):
        db = InMemoryDatabase()
        # expire at 16
        assert db.set_at_with_ttl('A', 'BC', 'D', '1', '15') == ''
        # expire at 22
        assert db.set_at_with_ttl('A', 'EF', 'G', '2', '20') == ''
        assert db.scan_at('A', '3') == 'BC(D), EF(G)'
        assert db.scan_at('B', '4') == ''
        assert db.scan_at('A', '16') == 'EF(G)'
        assert db.scan_at('A', '22') == ''
    
    def test_scan_by_prefix_at(self):
        db = InMemoryDatabase()
        # expire at 16
        assert db.set_at_with_ttl('A', 'BC', 'D', '1', '15') == ''
        # expire at 22
        assert db.set_at_with_ttl('A', 'EF', 'G', '2', '20') == ''
        # expire at 33
        assert db.set_at_with_ttl('A', 'BD', 'E', '3', '30') == ''
        assert db.scan_at('A', '4') == 'BC(D), BD(E), EF(G)'
        assert db.scan_at('B', '5') == ''
        assert db.scan_by_prefix_at('A', 'B', '6') == 'BC(D), BD(E)'
        assert db.scan_by_prefix_at('A', 'E', '16') == 'EF(G)'
        assert db.scan_by_prefix_at('A', 'B', '17') == 'BD(E)'
        assert db.scan_by_prefix_at('A', 'C', '19') == ''
        assert db.scan_by_prefix_at('B', 'B', '21') == ''
        assert db.scan_by_prefix_at('A', 'E', '33') == ''

        


class Level4:
    pass