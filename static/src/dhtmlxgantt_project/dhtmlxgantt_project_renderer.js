/** @odoo-module **/
import AbstractRendererOwl from 'web.AbstractRendererOwl';
import core  from 'web.core';
import QWeb from 'web.QWeb';
import session from 'web.session';
import utils from 'web.utils';

const _t = core._t;
const { useState } = owl.hooks;
var rpc = require('web.rpc');


class DhtmlxganttProjectRenderer extends AbstractRendererOwl {
    constructor(parent, props) {
        super(...arguments);
        this.qweb = new QWeb(this.env.isDebug(), {_s: session.origin});
        this.qweb.add_template(utils.json_node_to_xml(props.templates));
 
        //useState permet de faire un lien entre la vue XML et l'Object Javascript
        //Chaque modification de l'objet this.state entraine une modification de l'interface utilisateur
        this.state = useState({
            dict:{},
        });
    }

    mounted() {
        this.GetDocuments();
    }


    // Click pour colorier une ligne
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
            ev.target.style="background-color:#FFFF00;opacity: 0.5;";
        }
    }
    TrClick(ev) {
        var click=ev.target.parentElement.attributes.click;
        if (click!==undefined){
            click.value=-click.value
            if (click.value==1){
                ev.target.parentElement.style="background-color:rgb(204, 255, 204);opacity: 0.5;";
            } else {
                const memstyle = ev.target.parentElement.attributes.memstyle.value;
                ev.target.parentElement.style=memstyle;
            }
            ev.target.parentElement.attributes.click.value=click.value;
        }
    }


    PrecedentClick(ev) {
        console.log('PrecedentClick')
    }
    SuivantClick(ev) {
        console.log('SuivantClick')
    }
    OKButtonClick(ev) {
        console.log('OKButtonClick')
        this.GetDocuments();
    }

    async GetDocuments(s){
        console.log('GetDocuments')
        // var self=this;
        // rpc.query({
        //     model: 'is.chantier',
        //     method: 'get_chantiers',
        //     kwargs: {
        //         domain         : this.props.domain,
        //         decale_planning: this.state.decale_planning,
        //         nb_semaines    : this.state.nb_semaines,
        //     }
        // }).then(function (result) {
        //     self.state.dict     = result.dict;
        //     self.state.mois     = result.mois;
        //     self.state.semaines = result.semaines;
        //     self.state.nb_semaines     = result.nb_semaines;
        //     self.state.decale_planning = result.decale_planning;
        // });
    }
}

DhtmlxganttProjectRenderer.components = {};
DhtmlxganttProjectRenderer.template = 'is_dynacase2odoo.DhtmlxganttProjectTemplate';
export default DhtmlxganttProjectRenderer;
