// Copyright (c) 2016, HCG and contributors
// For license information, please see license.txt
/* eslint-disable */
let years = []
for(let i=2012;i<2033;i++){
	years.push(""+i)
}
frappe.query_reports["Employee Leave Overview"] = {
	"filters": [
		{
			"fieldname":"year",
			"label": __("Year"),
			"fieldtype": "Select",
			"options": years,
			"default": frappe.datetime.year_end().substring(0,4),
			"width": "50"
		},
		{
			"fieldname":"acm_date",
			"label": __("Accumulation Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": frappe.datetime.get_today()
		},

		// {
		// 	"fieldname":"to_date",
		// 	"label": __("To Date"),
		// 	"fieldtype": "Date",
		// 	"reqd": 1,
		// 	"default": frappe.datetime.year_end()
		// }
	]
};
