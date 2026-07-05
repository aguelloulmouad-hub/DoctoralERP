from odoo import models, fields, api, _

class EntrerResultatSoutenanceWizard(models.TransientModel):
    _name = 'entrer.resultat.soutenance.wizard'
    _description = 'Wizard pour saisir le résultat et la mention de la soutenance'

    soutenance_id = fields.Many2one('stc.soutenance', string='Soutenance', required=True, ondelete='cascade')
    mention = fields.Selection([
        ('tres_honorable', 'Très honorable'),
        ('honorable', 'Honorable'),
    ], string='Mention', required=True)
    resultat = fields.Selection([
        ('admise', 'Admis(e)'),
        ('ajournee', 'Ajourné(e)'),
    ], string='Résultat', required=True)
    specialite = fields.Char(string='Spécialité')
    intitule = fields.Char(string="Intitulé de la thèse")
    specialite_id = fields.Many2one('stc.specialite', string="Spécialité")
    discipline_id = fields.Many2one('stc.discipline', string="Discipline")

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        soutenance = self.env['stc.soutenance'].browse(self.env.context.get('default_soutenance_id'))
        res['soutenance_id'] = soutenance.id
        res['mention'] = 'tres_honorable' if soutenance.mention == 'Très honorable' else False
        res['resultat'] = 'admise' if soutenance.resultat == 'Admis(e)' else False
        res['specialite'] = soutenance.specialite
        res['intitule'] = soutenance.name
        res['specialite_id'] = soutenance.specialite_id.id
        res['discipline_id'] = soutenance.discipline_id.id
        return res

    def action_apply(self):
        self.ensure_one()
        self.soutenance_id.write({
            'mention': dict(self._fields['mention'].selection).get(self.mention),
            'resultat': dict(self._fields['resultat'].selection).get(self.resultat),
            'specialite': self.specialite,
            'name': self.intitule,
            'specialite_id': self.specialite_id.id,
            'discipline_id': self.discipline_id.id,
        })
        return {'type': 'ir.actions.act_window_close'}
