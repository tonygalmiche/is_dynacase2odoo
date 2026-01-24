# -*- coding: utf-8 -*-
from odoo import models, fields


class IsProdstarFp2art(models.Model):
    _name = "is.prodstar.fp2art"
    _description = "Prodstar FP2ART"
    _rec_name = "code_pg"
    _order = "code_pg"

    soc            = fields.Char(string="Soc")
    code_pg        = fields.Char(string="Code PG")
    cat            = fields.Char(string="Cat")
    fam            = fields.Char(string="Fam")
    gest           = fields.Char(string="Gest")
    moule          = fields.Char(string="Moule")
    projet         = fields.Char(string="Projet")
    designation    = fields.Char(string="Désignation")
    specif_interne = fields.Text(string="Spécif Interne")
    ref_plan       = fields.Char(string="Ref Plan")
    ind            = fields.Char(string="Ind")
    us             = fields.Char(string="US")
    uc             = fields.Char(string="UC")
    uc_us          = fields.Float(string="UC/US")
    designation_uc = fields.Char(string="Désignation UC")
    um_uc          = fields.Float(string="UM/UC")
    sr             = fields.Char(string="SR")


class IsProdstarFp2nomq(models.Model):
    _name = "is.prodstar.fp2nomq"
    _description = "Prodstar FP2NOMQ"
    _rec_name = "compose"
    _order = "compose, lig"

    soc         = fields.Char(string="Soc")
    compose     = fields.Char(string="Composé")
    alternative = fields.Char(string="Alternative")
    lig         = fields.Integer(string="Lig")
    composant   = fields.Char(string="Composant")
    date_debut  = fields.Date(string="Date début")
    date_fin    = fields.Date(string="Date fin")
    quantite    = fields.Float(string="Quantité")


class IsProdstarFp2game(models.Model):
    _name = "is.prodstar.fp2game"
    _description = "Prodstar FP2GAME"
    _rec_name = "article"
    _order = "article, alternative"

    soc         = fields.Char(string="Soc")
    article     = fields.Char(string="Article")
    alternative = fields.Char(string="Alternative")
    coef        = fields.Float(string="Coef")





class IsProdstarFp2gamo(models.Model):
    _name = "is.prodstar.fp2gamo"
    _description = "Prodstar FP2GAMO"
    _rec_name = "article"
    _order = "article, alternative, ordre"


    # QI0001, QI0003 , QI0023     , QI0025, QI0028, QI0034      , QI0035 , QI0038      , QI0102         , QI0114
    # Soc   , Article, Alternative, Ordre , QI0028, Type section, Section, Sous-section, Tps Préparation, Tps Fab
    soc            = fields.Char(string="Soc")
    article        = fields.Char(string="Article")
    alternative    = fields.Char(string="Alternative")
    ordre          = fields.Integer(string="Ordre")
    qi0028         = fields.Char(string="QI0028")
    type_section   = fields.Char(string="Type section")
    section        = fields.Char(string="Section")
    sous_section   = fields.Char(string="Sous-section")
    tps_preparation = fields.Float(string="Tps Préparation")
    tps_fab        = fields.Float(string="Tps Fab")


class IsProdstarFp2sec(models.Model):
    _name = "is.prodstar.fp2sec"
    _description = "Prodstar FP2SEC"
    _rec_name = "nom_section"
    _order = "type_section, section, sous_section"

    # PC0001, PC0003      , PC0004 , PC0007      , PC0013     , PC0096, PC0111
    # Soc   , Type section, Section, Sous-section, Nom section, PC0096, PC0111
    soc          = fields.Char(string="Soc")
    type_section = fields.Char(string="Type section")
    section      = fields.Char(string="Section")
    sous_section = fields.Char(string="Sous-section")
    nom_section  = fields.Char(string="Nom section")
    cout_preparation = fields.Char(string="Cout Préparation")
    cout_unitaire    = fields.Char(string="Cout Unitaire")


class IsProdstarFp2gams(models.Model):
    _name = "is.prodstar.fp2gams"
    _description = "Prodstar FP2GAMS"
    _rec_name = "article"
    _order = "article, alternative"

    # QL0001, QL0003 , QL0023,    , QL0034       , QL0097   , QL0105
    # Soc   , Article, Alternative, Sous-traitant, Cout Fixe, Cout Variable
    soc           = fields.Char(string="Soc")
    article       = fields.Char(string="Article")
    alternative   = fields.Char(string="Alternative")
    sous_traitant = fields.Char(string="Sous-traitant")
    cout_fixe     = fields.Float(string="Cout Fixe")
    cout_variable = fields.Float(string="Cout Variable")


