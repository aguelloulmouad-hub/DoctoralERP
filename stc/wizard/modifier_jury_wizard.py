from odoo import models, fields, api, _

class ModifierJuryWizard(models.TransientModel):
    _name = 'modifier.jury.wizard'
    _description = 'Wizard pour modifier les membres du jury'

    soutenance_id = fields.Many2one('stc.soutenance', string='Soutenance', required=True, ondelete='cascade')
    jury_lines = fields.One2many('modifier.jury.line.wizard', 'wizard_id', string='Jurys')
    numero_bo_global = fields.Char(string="N° Bureau d'Ordre (pour tous les jurys)")
    date_global = fields.Date(string="Date (pour tous les jurys)")

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        soutenance = self.env['stc.soutenance'].browse(self.env.context.get('active_id'))
        res['soutenance_id'] = soutenance.id
        lines = []
        for j in soutenance.jurys_ids:
            lines.append((0, 0, {
                'jury_id': j.id,
                'nom': j.nom,
                'grade': j.grade,
                'institution': j.institution,
                'email': j.email,
                'role': j.role,
                'role_par_ced': j.role_par_ced.id if j.role_par_ced else False,
                'numero_bo': j.numero_bo,
                'date': j.date,
                'nom_ar': j.nom_ar,
                'tel': j.tel,
            }))
        res['jury_lines'] = lines
        return res

    def action_apply(self):
        self.ensure_one()
        jury_ids_initial = set(self.soutenance_id.jurys_ids.ids)
        jury_ids_wizard = set([line.jury_id.id for line in self.jury_lines if line.jury_id])
        # Mise à jour des jurys existants
        for line in self.jury_lines:
            if line.jury_id:
                vals = {}
                # numero_bo et date sont toujours modifiables
                vals['numero_bo'] = line.numero_bo
                vals['date'] = line.date
                # Les autres champs ne sont modifiables que si jurys_valides est False
                if not self.soutenance_id.jurys_valides:
                    vals.update({
                        'nom': line.nom,
                        'grade': line.grade,
                        'institution': line.institution,
                        'email': line.email,
                        'role': line.role,
                        'role_par_ced': line.role_par_ced.id if line.role_par_ced else False,
                        'nom_ar': line.nom_ar,
                        'tel': line.tel,
                    })
                line.jury_id.write(vals)
        # Si numero_bo_global ou date_global sont renseignés, appliquer à tous les jurys
        if self.numero_bo_global or self.date_global:
            for jury in self.soutenance_id.jurys_ids:
                vals = {}
                if self.numero_bo_global:
                    vals['numero_bo'] = self.numero_bo_global
                if self.date_global:
                    vals['date'] = self.date_global
                if vals:
                    jury.write(vals)
        # Suppression des jurys retirés dans le wizard
        to_unlink = jury_ids_initial - jury_ids_wizard
        if to_unlink:
            self.env['stc.jury'].browse(list(to_unlink)).unlink()
        return {'type': 'ir.actions.act_window_close'}

class ModifierJuryLineWizard(models.TransientModel):
    _name = 'modifier.jury.line.wizard'
    _description = 'Ligne de modification de membre du jury'

    wizard_id = fields.Many2one('modifier.jury.wizard', string='Wizard')
    jury_id = fields.Many2one('stc.jury', string='Jury')
    nom = fields.Char(string='Nom', required=True)
    grade = fields.Char(string='Grade')
    institution = fields.Char(string='Institution ou Organisme')
    email = fields.Char(string='Email')
    role = fields.Char(string='Rôle', required=True)
    role_par_ced = fields.Many2one('stc.role', string='Rôle validé par le CED')
    numero_bo = fields.Char(string="N° Bureau d'Ordre")
    date = fields.Date(string="Date")
    soutenance_id = fields.Many2one('stc.soutenance', string='Soutenance')
    nom_ar = fields.Char(string='Nom (arabe)')
    tel = fields.Char(string='Téléphone')

    def action_apply(self):
        self.ensure_one()
        jury_ids_initial = set(self.soutenance_id.jurys_ids.ids)
        jury_ids_wizard = set([line.jury_id.id for line in self.jury_lines if line.jury_id])
        # Mise à jour des jurys existants
        for line in self.jury_lines:
            if line.jury_id:
                line.jury_id.write({
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
        # Suppression des jurys retirés dans le wizard
        to_unlink = jury_ids_initial - jury_ids_wizard
        if to_unlink:
            self.env['stc.jury'].browse(list(to_unlink)).unlink()
        return {'type': 'ir.actions.act_window_close'} 