from odoo import models, fields

class Doctorant(models.Model):
    _name = 'stc.doctorant'
    _description = 'Doctorant'

    name = fields.Char(string='Nom')
    encadrant_id = fields.Many2one('stc.personnel', string="Encadrant")
    annee_inscription = fields.Char(string="Année d'inscription")
    date_debut_these = fields.Date(string='Date de début de thèse')
    credits = fields.Integer(string='Crédits')
    documents_ids = fields.One2many('stc.document', 'doctorant_id', string='Documents')
    soutenance_ids = fields.One2many('stc.soutenance', 'doctorant_id', string='Soutenances')
    user_id = fields.Many2one('res.users', string='Utilisateur lié')
    formation_doctorale = fields.Char(string="Formation doctorale")
    code = fields.Char(string='Code') 