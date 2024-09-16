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

    onChangeInput(ev) {
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


        console.log('TEST 2');

        // <td><input name="suivi_projet_cp"         t-att-value="state.suivi_projet_cp"         t-on-change="onChangeInput" t-on-keyup="OKkey" type="text" class="form-control"/></td>
        // <td><input name="suivi_projet_client"     t-att-value="state.suivi_projet_client"     t-on-change="onChangeInput" t-on-keyup="OKkey" type="text" class="form-control"/></td>
        // <td><input name="suivi_projet_projet"     t-att-value="state.suivi_projet_projet"     t-on-change="onChangeInput" t-on-keyup="OKkey" type="text" class="form-control"/></td>
        // <td><input name="suivi_projet_moule"      t-att-value="state.suivi_projet_moule"      t-on-change="onChangeInput" t-on-keyup="OKkey" type="text" class="form-control"/></td>
        // <td><input name="suivi_projet_type_moule" t-att-value="state.suivi_projet_type_moule" t-on-change="onChangeInput" t-on-keyup="OKkey" type="text" class="form-control"/></td>
        // <td><input name="suivi_projet_modele"     t-att-value="state.suivi_projet_modele"     t-on-change="onChangeInput" t-on-keyup="OKkey" type="text" class="form-control"/></td>



        const params={
            "cp"         : this.state.suivi_projet_cp,        
            "client"     : this.state.suivi_projet_client,        
            "projet"     : this.state.suivi_projet_projet,        
            "moule"      : this.state.suivi_projet_moule,        
            "type_moule" : this.state.suivi_projet_type_moule,        
            "modele"     : this.state.suivi_projet_modele,        
            "ok"         : ok,
        }
        var res = await this.orm.call("is.doc.moule", 'get_suivi_projet', [false],params);
        this.state.suivi_projet_cp         = res.cp;
        this.state.suivi_projet_client     = res.client;
        this.state.suivi_projet_projet     = res.projet;
        this.state.suivi_projet_moule      = res.moule;
        this.state.suivi_projet_type_moule = res.type_moule;
        this.state.suivi_projet_modele     = res.modele;
        this.state.dict  = res.dict;
    }
}

SuiviProjet.components = { Layout };
SuiviProjet.template = "is_dynacase2odoo.suivi_projet_template";
registry.category("actions").add("is_dynacase2odoo.suivi_projet_registry", SuiviProjet);

