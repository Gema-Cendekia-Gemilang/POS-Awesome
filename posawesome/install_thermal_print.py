import frappe
import os

def install_thermal_print_format():
    """Install Thermal Receipt 58mm Print Format"""
    
    # Check if print format already exists
    if frappe.db.exists("Print Format", "Thermal Receipt 58mm"):
        print("Print Format 'Thermal Receipt 58mm' already exists. Updating...")
        # Update existing
        doc = frappe.get_doc("Print Format", "Thermal Receipt 58mm")
    else:
        # Create new
        doc = frappe.new_doc("Print Format")
        doc.name = "Thermal Receipt 58mm"
    
    # Get HTML content from file
    app_path = frappe.get_app_path("posawesome")
    html_path = os.path.join(
        app_path, 
        "posawesome", 
        "print_format", 
        "thermal_receipt_58mm", 
        "thermal_receipt_58mm.html"
    )
    
    with open(html_path, 'r') as f:
        html_content = f.read()
    
    # Set/Update fields
    doc.doc_type = "POS Invoice"
    doc.module = "POSAwesome"
    doc.standard = "Yes"
    doc.custom_format = 1
    doc.html = html_content
    doc.print_format_type = "Jinja"
    doc.font_size = 9
    doc.margin_top = 5.0
    doc.margin_bottom = 5.0
    doc.margin_left = 2.0
    doc.margin_right = 2.0
    doc.show_section_headings = 0
    doc.line_breaks = 0
    
    if frappe.db.exists("Print Format", "Thermal Receipt 58mm"):
        doc.save(ignore_permissions=True)
        print("Print Format 'Thermal Receipt 58mm' updated successfully!")
    else:
        doc.insert(ignore_permissions=True)
        print("Print Format 'Thermal Receipt 58mm' installed successfully!")
    
    frappe.db.commit()

if __name__ == "__main__":
    install_thermal_print_format()
