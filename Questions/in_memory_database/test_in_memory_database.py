import pytest
from simulation_solution import InMemoryDatabase
from simulation import Simulation
class Level1:
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

class Level2:
    pass

class Level3:
    pass

class Level4:
    pass