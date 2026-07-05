from odoo import models, fields

class Session(models.Model):
    _name = 'stc.session'
    _description = 'Session Académique'

    name = fields.Char(string='Nom', required=True)
    date = fields.Date(string='Date', required=True)
    statut = fields.Selection([
        ('brouillon', 'Brouillon'),
        ('ouverte', 'Ouverte'),
        ('fermee', 'Fermée'),
    ], string='Statut', default='brouillon', required=True) 