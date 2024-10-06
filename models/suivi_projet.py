# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.addons.is_dynacase2odoo.models.is_param_project import GESTION_J
from datetime import datetime, timedelta, date
import copy
import logging
_logger = logging.getLogger(__name__)


#TODO:
#- Pb syncro avec le champ 'Etat' des documents
#- Manque champ 'J actuelle' dans le moule et d'autres champs de Dynacase
#- Manque la famille 'Dossier de Fab'
#- Résoudre problème calcul note
#- Ajouter trobonne et bulle dans indicateur
#- Ajouter les icones en lignes et en colonne pour effectuer les différentes actions (zip,...)
#- Bouton pour actualiser une ligne sans tout recharger (idem Analyse CBN) 
#- Manque champ plasfil_rsp_date, plasfil_rsp_texte et plasfil_rsp_html (pas utilisé) dans is.doc.moule (pb de syncro)



    # //** Indicateur HTML ******************************************************
    # $dend=$this->getValue("PLASFIL_DATEEND");
    # $etat = $this->getValue("PLASFIL_J_ETAT");
    # $color = "Lavender";
    # if ($dend=="") {
    #     $LaDate="(date)";
    #     $color = "orange";
    # } else {
    #     $LaDate=$dend; 
    # }

    # if ($this->getValue("PLASFIL_J_ACTION")=="") $color = "Lavender";
    # if ($etat=="AF")        $color = "CornflowerBlue";
    # if ($etat=="D")         $color = "Orange";
    # if ($dend!="") {
    #     $tj=time();
    #     $tab=explode("/", $dend);
    #     $te=mktime(0, 0, 0, $tab[1], $tab[0], $tab[2]);
    #     if ($tj>=$te) $color = "Red";
    # } 
    # if ($etat=="F")         $color = "SpringGreen";
    # if ($name_fam=="DFAB")  $color = "Lavender"; // Traitement particulier pour les dossiers de fab

    # //** Affichage de la réponse **************************
    # $rsp_texte = $this->getValue("plasfil_rsp_texte");
    # if($rsp_texte!="") $trombone='<a href="#" title="'.$rsp_texte.'">'.substr($rsp_texte,0,5).'</a>';

    # $rsp_date = $this->getValue("plasfil_rsp_date");
    # if($rsp_date!="") $trombone='<a href="#" title="'.$rsp_date.'">'.substr($rsp_date,0,5).'</a>';

    # $piecejointe=$this->getTValue("PLASFIL_ANNEX");
    # if (count($piecejointe)>0) {
    #   $trombone="<img border=0 src=\"/www/Images/tronbonne.gif\">";
    # }
    # //*****************************************************

    # if ($this->getValue("plasfil_rsp_date")<>"" or $this->getValue("plasfil_rsp_texte")<>"" ) {
    #   $txt=$this->getValue("plasfil_rsp_date")." ".$this->getValue("plasfil_rsp_texte");
    #   $bulle="<a href=\"#\" title=\"$txt\"><img border=0 src=\"Images/pg_bulle.png\"></a>";
    # }

    # $r="";
    # if ($coefficient>0) $r=($note/1)."/".($coefficient/1);

    # $html="
    #     <table style=\"border-collapse:collapse;width:100%\">
    #         <tr>
    #             <td style=\"border:none;text-align:center;white-space:nowrap;background-color:$color\" colspan=\"2\">
    #                 <a style=\"color:black\" href=\"?sole=Y&app=FDL&action=FDL_CARD&latest=Y&id=".$this->id."\">$LaDate</a>
    #             </td>
    #         </tr>
    #         <tr>
    #             <td style=\"border:none;text-align:left;white-space:nowrap;background-color:$color\">$r &nbsp;</td>
    #             <td style=\"border:none;text-align:right;white-space:nowrap;background-color:$color\">$bulle $trombone</td>
    #         </tr>
    #     </table>";
    # $this->setValue("PLASFIL_J_INDICATEUR", $html);






