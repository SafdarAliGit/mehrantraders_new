// Calculates row qty (kg) from pieces for sales transaction child tables.
//  Coil item groups:   qty = W * L * T * Density * Qty(pcs) * (1 + Tolerance%/100)
//  Other item groups:  qty = (Foot or Meter, by row UOM) * Qty(pcs) * (1 + Tolerance%/100)

(function () {
	const CHILD_DOCTYPES = [
		"Quotation Item",
		"Sales Order Item",
		"Delivery Note Item",
		"Sales Invoice Item",
	];
	const TRIGGER_FIELDS = [
		"qty_pcs", "width", "length", "thickness", "density",
		"tolerance", "foot", "meter", "uom", "item_group",
	];

	let coil_groups_promise = null;
	function get_coil_groups() {
		if (!coil_groups_promise) {
			coil_groups_promise = frappe
				.xcall("mehrantraders_new.api.get_coil_item_groups")
				.then((groups) => new Set(groups || []))
				.catch(() => {
					coil_groups_promise = null;
					return new Set();
				});
		}
		return coil_groups_promise;
	}

	async function get_item_group(row) {
		if (row.item_group) return row.item_group;
		if (!row.item_code) return null;
		const r = await frappe.db.get_value("Item", row.item_code, "item_group");
		return r && r.message ? r.message.item_group : null;
	}

	async function calculate_qty_from_pcs(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (!row || !row.item_code || !flt(row.qty_pcs)) return;

		const [coil_groups, item_group] = await Promise.all([get_coil_groups(), get_item_group(row)]);
		const tolerance_factor = 1 + flt(row.tolerance) / 100;
		let base = 0;

		if (item_group && coil_groups.has(item_group)) {
			base = flt(row.width) * flt(row.length) * flt(row.thickness) * flt(row.density);
		} else if (row.uom === "Foot") {
			base = flt(row.foot);
		} else if (row.uom === "Meter") {
			base = flt(row.meter);
		}

		if (!base) return;

		const qty = flt(base * flt(row.qty_pcs) * tolerance_factor, precision("qty", row));
		if (qty !== flt(row.qty)) {
			await frappe.model.set_value(cdt, cdn, "qty", qty);
		}
	}

	const handlers = {
		item_code(frm, cdt, cdn) {
			// wait for ERPNext's item details / fetch_from to populate the row
			frappe.after_ajax(() => calculate_qty_from_pcs(frm, cdt, cdn));
		},
	};
	TRIGGER_FIELDS.forEach((f) => (handlers[f] = calculate_qty_from_pcs));

	CHILD_DOCTYPES.forEach((dt) => frappe.ui.form.on(dt, handlers));

	window.mehrantraders_new = Object.assign(window.mehrantraders_new || {}, {
		calculate_qty_from_pcs,
	});
})();
