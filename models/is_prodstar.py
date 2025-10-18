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
    pc0096       = fields.Char(string="PC0096")
    pc0111       = fields.Char(string="PC0111")
