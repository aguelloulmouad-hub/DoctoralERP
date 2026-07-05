from odoo import models, fields, api, _

class ModifierRapporteursWizard(models.TransientModel):
    _name = 'modifier.rapporteurs.wizard'
    _description = 'Wizard pour modifier les rapporteurs'

    soutenance_id = fields.Many2one('stc.soutenance', string='Soutenance', required=True, ondelete='cascade')
    rapporteurs_lines = fields.One2many('modifier.rapporteurs.line.wizard', 'wizard_id', string='Rapporteurs')
    numero_bo = fields.Char(string="N° Bureau d'Ordre (pour rapporteurs choisis)")
    date = fields.Date(string="Date (pour rapporteurs choisis)")

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        soutenance = self.env['stc.soutenance'].browse(self.env.context.get('active_id'))
        res['soutenance_id'] = soutenance.id
        lines = []
        for r in soutenance.rapporteurs_ids:
            lines.append((0, 0, {
                'rapporteur_id': r.id,
                'rapporteur_nom': r.rapporteur_nom,
                'grade': r.grade,
                'institution': r.institution,
                'email': r.email,
                'numero_bo': r.numero_bo,
                'date': r.date,
                'tel': r.tel,
            }))
        res['rapporteurs_lines'] = lines
        return res

    def action_apply(self):
        self.ensure_one()
        rapporteur_ids_initial = set(self.soutenance_id.rapporteurs_ids.ids)
        rapporteur_ids_wizard = set([line.rapporteur_id.id for line in self.rapporteurs_lines if line.rapporteur_id])
        # Mise à jour des rapporteurs existants
        for line in self.rapporteurs_lines:
            if line.rapporteur_id:
                vals = {}
                # numero_bo et date sont toujours modifiables
                vals['numero_bo'] = line.numero_bo
                vals['date'] = line.date
                # Les autres champs ne sont modifiables que si rapporteurs_valides est False
                if not self.soutenance_id.rapporteurs_valides:
                    vals.update({
                        'rapporteur_nom': line.rapporteur_nom,
                        'grade': line.grade,
                        'institution': line.institution,
                        'email': line.email,
                        'tel': line.tel,
                    })
                line.rapporteur_id.write(vals)
        # Si numero_bo ou date sont renseignés, appliquer à tous les rapporteurs choisis
        if self.numero_bo or self.date:
            for rapp in self.soutenance_id.rapporteurs_ids.filtered(lambda r: r.choisie):
                vals = {}
                if self.numero_bo:
                    vals['numero_bo'] = self.numero_bo
                if self.date:
                    vals['date'] = self.date
                if vals:
                    rapp.write(vals)
        # Suppression des rapporteurs retirés dans le wizard
        to_unlink = rapporteur_ids_initial - rapporteur_ids_wizard
        if to_unlink:
            self.env['stc.rapporteur.proposition'].browse(list(to_unlink)).unlink()
        return {'type': 'ir.actions.act_window_close'}

class ModifierRapporteursLineWizard(models.TransientModel):
    _name = 'modifier.rapporteurs.line.wizard'
    _description = 'Ligne de modification de rapporteur'

    wizard_id = fields.Many2one('modifier.rapporteurs.wizard', string='Wizard')
    rapporteur_id = fields.Many2one('stc.rapporteur.proposition', string='Rapporteur')
    rapporteur_nom = fields.Char(string='Nom du rapporteur', required=True)
    grade = fields.Char(string='Grade')
    institution = fields.Char(string='Institution ou Organisme')
    email = fields.Char(string='Email')
    numero_bo = fields.Char(string="N° Bureau d'Ordre")
    date = fields.Date(string="Date")
    tel = fields.Char(string='Téléphone')
    soutenance_id = fields.Many2one('stc.soutenance', string='Soutenance')

    def action_apply(self):
        self.ensure_one()
        rapporteur_ids_initial = set(self.soutenance_id.rapporteurs_ids.ids)
        rapporteur_ids_wizard = set([line.rapporteur_id.id for line in self.rapporteurs_lines if line.rapporteur_id])
        # Mise à jour des rapporteurs existants
        for line in self.rapporteurs_lines:
            if line.rapporteur_id:
                line.rapporteur_id.write({
                    'rapporteur_nom': line.rapporteur_nom,
                    'grade': line.grade,
                    'institution': line.institution,
                    'email': line.email,
                    'numero_bo': line.numero_bo,
                    'date': line.date,
                    'tel': line.tel,
                })
        # Suppression des rapporteurs retirés dans le wizard
        to_unlink = rapporteur_ids_initial - rapporteur_ids_wizard
        if to_unlink:
            self.env['stc.rapporteur.proposition'].browse(list(to_unlink)).unlink()
        return {'type': 'ir.actions.act_window_close'} 