class IsProdstarFp2gamu(models.Model):
    _name = "is.prodstar.fp2gamu"
    _description = "Prodstar FP2GAMU"
    _rec_name = "article"
    _order = "article, alternative, ordre"

    soc             = fields.Char(string="Soc")
    article         = fields.Char(string="Article")
    alternative     = fields.Char(string="Alternative")
    ordre           = fields.Integer(string="Ordre")
    moule           = fields.Char(string="Moule")
    nb_empreintes   = fields.Integer(string="Nb Empreintes")
    coefficient_cpi = fields.Float(string="Coefficient CPI")


class IsProdstarFa2rcp(models.Model):
    _name = "is.prodstar.fa2rcp"
    _description = "Prodstar FA2RCP"
    _rec_name = "num_rcp"
    _order = "date_rcp desc, num_rcp desc"

    soc         = fields.Char(string="Soc")
    date_rcp    = fields.Date(string="Date Rcp")
    num_rcp     = fields.Char(string="N°Rcp")
    fournisseur = fields.Char(string="Fournisseur")
    code_fou    = fields.Char(string="Code Fou")
    code_pg     = fields.Char(string="Code PG")
    num_cde     = fields.Char(string="N°Cde")
    lig         = fields.Integer(string="Lig")
    num_bl      = fields.Char(string="N°BL")
    num_lot_fourn = fields.Char(string="N°Lot Fourn")
    us          = fields.Char(string="US")
    qt_rcp      = fields.Float(string="Qt Rcp")
    qt_fac      = fields.Float(string="Qt Fac")
    ope_rcp     = fields.Char(string="Ope Rcp")


# UPDATE is_prodstar_fa2rcp rcp
# SET fournisseur = fou.raison_sociale
# FROM is_prodstar_fa2fou fou
# WHERE rcp.soc = fou.soc 
# AND rcp.code_fou = fou.code_fournisseur;


class IsProdstarFa2fou(models.Model):
    _name = "is.prodstar.fa2fou"
    _description = "Prodstar FA2FOU - Fournisseurs"
    _rec_name = "raison_sociale"
    _order = "code_fournisseur"

    soc              = fields.Char(string="Soc")               # AA0001
    code_fournisseur = fields.Char(string="Code Fournisseur")  # AA0003
    raison_sociale   = fields.Char(string="Raison Sociale")    # AA0074
    rue1             = fields.Char(string="Rue1")              # AA0134
    rue2             = fields.Char(string="Rue2")              # AA0164
    cp               = fields.Char(string="CP")                # AA0194
    ville            = fields.Char(string="Ville")             # AA0204
    critere_alpha    = fields.Char(string="Critère Alpha")     # AA0031
    categorie        = fields.Char(string="Catégorie")         # AA0487
    contact          = fields.Char(string="Contact")           # AA0240
    telephone        = fields.Char(string="Téléphone")         # AA0405
    fax              = fields.Char(string="Fax")               # AA0435


class IsProdstarTarifCial(models.Model):
    _name = "is.prodstar.tarif_cial"
    _description = "Prodstar Tarif Commercial"
    _rec_name = "code_pg"
    _order = "client, code_pg, ind_prix"

    client         = fields.Char(string="Client")                          # CLIENT
    code_pg        = fields.Char(string="CodePG")                          # CODEPG
    ind_prix       = fields.Integer(string="Ind")                          # INDPRIX
    moule          = fields.Char(string="Moule")                           # PA0169
    plastika       = fields.Char(string="Plastika")                        # PLASTIKA
    date_debut     = fields.Date(string="Date Début")                      # DATEDEB
    date_fin       = fields.Date(string="Date Fin")                        # DATEFIN
    type_evolu     = fields.Char(string="Type Evolu.")                     # TYPEEVOLU
    projet         = fields.Char(string="Projet")                          # PROJET
    part_mat       = fields.Float(string="Part Mat", digits=(12, 4))       # MATIERE
    part_comp      = fields.Float(string="Part Comp.", digits=(12, 4))     # COMPOSANT
    part_emb       = fields.Float(string="Part Emb.", digits=(12, 4))      # EMBALLAGE
    va_inj         = fields.Float(string="VA Inj", digits=(12, 4))         # INJECTION
    va_ass         = fields.Float(string="VA Ass", digits=(12, 4))         # ASSEMBLAGE
    frais_port     = fields.Float(string="Frais Port", digits=(12, 4))     # PORT
    logistique     = fields.Float(string="Logis.", digits=(12, 4))         # LOGISTIQUE
    amt_moule      = fields.Float(string="Amt Moule", digits=(12, 4))      # AMTMOULE
    cout_preserie  = fields.Float(string="Surcôut Pré-série", digits=(12, 4))  # COUTPRESERIE
    prix_vente     = fields.Float(string="Prix Vente", digits=(12, 4))     # PRIXVENTE
    commentaire    = fields.Text(string="Commentaire")                     # COMMENTAIR


