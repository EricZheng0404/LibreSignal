import pytest
from simulation_solution import InMemoryDatabase
# Uncomment the following line to import your implementation of the InMemoryDatabase class:
# from simulation import Simulation

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
        assert db.set("user1", "name", "Alice") == ""
        assert db.set("user1", "age", "30") == ""
        assert db.set("user1", "city", "NY") == ""
        assert db.set("user1", "abc", "123") == ""
        assert db.scan("user1") == "abc(123), age(30), city(NY), name(Alice)"
        assert db.scan("non_existent") == ""

    def test_scan_by_prefix(self):
        db = InMemoryDatabase()
        assert db.set("user1", "name", "Alice") == ""
        assert db.set("user1", "age", "30") == ""
        assert db.set("user1", "city", "NY") == ""
        assert db.set("user1", "abc", "123") == ""
        assert db.scan_by_prefix("user1", "a") == "abc(123), age(30)"
        assert db.scan_by_prefix("user1", "n") == "name(Alice)"
        assert db.scan_by_prefix("user1", "xyz") == ""

class TestLevel3:
    # set_at and get_at are tested together since they are closely related. 
    # The same goes for set_at_with_ttl and get_at.
    def test_set_at_and_get_at(self):
        db = InMemoryDatabase()
        assert db.set_at("user1", "name", "Alice", timestamp=100) == ""
        assert db.set_at("user1", "age", "30", timestamp=101) == ""
        assert db.get_at("user1", "name", timestamp=102) == "Alice"
        assert db.get_at("user1", "age", timestamp=103) == "30"

    def test_get_at_non_existent(self):
        db = InMemoryDatabase()
        assert db.get_at("user2", "name", timestamp=100) == ""
        # Test that get_at returns empty string for non-existent field
        assert db.get_at("user1", "non_existent", timestamp=101) == ""

    def test_set_at_with_ttl_and_get_at(self):
        db = InMemoryDatabase()
        # The field is available between [100, 110)
        assert db.set_at_with_ttl("user1", "name", "Alice", timestamp=100, ttl=10) == ""
        # At timestamp 105, the field should still be available
        assert db.get_at("user1", "name", timestamp=105) == "Alice"
        # At timestamp 110, the field should have expired
        assert db.get_at("user1", "name", timestamp=110) == ""
        # At timestamp 115, the field should still be expired
        assert db.get_at("user1", "name", timestamp=115) == ""

    # Test that set_at_with_ttl can overwrite an existing field and reset the 
    # expiry time
    def test_set_at_with_ttl_overwrite_without_expiry(self):
        db = InMemoryDatabase()
        # Set a field with TTL
        assert db.set_at_with_ttl("user1", "name", "Alice", 
                                  timestamp=100, ttl=10) == ""
        # Overwrite the same field without TTL
        assert db.set_at("user1", "name", "Bob", timestamp=105) == ""
        # The field should now return the new value and will not expire
        assert db.get_at("user1", "name", timestamp=110) == "Bob"
        assert db.get_at("user1", "name", timestamp=140) == "Bob"

    def test_set_at_with_ttl_overwrite_with_expiry(self):
        db = InMemoryDatabase()
        # Set a field with TTL
        assert db.set_at_with_ttl("user1", "name", "Alice", timestamp=100, ttl=10) == ""
        # At timestamp 105, the field should still be available
        assert db.get_at("user1", "name", timestamp=105) == "Alice"
        # Overwrite the same field with a new TTL: [106, 116)
        assert db.set_at_with_ttl("user1", "name", "Bob", timestamp=106, ttl=10) == ""
        # The field should now return the new value and expire at timestamp 116
        assert db.get_at("user1", "name", timestamp=110) == "Bob"
        assert db.get_at("user1", "name", timestamp=117) == ""

    def test_set_at_with_ttl_and_get_all(self):
        db = InMemoryDatabase()
        # Field name "name" is available between [100, 110)
        assert db.set_at_with_ttl("user1", "name", "Alice", timestamp=100, ttl=10) == ""
        # Field name "age" is available between [101, 106)
        assert db.set_at_with_ttl("user1", "age", "30", timestamp=101, ttl=5) == ""
        # Field name "city" is available between [102, 117)
        assert db.set_at_with_ttl("user1", "city", "NY", timestamp=102, ttl=15) == ""
        # All fields should be available at anytime
        assert db.get("user1", "name") == "Alice"
        assert db.get("user1", "age") == "30"
        assert db.get("user1", "city") == "NY"

    def test_scan_at(self):
        db = InMemoryDatabase()
        # Field name "name" is available between [100, 110)
        assert db.set_at_with_ttl("user1", "name", "Alice", timestamp=100, ttl=10) == ""
        # Field name "age" is available between [101, 106)
        assert db.set_at_with_ttl("user1", "age", "30", timestamp=101, ttl=5) == ""
        # Field name "city" is available between [102, 117)
        assert db.set_at_with_ttl("user1", "city", "NY", timestamp=102, ttl=15) == ""
        # At timestamp 105, all fields should be available
        assert db.scan_at("user1", timestamp=105) == "age(30), city(NY), name(Alice)"
        # At timestamp 106, only "age" should have expired
        assert db.scan_at("user1", timestamp=106) == "city(NY), name(Alice)"
        # At timestamp 110, only "name" should have expired
        assert db.scan_at("user1", timestamp=110) == "city(NY)"
        # At timestamp 116, still only "city" should be available
        assert db.scan_at("user1", timestamp=116) == "city(NY)"
        # At timestamp 117, all fields should have expired
        assert db.scan_at("user1", timestamp=117) == ""
    
    # scan() doesn't consider expiry time, so it should return all fields 
    # regardless of the timestamp
    def test_scan(self):
        db = InMemoryDatabase()
        # Field name "name" is available between [100, 110)
        assert db.set_at_with_ttl("user1", "name", "Alice", timestamp=100, ttl=10) == ""
        # Field name "age" is available between [101, 106)
        assert db.set_at_with_ttl("user1", "age", "30", timestamp=101, ttl=5) == ""
        # Field name "city" is available between [102, 117)
        assert db.set_at_with_ttl("user1", "city", "NY", timestamp=102, ttl=15) == ""
        # scan should return all fields regardless of expiry time
        assert db.scan("user1") == "age(30), city(NY), name(Alice)"

    def test_scan_by_prefix_at(self):
        db = InMemoryDatabase()
        # Field name "name" is available between [100, 110)
        assert db.set_at_with_ttl("user1", "name", "Alice", timestamp=100, ttl=10) == ""
        # Field name "age" is available between [101, 106)
        assert db.set_at_with_ttl("user1", "age", "30", timestamp=101, ttl=5) == ""
        # Field name "city" is available between [102, 117)
        assert db.set_at_with_ttl("user1", "city", "NY", timestamp=102, ttl=15) == ""
        # Field name "nationality" is available between [103, 108)
        assert db.set_at_with_ttl("user1", "nationality", "free_country", timestamp=103, ttl=5) == ""
        # At timestamp 105, both "age" and "name" should be returned
        assert db.scan_by_prefix_at("user1", prefix="a", timestamp=105) == "age(30)"
        # At timestamp 106, "age" should have expired, so it should return empty string
        assert db.scan_by_prefix_at("user1", prefix="a", timestamp=106) == ""
        # At timestamp 107, both "name" and "nationality" should be returned
        assert db.scan_by_prefix_at("user1", prefix="n", timestamp=107) == "name(Alice), nationality(free_country)"
        # At timestamp 109, "nationality" should have expired, so it should only return "name"
        assert db.scan_by_prefix_at("user1", prefix="n", timestamp=109) == "name(Alice)"

    # scan_by_prefix() doesn't consider expiry time, so it should return all fields with the given prefix regardless of the timestamp
    def test_scan_by_prefix(self):
        db = InMemoryDatabase()
        # Field name "name" is available between [100, 110)
        assert db.set_at_with_ttl("user1", "name", "Alice", timestamp=100, ttl=10) == ""
        # Field name "age" is available between [101, 106)
        assert db.set_at_with_ttl("user1", "age", "30", timestamp=101, ttl=5) == ""
        # Field name "city" is available between [102, 117)
        assert db.set_at_with_ttl("user1", "city", "NY", timestamp=102, ttl=15) == ""
        # Field name "nationality" is available between [103, 108)
        assert db.set_at_with_ttl("user1", "nationality", "free_country", timestamp=103, ttl=5) == ""
        # All field should be still be returned by scan_by_prefix regardless of expiry time
        assert db.scan_by_prefix("user1", prefix="a") == "age(30)"
        assert db.scan_by_prefix("user1", prefix="n") == "name(Alice), nationality(free_country)"
        
        """
        user1: name: Alice [100, 110)
                age: 30 [101, 106)
                city: NY [102, 117)
                nationality: free_country [103, 108)


        """
    
class TestLevel4:
    pass