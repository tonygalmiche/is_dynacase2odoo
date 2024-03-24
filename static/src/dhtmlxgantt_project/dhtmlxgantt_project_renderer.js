/** @odoo-module **/

import ActivityRecord from '@mail/js/views/activity/activity_record';

import AbstractRendererOwl from 'web.AbstractRendererOwl';
import core from 'web.core';
import field_registry from 'web.field_registry';
import KanbanColumnProgressBar from 'web.KanbanColumnProgressBar';
import { ComponentAdapter } from 'web.OwlCompatibility';
import QWeb from 'web.QWeb';
import session from 'web.session';
import utils from 'web.utils';

const { useState } = owl;
const _t = core._t;
const KanbanActivity = field_registry.get('kanban_activity');



class DhtmlxganttProjectRenderer extends AbstractRendererOwl {
    setup() {
        super.setup(...arguments);
        this.qweb = new QWeb(this.env.isDebug(), {_s: session.origin});
        this.qweb.add_template(utils.json_node_to_xml(this.props.templates));
        this.activeFilter = useState({
            state: null,
            //activityTypeId: null,
            //resIds: []
        });
        // this.widgetComponents = {
        //     ActivityRecord,
        //     KanbanActivity,
        //     KanbanColumnProgressBar,
        // };
    }


}

// DhtmlxganttProjectRenderer.components = {
//     ActivityRecordAdapter,
//     ActivityCellAdapter,
//     KanbanColumnProgressBarAdapter,
// };
DhtmlxganttProjectRenderer.template = 'is_dynacase2odoo.DhtmlxganttProjectTemplate';

export default DhtmlxganttProjectRenderer;

























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
