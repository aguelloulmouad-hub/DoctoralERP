from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
import io
import xlrd

class ImportRapporteursWizard(models.TransientModel):
    _name = 'import.rapporteurs.wizard'
    _description = 'Wizard d\'import des rapporteurs depuis un fichier Excel'

    file = fields.Binary(string='Fichier Excel (.xlsx)', required=True)
    soutenance_id = fields.Many2one('stc.soutenance', string='Soutenance', required=True, ondelete='cascade')
    rapporteurs_lines = fields.One2many('import.rapporteurs.wizard.line', 'wizard_id', string='Rapporteurs à importer')
    state = fields.Selection([
        ('import', 'Import'),
        ('preview', 'Aperçu')
    ], string='État', default='import')

    def action_import(self):
        """Lit le fichier Excel et prépare les données pour l'aperçu"""
        if not self.file:
            raise UserError(_('Veuillez sélectionner un fichier Excel.'))
        
        # Supprimer les lignes existantes
        self.rapporteurs_lines.unlink()
        
        file_data = base64.b64decode(self.file)
        workbook = xlrd.open_workbook(file_contents=file_data)
        sheet = workbook.sheet_by_index(0)
        
        # Créer les lignes temporaires pour l'aperçu
        for row_idx in range(1, sheet.nrows):  # On saute l'en-tête
            # Récupère les 5 premières colonnes, ou '' si manquant
            values = [sheet.cell(row_idx, col_idx).value if col_idx < sheet.ncols else '' for col_idx in range(5)]
            # Ignore les lignes vides
            if not any(values):
                continue
            rapporteur_nom, grade, institution, email, tel = values
            tel = str(tel) if tel else ''
            if tel.endswith('.0'):
                tel = tel[:-2]
            
            # Créer une ligne temporaire
            self.env['import.rapporteurs.wizard.line'].create({
                'wizard_id': self.id,
                'rapporteur_nom': rapporteur_nom,
                'grade': grade,
                'institution': institution,
                'email': email,
                'tel': tel,
            })
        
        # Passer à l'état aperçu
        self.state = 'preview'
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'import.rapporteurs.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }

    def action_confirm_import(self):
        """Confirme l'import en créant les rapporteurs dans la base de données et stocke le fichier Excel sur la soutenance"""
        for line in self.rapporteurs_lines:
            self.env['stc.rapporteur.proposition'].create({
                'soutenance_id': self.soutenance_id.id,
                'rapporteur_nom': line.rapporteur_nom,
                'grade': line.grade,
                'institution': line.institution,
                'email': line.email,
                'tel': line.tel,
            })
        
        # Stocker le fichier Excel sur la soutenance
        filename = 'rapporteurs_import_%s.xlsx' % (self.soutenance_id.name.replace(' ', '_') if self.soutenance_id.name else 'soutenance')
        self.soutenance_id.write({
            'rapporteurs_import_file': self.file,
            'rapporteurs_import_filename': filename,
        })
        
        # Poster un message dans le chatter de la soutenance
        self.soutenance_id.message_post(
            body=_('Import de %d rapporteurs effectué avec succès.') % len(self.rapporteurs_lines)
        )
        
        return {'type': 'ir.actions.act_window_close'}

    def action_back_to_import(self):
        """Retour à l'étape d'import"""
        self.state = 'import'
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'import.rapporteurs.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }


class ImportRapporteursWizardLine(models.TransientModel):
    _name = 'import.rapporteurs.wizard.line'
    _description = 'Ligne temporaire pour l\'import des rapporteurs'

    wizard_id = fields.Many2one('import.rapporteurs.wizard', string='Wizard', ondelete='cascade')
    rapporteur_nom = fields.Char(string='Nom du rapporteur', required=True)
    grade = fields.Char(string='Grade')
    institution = fields.Char(string='Institution')
    email = fields.Char(string='Email')
    tel = fields.Char(string='Téléphone')
    numero_bo = fields.Char(string="N° Bureau d'Ordre")
    date = fields.Date(string="Date") 