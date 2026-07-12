from odoo import fields, models
from odoo.exceptions import ValidationError


class AssetTransfer(models.Model):
    _name = "asset.transfer"
    _description = "Asset Transfer"
    _order = "request_date desc, id desc"

    asset_id = fields.Many2one("asset.asset", required=True, ondelete="restrict")
    current_holder_id = fields.Many2one(
        "hr.employee",
        related="asset_id.current_holder_id",
        store=True,
        readonly=True,
    )
    new_holder_id = fields.Many2one("hr.employee", required=True, ondelete="restrict")
    reason = fields.Text(required=True)
    request_date = fields.Date(required=True, default=fields.Date.context_today)
    approval_date = fields.Date(readonly=True)
    state = fields.Selection(
        [
            ("requested", "Requested"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
            ("completed", "Completed"),
        ],
        required=True,
        default="requested",
    )

    def action_approve(self):
        self.ensure_one()
        if self.state != "requested":
            raise ValidationError("Only requested transfers can be approved.")

        self.write({"state": "approved"})

    def action_reject(self):
        self.ensure_one()
        if self.state != "requested":
            raise ValidationError("Only requested transfers can be rejected.")

        self.write({"state": "rejected"})

    def action_complete(self):
        self.ensure_one()
        if self.state != "approved":
            raise ValidationError("Only approved transfers can be completed.")

        self.asset_id.write(
            {
                "current_holder_id": self.new_holder_id.id,
                "status": "allocated",
            }
        )
        self.write({"state": "completed"})

