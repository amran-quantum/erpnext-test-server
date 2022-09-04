// Copyright (c) 2016, HCG and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Leave Application Statistics"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": frappe.datetime.year_start()
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": frappe.datetime.year_end()
		}
	]
};
