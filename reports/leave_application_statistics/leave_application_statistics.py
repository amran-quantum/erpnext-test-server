# Copyright (c) 2013, amran and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
	columns, data = [], []

	columns, leave_type_list = get_columns()
	data = get_data(filters,leave_type_list)
	return columns, data
def get_columns():
	leave_type_list_from_db1 = frappe.db.sql("""
	select distinct leave_type from `tabLeave Application` where leave_type like %(leave_type)s order by leave_type asc
	""",{"leave_type":"%Annual%"},as_dict=True)
	leave_type_list_from_db2 = frappe.db.sql("""
	select distinct leave_type from `tabLeave Application` where leave_type not like %(leave_type)s order by leave_type asc
	""",{"leave_type":"%Annual%"},as_dict=True)
	leave_type_list_from_db = leave_type_list_from_db1 + leave_type_list_from_db2

	leave_type_list = []
	count = 0
	for el in leave_type_list_from_db:
		if "Annual" in el.leave_type:
			el.leave_type = "Annual Leave"
			count = count + 1
			if count < 2:
				leave_type_list.append(el)
		else: leave_type_list.append(el)


	cols = ["Department Code",_("Employee")+":Link/Employee:140","Employee Name"]
	for el in leave_type_list:
		if "Annual" in el.leave_type:
			cols.append("Annual Leave Start")
			cols.append("Annual Leave End")
			cols.append("Annual Leave Total")
		else:
			cols.append(el.leave_type+" Start")
			cols.append(el.leave_type+" End")
			cols.append(el.leave_type+" Total")
			
	return cols,leave_type_list

def get_data(filters,leave_type_list):
	data = frappe.db.sql("""
	select e.department_code,la.employee, la.employee_name, la.leave_type, la.from_date, la.to_date, la.total_leave_days from `tabLeave Application` la, `tabEmployee` e where e.employee = la.employee and la.from_date >= %(from_date)s  and la.to_date <= %(to_date)s and la.status=%(status)s
	order by la.employee, la.leave_type asc""",{"from_date":filters.from_date,"to_date":filters.to_date,"status":"Approved"},as_dict=1)
	
	result = []
	for item in data:
		row = []
		row.append(item.department_code)
		row.append(item.employee)
		row.append(item.employee_name)

		for litem in leave_type_list:
			row.append("")
			row.append("")
			row.append("")
		for index,ritem in enumerate(leave_type_list):
			if "Annual" in ritem.leave_type and "Annual" in item.leave_type:
				row[3+ 3*index] = item.from_date
				row[4+ 3*index] = item.to_date
				row[5+ 3*index] = item.total_leave_days
			elif ritem.leave_type == item.leave_type:
				row[3+ 3*index] = item.from_date
				row[4+ 3*index] = item.to_date
				row[5+ 3*index] = item.total_leave_days
		result.append(row)
	
	# data arrangement from the top

	for i in range(len(leave_type_list)):
		for elem in range((len(result)-1),0,-1):
			if result[elem][0] == result[elem - 1][0] and elem != 0:
				for i in range(len(leave_type_list)):
					if result[elem][3+ 3*i] != "" and result[elem - 1][3+ 3*i ] == "":
						temp = result[elem][3+ 3*i]
						result[elem - 1][3+ 3*i] = temp
						result[elem][3+ 3*i] = ""
						temp2 = result[elem][4+ 3*i]
						result[elem - 1][4+ 3*i] = temp2
						result[elem][4+ 3*i] = ""
						temp3 = result[elem][5+ 3*i]
						result[elem - 1][5+ 3*i] = temp3
						result[elem][5+ 3*i] = ""
	

	# empty data elimination
	for elem in range((len(result)-1),0,-1):
		flag = 0
		if elem != 0:
			for i in range(len(leave_type_list)):
				if result[elem][3+ 3*i] != "":
					flag = flag + 1
		if flag == 0:
			result.pop(elem)
	
	# sort by department code
	result.sort(key=lambda y: y[0])

	# name correction
	for elem in range((len(result)-1),0,-1):
		if result[elem][1] == result[elem - 1][1] and elem != 0:
			result[elem][0] = ""
			result[elem][1] = ""
			result[elem][2] = ""
						
	return result