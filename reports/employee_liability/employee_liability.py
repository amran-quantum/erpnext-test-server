# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from datetime import date
from datetime import datetime
import calendar
from frappe import _


from frappe.utils.data import flt

def execute(filters=None):
	columns, data = [], []
	columns = get_columns()
	tdata = get_emp_list(filters)
	row = []

	for item in tdata:
		item_break = item[6]
		sub_item = item_break[1:-1]
		split_sub_item = sub_item.split(', {')
		for elem in split_sub_item:
			if elem.count('{')==0:
				sse = elem[:-1].split(',')
				sc = sse[1].split(':')[1][1:-1]
				if row.count(sc[:-1]) == 0 and sc[:-1] == 'Basic' :
					row.append(sc[:-1])
			else:
				esse = elem[1:-1].split(',')
				sc = esse[1].split(':')[1][1:-1]
				if row.count(sc[:-1]) == 0 and sc[:-1] == 'Basic':
					row.append(sc[:-1])
			
	for item in tdata:
		# leave encashment
		leave_encashment = 0
		yfd = datetime.now().date().replace(month=1, day=1)
		yld = datetime.now().date().replace(month=12, day=31)
		encashed_leave_type = frappe.get_list('Leave Type',filters={"leave_type_name":['like', '%Annual%']},pluck="leave_type_name")
		lv_al = frappe.get_list('Leave Allocation', 
		filters={"employee":item[1],"leave_type": ('in',tuple(encashed_leave_type))},
		fields={"total_leaves_allocated"})
		tot_leave = 0
		for elem in lv_al:
			tot_leave += elem.total_leaves_allocated
		
		lv_app = frappe.get_list('Leave Application', 
		filters={"employee":item[1],"status":"Approved",
		"leave_type": ('in',tuple(encashed_leave_type))},
		fields={"total_leave_days"})

		# current_year_leave_app = cyla
		cyla = frappe.get_list('Leave Application', 
		filters={"employee":item[1],"status":"Approved",
		"leave_type": ('in',tuple(encashed_leave_type)),
		#  "from_date":['>=',yfd],    
		#   "to_date": ['<=',yld]
		}, 
		fields={"total_leave_days"})
		cyla_total = 0
		for e in cyla:
			cyla_total = cyla_total + e.total_leave_days

		#  current_year_leave_app_till_today = cylatt
		cylatt = frappe.get_list('Leave Application', 
		filters={"employee":item[1],"status":"Approved",
		"leave_type": ('in',tuple(encashed_leave_type)),
		"to_date": ['<=',filters.ending_date]}, 
		fields={"total_leave_days"})

		cylatt_total = 0
		for e in cylatt:
			cylatt_total = cylatt_total + e.total_leave_days
			
		# current year leave app extra = cylax
		cylax = cyla_total - cylatt_total

		tot_taken_leave = 0
		for el in lv_app:
			tot_taken_leave += el.total_leave_days
		
        #leave encashment ends

		grand_total = 0
		item_break = item[6]
		sub_item = item_break[1:-1]
		split_sub_item = sub_item.split(', {')
		col = []
		for el in row:
			col.append({'amount':0,'sc':el})

		first_date = str(yfd).split('-')
		first_date_number = date(int(first_date[0]),int(first_date[1]),int(first_date[2]))

		today = date.today()
		tdate = str(item[4]).split('-')
		a = date(int(today.strftime("%Y")),int(today.strftime("%m")),int(today.strftime("%d")))
		b = date(int(tdate[0]),int(tdate[1]),int(tdate[2]))

		days = (a-b).days - cylax
		dffd_days = (first_date_number-b).days

		# check joining date is less than current year 1st date
		# if yes total days for leve encashment is total days from 1st day of this year
		# if not total days for leave encashment = today - joining

		if dffd_days > 0: 
			tot_days = (a - first_date_number).days
		else: 
			tot_days = days

		grat = 0
		one_day_amount = 0
		for elem in split_sub_item:
			if elem.count('{')==0:
				csse = elem[:-1].split(',')
				amount = csse[0].split(':')[1]
				one_day_amount = flt(amount) / 30
				sc = csse[1].split(':')[1][1:-1]
				if sc[:-1] == 'Basic':
					index = in_dictlist('sc',sc[:-1], col)
					if days/365 > 1 or days/365 == 1:
						grat = flt((one_day_amount)*21 * (days/365),2)
					col[index].update({'amount':amount})
			else:
				esse = elem[1:-1].split(',')
				amount = esse[0].split(':')[1]
				one_day_amount = flt(amount) / 30
				sc = esse[1].split(':')[1][1:-1]
				if sc[:-1] == 'Basic':
					index = in_dictlist('sc',sc[:-1], col)
					if days/365 > 1 or days/365 == 1:
						grat = flt((one_day_amount)*21 * (days/365),2)
					col[index].update({'amount':amount})
		
			
		for idx,value in enumerate(row):
			item.append(flt(col[idx]['amount']))
		item.append(flt(grat,0))
		item.append(days)
		# item.append(flt(days/365,2))
		department_list = frappe.get_list('Department',filters={"department_name":item[5]},fields={"department_name","department_policy"})
		if len(department_list)>0:
			dp_check = frappe.get_list('Department Policy',filters={"name": department_list[0].department_policy},fields={"air_ticket_initial"})
			dp_year = 0
			t_quantity = 0
			te_amount = 0
			if len(dp_check)>0:
				dp_year = int(dp_check[0].air_ticket_initial.split(' ')[1])
			
				if days/365 > dp_year or days/365 == dp_year:
					te = frappe.get_list('Employee Air Ticket',filters={"employee":item[1]},fields={"amount"})
					if len(te)>0:
						t_quantity = len(te)
						for el in te:
							te_amount += int(el.amount)
				item.append(te_amount)
				item.append(t_quantity)
			else: 
				item.append(0)
				item.append(0)
		else: 
			item.append(0)
			item.append(0)

		leave_encashment = ((tot_leave/365)*tot_days) - tot_taken_leave - cylax
		item.append(flt(leave_encashment,0))
		item.append(flt((leave_encashment*one_day_amount),0))
		grand_total = grat + te_amount + (leave_encashment*one_day_amount)
		item.append(flt(grand_total,0))
		item.pop(6)

	row.append("Gratuity")
	row.append("Work Duration(Days)")
	row.append("Ticket(amount)")
	row.append("Ticket(quantity)")
	row.append("Leave Encashment(days)")
	row.append("Leave Encashment(amount)")
	row.append("Total")
	columns += row

	
	data = tdata


	return columns, data

