from odoo import models, fields

class Jury(models.Model):
    _name = 'stc.jury'
    _description = 'Jury de soutenance'

    soutenance_id = fields.Many2one('stc.soutenance', string='Soutenance')
    nom = fields.Char(string='Nom')
    grade = fields.Char(string="Grade")
    institution = fields.Char(string="Institution ou Organisme")
    email = fields.Char(string="Email")
    role = fields.Char(string="Rôle")
    role_par_ced = fields.Many2one('stc.role', string='Rôle validé par le CED')
    numero_bo = fields.Char(string="N° Bureau d'Ordre")
    date = fields.Date(string="Date")
    tel = fields.Char(string="Téléphone")
    nom_ar = fields.Char(string="Nom (arabe)")