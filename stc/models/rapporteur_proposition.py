from odoo import models, fields, api, _
from odoo.exceptions import UserError

class RapporteurProposition(models.Model):
    _name = 'stc.rapporteur.proposition'
    _description = 'Proposition de rapporteur'

    soutenance_id = fields.Many2one('stc.soutenance', string='Soutenance')
    rapporteur_nom = fields.Char(string='Nom du rapporteur')
    fichier = fields.Binary(string='Fichier')
    filename = fields.Char(string='Nom du fichier')
    avis = fields.Selection([
        ('favorable', 'Favorable'),
        ('defavorable', 'Défavorable')
    ], string='Avis')
    grade = fields.Char(string="Grade")
    institution = fields.Char(string="Institution ou Organisme")
    email = fields.Char(string="Email")
    avis_favorable = fields.Boolean(string="Avis favorable", default=False)
    choisie = fields.Boolean(string="Choisi", default=False)
    numero_bo = fields.Char(string="N° Bureau d'Ordre")
    date = fields.Date(string="Date")
    tel = fields.Char(string="Téléphone")
    CV_fichier = fields.Binary(string="CV du rapporteur")
    CV_filename = fields.Char(string="Nom du fichier CV")


    @api.model
    def create(self, vals):
        sout_id = vals.get('soutenance_id')
        if sout_id:
            sout = self.env['stc.soutenance'].browse(sout_id)
            if sout.rapporteurs_valides:
                raise UserError(_('Les rapporteurs ont déjà été validés, vous ne pouvez plus ajouter de rapporteurs.'))
        return super(RapporteurProposition, self).create(vals)

    def write(self, vals):
        # Empêcher la modification de 'choisie' si rapporteurs_valides est True
        if 'choisie' in vals:
            for rec in self:
                if rec.soutenance_id.rapporteurs_valides:
                    raise UserError(_('Vous ne pouvez plus modifier "Choisi" après validation des rapporteurs.'))
        # Empêcher la modification de 'choisie' et 'avis_favorable' si le statut n'est pas 'rapporteurs'
        if 'choisie' in vals or 'avis_favorable' in vals:
            for rec in self:
                if rec.soutenance_id.statut != 'rapporteurs':
                    raise UserError(_('Vous ne pouvez modifier "Choisi" ou "Avis favorable" que lorsque le statut est "rapporteurs".'))
        protected_fields = {'fichier', 'filename', 'avis_favorable', 'avis'}
        if protected_fields.intersection(vals.keys()):
            for rec in self:
                if not rec.soutenance_id.rapporteurs_valides:
                    raise UserError(_('Les rapporteurs ne sont pas encore validés par le doyen. Modification interdite.'))
        return super(RapporteurProposition, self).write(vals)

    def action_toggle_avis(self):
        for rec in self:
            if rec.soutenance_id.statut != 'rapporteurs':
                raise UserError(_('Vous ne pouvez modifier l\'avis que lorsque le statut est "rapporteurs".'))
            if not rec.soutenance_id.rapporteurs_valides:
                raise UserError(_('Les rapporteurs ne sont pas encore validés, impossible de modifier l\'avis.'))
            rec.avis_favorable = not rec.avis_favorable

    def action_upload_fichier(self):
        if self.soutenance_id.statut != 'rapporteurs':
            raise UserError(_('Vous ne pouvez modifier le fichier que lorsque le statut est "rapporteurs".'))
        if not self.soutenance_id.rapporteurs_valides:
            raise UserError(_('Les rapporteurs ne sont pas encore validés, impossible d\'ajouter ou de modifier le fichier.'))
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'rapporteur.upload.fichier.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_rapporteur_id': self.id},
        }

    def action_upload_cv(self):
        if self.soutenance_id.statut != 'rapporteurs':
            raise UserError(_('Vous ne pouvez modifier le CV que lorsque le statut est "rapporteurs".'))
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'rapporteur.upload.cv.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_rapporteur_id': self.id},
        }