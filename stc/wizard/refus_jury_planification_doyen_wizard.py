from odoo import models, fields, api, _
from odoo.exceptions import UserError

class RefusJuryPlanificationDoyenWizard(models.TransientModel):
    _name = 'refus.jury.planification.doyen.wizard'
    _description = 'Refus du jury/planification par le doyen'

    soutenance_id = fields.Many2one('stc.soutenance', required=True, ondelete='cascade')
    message = fields.Text(string='Message au service CED', required=True)

    def action_confirm(self):
        self.ensure_one()
        template = self.env.ref('stc.mail_template_refus_jury_planification_doyen')
        group_ced = self.env.ref('stc.group_service_ced')
        users_ced = self.env['res.users'].search([('groups_id', 'in', group_ced.id)])
        emails = [u.partner_id.email for u in users_ced if u.partner_id.email]
        if not emails:
            emails = ['mouadagl10@gmail.com']
        email_to = ','.join(emails)
        ctx = {
            'default_email_to': email_to,
            'default_body_html': '<p>%s</p>' % self.message,
            'message': self.message,
        }
        template.with_context(ctx).send_mail(self.soutenance_id.id, force_send=True, email_values={'email_to': email_to})
        self.soutenance_id.message_post(body=_('Le doyen a refusé la planification/le jury et a demandé une modification au service CED :<br>%s') % self.message)
        return {'type': 'ir.actions.act_window_close'} 