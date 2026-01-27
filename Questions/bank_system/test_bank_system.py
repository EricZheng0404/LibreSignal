"""
Testing suite for the Bank System simulation.
============================================================
This suite uses pytest to validate the functionality of the bank system 
simulation.

Author: Eric Zheng
Date: Jan 2026
"""
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
    def test_pay_no_account_id(self):
        simulation = Simulation()
        assert simulation.pay(1, "non_existent", 100) == None
        assert simulation.get_payment_status(2, "non_existent", "payment1") == None

    def test_pay_insufficient_funds(self):
        simulation = Simulation()
        simulation.create_account(1, "acc1")
        simulation.deposit(2, "acc1", 100)
        assert simulation.pay(3, "acc1", 200) == None

    def test_pay_top_spenders(self):
        simulation = Simulation()
        simulation.create_account(1, "acc1")
        simulation.deposit(2, "acc1", 1000)
        payment_id1 = simulation.pay(3, "acc1", 500)
        assert payment_id1 == "payment1"
        payment_id2 = simulation.pay(4, "acc1", 300)
        assert payment_id2 == "payment2"
        simulation.create_account(5, "acc2")
        simulation.deposit(6, "acc2", 800)
        simulation.transfer(7, "acc2", "acc1", 200)
        top_1 = simulation.top_spenders(5, 2)
        assert top_1 == ["acc1(800)", "acc2(200)"]

    def test_payment_status_non_existent_account(self):
        simulation = Simulation()
        assert simulation.get_payment_status(1, "non_existent", "payment1") == None

    def test_payment_status_non_existent_payment(self):
        simulation = Simulation()
        simulation.create_account(1, "acc1")
        assert simulation.get_payment_status(2, "acc1", "payment1") == None

    def test_payment_status_inconsistent_accountid_and_paymentid(self):
        simulation = Simulation()
        simulation.create_account(1, "acc1")
        simulation.deposit(2, "acc1", 1000)
        payment_id = simulation.pay(3, "acc1", 500)
        assert payment_id == "payment1"
        # Create a different account
        simulation.create_account(4, "acc2")
        # Querying payment status with wrong account_id
        assert simulation.get_payment_status(4, "acc2", payment_id) == None 

    def test_pay_cashback_and_status(self):
        simulation = Simulation()
        simulation.create_account(1, "acc1")
        simulation.deposit(2, "acc1", 1000)
        payment_id = simulation.pay(3, "acc1", 500)
        assert payment_id == "payment1"
        # Before cashback time
        status_in_progress = simulation.get_payment_status(4, "acc1", 
                                                           payment_id)
        assert status_in_progress == "IN_PROGRESS"
        status_before_cashback = simulation.get_payment_status(26*3600, 
                                                               "acc1", 
                                                               payment_id)
        # After cashback time (Exactly 24 hours after the payment)
        status_after_cashback = simulation.get_payment_status(24 * 60 * 60 * 1000 + 3, 
                                                              "acc1", 
                                                              payment_id)
        assert status_after_cashback == "CASHBACK_RECEIVED"
        # Check balance after cashback
        final_balance = simulation.deposit(28*3600, "acc1", 0)  # deposit 0 to get current balance
        assert final_balance == 1000 - 500 + 10  # 2% of 500 is 10

class TestLevel4:
    def test_account_id_1_not_exist(self):
        simulation = Simulation()
        simulation.create_account(1, "acc2")
        assert simulation.merge_accounts(2, "acc1", "acc2") == False

    def test_account_id_2_not_exist(self):
        simulation = Simulation()
        simulation.create_account(1, "acc1")
        assert simulation.merge_accounts(2, "acc1", "acc2") == False

    def test_merge_cashback(self):
        simulation = Simulation()
        simulation.create_account(1, "acc1")
        simulation.deposit(2, "acc1", 1000)
        payment_id = simulation.pay(3, "acc1", 500) 
        assert payment_id is not None
        simulation.create_account(4, "acc2")
        simulation.merge_accounts(5, "acc2", "acc1")
        status_acc2 = simulation.get_payment_status(6, "acc2", payment_id)
        assert status_acc2 == "IN_PROGRESS"
        status_after_cashback = simulation.get_payment_status(24 * 60 * 60 * 1000 + 3, 
                                                              "acc2",
                                                                payment_id)
        assert status_after_cashback == "CASHBACK_RECEIVED"
        assert simulation.deposit(24 * 60 * 60 * 1000 + 5, "acc2", 0) == 510

    def test_merge_top_spender(self):
        simulation = Simulation()
        simulation.create_account(1, "acc1")
        simulation.deposit(2, "acc1", 1000)
        simulation.pay(3, "acc1", 500) 
        simulation.create_account(4, "acc2")
        simulation.deposit(5, "acc2", 2000)
        simulation.pay(6, "acc2", 800) 
        simulation.merge_accounts(7, "acc1", "acc2")
        top_1 = simulation.top_spenders(8, 1)
        assert top_1 == ["acc1(1300)"]  # acc1 now has acc2's outgoing too

    def test_cashback(self):
        simulation = Simulation()
        simulation.create_account(1, "acc1")
        simulation.deposit(2, "acc1", 1000)
        simulation.pay(3, "acc1", 300)
        assert simulation.get_balance(4, "acc1", 3) == 700
        assert simulation.get_balance(24 * 60 * 60 * 1000 + 5, 
                                      "acc1", 
                                      24 * 60 * 60 * 1000 + 2) == 700
        assert simulation.get_balance(24 * 60 * 60 * 1000 + 5, 
                                      "acc1", 
                                      24 * 60 * 60 * 1000 + 3) == 706



