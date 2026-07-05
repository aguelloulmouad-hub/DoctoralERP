from odoo import models, fields

class Specialite(models.Model):
    _name = 'stc.specialite'
    _description = 'Spécialité'

    name = fields.Char(string='Nom', required=True) 