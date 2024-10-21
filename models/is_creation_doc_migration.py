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


            nb_a_creer_total=0
            for line in lines:
                print(line.param_project_id.ppr_famille)


                famille_id = line.param_project_id.id
                nb_doc_famille = familles.get(famille_id)
                j_prevue=str(dict(GESTION_J).get(line.j_prevue)).ljust(15)


                #** Recherche des documents à créer après la J actuelle *******
                if nb_doc_famille==1:
                    for param in line.param_project_id.array_ids:
                        if param.ppp_j>obj.moule_id.j_actuelle and param.ppr_irv:
                            nb_a_creer_total+=1
                            #print('-',obj.moule_id.j_actuelle, param.ppp_j, param.ppr_irv)



                            analyse.append('- %s : nb_doc=%s : J prévue=%s : %s'%(
                                j_prevue,
                                str(nb_doc_famille).ljust(2),
                                param.ppp_j,
                                line.param_project_id.ppr_famille[:48].ljust(50))
                            )




                #**************************************************************

                # if nb_a_creer>0:
                #     analyse.append('- %s : nb_doc=%s : nb_a_creer=%s : %s'%(
                #         j_prevue,
                #         str(nb_doc_famille).ljust(2),
                #         str(nb_a_creer).ljust(2),
                #         line.param_project_id.ppr_famille[:48].ljust(50))
                #     )

            analyse.append('%s documents à créer au total'%nb_a_creer_total)


            obj.analyse = '\n'.join(analyse)