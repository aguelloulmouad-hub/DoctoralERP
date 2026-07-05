from odoo import models, fields, api, _

class AjoutRapporteursWizard(models.TransientModel):
    _name = 'ajout.rapporteurs.wizard'
    _description = 'Wizard pour ajouter des rapporteurs'

    soutenance_id = fields.Many2one('stc.soutenance', string='Soutenance', required=True, ondelete='cascade')
    rapporteurs_lines = fields.One2many('ajout.rapporteurs.line.wizard', 'wizard_id', string='Rapporteurs à ajouter')

    def action_add(self):
        for line in self.rapporteurs_lines:
            self.env['stc.rapporteur.proposition'].create({
                'soutenance_id': self.soutenance_id.id,
                'rapporteur_nom': line.rapporteur_nom,
                'grade': line.grade,
                'institution': line.institution,
                'email': line.email,
                'numero_bo': line.numero_bo,
                'date': line.date,
                'tel': line.tel,
            })
        return {'type': 'ir.actions.act_window_close'}

class AjoutRapporteursLineWizard(models.TransientModel):
    _name = 'ajout.rapporteurs.line.wizard'
    _description = 'Ligne d\'ajout de rapporteur'

    wizard_id = fields.Many2one('ajout.rapporteurs.wizard', string='Wizard', ondelete='cascade')
    rapporteur_nom = fields.Char(string='Nom du rapporteur', required=True)
    grade = fields.Char(string='Grade')
    institution = fields.Char(string='Institution ou Organisme')
    email = fields.Char(string='Email')
    numero_bo = fields.Char(string="N° Bureau d'Ordre")
    date = fields.Date(string="Date")
    tel = fields.Char(string='Téléphone')

    def action_add(self):
        for line in self.rapporteurs_lines:
            self.env['stc.rapporteur.proposition'].create({
                'soutenance_id': self.soutenance_id.id,
                'rapporteur_nom': line.rapporteur_nom,
                'grade': line.grade,
                'institution': line.institution,
                'email': line.email,
                'numero_bo': line.numero_bo,
                'date': line.date,
                'tel': line.tel,
            })
        return {'type': 'ir.actions.act_window_close'} 