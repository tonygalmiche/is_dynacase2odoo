from odoo import models, fields, api  # type: ignore


# class IsCtrlRcpGamme(models.Model):
#     _name = "is.ctrl.rcp.gamme"
#     _inherit = ["mail.thread", "mail.activity.mixin"]
#     _description = "Gamme Contrôle Réception"
#     _rec_name = "dossier_article_id"
#     _order = "dossier_article_id"

#     dossier_article_id = fields.Many2one("is.dossier.article", string="Dossier article", required=False, index=True, tracking=True)
#     dossier_article    = fields.Char(string="Dossier article (archivé)", tracking=True, copy=False, readonly=True)
#     responsable_id     = fields.Many2one("res.users", string="Responsable", tracking=True, default=lambda self: self.env.uid)
#     date_fin_prevue    = fields.Date(string="Date de fin prévue", tracking=True, default=lambda *a: fields.datetime.now())
#     etat = fields.Selection(
#         [
#             ("", ""),
#             ("AF", "A Faire"),
#             ("F", "Fait"),
#         ],
#         string="État",
#         default="F",
#         tracking=True,
#     )
#     active = fields.Boolean(string="Actif", default=True, tracking=True)
#     piece_jointe_ids = fields.Many2many("ir.attachment", "is_ctrl_rcp_gamme_piece_jointe_rel", "piece_jointe", "att_id", string="Pièce jointe")
#     controle_ids = fields.One2many(
#         "is.ctrl.rcp.gamme.controle",
#         "gamme_id",
#         string="Contrôles",
#         tracking=True,
#     )
#     dynacase_id = fields.Integer(string="Id Dynacase", index=True, copy=False)


#     def lien_vers_dynacase_action(self):
#         for obj in self:
#             url = "https://dynacase-rp/?sole=Y&app=FDL&action=FDL_CARD&latest=Y&id=%s" % obj.dynacase_id
#             return {
#                 "type": "ir.actions.act_url",
#                 "url": url,
#                 "target": "new",
#             }



class IsCtrlRcpGammeControle(models.Model):
    _name = "is.ctrl.rcp.gamme.controle"
    _description = "Contrôle de la gamme RCP"
    _order = "id"

    doc_gamme_id = fields.Many2one(
        "is.doc.moule",
        string="Gamme",
        required=True,
        ondelete="cascade",
        index=True,
    )
    intitule_controle = fields.Char(string="Intitulé du contrôle", required=True)
    tolerance_mini    = fields.Char(string="Tolérance mini")
    tolerance_maxi    = fields.Char(string="Tolérance maxi")

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            if record.doc_gamme_id:
                message = f"Nouveau contrôle ajouté : {record.intitule_controle}"
                if record.tolerance_mini or record.tolerance_maxi:
                    tolerances = []
                    if record.tolerance_mini:
                        tolerances.append(f"Mini: {record.tolerance_mini}")
                    if record.tolerance_maxi:
                        tolerances.append(f"Maxi: {record.tolerance_maxi}")
                    message += f" ({', '.join(tolerances)})"
                record.doc_gamme_id.message_post(body=message)
        return records

    def write(self, vals):
        # Sauvegarder les anciennes valeurs pour comparaison
        old_values = {}
        for record in self:
            old_values[record.id] = {
                'intitule_controle': record.intitule_controle,
                'tolerance_mini': record.tolerance_mini,
                'tolerance_maxi': record.tolerance_maxi,
            }
        
        result = super().write(vals)
        
        # Poster un message si des valeurs ont changé
        for record in self:
            if record.doc_gamme_id:
                old_val = old_values[record.id]
                messages = []
                
                # Vérifier l'intitulé du contrôle
                if 'intitule_controle' in vals and old_val['intitule_controle'] != record.intitule_controle:
                    messages.append(f"Intitulé modifié : '{old_val['intitule_controle']}' → '{record.intitule_controle}'")
                
                # Vérifier la tolérance mini
                if 'tolerance_mini' in vals and old_val['tolerance_mini'] != record.tolerance_mini:
                    old_mini = old_val['tolerance_mini'] or 'vide'
                    new_mini = record.tolerance_mini or 'vide'
                    messages.append(f"Tolérance mini modifiée : {old_mini} → {new_mini}")
                
                # Vérifier la tolérance maxi
                if 'tolerance_maxi' in vals and old_val['tolerance_maxi'] != record.tolerance_maxi:
                    old_maxi = old_val['tolerance_maxi'] or 'vide'
                    new_maxi = record.tolerance_maxi or 'vide'
                    messages.append(f"Tolérance maxi modifiée : {old_maxi} → {new_maxi}")
                
                if messages:
                    full_message = f"Contrôle '{record.intitule_controle}' modifié :<br/>" + "<br/>".join([f"• {msg}" for msg in messages])
                    record.doc_gamme_id.message_post(body=full_message)
        
        return result

    def unlink(self):
        # Sauvegarder les informations avant suppression
        deleted_controls = []
        for record in self:
            if record.doc_gamme_id:
                deleted_controls.append({
                    'doc_gamme_id': record.doc_gamme_id,
                    'intitule_controle': record.intitule_controle,
                })
        
        result = super().unlink()
        
        # Poster un message après suppression
        for control_info in deleted_controls:
            message = f"Contrôle supprimé : {control_info['intitule_controle']}"
            control_info['doc_gamme_id'].message_post(body=message)
        
        return result


