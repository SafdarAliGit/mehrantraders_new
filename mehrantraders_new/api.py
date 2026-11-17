import frappe
from frappe.utils.nestedset import get_descendants_of

COIL_ITEM_GROUP = "Coil"


@frappe.whitelist()
def get_coil_item_groups():
	"""Return "Coil" and all of its descendant item groups."""
	if not frappe.db.exists("Item Group", COIL_ITEM_GROUP):
		return []
	return [COIL_ITEM_GROUP, *get_descendants_of("Item Group", COIL_ITEM_GROUP)]
