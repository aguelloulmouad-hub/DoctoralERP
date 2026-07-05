from odoo import api, models, fields, _
import logging
from odoo.exceptions import UserError
import base64
import os
from odoo.modules.module import get_module_path

class Soutenance(models.Model):
    _name = 'stc.soutenance'
    _description = 'Soutenance de Thèse'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Titre')
    doctorant_id = fields.Many2one('stc.doctorant', string='Doctorant')
    date_soutenance = fields.Date(string='Date de soutenance')
    lieu = fields.Char(string='Lieu')
    rapporteurs_valides = fields.Boolean(string='Rapporteurs validés', default=False)
    jurys_valides = fields.Boolean(string='Jurys validés', default=False)
    jurys_ced_valides = fields.Boolean(string='Jurys validés CED', default=False)

    statut = fields.Selection([
        ('brouillon', 'Déposée'),
        ('en_commission', 'Commission'),
        ('rapporteurs', 'Rapporteurs'),
        ('jury_et_planification', 'Jury et Planification'),
        ('planifie', 'Planifiée'),
        ('fermee', 'Fermée'),
        ('rejetee', 'Rejetée'),
    ], string='Statut', default='brouillon')
    note = fields.Text(string='Note')
    motif_rejet = fields.Text(string='Motif du rejet')
    decision_commission = fields.Text(string='Décision de la commission')
    avis_commission = fields.Text(string="Avis de la commission")
    documents_ids = fields.One2many('stc.document', 'soutenance_id', string='Documents')
    rapporteurs_ids = fields.One2many('stc.rapporteur.proposition', 'soutenance_id', string='Propositions de rapporteurs')
    jurys_ids = fields.One2many('stc.jury', 'soutenance_id', string='Jurys')
    diplome_id = fields.One2many('stc.diplome', 'soutenance_id', string='Diplômes')
    encadrant_id = fields.Many2one(
        'stc.personnel',
        string="Encadrant",
        related='doctorant_id.encadrant_id',
        store=True,
        readonly=True,
    )
    encardrant_email = fields.Char(
        string="Email de l'encadrant",
        related='doctorant_id.encadrant_id.email',
        store=True,
        readonly=True,
    )
    mention = fields.Char(string="Mention")
    resultat = fields.Char(string="Résultat")
    specialite_id = fields.Many2one('stc.specialite', string="Spécialité")
    discipline_id = fields.Many2one('stc.discipline', string="Discipline")

    session_id = fields.Many2one('stc.session', string='Session', readonly=True)

    nb_articles = fields.Integer(string="Nombre d'articles (Scopus)")
    nb_chapter_books = fields.Integer(string="Nombre de conférences/Chapter book (Scopus)")
    nb_communications = fields.Integer(string="Nombre de communications")
    traite_par_id = fields.Many2one('stc.personnel', string="Dossier traité par")

    rapporteurs_import_file = fields.Binary(string="Fichier Excel rapporteurs importé")
    rapporteurs_import_filename = fields.Char(string="Nom du fichier Excel rapporteurs")

    jury_import_file = fields.Binary(string="Fichier Excel jury importé")
    jury_import_filename = fields.Char(string="Nom du fichier Excel jury")

    @api.model
    def create(self, vals):
        if not vals.get('session_id'):
            session = self.env['stc.session'].search([('statut', '=', 'ouverte')], limit=1)
            if session:
                vals['session_id'] = session.id
        return super(Soutenance, self).create(vals)

    @api.multi
    def action_soumettre_demande(self):
        for record in self:
            doc_types = self.env['stc.document_type'].search([('obligatoire', '=', True)])
            for doc_type in doc_types:
                if not record.documents_ids.filtered(lambda d: d.typedoc_id == doc_type):
                    raise UserError(_("Le document obligatoire '%s' n'est pas fourni.") % doc_type.name)
            record.statut = 'brouillon'

    # --- BROUILLON ---
    @api.multi
    def action_modifier_demande(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'modifier.demande.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('stc.view_modifier_demande_wizard_form').id,
            'target': 'new',
            'context': {'active_id': self.id},
        }

    @api.multi
    def action_valider_ced(self):
        for record in self:
            # Vérification intitulé
            if not record.name:
                raise UserError(_('Veuillez renseigner l\'intitulé de la thèse.'))
            # Vérification doctorant
            if not record.doctorant_id:
                raise UserError(_('Veuillez sélectionner le doctorant.'))
            # Vérification documents obligatoires
            doc_types = self.env['stc.document_type'].search([('obligatoire', '=', True)])
            for doc_type in doc_types:
                if not record.documents_ids.filtered(lambda d: d.typedoc_id == doc_type):
                    raise UserError(_("Le document obligatoire '%s' n'est pas fourni.") % doc_type.name)
            record.statut = 'en_commission'

    @api.multi
    def action_refuser_ced(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'refus.ced.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_soutenance_id': self.id},
        }

    # --- en_co ---
    @api.multi
    def action_valider_commission(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'avis.commission.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_soutenance_id': self.id},
        }

    @api.multi
    def action_refuser_commission(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'avis.commission.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_soutenance_id': self.id},
        }

    @api.multi
    def action_annuler_ced(self):
        for record in self:
            record.statut = 'brouillon'
            record.motif_rejet = ''

    # --- rapporteurs ---
    @api.multi
    def action_importer_rapporteurs(self):
        self.ensure_one()
        if self.rapporteurs_valides:
            raise UserError(_('Les rapporteurs ont déjà été validés et il n\'est plus possible d\'en importer.'))
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'import.rapporteurs.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_soutenance_id': self.id},
        }

    @api.multi
    def action_envoyer_invitations(self):
        """Génère le PDF d'invitation et l'envoie par email à chaque rapporteur via un template."""
        self.ensure_one() 
        template = self.env.ref('stc.mail_template_rapporteur_invitation')
        report_action = self.env.ref('stc.action_report_rapporteur_invitation')

        if self.statut != 'rapporteurs':
            raise UserError(_('Le statut doit être "Accepté Commission" pour envoyer les invitations.'))
        if not self.rapporteurs_valides:
            raise UserError(_('Les rapporteurs doivent être validés par le doyen avant l\'envoi des invitations.'))

        for rapp in self.rapporteurs_ids.filtered(lambda r: r.email and r.choisie):
            # Générer le PDF du rapport d'invitation pour un seul rapporteur
            pdf_bytes, _discard = report_action.render_qweb_pdf(self.id, data={'rapporteur_id': rapp.id})
            pdf_b64 = base64.b64encode(pdf_bytes)
            
            attachment_name = 'Invitation_Rapporteur_%s.pdf' % (rapp.rapporteur_nom or 'SansNom')
            attachment = self.env['ir.attachment'].create({
                'name': attachment_name,
                'type': 'binary',
                'datas': pdf_b64,
                'datas_fname': attachment_name,
                'res_model': 'mail.message',
                'res_id': 0
            })
            
            email_values = {
                'attachment_ids': [attachment.id]
            }

            # Envoyer l'email avec la pièce jointe
            template.send_mail(rapp.id, force_send=True, email_values=email_values)

        self.message_post(body=_('Invitations envoyées aux rapporteurs.'))
        return True

    @api.multi
    def action_modifier_rapporteurs(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'modifier.rapporteurs.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_id': self.id},
        }

    @api.multi
    def action_ajouter_rapporteurs(self):
        self.ensure_one()
        if self.rapporteurs_valides:
            raise UserError(_('Les rapporteurs ont déjà été validés et il n\'est plus possible d\'en ajouter.'))
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'ajout.rapporteurs.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_soutenance_id': self.id},
        }

    @api.multi
    def action_valider_rapporteurs_doyen(self):
        self.ensure_one()
        choisis = self.rapporteurs_ids.filtered(lambda r: r.choisie)
        if len(choisis) != 3:
            raise UserError(_('Il doit y avoir exactement 3 rapporteurs choisis pour valider cette étape.'))
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'confirmation.valider.rapporteurs.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_soutenance_id': self.id},
        }

    @api.multi
    def action_valider_rapporteurs_ced(self):
        for record in self:
            choisis = record.rapporteurs_ids.filtered(lambda r: r.choisie)
            if len(choisis) != 3:
                raise UserError(_('Il doit y avoir exactement 3 rapporteurs choisis pour valider cette étape.'))
            if not all(r.avis_favorable for r in choisis):
                raise UserError(_('Tous les rapporteurs choisis doivent avoir un avis favorable pour passer à l\'étape suivante.'))
            if not record.rapporteurs_valides:
                raise UserError(_('Les rapporteurs doivent être validés par le doyen avant de passer à l\'étape suivante.'))
            record.statut = 'jury_et_planification'

    # --- JURY_ET_PLANIFICATION ---
    @api.multi
    def action_importer_jury_planification(self):
        self.ensure_one()
        if self.jurys_valides:
            raise UserError(_('Le jury et la planification ont déjà été validés et ne peut plus être modifiés.'))
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'import.jury.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_soutenance_id': self.id},
        }

    @api.multi
    def action_envoyer_convocations(self):
        """Génère la convocation jury et l'envoie à chaque membre du jury via un template."""
        self.ensure_one()
        template = self.env.ref('stc.mail_template_jury_convocation')
        report_action = self.env.ref('stc.action_report_jury_convocation')

        if self.statut != 'jury_et_planification':
            raise UserError(_('Le statut doit être "Jury et Planification" pour envoyer les convocations.'))
        if not self.jurys_valides:
            raise UserError(_('Le jury doit être validé par le doyen avant l\'envoi des convocations.'))

        for jury in self.jurys_ids.filtered(lambda j: j.email):
            # Générer le PDF
            pdf_bytes, _discard = report_action.render_qweb_pdf(self.id, data={'jury_id': jury.id})
            pdf_b64 = base64.b64encode(pdf_bytes)
            
            attachment_name = 'Convocation_Jury_%s.pdf' % (jury.nom or 'SansNom')
            attachment = self.env['ir.attachment'].create({
                'name': attachment_name,
                'type': 'binary',
                'datas': pdf_b64,
                'datas_fname': attachment_name,
                'res_model': 'mail.message',
                'res_id': 0
            })
            
            email_values = {
                'attachment_ids': [attachment.id]
            }

            # Envoyer l'email
            template.send_mail(jury.id, force_send=True, email_values=email_values)

        self.message_post(body=_('Convocations envoyées au jury.'))
        return True

    @api.multi
    def action_modifier_jury(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'modifier.jury.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_id': self.id},
        }

    @api.multi
    def action_modifier_planification(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'modifier.planification.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_id': self.id},
        }

    @api.multi
    def action_ajouter_jury(self):
        self.ensure_one()
        if self.jurys_valides:
            raise UserError(_('Le jury a déjà été validé et il n\'est plus possible d\'en ajouter.'))
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'ajout.jury.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_soutenance_id': self.id},
        }

    @api.multi
    def action_ajouter_planification(self):
        self.ensure_one()
        if self.jurys_valides:
            raise UserError(_('La planification a déjà été validée et il n\'est plus possible d\'en ajouter.'))
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'ajout.planification.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_soutenance_id': self.id},
        }

    @api.multi
    def action_annuler_commission(self):
        """Ramène la soutenance à l'étape rapporteurs et nettoie les données déjà saisies
        (rapporteurs, jury, planification) pour repartir proprement.
        """
        for record in self:
            # Supprimer rapporteurs et jury existants
            if record.rapporteurs_ids:
                record.rapporteurs_ids.unlink()
            if record.jurys_ids:
                record.jurys_ids.unlink()
            # Réinitialiser la planification (date et lieu)
            record.date_soutenance = False
            record.lieu = False
            # Réinitialiser les validations
            record.rapporteurs_valides = False
            record.jurys_valides = False

            # Réinitialiser les champs de décision et repasser au statut adéquat
            record.statut = 'en_commission'
            record.motif_rejet = ''
            record.decision_commission = ''


    @api.multi
    def action_valider_jury_et_planification_doyen(self):
        self.ensure_one()
        if not self.date_soutenance or not self.lieu:
            raise UserError(_('La date et le lieu de la soutenance doivent être renseignés pour valider cette étape.'))
        if not self.jurys_ids:
            raise UserError(_('Au moins un membre du jury doit être renseigné pour valider cette étape.'))
        if any(not jury.role_par_ced for jury in self.jurys_ids):
            raise UserError(_('Chaque membre du jury doit avoir un rôle validé par le CED (champ "Rôle validé par le CED").'))
        if not self.jurys_ced_valides:
            raise UserError(_('Le jury doit être validé par le CED avant d\'être validé par le doyen.'))
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'confirmation.valider.jury.planification.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_soutenance_id': self.id},
        }
    
    @api.multi
    def action_valider_jury_et_planification_ced(self):
        self.ensure_one()
        if not self.date_soutenance or not self.lieu:
            raise UserError(_('La date et le lieu de la soutenance doivent être renseignés pour valider cette étape.'))
        if not self.jurys_ids:
            raise UserError(_('Au moins un membre du jury doit être renseigné pour valider cette étape.'))
        if any(not jury.role_par_ced for jury in self.jurys_ids):
            raise UserError(_('Chaque membre du jury doit avoir un rôle validé par le CED (champ "Rôle validé par le CED").'))
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'confirmation.valider.jury.planification.ced.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_soutenance_id': self.id},
        }

    @api.multi
    def action_planifie(self):
        for record in self:
            if not record.date_soutenance or not record.lieu:
                raise UserError(_('La date et le lieu de la soutenance doivent être renseignés.'))
            if not record.jurys_ids:
                raise UserError(_('Au moins un membre du jury doit être renseigné.'))
            if not record.jurys_valides:
                raise UserError(_('Le jury doit être validé par le doyen avant de planifier la soutenance.'))
            record.statut = 'planifie'

    # --- PLANIFIE ---
    @api.multi
    def action_entrer_resultat_soutenance(self):
        """Ouvre un wizard pour saisir le résultat et la mention de la soutenance."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'entrer.resultat.soutenance.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_soutenance_id': self.id},
        }

    # --- PLANIFIE ---
    @api.multi
    def action_resultat_soutenance(self):
        for record in self:
            if not record.resultat:
                raise UserError(_('Veuillez renseigner le résultat de la soutenance avant de la fermer.'))
            record.statut = 'fermee'

    # --- FERMEE ---
    @api.multi
    def action_generer_diplome_finale(self):
        # TODO: Générer diplôme final à la demande (print)
        pass

    # --- REJETEE ---
    # Pas d'action spécifique, affichage du motif de rejet

    @api.multi
    def action_informer_directeur_these(self):
        """Envoie un email à l'encadrant pour l'informer de proposer 6 rapporteurs, avec le fichier rapporteurs.xlsx en pièce jointe."""
        self.ensure_one()
        template = self.env.ref('stc.mail_template_rapporteurs_directeur')
        # Chemin du fichier rapporteurs.xlsx dans le module
        module_path = get_module_path('stc')
        fichier_path = os.path.join(module_path, 'static', 'src', 'rapporteurs.xlsx')
        try:
            with open(fichier_path, 'rb') as f:
                fichier_data = f.read()
        except Exception as e:
            raise UserError(_('Impossible de lire le fichier rapporteurs.xlsx : %s') % e)
        fichier_b64 = base64.b64encode(fichier_data)
        attachment = self.env['ir.attachment'].create({
            'name': 'rapporteurs.xlsx',
            'type': 'binary',
            'datas': fichier_b64,
            'datas_fname': 'rapporteurs.xlsx',
            'res_model': 'mail.message',
            'res_id': 0
        })
        email_values = {
            'attachment_ids': [attachment.id]
        }
        template.send_mail(self.id, force_send=True, email_values=email_values)
        self.message_post(body=_('Email envoyé à l\'encadrant pour la proposition des rapporteurs.'))
        return True

    @api.multi
    def action_informer_directeur_these_jury(self):
        """Envoie un email à l'encadrant pour l'informer de proposer une composition de jury, avec le fichier jury.xlsx en pièce jointe."""
        self.ensure_one()
        template = self.env.ref('stc.mail_template_jury_directeur')
        module_path = get_module_path('stc')
        fichier_path = os.path.join(module_path, 'static', 'src', 'jury.xlsx')
        try:
            with open(fichier_path, 'rb') as f:
                fichier_data = f.read()
        except Exception as e:
            raise UserError(_('Impossible de lire le fichier jury.xlsx : %s') % e)
        fichier_b64 = base64.b64encode(fichier_data)
        attachment = self.env['ir.attachment'].create({
            'name': 'jury.xlsx',
            'type': 'binary',
            'datas': fichier_b64,
            'datas_fname': 'jury.xlsx',
            'res_model': 'mail.message',
            'res_id': 0
        })
        email_values = {
            'attachment_ids': [attachment.id]
        }
        template.send_mail(self.id, force_send=True, email_values=email_values)
        self.message_post(body=_('Email envoyé à l\'encadrant pour la proposition du jury.'))
        return True