from odoo import api, models, _

class AttestationParticipationJuryReport(models.AbstractModel):
    _name = 'report.stc.attestation_participation_jury_template'
    _description = "Rapport Attestation Participation Jury"

    @api.model
    def _get_report_values(self, docids, data=None):
        jurys = self.env['stc.jury'].browse(docids)
        result = []
        for jury in jurys:
            # Chercher toutes les participations de ce membre dans les jurys
            participations = self.env['stc.jury'].search([
                ('nom', '=', jury.nom),
                ('email', '=', jury.email),
            ])
            result.append({
                'jury': jury,
                'participations': participations,
            })
        return {
            'doc_ids': docids,
            'doc_model': 'stc.jury',
            'docs': result,
        } 