from odoo import models, fields

class Discipline(models.Model):
    _name = 'stc.discipline'
    _description = 'Discipline'

    name = fields.Char(string='Nom', required=True)
    id_specialite = fields.Many2one('stc.specialite', string='Spécialité') 