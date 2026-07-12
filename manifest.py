# -*- coding: utf-8 -*-
{
    'name': 'AssetFlow - Organization & User Management',
    'version': '18.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Organization structure, employee management, and category management for AssetFlow',
    'author': 'AssetFlow Development Team',
    'license': 'LGPL-3',

    # 'mail' brings chatter/activity tracking on Department, Employee, and
    # Category records - useful for an audit trail. 'hr' is intentionally
    # NOT included: assetflow.employee is a standalone model with its own
    # fields and sequence, not an extension of hr.employee, so pulling in
    # the full HR app would just add a duplicate/conflicting Employees menu.
    'depends': [
        'base',
        'mail',
    ],

    'data': [
        # Security must load first: groups are referenced by
        # ir.model.access.csv and by view visibility rules.
        'security/security.xml',
        'security/ir.model.access.csv',

        # Sequences must exist before any employee records can be created.
        'data/sequences.xml',

        # Views must load before the menu, since menu items reference the
        # action XML IDs defined inside these files.
        'views/department_views.xml',
        'views/employee_views.xml',
        'views/category_views.xml',
        'views/menu.xml',
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}
