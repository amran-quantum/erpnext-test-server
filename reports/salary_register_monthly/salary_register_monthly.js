// Copyright (c) 2016, HCG and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Salary Register Monthly"] = {
	"filters": [

	]
};
// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Salary Register Monthly"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From"),
			"fieldtype": "Date",
			"default": moment(frappe.datetime.get_today()).startOf('month').format('YYYY-MM-DD'),
			"reqd": 1,
			"width": "100px"
		},
		{
			"fieldname":"to_date",
			"label": __("To"),
			"fieldtype": "Date",
			"default": moment(frappe.datetime.get_today()).endOf('month').format('YYYY-MM-DD'),
			"reqd": 1,
			"width": "100px"
		},
		{
			"fieldname": "currency",
			"fieldtype": "Link",
			"options": "Currency",
			"label": __("Currency"),
			"default": erpnext.get_currency(frappe.defaults.get_default("Company")),
			"width": "50px"
		},
		{
			"fieldname": "department",
			"fieldtype": "Link",
			"options": "Department",
			"label": __("Deparment"),
			"width": "50px"
		},
		{
			"fieldname":"employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options": "Employee",
			"width": "100px"
		},
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"width": "100px",
			"reqd": 1
		},
		{
			"fieldname":"docstatus",
			"label":__("Document Status"),
			"fieldtype":"Select",
			"options":["Draft", "Submitted", "Cancelled"],
			"default": "Draft",
			"width": "100px"
		}
	]
}
