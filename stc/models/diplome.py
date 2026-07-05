from odoo import models, fields

class Diplome(models.Model):
    _name = 'stc.diplome'
    _description = 'Diplôme final du doctorant'

    fichier = fields.Binary(string='Fichier')
    date_gen = fields.Date(string='Date de génération')
    soutenance_id = fields.Many2one('stc.soutenance', string='Soutenance') 