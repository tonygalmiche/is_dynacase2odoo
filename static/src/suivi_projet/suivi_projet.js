/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";
import { getDefaultConfig } from "@web/views/view";
import { useService } from "@web/core/utils/hooks";
const { Component, useSubEnv, useState, onWillStart } = owl;


class SuiviProjet extends Component {
    setup() {
        this.user_id = useService("user").context.uid;
        this.action  = useService("action");
        this.orm     = useService("orm");
        this.state   = useState({
            'dict': {},
        });

        useSubEnv({
            config: {
                ...getDefaultConfig(),
                ...this.env.config,
            },
        });
        this.display = {
            controlPanel: { "top-right": false, "bottom-right": false },
        };
        onWillStart(async () => {
            this.getSuiviProjet();
        });
    } 

    OKclick(ev) {
        this.getSuiviProjet(true);
    }

    // onChangeInput(ev) {
    //     this.state[ev.target.name] = ev.target.value;
    // }



    onChangeInput(ev) {
        console.log("onChangeInput",ev.target.name,ev.target.value);
        this.state[ev.target.name] = ev.target.value;
    }



    OKkey(ev) {
        if (ev.keyCode === 13) {
            this.getSuiviProjet(true);
        }
    }


    TrMouseLeave(ev) {
        const click=ev.target.attributes.click.value;
        if (click!="1"){
            const memstyle = ev.target.attributes.memstyle.value;
            ev.target.style=memstyle;
        }
    }

    TrMouseEnter(ev) {
        const click=ev.target.attributes.click.value;
        if (click!="1"){
            ev.target.style="background-color:#FFFF00";
        }
    }

    TrClick(ev) {
        //var click=parseInt(ev.target.parentElement.attributes.click.value);
        var click=ev.target.parentElement.attributes.click;
        if (click!==undefined){
            click.value=-click.value
            if (click.value==1){
                ev.target.parentElement.style="background-color:#ecf5e8";
            } else {
                const memstyle = ev.target.parentElement.attributes.memstyle.value;
                ev.target.parentElement.style=memstyle;
            }
            ev.target.parentElement.attributes.click.value=click.value;
        }
    }


    DateClick(ev) {
        const res_id    = ev.target.attributes.res_id.value;
        this.action.doAction({
            type: 'ir.actions.act_window',
            target: 'new',
            res_id: parseInt(res_id),
            res_model: 'is.doc.moule',
            views: [[false, 'form']],
        });
    }
    ProjetClick(ev) {
        const projet_id    = ev.target.attributes.projet_id.value;
        this.action.doAction({
            type: 'ir.actions.act_window',
            target: 'new',
            res_id: parseInt(projet_id),
            res_model: 'is.mold.project',
            views: [[false, 'form']],
        });
    }
    MouleDossierfClick(ev) {
        const res_model = ev.target.attributes.res_model.value;
        const res_id    = ev.target.attributes.res_id.value;
        console.log(res_model, res_id)
        this.action.doAction({
            type: 'ir.actions.act_window',
            target: 'new',
            res_id: parseInt(res_id),
            res_model: res_model,
            views: [[false, 'form']],
        });
    }
    DynacaseClick(ev) {
        const dynacase_id    = ev.target.attributes.dynacase_id.value;
        const url="https://dynacase-rp/?sole=Y&app=FDL&action=FDL_CARD&latest=Y&id="+dynacase_id;
        console.log('dynacase_id=',dynacase_id,url);
        this.action.doAction({
            type: 'ir.actions.act_url',
            target: 'new',
            url: url,
        });
    }
    


    ListeDocClick(ev) {

        console.log(this.state.suivi_projet_modele_id);

        const res_model = ev.target.attributes.res_model.value;
        const res_id    = ev.target.attributes.res_id.value;
        const modele_id = this.state.suivi_projet_modele_id;


        this.getDocModele(res_model,res_id,modele_id);


    }



    async getDocModele(res_model,res_id,modele_id){
        const params={
            "res_model": res_model,        
            "res_id"   : res_id,        
            "modele_id": modele_id,        
        }
        var res = await this.orm.call("is.doc.moule", 'get_doc_modele', [false],params);
        console.log(res_model,res_id,modele_id,res);
  

        this.action.doAction({
            type: 'ir.actions.act_window',
            name: 'Liste',
            target: 'current',
            res_model: 'is.doc.moule',
            views: [[false, 'tree'],[false, 'form']],
            domain: [
                ['id','in',res.ids],
            ],
        });




    }




    async getSuiviProjet(ok=false){
        const params={
            "cp_id"      : this.state.suivi_projet_cp_id,        
            "client"     : this.state.suivi_projet_client,        
            "projet"     : this.state.suivi_projet_projet,        
            "moule"      : this.state.suivi_projet_moule,        
            "type_moule" : this.state.suivi_projet_type_moule,        
            "avec_photo" : this.state.suivi_projet_avec_photo,        
            "modele_id"  : this.state.suivi_projet_modele_id,        
            "ok"         : ok,
        }
        var res = await this.orm.call("is.doc.moule", 'get_suivi_projet', [false],params);
        this.state.dict                    = res.dict;
        this.state.familles                = res.familles;
        this.state.suivi_projet_client     = res.client;
        this.state.suivi_projet_projet     = res.projet;
        this.state.suivi_projet_moule      = res.moule;
        this.state.suivi_projet_cp_id      = res.cp_id;
        this.state.cp_options              = res.cp_options;
        this.state.suivi_projet_type_moule = res.type_moule;
        this.state.type_moule_options      = res.type_moule_options;
        this.state.suivi_projet_avec_photo = res.avec_photo;
        this.state.avec_photo_options      = res.avec_photo_options;
        this.state.suivi_projet_modele_id  = res.modele_id;
        this.state.modele_options          = res.modele_options;
    }
}

SuiviProjet.components = { Layout };
SuiviProjet.template = "is_dynacase2odoo.suivi_projet_template";
registry.category("actions").add("is_dynacase2odoo.suivi_projet_registry", SuiviProjet);

