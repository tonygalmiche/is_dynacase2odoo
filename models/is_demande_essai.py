from odoo import models, fields, api         # type: ignore


_IDENTIFICATION_PARTICULIERE=([
    ("01", "01 - YELLOW (jaune)"),            
    ("02", "02 - BLUE (bleu)"),            
    ("03", "03 - BLACK (noir)"),            
    ("04", "04 - WHITE (blanc)"),            
    ("05", "05 - PURPLE (violet)"),            
    ("06", "06 - GREY (gris)"),            
    ("07", "07 - BROWN (brun)"),            
    ("08", "08 - PINK (rose)"),            
    ("09", "09 - YELLOW (jaune)"),            
    ("10", "10 - BLUE (bleu)"),            
    ("11", "11 - BLACK (noir)"),            
    ("12", "12 - WHITE (blanc)"),            
    ("13", "13 - PURPLE (violet)"),            
    ("14", "14 - GREY (gris)"),            
    ("15", "15 - BROWN (brun)"),            
    ("16", "16 - PINK (rose)"),            
    ("17", "17 - YELLOW (jaune)"),            
])


_STATE = ([
    ('brouillon', 'Brouillon'),
    ('diffuse', 'Diffusé Planning'),
    ('planifie', 'Planifié'),
    ('cr', 'CR Essai à faire'),
    ('metrologie', 'Métrologie à faire'),
    ('termine', 'Terminé'),
    ('solde', 'Soldé'),
])


_LANG = ([
    ('FR' , 'Français'),
    ('EN' , 'Anglais'),
])

_TYPE_ESSAI = ([
    ('moule' , 'Moule'),
    ('assemblage' , 'Assemblage'),
    ('erd' , 'ERD'),
])


_ETAT_STOCK = ([
    ('obsolete' , 'Obsolètes => INFORMER le service qualité pour la destruction'),
    ('livrable' , 'Livrable'),
    ('non-applicable' , 'Non Applicable'),
])

_TEMPS_IMMOB = ([
    ('4' , '4H'),
    ('8' , '8H'),
    ('12' , '12H'),
    ('16' , '16H'),
])

_LIEN_STOCK_MAT = ([
    ('stock_usine' , 'Stock usine'),
    ('stock_be' , 'Stock BE'),
])

_NB_MO = ([
    ('25' , '0.25'),
    ('50' , '0.50'),
    ('75' , '0.75'),
    ('100' , '1'),
    ('150' , '1.5'),
    ('200' , '2'),
])


