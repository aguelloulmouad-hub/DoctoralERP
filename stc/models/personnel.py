from odoo import models, fields

class Personnel(models.Model):
    _name = 'stc.personnel'
    _description = 'Personnel'

    name = fields.Char(string='Nom', required=True)
    prenom = fields.Char(string='Prénom', required=True)
    grade = fields.Char(string='Grade')
    email = fields.Char(string='Email') 