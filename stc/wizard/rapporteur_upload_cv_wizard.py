from odoo import models, fields, api, _

class RapporteurUploadCVWizard(models.TransientModel):
    _name = 'rapporteur.upload.cv.wizard'
    _description = 'Wizard pour uploader le CV du rapporteur'

    rapporteur_id = fields.Many2one('stc.rapporteur.proposition', string="Rapporteur", required=True)
    cv_fichier = fields.Binary(string="CV", required=True)
    cv_filename = fields.Char(string="Nom du fichier CV")

    @api.onchange('cv_fichier')
    def _onchange_cv_fichier(self):
        if self.cv_fichier:
            filename_ctx = self._context.get('filename')
            if filename_ctx:
                self.cv_filename = filename_ctx
            elif self.rapporteur_id:
                rapporteur_nom = self.rapporteur_id.rapporteur_nom.replace(' ', '_')
                self.cv_filename = f"{rapporteur_nom}_CV.pdf"
            else:
                self.cv_filename = 'rapporteur_cv.pdf'
        else:
            self.cv_filename = False

    def action_upload(self):
        self.ensure_one()
        self.rapporteur_id.write({
            'CV_fichier': self.cv_fichier,
            'CV_filename': self.cv_filename,
        })
        return {'type': 'ir.actions.act_window_close'} 