import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

COIL_ITEM_GROUP = "Coil"

SALES_CHILD_DOCTYPES = (
	"Quotation Item",
	"Sales Order Item",
	"Delivery Note Item",
	"Sales Invoice Item",
)


def after_install():
	setup()


def after_migrate():
	setup()


def setup():
	create_coil_item_group()
	create_custom_fields(get_custom_fields(), update=True)


def create_coil_item_group():
	if frappe.db.exists("Item Group", COIL_ITEM_GROUP):
		return

	parent = "Products" if frappe.db.exists("Item Group", "Products") else "All Item Groups"
	frappe.get_doc(
		{
			"doctype": "Item Group",
			"item_group_name": COIL_ITEM_GROUP,
			"parent_item_group": parent,
			"is_group": 1,
		}
	).insert(ignore_permissions=True)


def get_custom_fields():
	item_fields = [
		{
			"fieldname": "foot",
			"label": "Foot(kg)",
			"fieldtype": "Float",
			"insert_after": "weight_uom",
		},
		{
			"fieldname": "meter",
			"label": "Meter(kg)",
			"fieldtype": "Float",
			"insert_after": "foot",
		},
	]

	child_fields = [
		{
			"fieldname": "weight_calc_section",
			"label": "Weight Calculation",
			"fieldtype": "Section Break",
			"insert_after": "stock_qty",
		},
		{
			"fieldname": "qty_pcs",
			"label": "Qty(pcs)",
			"fieldtype": "Float",
			"insert_after": "weight_calc_section",
		},
		{
			"fieldname": "width",
			"label": "Width",
			"fieldtype": "Float",
			"insert_after": "qty_pcs",
		},
		{
			"fieldname": "length",
			"label": "Length",
			"fieldtype": "Float",
			"insert_after": "width",
		},
		{
			"fieldname": "thickness",
			"label": "Thickness",
			"fieldtype": "Float",
			"insert_after": "length",
		},
		{
			"fieldname": "weight_calc_col_break",
			"fieldtype": "Column Break",
			"insert_after": "thickness",
		},
		{
			"fieldname": "density",
			"label": "Density",
			"fieldtype": "Float",
			"precision": "8",
			"default": "0.00000785",
			"insert_after": "weight_calc_col_break",
		},
		{
			"fieldname": "tolerance",
			"label": "Tolerance %",
			"fieldtype": "Percent",
			"insert_after": "density",
		},
		{
			"fieldname": "foot",
			"label": "Foot(kg)",
			"fieldtype": "Float",
			"fetch_from": "item_code.foot",
			"read_only": 1,
			"insert_after": "tolerance",
		},
		{
			"fieldname": "meter",
			"label": "Meter(kg)",
			"fieldtype": "Float",
			"fetch_from": "item_code.meter",
			"read_only": 1,
			"insert_after": "foot",
		},
	]

	fields = {"Item": item_fields}
	for dt in SALES_CHILD_DOCTYPES:
		fields[dt] = [dict(df) for df in child_fields]
	return fields


@frappe.whitelist()
def get_coil_item_groups():
	"""Return "Coil" and all of its descendant item groups."""
	if not frappe.db.exists("Item Group", COIL_ITEM_GROUP):
		return []
	from frappe.utils.nestedset import get_descendants_of

	return [COIL_ITEM_GROUP, *get_descendants_of("Item Group", COIL_ITEM_GROUP)]
