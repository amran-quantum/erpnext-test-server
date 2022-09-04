// Copyright (c) 2016, HCG and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Employee Gratuity"] = {
	"filters": [
		{
			"fieldname":"ending_date",
			"label": __("Ending Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1,
			"width": "100px"
		}
	]
};
