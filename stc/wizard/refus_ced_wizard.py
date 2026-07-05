from odoo import models, fields, api, _
from odoo.exceptions import UserError

class RefusCEDWizard(models.TransientModel):
    _name = 'refus.ced.wizard'
    _description = 'Refus de la demande par le CED'

    soutenance_id = fields.Many2one('stc.soutenance', required=True, ondelete='cascade')
    motif_rejet = fields.Text(string='Motif du rejet', required=True)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        soutenance = self.env['stc.soutenance'].browse(self.env.context.get('default_soutenance_id'))
        res['soutenance_id'] = soutenance.id
        return res

    def action_apply(self):
        self.ensure_one()
        self.soutenance_id.write({
            'motif_rejet': self.motif_rejet,
            'statut': 'rejetee',
        })
        return {'type': 'ir.actions.act_window_close'} 