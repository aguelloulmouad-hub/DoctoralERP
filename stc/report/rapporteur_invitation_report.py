from odoo import api, models, _
from odoo.exceptions import UserError

class RapporteurInvitationReport(models.AbstractModel):
    _name = 'report.stc.rapporteur_invitation_template'
    _description = "Rapport Invitation Rapporteurs"

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['stc.soutenance'].browse(docids)
        for doc in docs:
            if doc.statut not in ['rapporteurs', 'jury_et_planification', 'planifie', 'fermee'] or not doc.rapporteurs_valides:
                raise UserError(_("L'invitation des rapporteurs ne peut être imprimée que si la soutenance est au statut 'Accepté Commission' et que les rapporteurs sont validés par le doyen."))
        return {
            'doc_ids': docids,
            'doc_model': 'stc.soutenance',
            'docs': docs,
        } 