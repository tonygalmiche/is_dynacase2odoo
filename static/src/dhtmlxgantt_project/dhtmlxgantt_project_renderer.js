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
        console.log('_unmount);')
        this.gantt.clearAll(); 
        this.gantt.detachAllEvents();


        console.log(this.state.markers)
        for (var k in this.state.markers) {
            var marker = this.state.markers[k];
            console.log(marker.id)
            this.gantt.deleteMarker(marker.id);
        }


    }


    _mounted() {
        console.log('_mounted');
        this.gantt = gantt;
        // Je n'ai pas trouvé d'autre solution que d'intégrer l'objet owl dans l'objet gantt pour pouvoir 
        // l'utiliser dans les évènements du Gantt
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
            tooltip: true, /* Infobulle sur les taches */
            marker: true,
            fullscreen: true,
            drag_timeline: true,
            multiselect: true,
        });


        this.gantt.attachEvent("onGanttReady", function(){
            var tooltips = gantt.ext.tooltips;
            tooltips.tooltip.setViewport(gantt.$task_data);
        });



        this.gantt.config.grid_width = 620;
        this.gantt.config.add_column = false;
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

        /*
        //La personnalisation du contenu de la task fonctionne, mais dans ce cas, le onTaskClick ne fonctionne plus
        this.gantt.templates.task_text = function (start, end, task) {
            var html = '<div><a href="https://infosaone.com">infosaone.com</a> : toto et tutu : <span style="background:green;color:red">RED</span</div>';
            return html;
        };
        */
    
        this.gantt.init("gantt_here");

        this.gantt.attachEvent("onTaskDblClick", function(id,e){
            if (e.target.className=="gantt_task_content"){
                const task = gantt.getTaskBy("id", [id])[0]; // Recherche de la task avec son id
                if (task.model !== undefined){
                    //console.log(gantt.getTaskCount());      // Nombre de tasks
                    //console.log(gantt.getTaskByTime());     // Retourne toutes les tasks
                    console.log(id,task.res_id,task.model);
                    gantt.owl.env.bus.trigger('do-action', {
                        action: {
                            type: 'ir.actions.act_window',
                            res_model: task.model,
                            res_id: parseInt(task.res_id),
                            view_mode: 'form,list',
                            views: [[false, 'form'],[false, 'list']],
                            //target: 'current',
                            target: 'new',
                        },
                    });
                }
            }
            return true;
        });

        //Désactiver l'affichage de la boite de dialogue en double cliquant sur une task
        this.gantt.attachEvent("onBeforeLightbox", function(id) {
            return false;
        });

        this.gantt.attachEvent("onAfterTaskUpdate", function(id,item){
            this.owl.WriteTask(id, item);
        });
 
        this.gantt.attachEvent("onAfterLinkAdd", function(id,item){
            console.log('onAfterLinkAdd : id,item=',id,item);
            this.owl.LinkAction('link_add', item);
        });

         this.gantt.attachEvent("onAfterLinkDelete", function(id,item){
            console.log('onAfterLinkDelete : id,item=',id,item);
            this.owl.LinkAction('link_delete', item);
        });

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
        var markers=[];
        var item={};
        var vals={};
        //var marker_id=0;

        for (var x in this.state.items) {
            item = this.state.items[x];
            //marker_id = item.id
            //Doc : https://docs.dhtmlx.com/gantt/desktop__task_properties.html
            vals={
                id:item.id,
                model:item.model,
                res_id:item.res_id,
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
        links   = this.state.links;
        markers = this.state.markers;
        console.log(markers);

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
        // if (marker_id>0){
        //     var current_time = this.gantt.getTask(marker_id).start_date;
        //     var text =  this.gantt.getTask(marker_id).text
        //     this.todayMarker = this.gantt.addMarker({ 
        //         start_date: current_time, 
        //         css: "today", 
        //         text: "Marqueur pour "+text,
        //     });
        // }




        this.gantt.todayMarker = this.gantt.addMarker({
            start_date:  new Date(),
            css: "today",
            text: 'Now',
        });
        
        //var marker = document.getElementsByClassName("gantt_marker")[0]


        //TODO : L'affichage des marqueurs ne fonctionne que la premiere fois. Après il faut rafraichir le navigateur
        for (var k in this.state.markers) {
            var marker = this.state.markers[k];
            var start_date = this.gantt.date.parseDate(marker.start_date,"%Y-%m-%d %H:%i:%s");
            console.log(k, marker.id, marker.start_date, marker.text,start_date);
            var res=this.gantt.addMarker({ 
                id        : marker.id, 
                start_date: start_date, 
                css       : marker.css, 
                text      : marker.text, 
            });
            console.log('res=',res);
        }
        this.gantt.renderMarkers();
        this.gantt.config.show_markers = true;
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
        console.log('AnneeClick')
        this.gantt.ext.zoom.setLevel("year");
    }
    MoisClick(ev) {
        console.log('MoisClick')
        this.gantt.ext.zoom.setLevel("month");
    }
    SemaineClick(ev) {
        console.log('SemaineClick')
        this.gantt.ext.zoom.setLevel("week");
    }
 


    
    toggle_chart(ev){
        this.gantt.config.show_chart = !this.gantt.config.show_chart;
        this.gantt.render();
        //this.gantt.init("gantt_here");
    }
    
    recreate_marker(ev){
      //gantt.init("gantt_here");

      //var current_time = this.gantt.getTask(1).start_date;
      this.gantt.deleteMarker(this.gantt.todayMarker);
      this.gantt.todayMarker = this.gantt.addMarker({
        start_date: new Date(), 
        css: "today",
        text: 'Now 2',
      });
      console.log(this.gantt.todayMarker, "todayMarker");

      this.gantt.render();
      this.gantt.renderMarkers();
      this.gantt.config.show_markers = true;


      this.gantt.message("Re-created marker")
    }

    gantt_init(ev){
        this.gantt.init("gantt_here");
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

            console.log('markers=',self.state.markers);


            self.renderDhtmlxGantt();
        });
    }

    async WriteTask(id,item){
        rpc.query({
            model: 'is.doc.moule',
            method: 'write_task',
            args: [[parseInt(item.res_id)], item.end_date, item.duration]
        }).then(function (result) {
            console.log('WriteTask : result=',result);
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

