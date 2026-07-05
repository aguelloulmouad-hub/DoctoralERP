from odoo import api, models, _
from odoo.exceptions import UserError

class AttestationJuryReport(models.AbstractModel):
    _name = 'report.stc.attestation_jury_template'
    _description = "Rapport Attestation Jury"

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['stc.soutenance'].browse(docids)
        for doc in docs:
            if doc.statut not in ['jury_et_planification', 'planifie', 'fermee'] or not doc.jurys_valides:
                raise UserError(_("L'attestation de jury ne peut être imprimée que si le statut de la soutenance est correct et que le jury a été validé."))
        return {
            'doc_ids': docids,
            'doc_model': 'stc.soutenance',
            'docs': docs,
        } 