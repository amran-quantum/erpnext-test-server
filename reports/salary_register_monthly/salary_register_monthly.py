# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe, erpnext
from frappe.utils import flt
from frappe import _

def execute(filters=None):
	if not filters: filters = {}
	currency = None
	if filters.get('currency'):
		currency = filters.get('currency')
	company_currency = erpnext.get_company_currency(filters.get("company"))
	salary_slips = get_salary_slips(filters, company_currency)
	if not salary_slips: return [], []

	columns, earning_types, ded_types = get_columns(salary_slips)
	ss_earning_map = get_ss_earning_map(salary_slips, currency, company_currency)
	ss_ded_map = get_ss_ded_map(salary_slips,currency, company_currency)
	doj_map = get_employee_doj_map()
	department_code_map = get_employee_department_code()
	total_map = get_employee_total_salary()

	data = []
	for ss in salary_slips:
		row = [ss.employee, department_code_map.get(ss.employee), ss.employee_name, ss.leave_without_pay, ss.payment_days, total_map.get(ss.employee)]

		if ss.leave_without_pay is not None: columns[4] = columns[4].replace('-1','130')


		for e in earning_types:
			row.append(ss_earning_map.get(ss.name, {}).get(e))

		if currency == company_currency:
			row += [flt(ss.gross_pay) * flt(ss.exchange_rate)]
		else:
			row += [ss.gross_pay]

		for d in ded_types:
			row.append(ss_ded_map.get(ss.name, {}).get(d))

		row.append(ss.total_loan_repayment)

		if currency == company_currency:
			row += [flt(ss.total_deduction) * flt(ss.exchange_rate), flt(ss.net_pay) * flt(ss.exchange_rate)]
		else:
			row += [ss.total_deduction, ss.net_pay]
		row.append(currency or company_currency)
		data.append(row)

	return columns, data

def get_columns(salary_slips):
	"""
	columns = [
		_("Employee Code") + ":Link/Salary Slip:150",
		_("Employee") + ":Link/Employee:120",
		_("Employee Name") + "::140",
		_("Total Monthly Salary") + "::80",
		_("Branch") + ":Link/Branch:120",
		_("Department") + ":Link/Department:120",
		_("Designation") + ":Link/Designation:120",
		_("Company") + ":Link/Company:120",
		_("Start Date") + "::80",
		_("End Date") + "::80",
		_("Leave Without Pay") + ":Float:130",
		_("Payment Days") + ":Float:120",
		_("Currency") + ":Link/Currency:80"
	]
	"""
	columns = [
		_("Employee Code") + "::80",_("Department Code") + "::100",_("Employee Name") + ":Link/Employee:220",
		 _("Leave Without Pay") + ":Float:50", _("Payment Days") + ":Float:60", _("Total Monthly Salary") + ":Currency :100"
	]

	salary_components = {_("Earning"): [], _("Deduction"): []}

	for component in frappe.db.sql("""select distinct sd.salary_component, sc.type
		from `tabSalary Detail` sd, `tabSalary Component` sc
		where sc.name=sd.salary_component and sd.amount != 0 and sd.parent in (%s)""" %
		(', '.join(['%s']*len(salary_slips))), tuple([d.name for d in salary_slips]), as_dict=1):
		salary_components[_(component.type)].append(component.salary_component)

	columns = columns + [(e + ":Currency:100") for e in salary_components[_("Earning")]] + \
		[_("Gross Pay") + ":Currency:100"] + [(d + ":Currency:100") for d in salary_components[_("Deduction")]] + \
		[_("Loan Repayment") + ":Currency:100", _("Total Deduction") + ":Currency:100", _("Net Pay") + ":Currency:100"]

	return columns, salary_components[_("Earning")], salary_components[_("Deduction")]

def get_salary_slips(filters, company_currency):
	filters.update({"from_date": filters.get("from_date"), "to_date":filters.get("to_date")})
	conditions, filters = get_conditions(filters, company_currency)
	salary_slips = frappe.db.sql("""select * from `tabSalary Slip` where %s
		order by employee""" % conditions, filters, as_dict=1)

	return salary_slips or []

def get_conditions(filters, company_currency):
	conditions = ""
	doc_status = {"Draft": 0, "Submitted": 1, "Cancelled": 2}

	if filters.get("docstatus"):
		conditions += "docstatus = {0}".format(doc_status[filters.get("docstatus")])

	if filters.get("from_date"): conditions += " and start_date >= %(from_date)s"
	if filters.get("to_date"): conditions += " and end_date <= %(to_date)s"
	if filters.get("company"): conditions += " and company = %(company)s"
	if filters.get("employee"): conditions += " and employee = %(employee)s"
	if filters.get("department"): conditions += " and department = %(department)s"
	if filters.get("currency") and filters.get("currency") != company_currency:
		conditions += " and currency = %(currency)s"

	return conditions, filters

def get_employee_doj_map():
	return	frappe._dict(frappe.db.sql("""
				SELECT
					employee,
					date_of_joining
				FROM `tabEmployee`
				"""))
def get_employee_department_code():
	return	frappe._dict(frappe.db.sql("""
				SELECT
					employee,
					department_code
				FROM `tabEmployee`
				"""))
def get_employee_total_salary():
	return	frappe._dict(frappe.db.sql("""select emp.name, SUM(ss.amount)
		from `tabEmployee` emp
		INNER JOIN `tabSalary Structure Assignment` ssa  on (emp.name=ssa.employee)
		JOIN `tabSalary Detail` ss  on (ssa.salary_structure=ss.parent)
		GROUP BY ssa.name,ss.parent;"""))

def get_ss_earning_map(salary_slips, currency, company_currency):
	ss_earnings = frappe.db.sql("""select sd.parent, sd.salary_component, sd.amount, ss.exchange_rate, ss.name
		from `tabSalary Detail` sd, `tabSalary Slip` ss where sd.parent=ss.name and sd.parent in (%s)""" %
		(', '.join(['%s']*len(salary_slips))), tuple([d.name for d in salary_slips]), as_dict=1)

	ss_earning_map = {}
	for d in ss_earnings:
		ss_earning_map.setdefault(d.parent, frappe._dict()).setdefault(d.salary_component, [])
		if currency == company_currency:
			ss_earning_map[d.parent][d.salary_component] = flt(ss_earning_map[d.parent][d.salary_component]) + (flt(d.amount) * flt(d.exchange_rate if d.exchange_rate else 1))
		else:
			ss_earning_map[d.parent][d.salary_component] = flt(ss_earning_map[d.parent][d.salary_component]) +  flt(d.amount)

	return ss_earning_map

def get_ss_ded_map(salary_slips, currency, company_currency):
	ss_deductions = frappe.db.sql("""select sd.parent, sd.salary_component, sd.amount, ss.exchange_rate, ss.name
		from `tabSalary Detail` sd, `tabSalary Slip` ss where sd.parent=ss.name and sd.parent in (%s)""" %
		(', '.join(['%s']*len(salary_slips))), tuple([d.name for d in salary_slips]), as_dict=1)

	ss_ded_map = {}
	for d in ss_deductions:
		ss_ded_map.setdefault(d.parent, frappe._dict()).setdefault(d.salary_component, [])
		if currency == company_currency:
			ss_ded_map[d.parent][d.salary_component] = flt(ss_ded_map[d.parent][d.salary_component]) + (flt(d.amount) * flt(d.exchange_rate if d.exchange_rate else 1))
		else:
			ss_ded_map[d.parent][d.salary_component] = flt(ss_ded_map[d.parent][d.salary_component]) + flt(d.amount)

	return ss_ded_map
