from odoo import models, fields, api, _

class AjoutJuryWizard(models.TransientModel):
    _name = 'ajout.jury.wizard'
    _description = 'Wizard pour ajouter des membres du jury'

    soutenance_id = fields.Many2one('stc.soutenance', string='Soutenance', required=True, ondelete='cascade')
    jury_lines = fields.One2many('ajout.jury.line.wizard', 'wizard_id', string='Jurys à ajouter')

    def action_add(self):
        for line in self.jury_lines:
            self.env['stc.jury'].create({
                'soutenance_id': self.soutenance_id.id,
                'nom': line.nom,
                'grade': line.grade,
                'institution': line.institution,
                'email': line.email,
                'role': line.role,
                'role_par_ced': line.role_par_ced.id if line.role_par_ced else False,
                'numero_bo': line.numero_bo,
                'date': line.date,
                'nom_ar': line.nom_ar,
                'tel': line.tel,
            })
        return {'type': 'ir.actions.act_window_close'}

class AjoutJuryLineWizard(models.TransientModel):
    _name = 'ajout.jury.line.wizard'
    _description = 'Ligne d\'ajout de membre du jury'

    wizard_id = fields.Many2one('ajout.jury.wizard', string='Wizard')
    nom = fields.Char(string='Nom', required=True)
    grade = fields.Char(string='Grade')
    institution = fields.Char(string='Institution ou Organisme')
    email = fields.Char(string='Email')
    role = fields.Char(string='Rôle')
    role_par_ced = fields.Many2one('stc.role', string='Rôle validé par le CED')
    numero_bo = fields.Char(string="N° Bureau d'Ordre")
    date = fields.Date(string="Date")
    nom_ar = fields.Char(string='Nom (arabe)')
    tel = fields.Char(string='Téléphone')

    def action_add(self):
        for line in self.jury_lines:
            self.env['stc.jury'].create({
                'soutenance_id': self.soutenance_id.id,
                'nom': line.nom,
                'grade': line.grade,
                'institution': line.institution,
                'email': line.email,
                'role': line.role,
                'role_par_ced': line.role_par_ced.id if line.role_par_ced else False,
                'numero_bo': line.numero_bo,
                'date': line.date,
                'nom_ar': line.nom_ar,
                'tel': line.tel,
            })
        return {'type': 'ir.actions.act_window_close'} 