def in_dictlist(key, value, my_dictlist):
    for index,entry in enumerate(my_dictlist):
        if entry[key] == value:
            return index
    return {}

def get_columns():
	
	columns = ["Department Code",_("Employee")+":Link/Employee:140","Employee Name","Salary Structure","Date of Joining","Department"]
	
	return columns


@frappe.whitelist()
def get_joining_relieving_condition(start_date,end_date):
	cond = """
		and ifnull(t1.date_of_joining, '0000-00-00') <= '%(end_date)s'
		and ifnull(t1.relieving_date, '2199-12-31') >= '%(start_date)s'
	""" % {"start_date": start_date, "end_date": end_date}
	return cond


@frappe.whitelist()
def get_emp_list(filters):
	"""
		Returns list of active employees based on selected criteria
		and for which salary structure exists
	"""
	today = date.today()
	f = calendar.monthrange(int(today.strftime("%Y")), int(today.strftime("%m")))
	start_date = today.strftime("%Y-%m-")+ str(f[0])
	end_date = today.strftime("%Y-%m-")+ str(f[1])
	cond = get_joining_relieving_condition(start_date,end_date)

	condition = ''
	condition = """and payroll_frequency = '%(payroll_frequency)s'"""% {"payroll_frequency": "Monthly"}
	sal_struct = frappe.db.sql_list("""
			select
				name from `tabSalary Structure`
			where
				docstatus = 1 and
				is_active = 'Yes'
				and company = %(company)s
				and currency = %(currency)s and
				ifnull(salary_slip_based_on_timesheet,0) = %(salary_slip_based_on_timesheet)s
				{condition}""".format(condition=condition),
			{"company": "Human Capital Group", "currency": "QAR", "salary_slip_based_on_timesheet":0})
	if sal_struct:
		cond += "and t2.salary_structure IN %(sal_struct)s "
		cond += "and t2.payroll_payable_account = %(payroll_payable_account)s "
		cond += "and %(from_date)s >= t2.from_date"
		emp_list = frappe.db.sql("""
			select
				distinct t1.department_code, t1.department, t1.name as employee, t1.employee_name, t2.salary_structure, sd.parent, sd.sales,
				t1.date_of_joining, t1.status
			from
				`tabEmployee` t1, `tabSalary Structure Assignment` t2
			LEFT JOIN 
			( SELECT parent, CONCAT( 
			'[', 
			GROUP_CONCAT( CONCAT( '{ "amount":', amount, ', "salary_component":"', salary_component, '" }' ) SEPARATOR ', '),
			']' ) sales  FROM `tabSalary Detail` GROUP BY parent ) sd ON sd.parent = t2.salary_structure
			where
				t1.name = t2.employee
				and t2.docstatus = 1
				and t1.status = "Active"
		%s order by t1.department_code asc, t2.from_date desc
		""" % cond, {"sal_struct": tuple(sal_struct), "from_date": filters.ending_date, "payroll_payable_account": "Payroll Payable - HCG"}, as_dict=True)
		rdata = []
		names = ""
		
		for item in emp_list:
			if item.employee not in names:
				names += item.employee
				dep = item.department.split('-')[0]
				rdata.append([item.department_code, item.employee, item.employee_name, item.salary_structure, item.date_of_joining, dep, item.sales])
		return rdata