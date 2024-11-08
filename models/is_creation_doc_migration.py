from odoo import models, fields, api, _ # type: ignore
from odoo.addons.is_dynacase2odoo.models.is_param_project import GESTION_J  # type: ignore
from datetime import datetime, timedelta


TYPE_DOCUMENT=[
    ("Moule"                 , "Moule"),
    ("Dossier F"             , "Dossier F"),
]


class is_creation_doc_migration(models.Model):
    _name        = "is.creation.doc.migration"
    _description = "Gantt Copie"
    _order = "id desc"

    name          = fields.Char("N°", readonly=True)
    type_document = fields.Selection(TYPE_DOCUMENT,string="Type de document", default="Moule", required=True)
    moule_id      = fields.Many2one("is.mold"    , string="Moule")
    dossierf_id   = fields.Many2one("is.dossierf", string="Dossier")
    analyse       = fields.Text("Analyse", readonly=True)


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['name'] = self.env['ir.sequence'].next_by_code('is.creation.doc.migration')
        return super().create(vals_list)


    def creer_doc_action(self):
        for obj in self:
            rl = obj.moule_id.revue_lancement_id
            domain=[
                ('idmoule','=', obj.moule_id.id)
            ]
            lines=self.env['is.doc.moule'].search(domain)

            #TODO : 
            #- Si J prévu n'est pas renseigné et si un esule documment à faire => J prévue = J indiquée dans le paramètrage
            #- Si J prévue non renseignée et plusieurs documents à faire => La premiere J indiquée dans le paramétgrage
            # Il faudrait donc commencer par initialiser les J prévue de tous les documents pour connaitre les documents à créer

            #** Recherche du nombre de documents pas famille ******************
            familles={}
            for line in lines:
                famille_id = line.param_project_id.id
                if famille_id not in familles:
                    familles[famille_id]=0
                familles[famille_id]+=1

            analyse=[]
            j_actuelle=dict(GESTION_J).get(obj.moule_id.j_actuelle)
            analyse.append('%s documents actuellement'%len(lines))
            analyse.append('J actuelle : %s'%j_actuelle)


            nb_a_creer=0
            for line in lines:
                famille_id = line.param_project_id.id
                nb_doc_famille = familles.get(famille_id)
                j_prevue=str(dict(GESTION_J).get(line.j_prevue)).ljust(15)


                #** Nombre de documents de la famille à créer en tout *********
                nb_doc_besoin=0
                for param in line.param_project_id.array_ids:
                    if param.ppr_irv:
                        nb_doc_besoin+=1
                if nb_doc_besoin==0:
                    nb_doc_besoin=1
                #**************************************************************


                #** Recherche des documents à créer après la J actuelle *******
                num_irv=0
                for param in line.param_project_id.array_ids:
                    a_creer='n'
                    num_a_creer=''
                    if param.ppr_irv:
                        num_irv+=1
                        if param.ppp_j>obj.moule_id.j_actuelle and nb_doc_besoin>1 and nb_doc_famille==1 and num_irv>1:
                            a_creer='Oui'
                            nb_a_creer+=1
                            num_a_creer=nb_a_creer
                            dateend = False
                            if rl:
                                dateend = getattr(rl, "rl_date_%s"%param.ppp_j.lower())
                            vals={
                                'param_project_id'  : line.param_project_id.id,
                                'idmoule'           : line.idmoule.id,
                                'j_prevue'          : param.ppp_j,
                                'idresp'            : line.idresp.id,
                                'action'            : param.ppr_irv,
                                'etat'              : 'AF',
                                'dateend'           : dateend,
                                'date_debut_gantt'  : dateend,
                                'duree_gantt'       : 1,
                                'date_creation_auto': datetime.now(),
                            }
                            doc = self.env['is.doc.moule'].create(vals)
                            doc.set_fin_gantt()
                        analyse.append('- %s : %s : %s : %s : %s : nb_doc_famille=%s : nb_doc_besoin=%s : a_creer=%s : %s'%(
                            line.param_project_id.ppr_famille[:48].ljust(50),
                            (line.action or'').ljust(3),
                            param.ppp_j,
                            (param.ppr_irv or '').ljust(3),
                            str(num_irv).ljust(3),
                            str(nb_doc_famille).ljust(4),
                            str(nb_doc_besoin).ljust(4),
                            str(a_creer).ljust(4),
                            str(num_a_creer).ljust(3)
                        ))

            analyse.append('%s documents à créer au total'%nb_a_creer)
            obj.analyse = '\n'.join(analyse)


    def liste_doc_action(self):
        tree_id  = self.env.ref('is_dynacase2odoo.is_doc_moule_tree').id
        for obj in self:
            return {
                'name': obj.name,
                'view_mode': 'tree,form',
                "views"    : [
                    (tree_id, "tree"),
                    (False, "form")
                ],
                'res_model': 'is.doc.moule',
                'domain': [
                    ('idmoule','=',obj.moule_id.id),
                    ('date_creation_auto','!=',False),
                ],
                'type': 'ir.actions.act_window',
                'limit': 1000,
            }
           