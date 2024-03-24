/** @odoo-module **/
import KanbanRecord from 'web.KanbanRecord';

var DhtmlxganttProjectRecord = KanbanRecord.extend({
    /**
     * @override
     */
    init: function (parent, state) {
        this._super.apply(this,arguments);
        console.log("DhtmlxganttProjectRecord : __get : parent,state,this=",parent,state,this); 
        //this.fieldsInfo = state.fieldsInfo.activity;
    },
});

export default DhtmlxganttProjectRecord;
