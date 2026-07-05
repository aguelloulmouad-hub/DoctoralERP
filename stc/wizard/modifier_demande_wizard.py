from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ModifierDemandeWizard(models.TransientModel):
    _name = 'modifier.demande.wizard'
    _description = 'Modifier une demande de soutenance'

    soutenance_id = fields.Many2one('stc.soutenance', string='Soutenance', required=True, ondelete='cascade')
    name = fields.Char(string='Titre')
    doctorant_id = fields.Many2one('stc.doctorant', string='Doctorant')
    documents_ids = fields.One2many('modifier.demande.document.wizard', 'wizard_id', string='Documents')

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        soutenance = self.env['stc.soutenance'].browse(self.env.context.get('active_id'))
        res['soutenance_id'] = soutenance.id
        res['name'] = soutenance.name
        res['doctorant_id'] = soutenance.doctorant_id.id
        # Préparer les documents existants
        document_lines = []
        for doc in soutenance.documents_ids:
            document_lines.append((0, 0, {
                'document_id': doc.id,
                'typedoc_id': doc.typedoc_id.id,
                'fichier': doc.fichier,
                'filename': doc.filename,
            }))
        res['documents_ids'] = document_lines
        return res

    def action_apply(self):
        self.ensure_one()
        self.soutenance_id.write({
            'name': self.name,
            'doctorant_id': self.doctorant_id.id,
        })
        # Gestion suppression :
        doc_ids_initial = set(self.soutenance_id.documents_ids.ids)
        doc_ids_wizard = set([doc_wizard.document_id.id for doc_wizard in self.documents_ids if doc_wizard.document_id])
        # Mettre à jour ou créer les documents
        for doc_wizard in self.documents_ids:
            if doc_wizard.document_id:
                vals = {
                    'typedoc_id': doc_wizard.typedoc_id.id,
                }
                if doc_wizard.fichier:
                    vals['fichier'] = doc_wizard.fichier
                if doc_wizard.filename:
                    vals['filename'] = doc_wizard.filename
                doc_wizard.document_id.write(vals)
            else:
                # Création d'un nouveau document si pas de document_id
                if doc_wizard.fichier:
                    self.env['stc.document'].create({
                        'typedoc_id': doc_wizard.typedoc_id.id,
                        'fichier': doc_wizard.fichier,
                        'filename': doc_wizard.filename,
                        'soutenance_id': self.soutenance_id.id,
                        'doctorant_id': self.soutenance_id.doctorant_id.id,
                    })
        # Suppression des documents retirés dans le wizard
        docs_to_unlink = doc_ids_initial - doc_ids_wizard
        if docs_to_unlink:
            self.env['stc.document'].browse(list(docs_to_unlink)).unlink()
        return {'type': 'ir.actions.act_window_close'}

class ModifierDemandeDocumentWizard(models.TransientModel):
    _name = 'modifier.demande.document.wizard'
    _description = 'Document du wizard de modification de demande'

    wizard_id = fields.Many2one('modifier.demande.wizard', string='Wizard')
    document_id = fields.Many2one('stc.document', string='Document lié')
    typedoc_id = fields.Many2one('stc.document_type', string='Type de document')
    fichier = fields.Binary(string='Fichier')
    filename = fields.Char(string='Nom du fichier')

    @api.onchange('fichier', 'typedoc_id')
    def _onchange_fichier(self):
        if self.fichier:
            # Récupérer le nom du type de document
            type_doc = self.typedoc_id.name if self.typedoc_id else 'document'
            # Récupérer le nom du doctorant via le wizard parent
            doctorant_nom = self.wizard_id.doctorant_id.name or 'doctorant'
            # Récupérer l'extension réelle du fichier uploadé
            filename_ctx = self._context.get('filename')
            ext = '.pdf'
            if filename_ctx:
                # On prend la partie après le dernier point
                if '.' in filename_ctx:
                    ext = filename_ctx[filename_ctx.rfind('.'):]
            # Générer le nom du fichier
            self.filename = f'{type_doc}_{doctorant_nom}{ext}'
        else:
            self.filename = False
