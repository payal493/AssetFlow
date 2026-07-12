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
        today = fields.Date.context_today(self)
        for transfer in self:
            if transfer.state != "requested":
                raise ValidationError("Only requested transfers can be approved.")

            previous_holder = transfer.asset_id.current_holder_id
            transfer.write(
                {
                    "state": "approved",
                    "approval_date": today,
                }
            )

            transfer.asset_id.write(
                {
                    "current_holder_id": transfer.new_holder_id.id,
                    "status": "allocated",
                }
            )

            self.env["asset.transfer.history"].create(
                {
                    "transfer_id": transfer.id,
                    "asset_id": transfer.asset_id.id,
                    "previous_holder_id": previous_holder.id,
                    "new_holder_id": transfer.new_holder_id.id,
                    "action_date": today,
                    "action_type": "approved",
                }
            )

    def action_reject(self):
        for transfer in self:
            if transfer.state != "requested":
                raise ValidationError("Only requested transfers can be rejected.")

            transfer.write({"state": "rejected"})

    def action_complete(self):
        for transfer in self:
            if transfer.state != "approved":
                raise ValidationError("Only approved transfers can be completed.")

            transfer.write({"state": "completed"})

