from odoo import api, models, _
from odoo.exceptions import UserError

class PvSoutenanceReport(models.AbstractModel):
    _name = 'report.stc.pv_soutenance_template'
    _description = "Rapport PV de Soutenance"

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['stc.soutenance'].browse(docids)
        for doc in docs:
            if doc.statut not in ['jury_et_planification', 'planifie', 'fermee'] or not doc.jurys_valides:
                raise UserError(_("Le PV de soutenance ne peut être imprimé que si la soutenance est au statut 'Jury et Planification'."))
        return {
            'doc_ids': docids,
            'doc_model': 'stc.soutenance',
            'docs': docs,
        } 