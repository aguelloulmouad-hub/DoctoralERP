from odoo import models, fields

class DocumentType(models.Model):
    _name = 'stc.document_type'
    _description = 'Type de document exigé'

    name = fields.Char(string='Nom du type')
    obligatoire = fields.Boolean(string='Obligatoire') 

    def name_get(self):
        result = []
        for rec in self:
            suffix = " (Obligatoire)" if rec.obligatoire else " (Optionnel)"
            name = "%s%s" % (rec.name, suffix)
            result.append((rec.id, name))
        return result 