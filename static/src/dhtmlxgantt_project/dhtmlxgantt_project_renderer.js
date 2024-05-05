/** @odoo-module **/
import AbstractRendererOwl from 'web.AbstractRendererOwl';
import QWeb from 'web.QWeb';
import session from 'web.session';
import utils from 'web.utils';
//import { useService } from "@web/core/utils/hooks";

const { useState, onMounted, onPatched, onWillUnmount } = owl;



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
        this.events=[];
        this.ActivePatched=true;
        onMounted(() => this._mounted());
        onPatched(() => this._patched());
        //onWillUnmount(() => this._willUnmount());
    }


    // setup
    // willStart
    // willRender
    // rendered
    // mounted
    // willUpdateProps
    // willPatch
    // patched
    // willUnmount
    // willDestroy
    // onError






    _mounted() {
        console.log('mounted',this.state.items)


        this.gantt = gantt;
        // Je n'ai pas trouvé d'autre solution que d'intégrer l'objet owl dans l'objet gantt pour pouvoir 
        //l'utiliser dans les évènements du Gantt
        gantt.owl = this; 

        this.gantt.i18n.setLocale("fr");
        this.gantt.config.xml_date = "%Y-%m-%d %H:%i";
        this.gantt.scales = [
            { unit: "year", step: 1, format: "%Y" }
        ];

        this.gantt.config.lightbox.sections = [
            {name: "description", height: 70, map_to: "text", type: "textarea", focus: true},
            {name: "time", type: "duration", map_to: "auto"}
        ];
    
        // this.gantt.config.scale_height = 50;
    
        // this.gantt.config.scales = [
        //     {unit: "month", format: "%F, %Y"},
        //     {unit: "day", step: 1, format: "%D %j"}
        //     //{unit: "day", step: 1, format: "%j, %D"}
        // ];

        // this.gantt.attachEvent("onLightboxSave", function (id, task, is_new) {
        //     task.unscheduled = !task.start_date;
        //     return true;
        // });

        this.gantt.plugins({
            keyboard_navigation: true,
            undo: true,
            tooltip: true, /* Infobulle sur les taches => Cela fonctionne */
            marker: true,
        });


        this.gantt.attachEvent("onGanttReady", function(){
            var tooltips = gantt.ext.tooltips;
            tooltips.tooltip.setViewport(gantt.$task_data);
        });



        this.gantt.config.grid_width = 620;
        this.gantt.config.add_column = false;
        // this.gantt.templates.grid_row_class = function (start_date, end_date, item) {
        //     if (item.progress == 0) return "red";
        //     if (item.progress >= 1) return "green";
        // };
        // this.gantt.templates.task_row_class = function (start_date, end_date, item) {
        //     //if (item.progress == 0) return "red";
        //     //if (item.progress >= 1) return "green";
        // };

        //** Configuration des colonnes des tâches
        this.gantt.config.columns = [
            {name: "text", label: "Tâche", tree: true, width: 260},
            {name: "start_date", label: "Début", tree: true, width: 160},
            {
                name: "progress", label: "%", width: 80, align: "center",
                template: function (item) {
                    // if (item.progress >= 0.5)
                    //     return "Complete";
                    // if (item.progress == 0)
                    //     return "Not started";
                    return Math.round(item.progress * 100) + "%";
                }
            },
            // {
            //     name: "assigned", label: "Assigné à", align: "center", width: 160,
            //     // template: function (item) {
            //     //     if (!item.users) return "Nobody";
            //     //     return item.users.join(", ");
            //     // }
            // },
            {name: "duration", label: "Durée", tree: true, width: 120},
        ];


        /* ZOOM */
        var zoomConfig = {
            levels: [
                {
                    name:"week",
                    scale_height: 45,
                    min_column_width:25,
                    scales:[
                        {unit: "week", format: "%F %Y S%W"},
                        {unit: "day", format: "%d"},
                    ]
                },
                {
                    name:"month",
                    scale_height: 45,
                    min_column_width:30,
                    scales:[
                        {unit: "month", format: "%F %Y"},
                        {unit: "week", format: "S%W"},
                    ]
                },
                {
                    name:"year",
                    scale_height: 45,
                    min_column_width: 35,
                    scales:[
                        {unit: "year" , step: 1, format: "%Y"},
                        {unit: "month", step: 1, format: "%M"},
                    ]
                }
            ],
            useKey: "ctrlKey",
            trigger: "wheel",
            element: function(){
                return gantt.$root.querySelector(".gantt_task");
            }
        };
        this.gantt.ext.zoom.init(zoomConfig);


        // this.gantt.message({
        //     text: "Ceci est un message" ,
        //     expire: 2000
        // });


        this.gantt.config.sort = true;
        this.gantt.config.row_height = 25;


        /* Text à gauche de la task => https://docs.dhtmlx.com/gantt/desktop__timeline_templates.html */
        // const formatter = gantt.ext.formatters.durationFormatter({
        //     format: ["day"]
        // });
        // this.gantt.templates.leftside_text = function(start, end, task){
        //     return formatter.format(task.duration);
        // };

        /* Text à droite de la task */
        // this.gantt.templates.rightside_text = function(start, end, task){
        //     return "ID: #" + task.id;
        // };

        /* Text de progression de la task */
        // this.gantt.templates.progress_text=function(start, end, task){
        //     return Math.round(task.progress*100);
        // };
        /* Text de la task */
        gantt.templates.task_text=function(start, end, task){
            return "";
        };



        /* Text de l'infobulle de la task */
        this.gantt.templates.tooltip_text = function(start,end,task){
            return "<b>Task:</b> "+task.text+"<br/><b>Start date:</b> " + 
            gantt.templates.tooltip_date_format(start)+ 
            "<br/><b>End date:</b> "+gantt.templates.tooltip_date_format(end)+
            "<br/><b>Progress:</b> "+task.progress+
            "<br/>Durée: "+task.duration+
            "<br/><div style='color:red'>Autre: "+task.champ_perso+"</div>";
        };

        //Met une couleur sur les task en fonction de la priority ou de la couleur de la famille
        this.gantt.templates.task_class = function (start, end, task) {
            //var color_class = 'is_param_projet_10100';
            var color_class = task.color_class;
            console.log(task,color_class);
            return color_class;

            // var cl="";
            // switch (task.priority) {
            //     case 0:
            //         cl = "high";
            //         break;
            //     case 1:
            //         cl = "medium";
            //         break;
            //     case 2:
            //         cl= "low";
            //         break;
            // }
            // return cl;
        };
        this.gantt.init("gantt_here");
        this.GetDocuments();
    }


    _patched() {
        console.log('_patched : this.ActivePatched=',this.ActivePatched);
        if (this.ActivePatched==true) {
            this.ActivePatched=false;
            this.GetDocuments();
        } else {
            this.ActivePatched=true;
        }
        //this.renderDhtmlxGantt();
        //this.GetDocuments();
    }


    rnd() {
        //var x = Math.floor(Math.random()*100)/10;
        var x = Math.random();
        return x
    }


    renderDhtmlxGantt() {
        console.log('renderDhtmlxGantt : this.state.items=',this.state.items);
        var data=[];
        var links=[];
        var item={};
        var vals={};
        var marker_id=0;

        for (var x in this.state.items) {
            item = this.state.items[x];

            console.log('item=',item);


            marker_id = item.id
            //Doc : https://docs.dhtmlx.com/gantt/desktop__task_properties.html
            vals={
                id:item.id,
                text:item.text,
                //start_date:item.date_assign,
                //start_date:item.start_date,
                end_date:item.end_date,
                //duration:  Math.round(this.rnd()*100)+1,
                duration   : item.duration,
                progress   : this.rnd(),
                assigned   : item.assigned,
                priority   : item.priority,
                champ_perso: "Champ perso à mettre dans l'infobulle",
                parent     : item.parent,
                color_class: item.color_class,
            }
            data.push(vals);
        }
        links = this.state.links;

        this.gantt.clearAll(); 
        this.gantt.parse({
            data : data,
            links: links,
        });
        // this.gantt.message({
        //     text: "Ceci est un autre message" ,
        //     expire: 2000
        // });


        //Positionner un marker sur une task pour pouvoir ensuite se déplacer dessus avec le bouton OKclickMarker
        if (marker_id>0){
            var current_time = this.gantt.getTask(marker_id).start_date;
            var text =  this.gantt.getTask(marker_id).text
            this.todayMarker = this.gantt.addMarker({ 
                start_date: current_time, 
                css: "today", 
                text: "Marqueur pour "+text,
            });
        }
    
        // detach all saved events
        while (this.events.length)
            this.gantt.detachEvent(this.events.pop());
            //En cliqant sur une task, cela affiche la liste des clients d'Odoo
            this.gantt.attachEvent("onTaskClick", function(id,e){
            if (e.target.className=="gantt_task_content"){
                gantt.owl.env.bus.trigger('do-action', {
                    action: {
                        type: 'ir.actions.act_window',
                        res_model: 'project.task',
                        res_id: parseInt(id),
                        view_mode: 'form,list',
                        views: [[false, 'form'],[false, 'list']],
                        //target: 'current'
                        //target: 'new',
                    },
                });
            }
            return true;
        });


        this.events.push(this.gantt.attachEvent("onAfterTaskUpdate", function(id,item){
            console.log('onAfterTaskUpdate',id,item)
            //this.owl.WriteTask(id, item.end_date, item.duration);
        }));
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
        console.log('GetDocuments : this.ActivePatched=',this.ActivePatched)
        var self=this;
        rpc.query({
            model: 'is.doc.moule',
            method: 'get_dhtmlx',
            kwargs: {
                domain: this.props.domain,
            }
        }).then(function (result) {
            console.log('result=',result);
            self.state.items = result.items;
            self.state.links = result.links;
            self.renderDhtmlxGantt();
        });
    }
}
DhtmlxganttProjectRenderer.template = 'is_dynacase2odoo.DhtmlxganttProjectTemplate';
export default DhtmlxganttProjectRenderer;

