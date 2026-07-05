from odoo import models, fields, api, _

class ConfirmationValiderRapporteursWizard(models.TransientModel):
    _name = 'confirmation.valider.rapporteurs.wizard'
    _description = 'Confirmation de validation des rapporteurs'

    soutenance_id = fields.Many2one('stc.soutenance', required=True, ondelete='cascade')
    rapporteurs_ids = fields.One2many(
        comodel_name='stc.rapporteur.proposition',
        inverse_name='soutenance_id',
        string='Rapporteurs',
        related='soutenance_id.rapporteurs_ids',
        readonly=True,
        store=False,
    )

    @api.multi
    def action_confirm(self):
        self.ensure_one()
        self.soutenance_id.rapporteurs_valides = True
        self.soutenance_id.message_post(body=_('Les rapporteurs ont été validés par le doyen.'))
        return {'type': 'ir.actions.act_window_close'} 

    @api.multi
    def action_refuser(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'refus.rapporteurs.doyen.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_soutenance_id': self.soutenance_id.id},
        } 