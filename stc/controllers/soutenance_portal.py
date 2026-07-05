from odoo import http
from odoo.http import request
import logging
import base64

_logger = logging.getLogger(__name__)

class SoutenancePortal(http.Controller):

    @http.route('/soutenance/demande', type='http', auth='public', website=True)
    def soutenance_form(self, **kw):
        user = request.env.user
        doctorant = None
        if user._is_public():
            doctorant = request.env['stc.doctorant'].sudo().search([('name', '=', 'Doctorant Démo')], limit=1)
        else:
            doctorant = request.env['stc.doctorant'].sudo().search([('user_id', '=', user.id)], limit=1)
            if not doctorant:
                doctorant = request.env['stc.doctorant'].sudo().search([('name', '=', 'Doctorant Démo')], limit=1)
        session = request.env['stc.session'].sudo().search([('statut', '=', 'ouverte')], limit=1)
        if not session:
            return request.render('stc.soutenance_no_session_template', {})
        return request.render('stc.soutenance_form_template', {
            'doc_types': request.env['stc.document_type'].sudo().search([('obligatoire', '=', True)]),
            'user_name': doctorant.name if doctorant else 'Doctorant Démo',
            'encadrant_nom': doctorant.encadrant_id.name if doctorant and doctorant.encadrant_id else 'Pr. Encadrant Test',
            'doctorant_id': doctorant.id if doctorant else '',
            'session_id': session.id if session else '',
            'session_name': session.name if session else '',
        })

    @http.route('/soutenance/demande/submit', type='http', auth='public', website=True, csrf=True)
    def soutenance_form_submit(self, **post):
        user = request.env.user
        session = request.env['stc.session'].sudo().search([('statut', '=', 'ouverte')], limit=1)
        if not session:
            return request.render('stc.soutenance_no_session_template', {})
        if user._is_public():
            doctorant = request.env['stc.doctorant'].sudo().search([('name', '=', 'Doctorant Démo')], limit=1)
        else:
            doctorant = request.env['stc.doctorant'].sudo().search([('user_id', '=', user.id)], limit=1)
        doctorant_id = int(post.get('doctorant_id')) if post.get('doctorant_id') else (doctorant.id if doctorant else False)
        session_id = session.id if session else False
        _logger.info('doctorant_id reçu: %s', doctorant_id)
        vals = {
            'name': post.get('name'),
            'doctorant_id': doctorant_id,
            'note': post.get('note'),
            'statut': 'brouillon',
            'session_id': session_id,
        }
        soutenance = request.env['stc.soutenance'].sudo().create(vals)
        # Traiter les fichiers uploadés
        for doc_type in request.env['stc.document_type'].sudo().search([('obligatoire', '=', True)]):
            file = post.get('file_%s' % doc_type.id)
            if file:
                file.seek(0)
                data = file.read()
                data_b64 = base64.b64encode(data)
                _logger.info('Taille du fichier uploadé (avant base64) : %s octets', len(data))
                request.env['stc.document'].sudo().create({
                    'soutenance_id': soutenance.id,
                    'typedoc_id': doc_type.id,
                    'fichier': data_b64,
                    'filename': getattr(file, 'filename', 'document_uploadé.pdf'),
                    'doctorant_id': doctorant_id,
                })
        return request.render('stc.soutenance_form_success', {})

    @http.route('/soutenance/mes_demandes', type='http', auth='public', website=True)
    def soutenance_list(self, **kw):
        """Affiche la liste des demandes de soutenance du doctorant connecté."""
        user = request.env.user
        if user._is_public():
            doctorant = request.env['stc.doctorant'].sudo().search([('name', '=', 'Doctorant Démo')], limit=1)
        else:
            doctorant = request.env['stc.doctorant'].sudo().search([('user_id', '=', user.id)], limit=1)
            if not doctorant:
                doctorant = request.env['stc.doctorant'].sudo().search([('name', '=', 'Doctorant Démo')], limit=1)

        docs = request.env['stc.soutenance'].sudo().search([('doctorant_id', '=', doctorant.id)]) if doctorant else []
        return request.render('stc.soutenance_list_template', {
            'docs': docs,
        }) 