class IsProdstarFc2tad(models.Model):
    _name = "is.prodstar.fc2tad"
    _description = "Prodstar FC2TAD - Tarif Valide"
    _rec_name = "code_pg"
    _order = "soc, client, code_pg"

    soc           = fields.Char(string="Soc")                              # PA0001
    client        = fields.Char(string="Client")                           # SF0023
    code_pg       = fields.Char(string="Code PG")                          # PA0003
    cat           = fields.Integer(string="Cat")                           # PA0184
    gest          = fields.Integer(string="Gest")                          # PA0283
    moule         = fields.Char(string="Moule")                            # PA0169
    designation   = fields.Char(string="Désignation")                      # PA0047
    ref_client    = fields.Char(string="Ref Client")                       # PA0109
    uc1           = fields.Char(string="UC1")                              # SE0208
    uc1_uv        = fields.Integer(string="UC1/UV")                        # SE0219
    uc2           = fields.Char(string="UC2")                              # SE0210
    uc2_uc1       = fields.Integer(string="UC2/UC1")                       # SE0225
    date_bascule  = fields.Date(string="Date Bascule")                     # SE0369
    date_debut    = fields.Date(string="Date Début")                       # DateD (calculé)
    prix          = fields.Float(string="Prix*", digits=(12, 4))           # Prix (calculé)
    dev           = fields.Char(string="Dev")                              # SF0032


class IsProdstarFc2lid(models.Model):
    _name = "is.prodstar.fc2lid"
    _description = "Prodstar FC2LID - Livraisons"
    _rec_name = "num_liv"
    _order = "soc, num_liv, lig_liv"

    soc              = fields.Char(string="Soc")                           # PA0001
    client           = fields.Char(string="Client")                        # SW0063
    adr              = fields.Integer(string="Adr")                        # SW0068
    code_pg          = fields.Char(string="CodePG")                        # PA0003
    cat              = fields.Integer(string="Cat")                        # PA0184
    fam              = fields.Integer(string="Fam")                        # PA0186
    gest             = fields.Integer(string="Gest")                       # PA0283
    moule            = fields.Char(string="Moule")                         # PA0169
    projet           = fields.Char(string="Projet")                        # substring(PA0720,135,30)
    designation      = fields.Char(string="Désignation")                   # PA0047
    ref_client       = fields.Char(string="Ref Client")                    # PA0109
    t                = fields.Integer(string="T")                          # SR0005
    num_cde_prodstar = fields.Integer(string="N°Cde Prodstar")             # SR0006
    lig              = fields.Integer(string="Lig cde")                    # SR0016
    num_cde_client   = fields.Char(string="N°Cde Client")                  # SQ0030
    num_liv          = fields.Integer(string="N°Liv")                      # SX0006
    lig_liv          = fields.Integer(string="Lig liv")                    # SX0016
    date_exp         = fields.Date(string="Date Exp")                      # SX0097
    date_liv         = fields.Date(string="Date Liv")                      # SW0084
    qt_liv_us        = fields.Float(string="Qt Liv US", digits=(12, 2))    # SX0303
    qt_liv_uc        = fields.Integer(string="Qt Liv UC")                  # SX0303/PA0225
    montant          = fields.Integer(string="Montant")                    # SX0303*SX0374
    date_confirme    = fields.Date(string="Date Confirme")                 # Confirme
    commentaire      = fields.Text(string="Commentaire")                   # Commentaire
