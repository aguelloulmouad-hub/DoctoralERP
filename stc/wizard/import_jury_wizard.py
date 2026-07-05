from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
import io
import xlrd
import datetime

class ImportJuryWizard(models.TransientModel):
    _name = 'import.jury.wizard'
    _description = 'Importer les jurys depuis un fichier Excel'

    soutenance_id = fields.Many2one('stc.soutenance', string='Soutenance', required=True, ondelete='cascade')
    file = fields.Binary(string='Fichier Excel (.xlsx)', required=True)
    jury_lines = fields.One2many('import.jury.wizard.line', 'wizard_id', string='Membres du jury à importer')
    date_soutenance = fields.Date(string='Date de soutenance')
    lieu = fields.Char(string='Lieu de soutenance')
    state = fields.Selection([
        ('import', 'Import'),
        ('preview', 'Aperçu')
    ], string='État', default='import')

    def action_import(self):
        """Lit le fichier Excel et prépare les données pour l'aperçu (nouveau format)"""
        if not self.file:
            raise UserError(_('Veuillez sélectionner un fichier.'))
        
        # Supprimer les lignes existantes
        self.jury_lines.unlink()
        
        file_data = base64.b64decode(self.file)
        workbook = xlrd.open_workbook(file_contents=file_data)
        sheet = workbook.sheet_by_index(0)

        # Lire la planification dans les lignes 1 et 2 (A2, B2, A3, B3)
        try:
            date_soutenance = sheet.cell(1, 1).value  # B2
            if isinstance(date_soutenance, float):
                date_tuple = xlrd.xldate_as_tuple(date_soutenance, workbook.datemode)
                date_soutenance_str = '%04d-%02d-%02d' % (date_tuple[0], date_tuple[1], date_tuple[2])
                self.date_soutenance = date_soutenance_str
            else:
                self.date_soutenance = date_soutenance
            lieu = sheet.cell(2, 1).value  # B3
        except Exception:
            self.date_soutenance = ''
            lieu = ''
        self.lieu = lieu

        # La table jury commence à la ligne 6 (header), les membres à partir de la ligne 7
        for row_idx in range(6, sheet.nrows):
            nom = sheet.cell(row_idx, 0).value
            nom_ar = sheet.cell(row_idx, 1).value
            grade = sheet.cell(row_idx, 2).value
            institution = sheet.cell(row_idx, 3).value
            email = sheet.cell(row_idx, 4).value
            tel = sheet.cell(row_idx, 5).value if sheet.ncols > 5 else ''
            tel = str(tel) if tel else ''
            if tel.endswith('.0'):
                tel = tel[:-2]
            role = sheet.cell(row_idx, 6).value if sheet.ncols > 6 else ''
            if not nom or not role:
                continue
            self.env['import.jury.wizard.line'].create({
                'wizard_id': self.id,
                'nom': nom,
                'nom_ar': nom_ar,
                'grade': grade,
                'institution': institution,
                'email': email,
                'tel': tel,
                'role': role,
            })
        self.state = 'preview'
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'import.jury.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }

    def action_confirm_import(self):
        """Confirme l'import en créant les membres du jury dans la base de données et stocke le fichier Excel sur la soutenance"""
        # Créer les membres du jury
        for line in self.jury_lines:
            self.env['stc.jury'].create({
                'soutenance_id': self.soutenance_id.id,
                'nom': line.nom,
                'nom_ar': line.nom_ar,
                'grade': line.grade,
                'institution': line.institution,
                'email': line.email,
                'tel': line.tel,
                'role': line.role,
            })
        
        # Mettre à jour la date et le lieu de la soutenance
        vals = {}
        if self.date_soutenance:
            vals['date_soutenance'] = self.date_soutenance
        if self.lieu:
            vals['lieu'] = self.lieu
        if vals:
            self.soutenance_id.write(vals)
        
        # Stocker le fichier Excel sur la soutenance
        filename = 'jury_import_%s.xlsx' % (self.soutenance_id.name.replace(' ', '_') if self.soutenance_id.name else 'soutenance')
        self.soutenance_id.write({
            'jury_import_file': self.file,
            'jury_import_filename': filename,
        })
        
        # Poster un message dans le chatter de la soutenance
        message = _('Import de %d membres du jury et de la planification effectué avec succès.') % len(self.jury_lines)
        if self.date_soutenance or self.lieu:
            message += _(' Planification mise à jour.')
        self.soutenance_id.message_post(body=message)
        
        return {'type': 'ir.actions.act_window_close'}

    def action_back_to_import(self):
        """Retour à l'étape d'import"""
        self.state = 'import'
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'import.jury.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }


class ImportJuryWizardLine(models.TransientModel):
    _name = 'import.jury.wizard.line'
    _description = 'Ligne temporaire pour l\'import des membres du jury'

    wizard_id = fields.Many2one('import.jury.wizard', string='Wizard', ondelete='cascade')
    nom = fields.Char(string='Nom', required=True)
    nom_ar = fields.Char(string='Nom (arabe)')
    grade = fields.Char(string='Grade')
    institution = fields.Char(string='Institution')
    email = fields.Char(string='Email')
    tel = fields.Char(string='Téléphone')
    role = fields.Char(string='Rôle', required=True)
    role_par_ced = fields.Many2one('stc.role', string='Rôle validé par le CED')
    numero_bo = fields.Char(string="N° Bureau d'Ordre")
    date = fields.Date(string="Date") 