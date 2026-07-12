from odoo import _, api, fields, models


class AssetAsset(models.Model):
    _name = "asset.asset"
    _description = "Enterprise Asset"

    asset_tag = fields.Char(readonly=True, copy=False, default=lambda self: _("New"))
    name = fields.Char(required=True)
    category_id = fields.Many2one("asset.category")
    serial_number = fields.Char()
    acquisition_date = fields.Date()
    acquisition_cost = fields.Float()
    condition = fields.Selection(
        [
            ("excellent", "Excellent"),
            ("good", "Good"),
            ("fair", "Fair"),
            ("damaged", "Damaged"),
        ]
    )
    location = fields.Char()
    current_holder_id = fields.Many2one("hr.employee")
    status = fields.Selection(
        [
            ("available", "Available"),
            ("allocated", "Allocated"),
            ("reserved", "Reserved"),
            ("under_maintenance", "Under Maintenance"),
            ("lost", "Lost"),
            ("retired", "Retired"),
            ("disposed", "Disposed"),
        ],
        default="available",
        required=True,
    )

    _sql_constraints = [
        ("asset_asset_serial_number_unique", "unique(serial_number)", "Serial number must be unique."),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("asset_tag") or vals.get("asset_tag") == _("New"):
                vals["asset_tag"] = self.env["ir.sequence"].next_by_code("asset.asset") or _("New")

        return super().create(vals_list)
