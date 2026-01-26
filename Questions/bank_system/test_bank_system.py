import pytest
import sys
import os
from simulation import Simulation 
class TestLevel1:  
    def test_create_account(self):
        simulation = Simulation()
        assert simulation.create_account(1, "acc1") == True
        assert simulation.create_account(2, "acc1") == False
        assert simulation.create_account(3, "acc2") == True

    def test_deposit(self):
        simulation = Simulation()
        simulation.create_account(1, "acc1")
        assert simulation.deposit(2, "acc1", 500) == 500
        assert simulation.deposit(3, "acc1", 300) == 800
        assert simulation.deposit(4, "non_existent", 100) == None

    def test_transfer(self):
        simulation = Simulation()
        assert simulation.create_account(1, "acc1") == True
        assert simulation.create_account(2, "acc2") == True
        assert simulation.deposit(3, "acc1", 1000) == 1000
        assert simulation.transfer(4, "acc1", "acc2", 300) == 700
        # Insufficient funds
        assert simulation.transfer(5, "acc1", "acc2", 800) == None 
        # Non-existent account
        assert simulation.transfer(6, "acc1", "non_existent", 100) == None
        # Transfer to self
        assert simulation.transfer(7, "acc1", "acc1", 100) == None

    def test_1(self):
        simulation = Simulation()
        assert simulation.create_account(1, "account1") == True
        assert simulation.create_account(2, "account1") == False
        assert simulation.create_account(3, "account2") == True
        assert simulation.deposit(4, "non_existent", 100) == None
        assert simulation.deposit(5, "account1", 2700) == 2700
        assert simulation.transfer(6, "account1", "account2", 2701) == None
        assert simulation.transfer(7, "account1", "account2", 200) == 2500
    
    def test_2(self):
        simulation = Simulation()
        assert simulation.create_account(1, "A") == True
        assert simulation.create_account(2, "B") == True
        assert simulation.deposit(3, "A", 500) == 500
        assert simulation.transfer(4, "A", "B", 300) == 200
        assert simulation.deposit(5, "B", 200) == 500
        assert simulation.transfer(6, "B", "A", 600) == None
        assert simulation.transfer(7, "B", "A", 400) == 100

    def test_3(self):
        simulation = Simulation()
        assert simulation.create_account(1, "X") == True
        assert simulation.deposit(2, "X", 1000) == 1000
        assert simulation.create_account(3, "Y") == True
        assert simulation.transfer(4, "X", "Y", 500) == 500
        assert simulation.transfer(5, "Y", "X", 600) == None
        assert simulation.deposit(6, "Y", 300) == 800
        assert simulation.transfer(7, "Y", "X", 400) == 400

class TestLevel2:
    def test_top_spenders_empty(self):
        simulation = Simulation()
        top_0 = simulation.top_spenders(1, 0)
        assert top_0 == []
        top_5 = simulation.top_spenders(2, 5)
        assert top_5 == []
    
    def test_top_spenders_single_account_less_than_n(self):
        simulation = Simulation()
        simulation.create_account(1, "acc1")
        simulation.deposit(2, "acc1", 1000)
        simulation.create_account(3, "acc2")
        simulation.transfer(4, "acc1", "acc2", 500)
        top_1 = simulation.top_spenders(3, 1)
        assert top_1 == ["acc1(500)"]

    def test_top_spenders_tie(self):
        simulation = Simulation()
        simulation.create_account(1, "acc1")
        simulation.create_account(2, "acc2")
        simulation.create_account(3, "acc3")
        simulation.deposit(4, "acc1", 1000)
        simulation.deposit(5, "acc2", 1500)
        simulation.deposit(6, "acc3", 1200)
        simulation.transfer(8, "acc2", "acc3", 500)  # acc2 outgoing: 500
        simulation.transfer(7, "acc1", "acc2", 500)  # acc1 outgoing: 500
        simulation.transfer(9, "acc3", "acc1", 300)  # acc3 outgoing: 300
        top_2 = simulation.top_spenders(10, 3)
        assert top_2 == ["acc1(500)", "acc2(500)", "acc3(300)"]
        
class TestLevel3:
    def test_3(self):
        print("!")

class TestLevel4:
    def test_4(self):
        print("Goodbye")

# pytest Questions/bank_system/test_bank_system.py::TestLevel1 -v


