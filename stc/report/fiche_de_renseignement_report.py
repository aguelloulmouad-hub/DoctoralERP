from odoo import api, models, _
from odoo.exceptions import UserError

class FicheRenseignementReport(models.AbstractModel):
    _name = 'report.stc.fiche_de_renseignement_template'
    _description = 'Rapport Fiche de Renseignement Doctorant'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['stc.soutenance'].browse(docids)
        for doc in docs:
            if doc.statut != 'fermee':
                raise UserError(_("La fiche de renseignement ne peut être imprimée que si la soutenance est au statut 'Fermée'."))
        return {
            'doc_ids': docids,
            'doc_model': 'stc.soutenance',
            'docs': docs,
        }
