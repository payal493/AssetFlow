# -*- coding: utf-8 -*-

import re

from odoo import api, fields, models
from odoo.exceptions import ValidationError

# Basic phone validation: allows an optional leading +, then digits, spaces,
# hyphens, and parentheses, with a reasonable overall length. This is
# deliberately permissive (international formats vary widely) - it's meant
# to catch obvious junk input (letters, symbols) rather than fully validate
# a specific national numbering plan.
PHONE_REGEX = re.compile(r'^\+?[0-9\s\-\(\)]{7,20}$')


class AssetflowEmployee(models.Model):
    """Represents an employee record within AssetFlow.

    Each employee optionally links to an Odoo res.users account (user_id).
    Authentication itself is entirely handled by Odoo's built-in res.users
    model - this model does not implement any login/password logic.
    """
    _name = 'assetflow.employee'
    _description = 'AssetFlow Employee'
    _rec_name = 'name'
    _order = 'name'

    employee_id = fields.Char(
        string='Employee ID',
        required=True,
        copy=False,
        readonly=True,
        default='New',
        help='Auto-generated unique identifier (e.g. EMP0001). '
             'Assigned automatically on creation via sequence.',
    )
    name = fields.Char(
        string='Full Name',
        required=True,
        help='Full name of the employee.',
    )
    email = fields.Char(
        string='Email',
        required=True,
        help='Work email address. Must be unique across all employees.',
    )
    phone = fields.Char(
        string='Phone',
        help='Contact phone number. Digits, spaces, hyphens, parentheses, '
             'and an optional leading + are allowed.',
    )
    department_id = fields.Many2one(
        comodel_name='assetflow.department',
        string='Department',
        required=True,
        ondelete='restrict',
        help='Department this employee belongs to. Every employee must '
             'belong to exactly one department.',
    )
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Related User',
        ondelete='restrict',
        help='Odoo user account linked to this employee, used for login '
             'and access rights. Optional - not every employee record '
             'needs a system login.',
    )
    image_1920 = fields.Image(
        string='Photo',
        max_width=1920,
        max_height=1920,
        help='Employee photo.',
    )
    active = fields.Boolean(
        string='Active',
        default=True,
        help='Set to false to archive the employee instead of deleting '
             'them. Archiving also deactivates the linked user account, '
             'if any.',
    )
    notes = fields.Text(
        string='Notes',
        help='Free-text internal notes about the employee.',
    )

    _sql_constraints = [
        (
            'email_uniq',
            'unique(email)',
            'An employee with this email address already exists. '
            'Email addresses must be unique.',
        ),
    ]

    @api.constrains('email')
    def _check_email_unique(self):
        """Case-insensitive duplicate check, backstopping the SQL constraint.

        The unique SQL constraint prevents exact duplicates, but
        'Jane@Corp.com' and 'jane@corp.com' would otherwise both be
        accepted depending on database collation.
        """
        for employee in self:
            if not employee.email:
                continue
            duplicate = self.search([
                ('id', '!=', employee.id),
                ('email', '=ilike', employee.email.strip()),
            ], limit=1)
            if duplicate:
                raise ValidationError(
                    'An employee with the email "%s" already exists.' % employee.email
                )

    @api.constrains('phone')
    def _check_phone_format(self):
        """Validate phone number format, if provided.

        Phone is optional, so an empty value is allowed - this only
        rejects values that are present but malformed.
        """
        for employee in self:
            if employee.phone and not PHONE_REGEX.match(employee.phone.strip()):
                raise ValidationError(
                    'The phone number "%s" is not valid. Please use only '
                    'digits, spaces, hyphens, parentheses, and an optional '
                    'leading "+".' % employee.phone
                )

    @api.model_create_multi
    def create(self, vals_list):
        """Auto-assign employee_id from the assetflow.employee sequence.

        Uses model_create_multi so bulk creation (e.g. via import) makes
        a single efficient pass rather than one sequence lookup per record.
        """
        for vals in vals_list:
            if vals.get('employee_id', 'New') == 'New':
                vals['employee_id'] = self.env['ir.sequence'].next_by_code(
                    'assetflow.employee'
                ) or 'New'
        return super().create(vals_list)

    def write(self, vals):
        """Propagate deactivation to the linked user account.

        When an employee is archived (active=False), their linked
        res.users account is deactivated too, so they immediately lose
        system access. Reactivating the employee does NOT automatically
        reactivate the user - that's a deliberate choice, since restoring
        login access is a more sensitive action that should be an
        explicit, separate step for an administrator.
        """
        result = super().write(vals)
        if vals.get('active') is False:
            for employee in self:
                if employee.user_id and employee.user_id.active:
                    employee.user_id.active = False
        return result
