from odoo import models, fields, api  # type: ignore

_STATE = ([
    ('brouillon', 'Brouillon'),
    ('diffuse', 'Diffusé'),
    ('realise', 'Réalisé'),
])


class is_prise_avance(models.Model):
    _name='is.prise.avance'
    _inherit     = ["portal.mixin", "mail.thread", "mail.activity.mixin", "utm.mixin"]
    _description="Prise d'avance"
    _rec_name = "num_moule_id"
    _order='num_moule_id'

    num_moule_id                = fields.Many2one('is.mold', 'Numéro du moule', required=True, tracking=True)
    num_moule_id_ro             = fields.Boolean('num_moule_ro', compute='_compute_ro', readonly=True, store=False)
    active                      = fields.Boolean('Actif', default=True, tracking=True)
    user_id                     = fields.Many2one('res.users', 'Demandeur', tracking=True, default=lambda self: self.env.uid)
    user_id_ro                  = fields.Boolean('user_id_ro', compute='_compute_ro', readonly=True, store=False)
    user_id_vsb                 = fields.Boolean('user_id_vsb', compute='_compute_vsb', readonly=True, store=False)
    resp_prise_avance_id        = fields.Many2one('res.users', "Responsable de la prise d'avance", tracking=True)
    resp_prise_avance_id_ro     = fields.Boolean('resp_prise_avance_id_ro', compute="_compute_ro", readonly=True, store=False)
    motif_prise_avance          = fields.Selection([('m', 'Modification outillage'), ('t', 'Transfert outillage')], "Motif de la prise d'avance", tracking=True)
    motif_prise_avance_ro       = fields.Boolean('motif_prise_avance_ro', compute="_compute_ro", readonly=True, store=False)
    immobilisation              = fields.Boolean("Immobilisation complète", tracking=True)
    immobilisation_ro           = fields.Boolean('immobilisation_ro', compute="_compute_ro", readonly=True, store=False)
    immobilisation_vsb          = fields.Boolean('immobilisation_vsb', compute="_compute_vsb", readonly=True, store=False)
    pieces_modif                = fields.Boolean("Pièces avant modification livrables", tracking=True)
    pieces_modif_ro             = fields.Boolean("pieces_modif_ro", compute="_compute_ro", readonly=True, store=False)
    pieces_modif_vsb            = fields.Boolean("pieces_modif_vsb", compute="_compute_vsb", readonly=True, store=False)
    duree_immobilisation        = fields.Integer(string="Durée de l'immobilisation en jours ouvrables")
    duree_immobilisation_ro     = fields.Boolean("duree_immobilisation_ro", compute="_compute_ro", readonly=True, store=False)
    duree_immobilisation_vsb    = fields.Boolean("duree_immobilisation_vsb", compute="_compute_vsb", readonly=True, store=False)
    nb_jours                    = fields.Integer(string="Nombre de jours à couvrir", tracking=True)
    nb_jours_ro                 = fields.Boolean("nb_jours_ro", compute="_compute_ro", readonly=True, store=False)
    nb_jours_vsb                = fields.Boolean("nb_jours_vsb", compute="_compute_vsb", readonly=True, store=False)
    pieces_stck                 = fields.Integer(string="Nombre de pièces à avoir en stock à la fin de la prise d'avance", tracking=True)
    pieces_stck_ro              = fields.Boolean('pieces_stck_ro', compute='_compute_ro', readonly=True, store=False)
    pieces_stck_vsb             = fields.Boolean('pieces_stck_vsb' , compute='_compute_vsb', readonly=True, store=False)
    date_outillage              = fields.Date("Date de mise à disposition de l'outillage", tracking=True)
    date_outillage_ro           = fields.Boolean("date_outillage_ro", compute="_compute_ro", readonly=True, store=False)
    date_outillage_vsb          = fields.Boolean("date_outillage_vsb", compute="_compute_vsb", readonly=True, store=False)
    date_retour_outillage       = fields.Date("Date de retour souhaité de l'outillage", tracking=True)
    date_retour_outillage_ro    = fields.Boolean("date_retour_outillage_ro", compute="_compute_ro", readonly=True, store=False)
    date_retour_outillage_vsb   = fields.Boolean("date_retour_outillage_vsb", compute="_compute_vsb", readonly=True, store=False)
    state                       = fields.Selection(_STATE, "Etat", default=_STATE[0][0], required=True, tracking=True)
    dynacase_id                 = fields.Integer(string="Id Dynacase", index=True, copy=False)

    @api.depends("state")
    def _compute_ro(self):
        is_commerciaux = self.env['res.users'].has_group('is_plastigray16.is_commerciaux_group')
