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


class IsProdstarFc2lie(models.Model):
    _name = "is.prodstar.fc2lie"
    _description = "Prodstar FC2LIE"
    _rec_name = "sw0063"
    _order = "soc, sw0003, sw0005, sw0006"

    # Champs de jointure (clés)
    soc = fields.Char(string="Soc")
    sw0003 = fields.Char(string="SW0003") 
    sw0005 = fields.Char(string="SW0005")
    sw0006 = fields.Char(string="SW0006")
    
    # Champs métier SW
    sw0063 = fields.Char(string="Client")
    sw0068 = fields.Char(string="Adr")
    sw0084 = fields.Date(string="Date Liv")


class IsProdstarFc2lid(models.Model):
    _name = "is.prodstar.fc2lid"
    _description = "Prodstar FC2LID"
    _rec_name = "sx0016"
    _order = "soc, sx0003, sx0005, sx0006"

    # Champs de jointure (clés)
    soc = fields.Char(string="Soc")
    sx0003 = fields.Char(string="SX0003")
    sx0005 = fields.Char(string="SX0005")
    sx0006 = fields.Char(string="SX0006")
    sx0052 = fields.Char(string="SX0052")
    sx0024 = fields.Char(string="SX0024")
    sx0025 = fields.Char(string="SX0025")
    sx0035 = fields.Char(string="SX0035")
    
    # Champs métier SX
    sx0016 = fields.Char(string="N°Liv")
    sx0097 = fields.Date(string="Date Exp")
    sx0303 = fields.Float(string="Qt Liv US")
    prix_unitaire = fields.Float(string="Prix unitaire")
