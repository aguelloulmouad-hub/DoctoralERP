from odoo import models, fields, api, _
from os.path import splitext

class RapporteurUploadFichierWizard(models.TransientModel):
    _name = 'rapporteur.upload.fichier.wizard'
    _description = 'Wizard pour uploader un fichier rapporteur'

    rapporteur_id = fields.Many2one('stc.rapporteur.proposition', string="Rapporteur", required=True)
    fichier = fields.Binary(string="Fichier", required=True)
    filename = fields.Char(string="Nom du fichier")

    @api.onchange('fichier')
    def _onchange_fichier(self):
        if self.fichier:
            filename_ctx = self._context.get('filename')
            if filename_ctx:
                self.filename = filename_ctx
            elif self.rapporteur_id:
                rapporteur_nom = self.rapporteur_id.rapporteur_nom.replace(' ', '_')
                self.filename = f"{rapporteur_nom}_report.pdf"
            else:
                self.filename = 'rapporteur_report.pdf'
        else:
            self.filename = False

    def action_upload(self):
        self.ensure_one()
        self.rapporteur_id.write({
            'fichier': self.fichier,
            'filename': self.filename,
        })
        return {'type': 'ir.actions.act_window_close'} 