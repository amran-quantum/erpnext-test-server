// Copyright (c) 2022, HCG and contributors
// For license information, please see license.txt

frappe.ui.form.on('Month Year From Date', {
	refresh: function(frm) {
		if(frm.doc.docstatus==0)
		{
			
			if (frm.is_new()) {
				const date = new Date();
				const month = date.toLocaleString('default', { month: 'long' });
				console.log(month);
				frm.set_value("month", month);
				frm.set_value("year", date.getFullYear());
				frm.cscript.month = function(doc, cdt, cd){
					frm.events.callRefresh(frm)
				}
				frm.cscript.year = function(doc, cdt, cd){
					frm.events.callRefresh(frm)
				}

			}
		}
	}
});
