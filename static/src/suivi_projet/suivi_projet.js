/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";
import { getDefaultConfig } from "@web/views/view";
import { useService } from "@web/core/utils/hooks";

const { Component, useSubEnv, useState, onWillStart } = owl;


console.log('TEST 1');

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

    async getSuiviProjet(ok=false){
        const params={
            "cp_id"      : this.state.suivi_projet_cp_id,        
            "client"     : this.state.suivi_projet_client,        
            "projet"     : this.state.suivi_projet_projet,        
            "moule"      : this.state.suivi_projet_moule,        
            "type_moule" : this.state.suivi_projet_type_moule,        
            "modele_id"  : this.state.suivi_projet_modele_id,        
            "ok"         : ok,
        }
        var res = await this.orm.call("is.doc.moule", 'get_suivi_projet', [false],params);
        this.state.dict                    = res.dict;
        this.state.suivi_projet_client     = res.client;
        this.state.suivi_projet_projet     = res.projet;
        this.state.suivi_projet_moule      = res.moule;

        this.state.suivi_projet_cp_id      = res.cp_id;
        this.state.cp_options              = res.cp_options;

        this.state.suivi_projet_type_moule = res.type_moule;
        this.state.type_moule_options      = res.type_moule_options;

        this.state.suivi_projet_modele_id  = res.modele_id;
        this.state.modele_options          = res.modele_options;
    }
}

SuiviProjet.components = { Layout };
SuiviProjet.template = "is_dynacase2odoo.suivi_projet_template";
registry.category("actions").add("is_dynacase2odoo.suivi_projet_registry", SuiviProjet);

