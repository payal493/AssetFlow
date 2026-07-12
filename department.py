# AssetFlow - Department Model
# Copyright 2024 AssetFlow Development Team
# License LGPL-3

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Department(models.Model):
    """
    Department model for organizational structure.
    
    Supports hierarchical department organization with manager assignment.
    """
    
    _name = 'assetflow.department'
    _description = 'Department'
    _rec_name = 'name'
    _order = 'name asc'
    
    # Fields
    name = fields.Char(
        string='Department Name',
        required=True,
        index=True,
        help='Name of the department',
    )
    
    code = fields.Char(
        string='Department Code',
        help='Short code for the department (e.g., HR, IT, SALES)',
    )
    
    description = fields.Text(
        string='Description',
        help='Detailed description of the department',
    )
    
    manager_id = fields.Many2one(
        comodel_name='assetflow.employee',
        string='Department Manager',
        help='Employee responsible for this department',
        ondelete='set null',
    )
    
    parent_department_id = fields.Many2one(
        comodel_name='assetflow.department',
        string='Parent Department',
        help='Parent department in the hierarchy',
        ondelete='restrict',
    )
    
    employee_ids = fields.One2many(
        comodel_name='assetflow.employee',
        inverse_name='department_id',
        string='Employees',
        help='Employees assigned to this department',
    )
    
    active = fields.Boolean(
        string='Active',
        default=True,
        help='Uncheck to deactivate this department',
    )
    
    employee_count = fields.Integer(
        string='Employee Count',
        compute='_compute_employee_count',
        help='Total number of employees in this department',
    )
    
    # SQL Constraints
    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'Department name must be unique.'),
    ]
    
    # Computed Fields
    @api.depends('employee_ids')
    def _compute_employee_count(self):
        """Compute the total number of employees in this department."""
        for department in self:
            department.employee_count = len(department.employee_ids)
    
    # Constraints
    @api.constrains('parent_department_id')
    def _check_parent_department_recursion(self):
        """
        Prevent a department from being its own parent or creating circular hierarchy.
        """
        for department in self:
            if department.parent_department_id:
                if department.id == department.parent_department_id.id:
                    raise ValidationError(
                        'A department cannot be its own parent.'
                    )
                
                # Check for circular references in hierarchy
                current = department.parent_department_id
                while current:
                    if current.id == department.id:
                        raise ValidationError(
                            'Circular hierarchy detected. Cannot set parent department.'
                        )
                    current = current.parent_department_id
    
    @api.constrains('manager_id')
    def _check_manager_belongs_to_department(self):
        """
        Ensure that if a manager is assigned, they belong to this department.
        """
        for department in self:
            if department.manager_id and department.manager_id.department_id != department:
                raise ValidationError(
                    'The department manager must be an employee of this department.'
                )
    
    # ORM Methods
    def write(self, vals):
        """
        Override write to maintain data integrity.
        """
        return super().write(vals)
    
    def name_get(self):
        """
        Display department name with code if available.
        """
        result = []
        for department in self:
            if department.code:
                name = f'[{department.code}] {department.name}'
            else:
                name = department.name
            result.append((department.id, name))
        return result