# Array
# (
#     [J0] => Array
#         (
#             [IRV] => 
#             [Bloquant] =>  
#             [Note] =>  
#         )

#     [J1] => Array
#         (
#             [IRV] => 
#             [Bloquant] =>  
#             [Note] =>  
#         )

#     [J2] => Array
#         (
#             [IRV] => 
#             [Bloquant] =>  
#             [Note] =>  
#         )

#     [J3] => Array
#         (
#             [IRV] => 
#             [Bloquant] =>  
#             [Note] =>  
#         )

#     [J4] => Array
#         (
#             [IRV] => V
#             [Bloquant] => Oui
#             [Note] => 15
#         )

#     [J5] => Array
#         (
#             [IRV] => R
#             [Bloquant] => Oui
#             [Note] => 13
#         )


# Calcul de la note

# $notes=array("I"=>1,"R"=>3,"V"=>5);
# for($i=0;$i<count($j);$i++) {
#     $note=" ";
#     if ($irv[$i]<>"") $note=$notes[$irv[$i]];
#     if ($bloquant[$i]=="Oui") $note=$note+10;
#     if ($bloquant[$i]!="Oui") $bloquant[$i]=" "; //Pour éffacerr la valeur
#     $r[$j[$i]]=array("IRV"=>$irv[$i],"Bloquant"=>$bloquant[$i],"Note"=>$note);        
# }
# return $r;









