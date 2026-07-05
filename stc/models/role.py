from odoo import models, fields

class Role(models.Model):
    _name = 'stc.role'
    _description = 'Rôle de jury'
    _rec_name = 'role'

    role = fields.Char(string='Rôle', required=True) 