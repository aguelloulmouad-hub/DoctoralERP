from odoo import api, models, _
from odoo.exceptions import UserError
from datetime import datetime

class FormulaireDossierReport(models.AbstractModel):
    _name = 'report.stc.formulaire_dossier_template'
    _description = 'Rapport Formulaire Dossier Soutenance'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['stc.soutenance'].browse(docids)
        for doc in docs:
            if doc.statut not in ['en_commission', 'rapporteurs', 'jury_et_planification', 'planifie', 'fermee']:
                raise UserError(_("Le formulaire dossier ne peut être imprimé que si la soutenance est au statut 'En Commission'."))
        return {
            'doc_ids': docids,
            'doc_model': 'stc.soutenance',
            'docs': docs,
            'current_date': datetime.today().strftime('%d-%m-%Y'),
        } 