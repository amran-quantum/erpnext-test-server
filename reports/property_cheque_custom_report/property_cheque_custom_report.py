# Copyright (c) 2013, HCG and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import datetime

def execute(filters=None):
	columns, data = [], []
	
	columns = get_columns()
	data = get_data()
	return columns, data
def get_columns():
	return ["Customer Name","Expiry Date","Cheque Number", "Bank Name", "Numbers of Cheque","Withdraw Status"]


def get_data():

	to_date = datetime.date.today()
	from_date = datetime.date(to_date.year, to_date.month, 1)

	return frappe.db.sql("""SELECT customer_name, expiry_date, cheque_number, bank_name, numbers_of_cheque, withdraw_status FROM
	 `tabProperty Cheque` 
	 where withdraw_status=%(status)s and expiry_date  between %(from_date)s and %(to_date)s
	 """,
	 {"from_date":from_date,"to_date":to_date,"status":"Pending"}
	 )