class is_demande_essai(models.Model):
    _name='is.demande.essai'
    _inherit     = ["portal.mixin", "mail.thread", "mail.activity.mixin", "utm.mixin"]
    _description="Demande d'essai"
    _rec_name = "num_essai"
    _order='create_date desc'


    @api.depends("type_essai","moule_id","dossierf_id","num_erd_id")
    def _compute_num_essai(self):
        for obj in self:
            num_seq = 1
            num_essai = False
            designation = False
            if obj.id:
                domain=[
                    ('type_essai','=',obj.type_essai),
                    ('moule_id','=',obj.moule_id.id),
                    ('dossierf_id','=',obj.dossierf_id.id),
                    ('num_erd_id','=',obj.num_erd_id.id),
                    ('id','!=',obj.id),
                ]
                docs=self.env['is.demande.essai'].search(domain,order='num_seq desc',limit=1)
                for doc in docs:
                    num_seq = doc.num_seq + 1
            if obj.moule_id:
                num_essai = "%s-%s" % (obj.moule_id.name, f"{num_seq:03d}")
                designation = obj.moule_id.designation
            if obj.dossierf_id:
                num_essai = "%s-%s" % (obj.dossierf_id.name, f"{num_seq:03d}")
                designation = obj.dossierf_id.designation
            if obj.num_erd_id:
                num_essai = "%s-%s" % (obj.num_erd_id.numero, f"{num_seq:03d}")
                designation = obj.num_erd_id.designation

            obj.num_seq     = num_seq
            obj.num_essai   = num_essai
            obj.designation = designation


    @api.depends("nb_pieces_client","nb_pieces_metrologie","nb_pieces_chef_projet")
    def _compute_nb_pieces_total(self):
        def char2int(val):
            try:
                res = int(val)
            except:
                res=0
            return res   
        for obj in self:
            obj.nb_pieces_total = char2int(obj.nb_pieces_client) + char2int(obj.nb_pieces_metrologie) + char2int(obj.nb_pieces_chef_projet)


    state                       = fields.Selection(_STATE, "Etat", default=_STATE[0][0], tracking=True)
    active                      = fields.Boolean('Actif', default=True, tracking=True)
    langue                      = fields.Selection(_LANG, "Langue", tracking=True, default='FR')
    type_essai                  = fields.Selection(_TYPE_ESSAI, "Type essai", default='moule', tracking=True)
    num_seq                     = fields.Integer('Numéro séquentiel', tracking=True, compute="_compute_num_essai", readonly=True, store=True)
    num_essai                   = fields.Char('N° essai'            , tracking=True, compute="_compute_num_essai", readonly=True, store=True)
    date                        = fields.Date("Date", default=lambda *a: fields.datetime.now(), tracking=True,copy=False)
    user_id                     = fields.Many2one("res.users", string="Demandeur", default=lambda self: self.env.uid, tracking=True,copy=False)
    moule_id                    = fields.Many2one('is.mold', string="Moule", tracking=True)
    dossierf_id                 = fields.Many2one("is.dossierf", string="Dossier F", tracking=True)
    num_erd_id                  = fields.Many2one('is.erd', string='Numéro erd', tracking=True)
    designation                 = fields.Char("Désignation", tracking=True, compute="_compute_num_essai", readonly=True, store=True)
    outillage_dispo             = fields.Boolean('Outillage disponible', default=False, tracking=True,copy=False)
    date_disp_out               = fields.Date("Date de disponibilité de l'outillage", tracking=True,copy=False)
    etat_stock                  = fields.Selection(_ETAT_STOCK, string="Etat des produits en stock", tracking=True,copy=False)
    lieu_essai_id               = fields.Many2one('is.database', string="Lieu essai", tracking=True)
    lieu_essai_autre            = fields.Char('Autre', tracking=True)
    resp_essai_id               = fields.Many2one("res.users", string="Responsable de l'essai", tracking=True)
    resp_planning_id            = fields.Many2one("res.users", string="Responsable du planning", tracking=True)
    ident_commentaire           = fields.Text('Commentaire Traçabilité')
    autres_personnes_ids        = fields.Many2many("res.users", "is_demande_essai_autres_personnes_rel", "demande_essai_id", "user_id", string="Autres personnes à informer", tracking=True)
    semaine_essai               = fields.Char("Semaine ou jour de réalisation de l'essai", tracking=True,copy=False)
    identification_cmt          = fields.Text("Commentaire", tracking=True)
    temp_immob                  = fields.Selection(_TEMPS_IMMOB, "Temps d'immobilisation", tracking=True)
    nb_pieces_par_empreinte     = fields.Char("Nombre de pièces de chaque empreinte", tracking=True)
    nb_pieces_client            = fields.Char("Nombre de pièces pour le client", tracking=True)
    nb_pieces_metrologie        = fields.Char("Nombre de pièces pour la métrologie", tracking=True)
    nb_pieces_chef_projet       = fields.Char("Nombre de pièces pour le chef de projet", tracking=True)
    nb_pieces_total             = fields.Integer("Nombre de pièces total", tracking=True, compute='_compute_nb_pieces_total', store=True, readonly=True, copy=False)
    nb_pieces_comenntaire       = fields.Text("Commentaire sur le nombre de pièces demandées (versions...)", tracking=True)
    identification_particuliere       = fields.Selection(_IDENTIFICATION_PARTICULIERE, "Identification particulière", tracking=True)
    identification_particuliere_autre = fields.Char("Identification particulière (autre)", tracking=True)
    besoin_mod                  = fields.Boolean('Besoin MOD', default=False, tracking=True)
    code_matiere_id             = fields.Many2one("is.dossier.article", "Code matière", tracking=True)
    designation_mat             = fields.Char("Désignation matière", tracking=True)
    code_matiere_recyclage      = fields.Char("Code recyclage", tracking=True)  # readonly
    lieu_stockage_matiere       = fields.Selection(_LIEN_STOCK_MAT, "Lieu de stockage de la matière", tracking=True)
    mat_disp                    = fields.Boolean('Matière disponible', tracking=True)
    mat_date_disp               = fields.Date("Date de disponibilité de la matière", tracking=True)
    code_matiere2_id            = fields.Many2one("is.dossier.article", "Code matière 2", tracking=True)
    designation_mat2            = fields.Char("Désignation matière 2", tracking=True)
    code_matiere_recyclage2     = fields.Char("Code recyclage 2", tracking=True)  # readonly
    lieu_stockage_matiere2      = fields.Selection(_LIEN_STOCK_MAT, "Lieu de stockage de la matière 2", tracking=True)
    mat_disp2                   = fields.Boolean('Matière disponible 2', tracking=True)
    mat_date_disp2              = fields.Date("Date de disponibilité de la matière 2", tracking=True)
    code_colorant_id            = fields.Many2one("is.dossier.article", "Code colorant", tracking=True)
    designation_col             = fields.Char("Désignation colorant", tracking=True)
    lieu_stockage_colorant      = fields.Selection(_LIEN_STOCK_MAT, "Lieu de stockage du colorant", tracking=True)
    pourcent_colorant           = fields.Char("% de colorant", tracking=True)
    colorant_disp               = fields.Boolean('Colorant disponible', tracking=True)
    colorant_date_disp          = fields.Date("Date de disponibilité du colorant", tracking=True)
    fiche_tech_mat_ids          = fields.Many2many("ir.attachment", "is_demande_essai_fiche_tech_mat_rel", "fiche_tech_mat", "att_id", string="Fiche technique matière")
    piece_jointe_ids            = fields.Many2many("ir.attachment", "is_demande_essai_pieces_jointes_rel", "piece_jointe", "att_id", string="Pièce jointe")
    images_ids                  = fields.Many2many("ir.attachment", "is_demande_essai_images_rel", "images", "att_id", string="Images")
    te_piece_jointe_ids         = fields.Many2many("ir.attachment", "is_demande_essai_te_pieces_jointes_rel", "te_piece_jointe", "att_id", string="Compte-rendu")
    tps_cycle_standard          = fields.Char("Tps cycle standard", tracking=True)
    tps_cycle_objectif          = fields.Char("Tps cycle objectif", tracking=True,copy=False)
    tps_cycle_resultat          = fields.Char("Tps cycle résultat", tracking=True,copy=False)
    poids_piece_standard        = fields.Char("Poids pièce standard", tracking=True)
    poids_piece_objectif        = fields.Char("Poids pièce objectif", tracking=True,copy=False)
    poids_piece_resultat        = fields.Char("Poids pièce résultat", tracking=True,copy=False)
    presse_standard_id          = fields.Many2one('is.equipement', "Presse standard", tracking=True)
    presse_objectif_id          = fields.Many2one('is.equipement', "Presse objectif", tracking=True,copy=False)
    presse_resultat_id          = fields.Many2one('is.equipement', "Presse résultat", tracking=True,copy=False)
    nb_mo_standard              = fields.Selection(_NB_MO, "Nombre mo standard", tracking=True)
    nb_mo_objectif              = fields.Selection(_NB_MO, "Nombre mo objectif", tracking=True,copy=False)
    nb_mo_resultat              = fields.Selection(_NB_MO, "Nombre mo résultat", tracking=True,copy=False)
    de_piece_jointe_ids         = fields.Many2many("ir.attachment", "is_demande_essai_de_pieces_jointes_rel", "de_piece_jointe", "att_id", string="Pièce jointe DE",copy=False)
    de_commentaire_deroulement  = fields.Text('Commentaire déroulement essai', tracking=True,copy=False)
    resp_metrologie_id          = fields.Many2one("res.users", "Responsable métrologie", tracking=True)
    metro_rapport_controle      = fields.Boolean("Rapport de contrôle", tracking=True,copy=False)
    metro_rc_complet            = fields.Boolean("RC Complet", tracking=True,copy=False)
    metro_rc_partiel            = fields.Boolean("RC Partiel", tracking=True,copy=False)
    metro_gamme_geometrique     = fields.Boolean("Gamme géométrique", tracking=True,copy=False)
    metro_couleur               = fields.Boolean("Couleur", tracking=True,copy=False)
    metro_aspect                = fields.Boolean("Aspect", tracking=True,copy=False)
    metro_controle_visuel       = fields.Boolean("Contrôle visuel", tracking=True,copy=False)
    metro_brillance             = fields.Boolean("Brillance", tracking=True,copy=False)
    metro_choc                  = fields.Boolean("Choc", tracking=True,copy=False)
    metro_capabilite            = fields.Boolean("Capabilité", tracking=True,copy=False)
    metro_capa30                = fields.Boolean("Capabilité 30 pièces", tracking=True,copy=False)
    metro_capa50                = fields.Boolean("Capabilité 50 pièces", tracking=True,copy=False)
    metro_commentaire           = fields.Text('Commentaire métrologie', tracking=True,copy=False)
    rapport_de_controle_ids    = fields.Many2many("ir.attachment", "is_demande_essai_rapport_de_controle_rel", "rapport_de_controle", "att_id", string="Fichier rapport de contrôle",copy=False)
    rapport_cote_conforme      = fields.Integer("% cote conforme", tracking=True)
    rapport_commentaire        = fields.Text("Commentaire rapport métrologie", tracking=True,copy=False)
    date_planifiee             = fields.Date("Date planifiée", tracking=True,copy=False)
    date_realisation           = fields.Date("Date de réalisation de l'essai", tracking=True,copy=False)
    # demande_essai_pdf_ids      = fields.Many2many("ir.attachment", "is_demande_essai_demande_essai_pdf_rel", "demande_essai_pdf", "att_id", string="Demande d'essai PDF",copy=False)
    # etiquette_pdf_ids          = fields.Many2many("ir.attachment", "is_demande_essai_etiquette_pdf_rel", "etiquette_pdf", "att_id", string="Etiquette PDF",copy=False)
    dynacase_id         = fields.Integer(string="Id Dynacase", index=True, copy=False)
    mail_to_ids = fields.Many2many('res.users', compute='_compute_mail_to_cc_ids', string="Mail To")
    mail_cc_ids = fields.Many2many('res.users', compute='_compute_mail_to_cc_ids', string="Mail Cc")
    ro_user     = fields.Boolean("ro_user"    , compute='_compute_ro', store=False, readonly=True)
    ro_essai    = fields.Boolean("ro_essai"   , compute='_compute_ro', store=False, readonly=True)
    ro_planning = fields.Boolean("ro_planning", compute='_compute_ro', store=False, readonly=True)
    ro_metro    = fields.Boolean("ro_metro"   , compute='_compute_ro', store=False, readonly=True)


    @api.depends('state','user_id','resp_essai_id','resp_planning_id','resp_metrologie_id')
    def _compute_ro(self):
        uid = self._uid
        for obj in self:
            ro_user = ro_essai = ro_planning = ro_metro =True
            if obj.state in ('brouillon','diffuse','planifie','cr','metrologie') and uid==obj.user_id.id:
                ro_user = False
            if obj.state in ('diffuse') and uid==obj.resp_planning_id.id:
                ro_planning = False
            if obj.state in ('planifie','cr') and uid==obj.resp_essai_id.id:
                ro_essai = False
            if obj.state in ('metrologie') and uid==obj.resp_metrologie_id.id:
                ro_metro = False
            obj.ro_user = ro_user
            obj.ro_essai = ro_essai
            obj.ro_planning = ro_planning
            obj.ro_metro = ro_metro

 
    def get_doc_url(self):
        for obj in self:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            url = base_url + '/web#id=%s' '&view_type=form&model=%s'%(obj.id,self._name)
            return url

    def get_state_name(self):
        for obj in self:
            return dict(self._fields['state'].selection).get(self.state)

    @api.depends("state")
    def _compute_mail_to_cc_ids(self):
        for obj in self:
            to_ids=[]
            cc_ids=[]
            if obj.state=='diffuse':
                to_ids.append(obj.resp_essai_id)
                to_ids.append(obj.resp_planning_id)
                to_ids.append(obj.resp_metrologie_id)
                for personne in obj.autres_personnes_ids:
                    cc_ids.append(personne)
            if obj.state=='planifie':
                to_ids.append(obj.user_id)
                to_ids.append(obj.resp_essai_id)
                to_ids.append(obj.resp_metrologie_id)
            if obj.state=='metrologie':
                to_ids.append(obj.user_id)
                to_ids.append(obj.resp_metrologie_id)
            if obj.state=='termine':
                to_ids = self.env['is.liste.diffusion.mail'].get_users('is.demande.essai','termine')
                to_ids.append(obj.user_id)
                to_ids.append(obj.resp_essai_id)
                to_ids.append(obj.resp_metrologie_id)
            obj.mail_to_ids = self.env['is.liste.diffusion.mail'].get_users_ids(users=to_ids)
            obj.mail_cc_ids = self.env['is.liste.diffusion.mail'].get_users_ids(users=cc_ids)

    def users2mail(self,users):
        return self.env['is.liste.diffusion.mail'].users2mail(users=users)
      
    def users2partner_ids(self,users):
        return self.env['is.liste.diffusion.mail'].users2partner_ids(users=users)

    def envoi_mail(self):
        template = self.env.ref('is_dynacase2odoo.is_demande_essai_mail_template').sudo()     
        email_values = {
            'email_cc'      : self.users2mail(self.mail_cc_ids),
            'auto_delete'   : False,
            'recipient_ids' : self.users2partner_ids(self.mail_to_ids),
            'scheduled_date': False,
        }
        template.send_mail(self.id, force_send=True, raise_exception=False, email_values=email_values)

    def lien_vers_dynacase_action(self):
        for obj in self:
            url="https://dynacase-rp/?sole=Y&app=FDL&action=FDL_CARD&latest=Y&id=%s"%obj.dynacase_id
            return {
                'type' : 'ir.actions.act_url',
                'url': url,
                'target': 'new',
            }


    def vers_brouillon_action(self):
        for obj in self:
            obj.state='brouillon'

    def vers_diffuse_action(self):
        for obj in self:
            obj.state='diffuse'
            obj.envoi_mail()
 
    def vers_planifie_action(self):
        for obj in self:
            obj.state='planifie'
            obj.envoi_mail()

    def vers_cr_action(self):
        for obj in self:
            obj.state='cr'
 
    def vers_metrologie_action(self):
        for obj in self:
            obj.state='metrologie'
            obj.envoi_mail()
 
    def vers_termine_action(self):
        for obj in self:
            obj.state='termine'
            obj.envoi_mail()

    def vers_solde_action(self):
        for obj in self:
            obj.state='solde'

    @api.onchange('code_matiere_id')
    def onchange_code_matiere_id(self):
        for obj in self:
            obj.designation_mat = obj.code_matiere_id.designation

    @api.onchange('code_matiere2_id')
    def onchange_code_matiere2_id(self):
        for obj in self:
            obj.designation_mat2 = obj.code_matiere2_id.designation

    @api.onchange('code_colorant_id')
    def onchange_code_colorant_id(self):
        for obj in self:
            obj.designation_col = obj.code_colorant_id.designation
