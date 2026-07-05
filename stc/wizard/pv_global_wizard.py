import base64
import io
import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError

try:
    import xlwt
except ImportError:
    xlwt = None

class PVGlobalWizard(models.TransientModel):
    _name = 'pv.global.wizard'
    _description = 'Génération du PV global Excel'

    datas = fields.Binary('Fichier Excel', readonly=True)
    filename = fields.Char('Nom du fichier', default='PV_global.xls')

    def action_generate_excel(self):
        if not xlwt:
            raise UserError(_('Le module python xlwt doit être installé.'))
        output = io.BytesIO()
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet('PV Global')
        # En-têtes
        headers = [
            'N°', 'CNIE', 'Nom et Prénom', 'Email', 'Telephone', 'Titre de la thèse',
            'Directeur de thèse', 'Email2', 'Telephone2', 'Co-directeur de thèse',
            'Structure de recherche d\'accueil', 'Formation doctorale',
            'Date de la 1ère Inscription', 'Avis de la commission de Thèse'
        ]
        for col, h in enumerate(headers):
            sheet.write(0, col, h)
        # Recherche des soutenances
        soutenances = self.env['stc.soutenance'].search([
            ('statut', 'in', ['en_commission'])
        ])
        # Préparer les données avec la date d'inscription calculée pour le tri
        annee_actuelle = datetime.datetime.now().year
        soutenances_data = []
        for idx, s in enumerate(soutenances, 1):
            doctorant = s.doctorant_id
            code = doctorant.code or ''
            try:
                derniere_val = int(code[-1]) if code and code[-1].isdigit() else 0
                annee_inscription = annee_actuelle - derniere_val if derniere_val else None
            except Exception:
                annee_inscription = None
            soutenances_data.append((s, annee_inscription, idx))
        # Trier par année d'inscription (None à la fin)
        soutenances_data.sort(key=lambda x: (x[1] is None, x[1]))
        row = 1
        for idx, (s, annee_inscription, orig_idx) in enumerate(soutenances_data, 1):
            doctorant = s.doctorant_id
            encadrant = doctorant.encadrant_id
            sheet.write(row, 0, idx)
            sheet.write(row, 1, getattr(doctorant, 'cnie', '') or '')
            nom_prenom = doctorant.name
            if hasattr(doctorant, 'prenom') and doctorant.prenom:
                nom_prenom += ' ' + doctorant.prenom
            sheet.write(row, 2, nom_prenom)
            sheet.write(row, 3, getattr(doctorant, 'email', '') or '')
            sheet.write(row, 4, getattr(doctorant, 'telephone', '') or '')
            sheet.write(row, 5, s.name or '')
            dir_nom = encadrant.name if encadrant else ''
            if encadrant and hasattr(encadrant, 'prenom') and encadrant.prenom:
                dir_nom += ' ' + encadrant.prenom
            sheet.write(row, 6, dir_nom)
            sheet.write(row, 7, getattr(encadrant, 'email', '') if encadrant else '')
            sheet.write(row, 8, getattr(encadrant, 'telephone', '') if encadrant else '')
            sheet.write(row, 9, '')  # Co-directeur de thèse
            sheet.write(row, 10, '') # Structure de recherche d'accueil
            code = doctorant.code or ''
            formation_doctorale = code[:-1] if code and len(code) > 1 else ''
            sheet.write(row, 11, formation_doctorale)
            sheet.write(row, 12, str(annee_inscription) if annee_inscription else '')
            sheet.write(row, 13, s.avis_commission or '')
            row += 1
        workbook.save(output)
        output.seek(0)
        self.datas = base64.b64encode(output.read())
        self.filename = 'PV_global.xls'
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        } 