/** @odoo-module **/
import AbstractRendererOwl from 'web.AbstractRendererOwl';
import QWeb from 'web.QWeb';
import session from 'web.session';
import utils from 'web.utils';
//import { useService } from "@web/core/utils/hooks";

const { useState } = owl;
//const _t = core._t;
//const KanbanActivity = field_registry.get('kanban_activity');

var rpc = require('web.rpc');

class DhtmlxganttProjectRenderer extends AbstractRendererOwl {
    setup() {
        super.setup(...arguments);
        this.qweb = new QWeb(this.env.isDebug(), {_s: session.origin});
        this.qweb.add_template(utils.json_node_to_xml(this.props.templates));

        //this.orm = useService("orm");


        this.state = useState({
            dict: {},
            test:'toto et tutu',
            //activityTypeId: null,
            //resIds: []
        });
        // this.widgetComponents = {
        //     ActivityRecord,
        //     KanbanActivity,
        //     KanbanColumnProgressBar,
        // };
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
        var self=this;
        rpc.query({
            model: 'is.doc.moule',
            method: 'get_gantt_documents',
            kwargs: {
                domain         : this.props.domain,
                //decale_planning: this.state.decale_planning,
                //nb_semaines    : this.state.nb_semaines,
            }
        }).then(function (result) {
            console.log(result,self.state,self.test);
            self.state.dict = result.dict;
            // self.state.mois     = result.mois;
            // self.state.semaines = result.semaines;
            // self.state.nb_semaines     = result.nb_semaines;
            // self.state.decale_planning = result.decale_planning;
        });



    }




    // var mailDef = rpc.query({
    //     model: 'mail.mail',
    //     method: 'search_count',
    //     args: [[
    //         ['email_to', '=', 'test@test.test'],
    //         ['body_html', 'like', 'A useless message'],
    //         ['body_html', 'like', 'Service : Development Service'],
    //         ['body_html', 'like', 'State : 44 - UK'],
    //         ['body_html', 'like', 'Products : Xperia,Wiko Stairway']
    //     ]],
    // });




    // OKButtonClick(ev) {
    //     this.state.decale_planning = 0;
    //     this.GetChantiers(this.state.decale_planning, this.state.nb_semaines);
    // }
    // async GetChantiers(s){
    //     var self=this;
    //     rpc.query({
    //         model: 'is.chantier',
    //         method: 'get_chantiers',
    //         kwargs: {
    //             domain         : this.props.domain,
    //             decale_planning: this.state.decale_planning,
    //             nb_semaines    : this.state.nb_semaines,
    //         }
    //     }).then(function (result) {
    //         self.state.dict     = result.dict;
    //         self.state.mois     = result.mois;
    //         self.state.semaines = result.semaines;
    //         self.state.nb_semaines     = result.nb_semaines;
    //         self.state.decale_planning = result.decale_planning;
    //     });
    // }



    // OKButtonClick(ev) {
    //     this.state.decale_planning = 0;
    //     this.GetChantiers(this.state.decale_planning, this.state.nb_semaines);
    // }
    // async GetChantiers(s){
    //     var self=this;
    // }




}

// DhtmlxganttProjectRenderer.components = {
//     ActivityRecordAdapter,
//     ActivityCellAdapter,
//     KanbanColumnProgressBarAdapter,
// };
DhtmlxganttProjectRenderer.template = 'is_dynacase2odoo.DhtmlxganttProjectTemplate';

export default DhtmlxganttProjectRenderer;








// var res = await this.orm.call("product.product", 'get_analyse_cbn', [false],params);

















// import AbstractRendererOwl from 'web.AbstractRendererOwl';
// import core  from 'web.core';
// import QWeb from 'web.QWeb';
// import session from 'web.session';
// import utils from 'web.utils';

// const _t = core._t;
// const { Component, useSubEnv, useState, onWillStart } = owl;



// var rpc = require('web.rpc');


// console.log('DhtmlxganttProjectRenderer');




// class DhtmlxganttProjectRenderer extends AbstractRendererOwl {
//     constructor(parent, props) {
//         super(...arguments);
//         this.qweb = new QWeb(this.env.isDebug(), {_s: session.origin});
//         this.qweb.add_template(utils.json_node_to_xml(props.templates));
 
//         this.state = useState({
//             dict:{},
//         });
//     }

//     mounted() {
//         this.GetDocuments();
//     }

//     TrMouseLeave(ev) {
//         const click=ev.target.attributes.click.value;
//         if (click!="1"){
//             const memstyle = ev.target.attributes.memstyle.value;
//             ev.target.style=memstyle;
//         }
//     }
//     TrMouseEnter(ev) {
//         const click=ev.target.attributes.click.value;
//         if (click!="1"){
//             ev.target.style="background-color:#FFFF00;opacity: 0.5;";
//         }
//     }
//     TrClick(ev) {
//         var click=ev.target.parentElement.attributes.click;
//         if (click!==undefined){
//             click.value=-click.value
//             if (click.value==1){
//                 ev.target.parentElement.style="background-color:rgb(204, 255, 204);opacity: 0.5;";
//             } else {
//                 const memstyle = ev.target.parentElement.attributes.memstyle.value;
//                 ev.target.parentElement.style=memstyle;
//             }
//             ev.target.parentElement.attributes.click.value=click.value;
//         }
//     }


//     PrecedentClick(ev) {
//         console.log('PrecedentClick')
//     }
//     SuivantClick(ev) {
//         console.log('SuivantClick')
//     }
//     OKButtonClick(ev) {
//         console.log('OKButtonClick')
//         this.GetDocuments();
//     }

//     async GetDocuments(s){
//         console.log('GetDocuments')
//     }
// }

// DhtmlxganttProjectRenderer.components = {};
// DhtmlxganttProjectRenderer.template = 'is_dynacase2odoo.DhtmlxganttProjectTemplate';
// export default DhtmlxganttProjectRenderer;
