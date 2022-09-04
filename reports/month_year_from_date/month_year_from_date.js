// Copyright (c) 2016, HCG and contributors
// For license information, please see license.txt
/* eslint-disable */

let new_date = new Date();
let month = new_date.toLocaleString('default', { month: 'long' });
let year = new_date.getFullYear();

function make_data (input_date){
	 new_date = new Date(input_date);
	 month = new_date.toLocaleString('default', { month: 'long' });
	 year = new_date.getFullYear();
}

frappe.query_reports["Month Year From Date"] = {
	"filters": [
		{
			"fieldname":"date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": "80",
			"default": make_data(moment(frappe.datetime.get_today()).format('YYYY-MM-DD'))
		},
		{
			"fieldname": "month",
			"label": __("Month"),
			"fieldtype": "Select",
			"width": "80",
			"options": ["January","February","March","April","May","June","July","August","September","Octeber","November","December"],
			"default": month,
		},
		{
			"fieldname": "year",
			"label": __("Year"),
			"fieldtype": "Select",
			"width": "80",
			"options": [2020,2021,2022,2023],
			"default": year
		}

	]
};
