from odoo import api, models, _
from odoo.exceptions import UserError

class AttestationReussiteDoctorantReport(models.AbstractModel):
    _name = 'report.stc.attestation_reussite_doctorant_template'
    _description = "Rapport Attestation Réussite Doctorant"

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['stc.soutenance'].browse(docids)
        for doc in docs:
            if doc.statut not in ['planifie', 'fermee']:
                raise UserError(_("L'attestation de réussite ne peut être imprimée que si la soutenance est au statut 'Planifié' ou 'Fermée'."))
            if not doc.resultat or doc.resultat != 'Admis(e)':
                raise UserError(_("Le résultat de la soutenance doit être 'Admis(e)' pour imprimer l'attestation."))
            if not doc.mention:
                raise UserError(_("La mention doit être renseignée pour imprimer l'attestation."))
        return {
            'doc_ids': docids,
            'doc_model': 'stc.soutenance',
            'docs': docs,
        }