#        is_chef_projet = self.env['res.users'].has_group('is_plastigray16.is_chef_projet_group')
        for obj in self:
            is_new = not isinstance(obj.id, int)
            print('============')
            if is_new:
                print(1)
                obj.num_moule_id_ro = False
                obj.user_id_ro = True
                obj.resp_prise_avance_id_ro = False
                obj.motif_prise_avance_ro = False
                obj.immobilisation_ro = True
                obj.duree_immobilisation_ro = True
                obj.pieces_modif_ro = True
                obj.nb_jours_ro = True
                obj.pieces_stck_ro = True
                obj.date_outillage_ro = True
                obj.date_retour_outillage_ro = True
            elif is_commerciaux and obj.state in 'brouillon':
                print(2)
                obj.num_moule_id_ro = True
                obj.user_id_ro = True
                obj.resp_prise_avance_id_ro = True
                obj.motif_prise_avance_ro = False
                obj.immobilisation_ro = False
                obj.duree_immobilisation_ro = False
                obj.pieces_modif_ro = False
                obj.nb_jours_ro = False
                obj.pieces_stck_ro = True
                obj.date_outillage_ro = True
                obj.date_retour_outillage_ro = True
            elif is_commerciaux and obj.state in 'diffuse':
                print(3)
                obj.num_moule_id_ro = True
                obj.user_id_ro = True
                obj.resp_prise_avance_id_ro = True
                obj.motif_prise_avance_ro = True
                obj.immobilisation_ro = True
                obj.duree_immobilisation_ro = True
                obj.pieces_modif_ro = True
                obj.nb_jours_ro = True
                obj.pieces_stck_ro = False
                obj.date_outillage_ro = False
                obj.date_retour_outillage_ro = False
            else:
                print(4)
                obj.num_moule_id_ro = True
                obj.user_id_ro = True
                obj.resp_prise_avance_id_ro = True
                obj.motif_prise_avance_ro = True
                obj.immobilisation_ro = True
                obj.duree_immobilisation_ro = True
                obj.pieces_modif_ro = True
                obj.nb_jours_ro = True
                obj.pieces_stck_ro = True
                obj.date_outillage_ro = True
                obj.date_retour_outillage_ro = True

    @api.depends("state")
    def _compute_vsb(self):
#        commercial  = self.env['res.users'].has_group('is_plastigray16.is_commerciaux_group')
#        chef_projet = self.env['res.users'].has_group('is_plastigray16.is_chef_projet_group')
        for obj in self:
            is_new = not isinstance(obj.id, int)
            if is_new:
                print("1a")
                obj.user_id_vsb = False
                obj.immobilisation_vsb = False
                obj.pieces_modif_vsb = False
                obj.duree_immobilisation_vsb = False
                obj.nb_jours_vsb = False
                obj.pieces_stck_vsb = True
                obj.date_outillage_vsb = True
                obj.date_retour_outillage_vsb = False
            elif obj.state == 'brouillon':
                obj.user_id_vsb = True
                obj.immobilisation_vsb = True
                obj.pieces_modif_vsb = True
                obj.duree_immobilisation_vsb = True
                obj.nb_jours_vsb = False
                obj.pieces_stck_vsb = True
                obj.date_outillage_vsb = True
                obj.date_retour_outillage_vsb = True
            elif obj.state == 'diffuse':
                print("3a", obj.state)
                obj.user_id_vsb = True
                obj.immobilisation_vsb = True
                obj.pieces_modif_vsb = True
                obj.duree_immobilisation_vsb = True
                obj.nb_jours_vsb = False
                obj.pieces_stck_vsb = True
                obj.date_outillage_vsb = True
                obj.date_retour_outillage_vsb = True
            else:
                print("4a", obj.state)
                obj.user_id_vsb = True
                obj.immobilisation_vsb = True
                obj.pieces_modif_vsb = True
                obj.duree_immobilisation_vsb = True
                obj.nb_jours_vsb = False
                obj.pieces_stck_vsb = True
                obj.date_outillage_vsb = True
                obj.date_retour_outillage_vsb = True

    def vers_diffuse_action(self):
        for obj in self:
            obj.state='diffuse'

    def vers_realise_action(self):
        for obj in self:
            obj.state='realise'

    def vers_brouillon_action(self):
        for obj in self:
            obj.state='brouillon'

    def lien_vers_dynacase_action(self):
        for obj in self:
            url="https://dynacase-rp/?sole=Y&app=FDL&action=FDL_CARD&latest=Y&id=%s"%obj.dynacase_id
            return {
                'type' : 'ir.actions.act_url',
                'url': url,
                'target': 'new',
            }
