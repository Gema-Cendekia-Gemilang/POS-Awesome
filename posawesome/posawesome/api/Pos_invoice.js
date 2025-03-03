frappe.ui.form.on("POS Invoice", {
    refresh: function(frm) {
        // Tampilkan tombol jika dokumen sudah tersimpan dan status masih Draft
        if (!frm.doc.__islocal && frm.doc.status === "Draft") {
            frm.add_custom_button(__('Kirim Invoice'), function() {
                frappe.call({
                    method: "reparo.api.customer.send_draft_invoice",
                    args: {
                        invoice_name: frm.doc.name
                    },
                    callback: function(r) {
                        if (!r.exc) {
                            frappe.msgprint("Draft Invoice berhasil dikirim ke customer!");
                        }
                    }
                });
            }, __("Actions"));
        }
    }
});