class IsCtrlRcpRapport(models.Model):
    _name = "is.ctrl.rcp.rapport"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Rapport Contrôle Réception"
    _rec_name = "num_rapport"
    _order = "num_rapport desc"

    # Identification
    num_rapport      = fields.Integer(string="N°", tracking=True, readonly=1, index=True, copy=False)
    site_id          = fields.Many2one('is.database', "Site", tracking=True, default=lambda self: self._get_site_id(),)
    reception_id     = fields.Many2one('is.reception', "Réception", tracking=True)
    num_reception    = fields.Char(string="N° réception", tracking=True)
    fournisseur_id   = fields.Many2one('res.partner', 'Fournisseur', tracking=True, domain=[("is_company","=",True), ("supplier","=",True)])
    fournisseur      = fields.Char(string="Nom fournisseur", tracking=True)
    code_fournisseur = fields.Char(string="Code fournisseur", tracking=True)

    codepg        = fields.Char(string="Code PG", tracking=True)
    designation   = fields.Char(string="Désignation", tracking=True)
    moule         = fields.Char(string="Moule", tracking=True)
    qt_annonce    = fields.Float(string="Quantité annoncée", tracking=True)
    qt_recue      = fields.Float(string="Quantité reçue", tracking=True)
    num_lot_fourn = fields.Char(string="N° lot fournisseur", tracking=True)
    date_rcp      = fields.Date(string="Date de réception", tracking=True)
    num_bl        = fields.Char(string="N° BL Fournisseur", tracking=True)
    num_lot_of    = fields.Char(string="N° de lot ou d'OF", tracking=True)

    # Contrôle RCP
    date_ctrl = fields.Date(string="Date du contrôle", tracking=True)
    gamme_id  = fields.Many2one("is.doc.moule", string="Gamme de contrôle", tracking=True)

    # Résultats des contrôles
    condi_resultat = fields.Selection(
        selection=[("", ""), ("Conforme", "Conforme"), ("Non conforme", "Non conforme")],
        string="Conditionnement",
        default="",
        tracking=True,
    )
    conform_resultat = fields.Selection(
        selection=[("", ""), ("Conforme", "Conforme"), ("Non conforme", "Non conforme")],
        string="Conformité produit",
        default="",
        tracking=True,
    )
    decision_rcp = fields.Selection(
        selection=[
            ("Livraison refusée", "Livraison refusée"),
            ("Livraison acceptée", "Livraison acceptée"),
            ("Livraison dérogée", "Livraison dérogée"),
        ],
        string="Décision de la réception",
        tracking=True,
    )
    commentaire      = fields.Text(string="Commentaire", tracking=True)
    piece_jointe_ids = fields.Many2many("ir.attachment", "is_ctrl_rcp_rapport_piece_jointe_rel", "piece_jointe", "att_id", string="Pièce jointe")
    saisie_ids       = fields.One2many("is.ctrl.rcp.saisie","rapport_id",string="Saisies")
    active           = fields.Boolean(string="Actif", default=True, tracking=True)
    dynacase_id      = fields.Integer(string="Id Dynacase", index=True, copy=False, tracking=True)


    def _get_site_id(self):
        user = self.env['res.users'].browse(self._uid)
        site_id = user.is_site_id.id
        return site_id


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            print(vals)
            num_rapport=1
            if 'num_rapport' not in vals:
                last = self.env[self._name].search([('num_rapport','>',0)], order="num_rapport desc", limit=1)
                print(last)
                if last:
                    num_rapport = last.num_rapport + 1
            vals['num_rapport'] = num_rapport
            return super().create(vals_list)


    @api.onchange('reception_id')
    def onchange_reception_id(self):
        for obj in self:
            numero_reception = fournisseur_id = codepg = designation = moule = False
            numero_bl_fournisseur = quantite_livree = date_reception = False
            if obj.reception_id:
                numero_reception = obj.reception_id.numero_reception
                fournisseur_id   = obj.reception_id.fournisseur_id.id 
                codepg          = obj.reception_id.code_pg
                designation     = obj.reception_id.designation
                moule           = obj.reception_id.moule
                numero_bl_fournisseur = obj.reception_id.numero_bl_fournisseur
                quantite_livree     = obj.reception_id.quantite_livree
                date_reception      = obj.reception_id.date_reception
            #** Recherche de la gamme *****************************************
            if codepg:
                articles = self.env["is.dossier.article"].search([('code_pg', '=', codepg)], limit=1)
                for article in  articles:
                    domain=[
                        ('dossier_article_id', '=', article.id),
                        ('gamme_controle', '=', True),
                    ]
                    gammes = self.env["is.doc.moule"].search(domain, limit=1)
                    for gamme in gammes:
                        obj.gamme_id = gamme.id
            #******************************************************************
            obj.num_reception = numero_reception
            obj.fournisseur_id = fournisseur_id
            obj.codepg = codepg
            obj.designation = designation
            obj.moule = moule
            obj.num_bl = numero_bl_fournisseur
            obj.qt_annonce = quantite_livree
            obj.qt_recue = quantite_livree
            obj.date_rcp = date_reception


    @api.onchange('gamme_id')
    def onchange_gamme_id(self):
        """Crée automatiquement les saisies de contrôle basées sur la gamme sélectionnée"""
        for obj in self:
            if obj.gamme_id:
                # Supprimer les saisies existantes (seulement en mode création/modification)
                obj.saisie_ids = [(5, 0, 0)]
                
                # Créer une saisie pour chaque contrôle de la gamme
                saisies_vals = []
                lig=1
                for controle in obj.gamme_id.controle_ids:
                    saisie_vals = {
                        'rapport_lig': lig,
                        'controle_a_effectuer': controle.intitule_controle,
                        'tolerance_mini': controle.tolerance_mini,
                        'tolerance_maxi': controle.tolerance_maxi,
                    }
                    saisies_vals.append((0, 0, saisie_vals))
                    lig+=1
                
                obj.saisie_ids = saisies_vals

    @api.onchange('fournisseur_id')
    def onchange_fournisseur_id(self):
        for obj in self:
            fournisseur = code_fournisseur = False
            if obj.fournisseur_id:
                fournisseur = obj.fournisseur_id.name
                code_fournisseur = obj.fournisseur_id.is_code
            obj.fournisseur      = fournisseur
            obj.code_fournisseur = code_fournisseur


    def lien_vers_dynacase_action(self):
        for obj in self:
            url = "https://dynacase-rp/?sole=Y&app=FDL&action=FDL_CARD&latest=Y&id=%s" % obj.dynacase_id
            return {
                "type": "ir.actions.act_url",
                "url": url,
                "target": "new",
            }


