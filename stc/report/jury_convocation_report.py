from odoo import api, models, _
from odoo.exceptions import UserError

class JuryConvocationReport(models.AbstractModel):
    _name = 'report.stc.jury_convocation_template'
    _description = "Rapport Convocation Jury"

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['stc.soutenance'].browse(docids)
        for doc in docs:
            if doc.statut not in ['jury_et_planification', 'planifie', 'fermee'] or not doc.jurys_valides:
                raise UserError(_("La convocation du jury ne peut être imprimée que si la soutenance est au statut 'Jury et Planification'."))
        return {
            'doc_ids': docids,
            'doc_model': 'stc.soutenance',
            'docs': docs,
        } 