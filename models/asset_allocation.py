from odoo import api, fields, models
from odoo.exceptions import ValidationError


class AssetAllocation(models.Model):
    _name = "asset.allocation"
    _description = "Asset Allocation"

    asset_id = fields.Many2one("asset.asset", required=True, ondelete="restrict")
    employee_id = fields.Many2one("hr.employee", required=True, ondelete="restrict")
    allocation_date = fields.Date(required=True, default=fields.Date.context_today)
    expected_return_date = fields.Date()
    actual_return_date = fields.Date()
    status = fields.Selection(
        [
            ("allocated", "Allocated"),
            ("returned", "Returned"),
        ],
        required=True,
        default="allocated",
    )

    @api.model_create_multi
    def create(self, vals_list):
        allocations = self.env[self._name]

        for vals in vals_list:
            asset = self.env["asset.asset"].browse(vals["asset_id"])

            if not asset.exists() or asset.status != "available":
                raise ValidationError("Only assets with status 'Available' can be allocated.")

            asset.write(
                {
                    "status": "allocated",
                    "current_holder_id": vals["employee_id"],
                }
            )

            allocations |= super(AssetAllocation, self).create([vals])

        return allocations