class IsDocMoule(models.Model):
    _inherit        = "is.doc.moule"


    def get_suivi_projet(
            self, 
            cp_id=False,
            client=False,
            projet=False,
            moule=False,
            type_moule=False,
            modele_id=False,
            ok=False
        ):
        cr = self._cr

        #** set/get var *****************************************************
        debut=datetime.now()
        if ok:
            self.env['is.mem.var'].set(self._uid, 'suivi_projet_cp_id'     , cp_id)
            self.env['is.mem.var'].set(self._uid, 'suivi_projet_client'    , client)
            self.env['is.mem.var'].set(self._uid, 'suivi_projet_projet'    , projet)
            self.env['is.mem.var'].set(self._uid, 'suivi_projet_moule'     , moule)
            self.env['is.mem.var'].set(self._uid, 'suivi_projet_type_moule', type_moule)
            self.env['is.mem.var'].set(self._uid, 'suivi_projet_modele_id' , modele_id)
        else:
            cp_id      = self.env['is.mem.var'].get(self._uid, 'suivi_projet_cp_id')
            client     = self.env['is.mem.var'].get(self._uid, 'suivi_projet_client')
            projet     = self.env['is.mem.var'].get(self._uid, 'suivi_projet_projet')
            moule      = self.env['is.mem.var'].get(self._uid, 'suivi_projet_moule')
            type_moule = self.env['is.mem.var'].get(self._uid, 'suivi_projet_type_moule')
            modele_id  = self.env['is.mem.var'].get(self._uid, 'suivi_projet_modele_id')
        _logger.info("set/get var (durée=%.2fs)"%(datetime.now()-debut).total_seconds())


        #** Valeur par défaut *************************************************
        if not type_moule:
            type_moule='Actif'


        #** Liste de choix cp_options *****************************************
        cp_options=[]
        cp_options.append({
            "id"      : 0,
            "name"    : '',
            "selected": False,
        })
        group = self.env.ref('is_plastigray16.is_chef_projet_group')
        for user in group.users:
            selected=False
            if str(user.id)==cp_id:
                selected=True
            cp_options.append({
                "id"      : user.id,
                "name"    : user.name,
                "selected": selected,
            })

        #** Liste de choix type_moule_options *********************************
        options = ["Actif","Tous"]
        type_moule_options=[]
        for o in options:
            selected=False
            if o==type_moule:
                selected=True
            type_moule_options.append({
                "id": o,
                "name": o,
                "selected": selected,
            })

        #** Liste de choix modele_options *************************************
        modele_options=[]
        lines=self.env['is.modele.bilan'].search([],order='mb_titre')
        for line in lines:
            selected=False
            if str(line.id)==modele_id:
                selected=True
            modele_options.append({
                "id"      : line.id,
                "name"    : line.mb_titre,
                "selected": selected,
            })
        #**********************************************************************


        #** Recherche des familles du modele **********************************
        modele_ids=[]
        familles={}
        if modele_id:
            modeles=self.env['is.modele.bilan'].search([('id','=',modele_id)])

            for modele in modeles:
                ct=0
                for line in modele.line_ids:
                    ct+=1
                    id = line.param_project_id.id
                    if id:
                        modele_ids.append(str(id))
                        familles[ct]={
                            'ct'          : ct,
                            'id'          : id,
                            'name'        : line.param_project_id.ppr_famille,
                            'doc_id'      : False,
                            'etat'        : '',
                            'dateend'     : '',
                            'note'        : '',
                            'style'       : '',
                            'dynacase_id' : False,
                            'reponse'     : [False,False,False],
                        }

        mydict={}
        if len(modele_ids)>0:
            #** Moules ********************************************************
            SQL="""
                select
                    idm.id               id,
                    im.name              moule,
                    im.designation       designation,
                    im.id                moule_id,
                    'is.mold'            res_model,
                    imp.name             projet,
                    imp.id               projet_id,
                    rp.name              cp,
                    imp.chef_projet_id   cp_id,
                    client.name          client,
                    imp.client_id        client_id,
                    ipp.ppr_famille      famille,
                    ipp.id               famille_id,
                    idm.etat             etat
                from is_doc_moule idm inner join is_mold im         on idm.idmoule=im.id
                                    inner join is_mold_project imp  on im.project=imp.id
                                    inner join res_users ru         on imp.chef_projet_id=ru.id
                                    inner join res_partner rp       on ru.partner_id=rp.id
                                    inner join res_partner client   on imp.client_id=client.id
                                    inner join is_param_project ipp on idm.param_project_id=ipp.id
                where idm.active='t' and idm.param_project_id in (%s)
            """%','.join(modele_ids)
            if cp_id and cp_id!='0':
                SQL+=" and ru.id=%s "%cp_id
            if client:
                SQL+=" and client.name ilike '%"+client+"%' "
            if projet:
                SQL+=" and imp.name ilike '%"+projet+"%' "
            if moule:
                SQL+=" and im.name ilike '"+moule+"%' "
            if type_moule and type_moule=='Actif':
                SQL+=" and im.date_fin is null "


            #** Dossier F *****************************************************
            SQL+="""
                UNION

                select
                    idm.id               id,
                    im.name              moule,
                    im.designation       designation,
                    im.id                moule_id,
                    'is.dossierf'        res_model,
                    imp.name             projet,
                    imp.id               projet_id,
                    rp.name              cp,
                    imp.chef_projet_id   cp_id,
                    client.name          client,
                    imp.client_id        client_id,
                    ipp.ppr_famille      famille,
                    ipp.id               famille_id,
                    idm.etat             etat
                from is_doc_moule idm inner join is_dossierf im     on idm.dossierf_id=im.id
                                    inner join is_mold_project imp  on im.project=imp.id
                                    inner join res_users ru         on imp.chef_projet_id=ru.id
                                    inner join res_partner rp       on ru.partner_id=rp.id
                                    inner join res_partner client   on imp.client_id=client.id
                                    inner join is_param_project ipp on idm.param_project_id=ipp.id
                where idm.active='t' and idm.param_project_id in (%s)
            """%','.join(modele_ids)
            if cp_id and cp_id!='0':
                SQL+=" and ru.id=%s "%cp_id
            if client:
                SQL+=" and client.name ilike '%"+client+"%' "
            if projet:
                SQL+=" and imp.name ilike '%"+projet+"%' "
            if moule:
                SQL+=" and im.name ilike '"+moule+"%' "
            SQL+=" limit 500"
            cr.execute(SQL)
            rows = cr.dictfetchall()
            for row in rows:
                doc_id = row['id']
                doc = self.env['is.doc.moule'].browse(doc_id)
                if doc:
                    key="%s-%s"%(row['moule'],row['moule_id'])
                    if key not in mydict:
                        #** Recherche photo du moule **************************
                        photo=''
                        if doc.idmoule:
                            image = doc.idmoule.image
                            if image and image!='':
                                photo = 'data:image/png;base64, %s'%image.decode("utf-8")
                        #** avancement_j **************************************
                        avancement_j=[False,False]
                        if doc.idmoule:
                            if doc.idmoule.j_actuelle:
                                j_actuelle = dict(GESTION_J).get(doc.idmoule.j_actuelle,"?")
                                avancement_j=[j_actuelle, doc.idmoule.j_avancement]
                        if doc.dossierf_id:
                            avancement_j='Dossier F'
                        vals={
                            'key'         : key,
                            'res_model'   : row['res_model'],
                            'moule'       : row['moule'],
                            'designation' : row['designation'],
                            'moule_id'    : row['moule_id'],
                            'projet'      : row['projet'],
                            'projet_id'   : row['projet_id'],
                            'photo'       : photo,
                            'cp'          : row['cp'],
                            'cp_id'       : row['cp_id'],
                            'familles'    : copy.deepcopy(familles),
                            'avancement_j': avancement_j
                        }
                        mydict[key]=vals
                    for famille in mydict[key]['familles']:
                        famille_id = mydict[key]['familles'][famille]['id']
                        if row['famille_id']==famille_id:
                            #** dateend ***************************************
                            dateend='??'
                            if doc.dateend:
                                dateend=doc.dateend.strftime("%d/%m/%Y")
                            #** style *****************************************
                            color=doc.get_doc_color()
                            style='background-color:%s'%color
                            #** note_indicateur *******************************
                            note = doc.get_doc_note()
                            coefficient=note
                            if doc.etat!='F':
                                note=0
                            note_indicateur = "%s/%s"%(note,coefficient)
                            #** reponnse **************************************
                            reponse = doc.get_doc_reponse()
                            vals={
                                'doc_id'     : doc.id,
                                'etat'       : doc.etat,
                                'dateend'    : dateend,
                                'note'       : note_indicateur,
                                'style'      : style,
                                'dynacase_id': doc.dynacase_id,
                                'reponse'    : reponse,
                            }
                            mydict[key]['familles'][famille].update(vals)
                            # mydict[key]['familles'][famille]['doc_id']      = doc.id
                            # mydict[key]['familles'][famille]['etat']        = doc.etat
                            # mydict[key]['familles'][famille]['dateend']     = dateend
                            # mydict[key]['familles'][famille]['note']        = note_indicateur
                            # mydict[key]['familles'][famille]['style']       = style
                            # mydict[key]['familles'][famille]['dynacase_id'] = doc.dynacase_id
        sorted_dict = dict(sorted(mydict.items())) 

        #** Ajout de la couleur des lignes ************************************
        trcolor=""
        for k in sorted_dict:
            if trcolor=="#ffffff":
                trcolor="#f2f3f4"
            else:
                trcolor="#ffffff"
            #if mem_product_id:
            #    trcolor="#00FAA2"
            trstyle="background-color:%s"%(trcolor)
            sorted_dict[k]["trstyle"] = trstyle





        res={
            "dict"              : sorted_dict,
            "familles"          : familles,
            "client"            : client,
            "projet"            : projet,
            "moule"             : moule,
            "cp_id"             : cp_id,
            "cp_options"        : cp_options,
            "type_moule"        : type_moule,
            "type_moule_options": type_moule_options,
            "modele_id"         : modele_id,
            "modele_options"    : modele_options,
        }
        return res

    