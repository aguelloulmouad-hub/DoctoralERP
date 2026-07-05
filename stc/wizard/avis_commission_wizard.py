from odoo import models, fields, api, _

class AvisCommissionWizard(models.TransientModel):
    _name = 'avis.commission.wizard'
    _description = "Saisir l'avis de la commission"

    soutenance_id = fields.Many2one('stc.soutenance', string='Soutenance', required=True)
    avis_commission = fields.Text(string="Avis de la commission", required=True)
    action_type = fields.Selection([
        ('valider', 'Accepter'),
        ('accepter_conditionnel', 'Accepter conditionnel'),
        ('refuser', 'Refuser'),
    ], string="Action", required=True, default='valider')
    motif_rejet = fields.Text(string="Motif du rejet")
    nb_articles = fields.Integer(string="Nombre d'articles (Scopus)")
    nb_chapter_books = fields.Integer(string="Nombre de conférences/Chapter book (Scopus)")
    nb_communications = fields.Integer(string="Nombre de communications")
    traite_par_id = fields.Many2one('stc.personnel', string="Dossier traité par")

    @api.onchange('action_type')
    def _onchange_action_type(self):
        if self.action_type != 'refuser':
            self.motif_rejet = False
        if self.action_type in ('valider', 'accepter_conditionnel'):
            self.nb_articles = self.nb_articles or 0
            self.nb_chapter_books = self.nb_chapter_books or 0
            self.nb_communications = self.nb_communications or 0
            self.traite_par_id = self.traite_par_id or False

    def action_apply(self):
        self.ensure_one()
        self.soutenance_id.avis_commission = self.avis_commission
        vals = {}
        if self.action_type == 'valider':
            vals = {
                'statut': 'rapporteurs',
                'decision_commission': _('Demande acceptée par la commission.'),
                'motif_rejet': False,
                'nb_articles': self.nb_articles,
                'nb_chapter_books': self.nb_chapter_books,
                'nb_communications': self.nb_communications,
                'traite_par_id': self.traite_par_id.id if self.traite_par_id else False,
            }
        elif self.action_type == 'accepter_conditionnel':
            vals = {
                'statut': 'rapporteurs',
                'decision_commission': _('Demande acceptée par la commission sous condition.'),
                'motif_rejet': False,
                'nb_articles': self.nb_articles,
                'nb_chapter_books': self.nb_chapter_books,
                'nb_communications': self.nb_communications,
                'traite_par_id': self.traite_par_id.id if self.traite_par_id else False,
            }
        else:
            if not self.motif_rejet:
                raise models.ValidationError(_('Veuillez saisir le motif du rejet.'))
            vals = {
                'statut': 'rejetee',
                'motif_rejet': self.motif_rejet,
                'decision_commission': _('Demande rejetée par la commission.'),
            }
        self.soutenance_id.write(vals)
        return {'type': 'ir.actions.act_window_close'} 