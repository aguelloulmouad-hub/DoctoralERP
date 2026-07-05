from odoo import models, fields, api, _

class AjoutPlanificationWizard(models.TransientModel):
    _name = 'ajout.planification.wizard'
    _description = 'Wizard pour ajouter la planification de la soutenance'

    soutenance_id = fields.Many2one('stc.soutenance', string='Soutenance', required=True, ondelete='cascade')
    date_soutenance = fields.Date(string='Date de soutenance', required=True)
    lieu = fields.Char(string='Lieu', required=True)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        soutenance = self.env['stc.soutenance'].browse(self.env.context.get('default_soutenance_id'))
        res['soutenance_id'] = soutenance.id
        res['date_soutenance'] = soutenance.date_soutenance
        res['lieu'] = soutenance.lieu
        return res

    def action_add(self):
        self.ensure_one()
        self.soutenance_id.write({
            'date_soutenance': self.date_soutenance,
            'lieu': self.lieu,
        })
        return {'type': 'ir.actions.act_window_close'} 