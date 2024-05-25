/** @odoo-module **/
import AbstractRendererOwl from 'web.AbstractRendererOwl';
import QWeb from 'web.QWeb';
import session from 'web.session';
import utils from 'web.utils';

const { useState, onMounted, onPatched, onWillUnmount } = owl;
var rpc = require('web.rpc');

class DhtmlxganttProjectRenderer extends AbstractRendererOwl {
    setup() {
        super.setup(...arguments);
        this.qweb = new QWeb(this.env.isDebug(), {_s: session.origin});
        this.qweb.add_template(utils.json_node_to_xml(this.props.templates));
        //this.orm = useService("orm");
        this.state = useState({
            dict: {},
        });
        this.ActivePatched=true;
        onMounted(() => this._mounted());
        onPatched(() => this._patched());
        onWillUnmount(() => this._unmount());
    }


    _unmount(){
        while (this.gantt.events.length) {
            this.gantt.detachEvent(this.gantt.events.pop());
        }
    }


    _mounted() {
        this.gantt = gantt;
        this.gantt.lier = false;
        this.gantt.active_task_id = false;

        //Stocker la liste des events pour pouvoir les désactiver avec le _unmount
        if (typeof this.gantt.events === 'undefined') {
            this.gantt.events=[];
        }
        if (typeof this.gantt.markers === 'undefined') {
            this.gantt.markers=[];
        }

        // Je n'ai pas trouvé d'autre solution que d'intégrer l'objet owl dans l'objet gantt pour pouvoir 
        // l'utiliser dans les évènements du Gantt
        gantt.owl = this; 

        this.gantt.i18n.setLocale("fr");
        this.gantt.config.xml_date = "%Y-%m-%d %H:%i";
        //this.gantt.config.date_format = "%d/%m/%Y";
        this.gantt.config.date_grid = "%d/%m/%Y";
        this.gantt.scales = [
            { unit: "year", step: 1, format: "%Y" }
        ];

        this.gantt.config.lightbox.sections = [
            {name: "description", height: 70, map_to: "text", type: "textarea", focus: true},
            {name: "time", type: "duration", map_to: "auto"}
        ];
    
        this.gantt.plugins({
            keyboard_navigation: true,
            undo: true,
            tooltip: true, /* Infobulle sur les taches */
            marker: true,
            fullscreen: true,
            drag_timeline: true,
            multiselect: true,
        });

        this.gantt.events.push(this.gantt.attachEvent("onGanttReady", function(){
            var tooltips = gantt.ext.tooltips;
            tooltips.tooltip.setViewport(gantt.$task_data);
        }));

        this.gantt.config.grid_width = 450;
        this.gantt.config.add_column = false;
        this.gantt.config.drag_progress = false;
        this.gantt.config.scroll_size = 30;
        this.gantt.config.open_tree_initially = true; //Développer tous les niveaux par défaut


        // this.gantt.templates.grid_row_class = function (start_date, end_date, item) {
        //     if (item.progress == 0) return "red";
        //     if (item.progress >= 1) return "green";
        // };
        // this.gantt.templates.task_row_class = function (start_date, end_date, item) {
        //     //if (item.progress == 0) return "red";
        //     //if (item.progress >= 1) return "green";
        // };

        // gantt.config.columns = [
        //     {name:"text",       label:"Task name",  width:"*", tree:true },
        //     {name:"start_date", label:"Start time", align:"center" },
        //     {name:"duration",   label:"Duration",   align:"center" },
        //     {name:"add",        label:"",           width:44 }
        // ];


        //** Configuration des colonnes des tâches
        this.gantt.config.columns = [
            {name: "text"      , label: "Tâche", tree: true , width: "*"},
            {name: "start_date", label: "Début", tree: false, width: 80, align:"center" },
            {name: "duration"  , label: "Durée", tree: false, width: 50, align:"center" },
            // {name: "start_date", label: "Début", tree: true, width: 160},
            // {
            //     name: "progress", label: "%", width: 80, align: "center",
            //     template: function (item) {
            //         // if (item.progress >= 0.5)
            //         //     return "Complete";
            //         // if (item.progress == 0)
            //         //     return "Not started";
            //         return Math.round(item.progress * 100) + "%";
            //     }
            // },
            // {
            //     name: "assigned", label: "Assigné à", align: "center", width: 160,
            //     // template: function (item) {
            //     //     if (!item.users) return "Nobody";
            //     //     return item.users.join(", ");
            //     // }
            // },
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
                        {
                            unit: "day", 
                            format: "%d", 
                            css: function (date) {
                                var cl="jour_ouvert";
                                if(date.getDay()==0||date.getDay()==6){
                                    cl = "jour_ferme";
                                }
                                return cl;
                            }     
                        },
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


        // gantt.config.scales = [
        //     { unit: "month", step: 1, date: "%F" },
        //     { unit: "week", step: 1, date: "%W" },
        //     {
        //         unit: "day", step: 1, date: "%d", css: function (date) {             if (!gantt.isWorkTime({ date: date })) {                 return "weekend";             }         }     },
        // ];




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



        this.gantt.templates.timeline_cell_class = function(task,date){
            if(date.getDay()==0||date.getDay()==6){
                return "jour_ferme";
            }
        };

        this.gantt.templates.tooltip_date_format=function (date){
            var formatFunc = gantt.date.date_to_str("%d/%m/%Y");
            return formatFunc(date);
        };


        /* Text de l'infobulle de la task */
        this.gantt.templates.tooltip_text = function(start,end,task){
            var html=""+
                "<table>"+
                    "<tr style='background:#e5e8e8'><th style='text-align:right;font-weight: bold;'>Tâche      : </th><td>"+task.text+"</td></tr>"+
                    "<tr>                           <th style='text-align:right;font-weight: bold;'>Section    : </th><td>"+task.section+ "</td></tr>"+
                    "<tr>                           <th style='text-align:right;font-weight: bold;'>Responsable: </th><td>"+task.responsable+ "</td></tr>"+
                    "<tr>                           <th style='text-align:right;font-weight: bold;'>Date début : </th><td>"+gantt.templates.tooltip_date_format(start)+ "</td></tr>"+
                    "<tr>                           <th style='text-align:right;font-weight: bold;'>Date fin   : </th><td>"+gantt.templates.tooltip_date_format(end)+"</td></tr>"+
                    "<tr>                           <th style='text-align:right;font-weight: bold;'>Durée      : </th><td>"+task.duration+"</td></tr>"+
                "</table>";
            return html
        };

        //Met une couleur sur les task en fonction de la priority ou de la couleur de la famille
        this.gantt.templates.task_class = function (start, end, task) {
            return task.color_class;
        };

        /*
        //La personnalisation du contenu de la task fonctionne, mais dans ce cas, le onTaskClick ne fonctionne plus
        this.gantt.templates.task_text = function (start, end, task) {
            var html = '<div><a href="https://infosaone.com">infosaone.com</a> : toto et tutu : <span style="background:green;color:red">RED</span</div>';
            return html;
        };
        */
    
        this.gantt.init("gantt_here");

        this.gantt.events.push(this.gantt.attachEvent("onTaskDblClick", function(id,e){
            if (e.target.className=="gantt_task_content"){
                const task = gantt.getTaskBy("id", [id])[0]; // Recherche de la task avec son id
                if (task.model !== undefined){
                    gantt.owl.env.bus.trigger('do-action', {
                        action: {
                            type: 'ir.actions.act_window',
                            res_model: task.model,
                            res_id: parseInt(task.res_id),
                            view_mode: 'form,list',
                            views: [[false, 'form'],[false, 'list']],
                            target: 'new',
                        },
                    });
                }
            }
            return true;
        }));

        //Désactiver l'affichage de la boite de dialogue en double cliquant sur une task
        this.gantt.events.push(this.gantt.attachEvent("onBeforeLightbox", function(id) {
            return false;
        }));
        this.gantt.events.push(this.gantt.attachEvent("onAfterTaskUpdate", function(id,item,){
            this.owl.WriteTask(id, item);
        }));
        this.gantt.events.push(this.gantt.attachEvent("onAfterLinkAdd", function(id,item){
            this.owl.LinkAction('link_add', item);
        }));
        this.gantt.events.push(this.gantt.attachEvent("onAfterLinkDelete", function(id,item){
            this.owl.LinkAction('link_delete', item);
        }));

        this.gantt.events.push(this.gantt.attachEvent("onTaskRowClick", function(id,row){
            console.log('onTaskRowClick',id)
            gantt.active_task_id = id;
        }));



        this.GetDocuments();
    }


    _patched() {
        if (this.ActivePatched==true) {
            this.ActivePatched=false;
            this.GetDocuments();
        } else {
            this.ActivePatched=true;
        }
    }


    rnd() {
        //var x = Math.floor(Math.random()*100)/10;
        var x = Math.random();
        return x
    }


    renderDhtmlxGantt() {
        var data=[];
        var links=[];
        var item={};
        var vals={};

        for (var x in this.state.items) {
            item = this.state.items[x];
            //Doc : https://docs.dhtmlx.com/gantt/desktop__task_properties.html
            vals={
                id:item.id,
                model:item.model,
                res_id:item.res_id,
                text:item.text,
                end_date:item.end_date,
                duration   : item.duration,
                progress   : 0, //this.rnd(),
                assigned   : item.assigned,
                priority   : item.priority,
                champ_perso: "Champ perso à mettre dans l'infobulle",
                parent     : item.parent,
                color_class: item.color_class,
                section    : item.section,
                responsable: item.responsable,
            }
            data.push(vals);
        }
        links   = this.state.links;
        this.gantt.clearAll(); 
        this.gantt.parse({
            data : data,
            links: links,
        });

        
        //markers *************************************************************
        this.gantt.todayMarker = this.gantt.addMarker({
            start_date:  new Date(),
            css: "today",
            text: 'Now',
        });
        for (var k in this.state.markers) {
            var marker = this.state.markers[k];
            var start_date = this.gantt.date.parseDate(marker.start_date,"%Y-%m-%d %H:%i:%s");
            this.gantt.addMarker({ 
                id        : marker.id, 
                start_date: start_date, 
                css       : marker.css, 
                text      : marker.text, 
            });
            this.gantt.markers[marker.j] = marker.id;
        }
        this.gantt.renderMarkers();
        this.gantt.config.show_markers = true;
        //********************************************************************* */

        //** Positionner le gantt au même endroit après le rafrachissement ****
        var active_task_id = this.gantt.active_task_id;
        if (active_task_id!==false){
            var task = this.gantt.getTask(active_task_id)
            var pos = this.gantt.posFromDate(task.start_date);
            this.gantt.scrollTo(pos, null);
            this.gantt.selectTask(active_task_id);
        }
        //*********************************************************************
    }


    RafraichirClick(ev) {
        this.GetDocuments();
    }
    FullscreenClick(ev) {
        if (!this.gantt.getState().fullscreen) {   
            this.gantt.expand();   // expanding the gantt to full screen
        } else {  
            this.gantt.collapse(); // collapsing the gantt to the normal mode
        }
    }
    OpenTreeClick(ev) {
        this.gantt.eachTask(function(task){
            task.$open = true;
        });
        this.gantt.render();
    }
    CloseTreeClick(ev) {
        this.gantt.eachTask(function(task){
            task.$open = false;
        });
        this.gantt.render();
    }
    UndoClick(ev) {
        this.gantt.undo();
    }
    RedoClick(ev) {
        this.gantt.redo();
    }
    AnneeClick(ev) {
        this.gantt.ext.zoom.setLevel("year");
    }
    MoisClick(ev) {
        this.gantt.ext.zoom.setLevel("month");
    }
    SemaineClick(ev) {
        this.gantt.ext.zoom.setLevel("week");
    }
    GotoJ0Click(ev) {
        this.GotoJClick(ev,'j0');
    }
    GotoJ1Click(ev) {
        this.GotoJClick(ev,'j1');
    }
    GotoJ2Click(ev) {
        this.GotoJClick(ev,'j2');
    }
    GotoJ3Click(ev) {
        this.GotoJClick(ev,'j3');
    }
    GotoJ4Click(ev) {
        this.GotoJClick(ev,'j4');
    }
    GotoJ5Click(ev) {
        this.GotoJClick(ev,'j5');
    }
    GotoJClick(ev,j) {
        if (typeof this.gantt.getMarker(this.gantt.markers[j]) !== 'undefined') {
            var marker = this.gantt.getMarker(this.gantt.markers[j]);
            var marker_date = marker.start_date;
            this.gantt.showDate(marker_date)
        }
    }
    LierClick(ev){
        const lier=$(ev.target.checked);
        this.gantt.lier=false;
        if (typeof lier[0] !== 'undefined') this.gantt.lier=true;
    }

    
    async GetDocuments(s){
        var self=this;
        rpc.query({
            model: 'is.doc.moule',
            method: 'get_dhtmlx',
            kwargs: {
                domain: this.props.domain,
            }
        }).then(function (result) {
            self.state.items   = result.items;
            self.state.links   = result.links;
            self.state.markers = result.markers;
            self.renderDhtmlxGantt();
        });
    }

    async WriteTask(id,item){
        self.this = this;
        rpc.query({
            model: 'is.doc.moule',
            method: 'write_task',
            args: [[parseInt(item.res_id)], item.start_date, item.duration,this.gantt.lier]
        }).then(function (result) {
            self.this.GetDocuments();
        });
    }


    async LinkAction(method,item){
        rpc.query({
            model: 'is.doc.moule',
            method: method,
            args: [[false], item.source, item.target]
        }).then(function (result) {
            console.log('LinkAction : result=',result);
        });
    }

}
DhtmlxganttProjectRenderer.template = 'is_dynacase2odoo.DhtmlxganttProjectTemplate';
export default DhtmlxganttProjectRenderer;

