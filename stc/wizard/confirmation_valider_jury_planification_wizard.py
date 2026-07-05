from odoo import models, fields, api, _

class ConfirmationValiderJuryPlanificationWizard(models.TransientModel):
    _name = 'confirmation.valider.jury.planification.wizard'
    _description = 'Confirmation de validation du jury et de la planification'

    soutenance_id = fields.Many2one('stc.soutenance', required=True, ondelete='cascade')
    date_soutenance = fields.Date(related='soutenance_id.date_soutenance', readonly=True)
    lieu = fields.Char(related='soutenance_id.lieu', readonly=True)
    jurys_ids = fields.One2many(
        comodel_name='stc.jury',
        inverse_name='soutenance_id',
        string='Jurys',
        related='soutenance_id.jurys_ids',
        readonly=True,
        store=False,
    )

    def action_confirm(self):
        self.ensure_one()
        self.soutenance_id.jurys_valides = True
        self.soutenance_id.message_post(body=_('La planification et le jury ont été validés par le doyen.'))
        # Ajout : notification de la planification
        planning_msg = _('Planification de la soutenance :<br>Date : %s<br>Lieu : %s') % (
            self.date_soutenance or 'Non renseignée',
            self.lieu or 'Non renseigné'
        )
        self.soutenance_id.message_post(body=planning_msg)
        return {'type': 'ir.actions.act_window_close'}

    def action_refuser(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'refus.jury.planification.doyen.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_soutenance_id': self.soutenance_id.id},
        } 

class ConfirmationValiderJuryPlanificationCedWizard(models.TransientModel):
    _name = 'confirmation.valider.jury.planification.ced.wizard'
    _description = 'Confirmation de validation du jury et de la planification par le CED'

    soutenance_id = fields.Many2one('stc.soutenance', required=True, ondelete='cascade')
    date_soutenance = fields.Date(related='soutenance_id.date_soutenance', readonly=True)
    lieu = fields.Char(related='soutenance_id.lieu', readonly=True)
    jurys_ids = fields.One2many(
        comodel_name='stc.jury',
        inverse_name='soutenance_id',
        string='Jurys',
        related='soutenance_id.jurys_ids',
        readonly=True,
        store=False,
    )

    def action_confirm(self):
        self.ensure_one()
        self.soutenance_id.jurys_ced_valides = True
        self.soutenance_id.message_post(body=_('La planification et le jury ont été validés par le CED.'))
        return {'type': 'ir.actions.act_window_close'}

    def action_refuser(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'refus.jury.planification.ced.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_soutenance_id': self.soutenance_id.id},
        } 