class IsCtrlRcpSaisie(models.Model):
    _name = "is.ctrl.rcp.saisie"
    _description = "Saisie Contrôle Réception"
    _rec_name = "rapport_lig"
    _order = "rapport_id desc,rapport_lig"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    # Identification
    rapport_id       = fields.Many2one("is.ctrl.rcp.rapport",string="Rapport",required=True,ondelete="cascade",index=True)
    site_id          = fields.Many2one(related="rapport_id.site_id")
    reception_id     = fields.Many2one(related="rapport_id.reception_id")
    num_reception    = fields.Char(related="rapport_id.num_reception")
    fournisseur_id   = fields.Many2one(related="rapport_id.fournisseur_id")
    fournisseur      = fields.Char(related="rapport_id.fournisseur")
    code_fournisseur = fields.Char(related="rapport_id.code_fournisseur")
    codepg           = fields.Char(related="rapport_id.codepg")
    designation      = fields.Char(related="rapport_id.designation")
    moule            = fields.Char(related="rapport_id.moule")
    num_lot_fourn    = fields.Char(related="rapport_id.num_lot_fourn")
    date_ctrl        = fields.Date(related="rapport_id.date_ctrl")

    # Détails de contrôle
    rapport_lig          = fields.Integer(string="Ligne du rapport", tracking=True)
    controle_a_effectuer = fields.Char(string="Contrôle à effectuer", tracking=True)
    tolerance_mini       = fields.Char(string="Tolérance mini", tracking=True)
    tolerance_maxi       = fields.Char(string="Tolérance maxi", tracking=True)
    resultat = fields.Selection(
        selection=[
            ("OK", "OK"),
            ("nOK", "nOK"),
        ],
        string="Résultat du contrôle",
        compute="_compute_resultat",
        store=True,
        tracking=True,
        copy=False
    )
    resultat_display = fields.Html(string="Résultat", compute="_compute_resultat_display", store=True)
    mesure_ids   = fields.One2many("is.ctrl.rcp.saisie.mesure","saisie_id",string="Mesures", tracking=True)
    active       = fields.Boolean(string="Actif", default=True, tracking=True)
    dynacase_id  = fields.Integer(string="Id Dynacase", index=True, copy=False, tracking=True)

    @api.depends('mesure_ids.valeur_resultat')
    def _compute_resultat(self):
        for record in self:
            if not record.mesure_ids:
                record.resultat = False
                continue
            
            # Vérifier si toutes les mesures ont un résultat
            mesures_avec_resultat = record.mesure_ids.filtered(lambda m: m.valeur_resultat)
            
            if len(mesures_avec_resultat) == 0:
                # Aucune mesure n'a de résultat
                record.resultat = False
            elif len(mesures_avec_resultat) < len(record.mesure_ids):
                # Toutes les mesures ne sont pas faites
                record.resultat = False
            else:
                # Toutes les mesures ont un résultat
                mesures_nok = mesures_avec_resultat.filtered(lambda m: m.valeur_resultat == 'nOK')
                if mesures_nok:
                    # Au moins une mesure est nOK
                    record.resultat = 'nOK'
                else:
                    # Toutes les mesures sont OK
                    record.resultat = 'OK'

    @api.depends('resultat')
    def _compute_resultat_display(self):
        for record in self:
            res=False
            if record.resultat == 'OK':
                res = '<span style="color: green; font-size: 16px;">✓ OK</span>'
            if record.resultat == 'nOK':
                res = '<span style="color: red; font-size: 16px;">✗ nOK</span>'
            record.resultat_display = res


    def lien_vers_dynacase_action(self):
        for obj in self:
            url = "https://dynacase-rp/?sole=Y&app=FDL&action=FDL_CARD&latest=Y&id=%s" % obj.dynacase_id
            return {
                "type": "ir.actions.act_url",
                "url": url,
                "target": "new",
            }

    def ouvrir_fiche_saisie_action(self):
        """Action pour ouvrir la fiche complète de la saisie"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Saisie Contrôle Réception',
            'res_model': 'is.ctrl.rcp.saisie',
            'res_id': self.id,
            'view_mode': 'form',
            #'target': 'new',
            'context': self.env.context,
        }

    def creer_20_mesures_action(self):
        """Crée 20 lignes de mesures numérotées de 1 à 20"""
        self.ensure_one()
        # Créer 20 nouvelles mesures
        mesures_vals = []
        for i in range(1, 21):
            mesure_vals = {
                'saisie_id': self.id,
                'num_mesure': i,
                'valeur_mesuree': False,
            }
            mesures_vals.append(mesure_vals)
        self.env['is.ctrl.rcp.saisie.mesure'].create(mesures_vals)
        
 

class IsCtrlRcpSaisieMesure(models.Model):
    _name = "is.ctrl.rcp.saisie.mesure"
    _description = "Mesure de saisie de contrôle réception"
    _order = "id"

    saisie_id        = fields.Many2one("is.ctrl.rcp.saisie",string="Saisie",required=True,ondelete="cascade",index=True)
    num_mesure       = fields.Integer(string="N° de la mesure")
    valeur_mesuree   = fields.Char(string="Valeur mesurée")
    valeur_resultat  = fields.Selection(
        selection=[
            ("OK", "OK"),
            ("nOK", "nOK"),
        ],
        string="Résultat",
        compute="_compute_valeur_resultat",
        store=True,
    )
    valeur_resultat_display = fields.Html(string="Résultat Ctrl", compute="_compute_valeur_resultat_display", store=True)

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            if record.saisie_id and record.valeur_mesuree:
                message = f"Nouvelle mesure ajoutée : Mesure n°{record.num_mesure} = {record.valeur_mesuree}"
                record.saisie_id.message_post(body=message)
        return records

    def write(self, vals):
        # Sauvegarder les anciennes valeurs pour comparaison
        old_values = {}
        for record in self:
            old_values[record.id] = {
                'valeur_mesuree': record.valeur_mesuree,
                'num_mesure': record.num_mesure,
            }
        
        result = super().write(vals)
        
        # Poster un message si la valeur mesurée a changé
        if 'valeur_mesuree' in vals:
            for record in self:
                old_val = old_values[record.id]['valeur_mesuree']
                new_val = record.valeur_mesuree
                if old_val != new_val and record.saisie_id:
                    if old_val and new_val:
                        message = f"Mesure n°{record.num_mesure} modifiée : {old_val} → {new_val}"
                    elif not old_val and new_val:
                        message = f"Mesure n°{record.num_mesure} saisie : {new_val}"
                    elif old_val and not new_val:
                        message = f"Mesure n°{record.num_mesure} supprimée (était : {old_val})"
                    else:
                        continue
                    record.saisie_id.message_post(body=message)
        
        return result


    def str2float(self,val):
            try:
                res = float((val or '').replace(',', '.'))
            except (ValueError, AttributeError):
                res=0
            return res

    @api.depends('valeur_mesuree', 'saisie_id.tolerance_mini', 'saisie_id.tolerance_maxi')
    def _compute_valeur_resultat(self):
        for record in self:
            res = False
            # Si valeur_mesuree est vide, valeur_resultat reste vide
            if not record.valeur_mesuree:
                res = False
            elif (record.saisie_id.tolerance_mini or '').upper()=="OK":
                if (record.valeur_mesuree or '').upper()=="OK":
                    res='OK'
                else:
                    res = 'nOK'
            else:
                if record.valeur_mesuree and record.saisie_id.tolerance_mini and record.saisie_id.tolerance_maxi:
                    valeur = self.str2float(record.valeur_mesuree)
                    mini   = self.str2float(record.saisie_id.tolerance_mini)
                    maxi   = self.str2float(record.saisie_id.tolerance_maxi)
                    if mini <= valeur <= maxi:
                        res = 'OK'
                    else:
                        res = 'nOK'
            record.valeur_resultat = res


    @api.depends('valeur_resultat')
    def _compute_valeur_resultat_display(self):
        for record in self:
            res=False
            if record.valeur_resultat == 'OK':
                res = '<span style="color: green; font-size: 16px;">✓ OK</span>'
            if record.valeur_resultat == 'nOK':
                res = '<span style="color: red; font-size: 16px;">✗ nOK</span>'
            record.valeur_resultat_display = res

