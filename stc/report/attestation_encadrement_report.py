from odoo import api, models, _
from odoo.exceptions import UserError

class AttestationEncadrementReport(models.AbstractModel):
    _name = 'report.stc.attestation_encadrement_template'
    _description = "Rapport Attestation Encadrement"

    @api.model
    def _get_report_values(self, docids, data=None):
        personnels = self.env['stc.personnel'].browse(docids)
        result = []
        for personnel in personnels:
            # Chercher les soutenances planifiées ou fermées où ce personnel est encadrant
            soutenances = self.env['stc.soutenance'].search([
                ('encadrant_id', '=', personnel.id),
                ('statut', 'in', ['planifie', 'fermee'])
            ])
            result.append({
                'personnel': personnel,
                'soutenances': soutenances,
            })
        return {
            'doc_ids': docids,
            'doc_model': 'stc.personnel',
            'docs': result,
        } 