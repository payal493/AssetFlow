# AssetFlow - Category Model
# Copyright 2024 AssetFlow Development Team
# License LGPL-3

from odoo import models, fields


class Category(models.Model):
    """
    Category model for asset classification and organization.
    
    Provides a simple categorization system for organizing assets
    within the AssetFlow system.
    """
    
    _name = 'assetflow.category'
    _description = 'Asset Category'
    _rec_name = 'name'
    _order = 'name asc'
    
    # Fields
    name = fields.Char(
        string='Category Name',
        required=True,
        index=True,
        help='Name of the asset category',
    )
    
    description = fields.Text(
        string='Description',
        help='Detailed description of this category',
    )
    
    active = fields.Boolean(
        string='Active',
        default=True,
        help='Uncheck to deactivate this category',
    )
    
    # SQL Constraints
    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'Category name must be unique.'),
    ]
