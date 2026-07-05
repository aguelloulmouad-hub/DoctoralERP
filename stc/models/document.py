from odoo import models, fields

class Document(models.Model):
    _name = 'stc.document'
    _description = 'Document lié à la soutenance ou au doctorant'

    typedoc_id = fields.Many2one('stc.document_type', string='Type de document')
    fichier = fields.Binary(string='Fichier')
    filename = fields.Char(string='Nom du fichier')
    soutenance_id = fields.Many2one('stc.soutenance', string='Soutenance')
    doctorant_id = fields.Many2one('stc.doctorant', string='Doctorant') 