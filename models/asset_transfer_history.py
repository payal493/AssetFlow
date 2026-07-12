from odoo import fields, models


class AssetTransferHistory(models.Model):
    _name = "asset.transfer.history"
    _description = "Asset Transfer History"
    _order = "action_date desc, id desc"

    transfer_id = fields.Many2one("asset.transfer", required=True, ondelete="cascade")
    asset_id = fields.Many2one("asset.asset", required=True, ondelete="cascade")
    previous_holder_id = fields.Many2one("hr.employee", ondelete="set null")
    new_holder_id = fields.Many2one("hr.employee", ondelete="set null")
    action_date = fields.Date(required=True, default=fields.Date.context_today)
    action_type = fields.Selection(
        [
            ("approved", "Approved"),
        ],
        required=True,
        default="approved",
    )
