/** @odoo-module **/
import AbstractRendererOwl from 'web.AbstractRendererOwl';
import QWeb from 'web.QWeb';
import session from 'web.session';
import utils from 'web.utils';
const Dialog = require('web.Dialog');
const { useState, onMounted, onPatched, onWillUnmount } = owl;
var rpc = require('web.rpc');

class DhtmlxganttProjectRenderer extends AbstractRendererOwl {
    setup() {
        super.setup(...arguments);
        this.qweb = new QWeb(this.env.isDebug(), {_s: session.origin});
        this.qweb.add_template(utils.json_node_to_xml(this.props.templates));
        //this.orm = useService("orm");
        this.state = useState({
            dict         : {},
            lier         : false,
            dossier_id   : false,
            dossier_model: false,
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

        this.gantt.lier = this.state.lier;
        this.gantt.active_task_id = false;
        //this.gantt.scroll=false;

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
        //this.gantt.config.open_tree_initially = true; //Développer tous les niveaux par défaut


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



        // Ajouter dans le tableau du Gantt le champ « Action » => I, R, V
        // => Enlever la colonne « Durée » du  Gantt
        // => Ajouter les responsable => Première lettre du nom et du prénom


        //** Configuration des colonnes des tâches
        this.gantt.config.columns = [
            {name: "text"      , label: "Tâche", tree: true , width: "*"},
            {name: "trash",label: '',width: 25,template: function (task) {
                var button=''
                if(task.model=='is.doc.moule') {
                    button='<i class="fa fa-trash"  style="cursor: pointer;" title="Supprimer cette tâche" data-action="delete"></i>';
                }
                return (button);
            }},
            {name: "start_date", label: "Début", tree: false, width: 80, align:"center" },
            {name: "irv"      , label: "IRV", tree: false, width: 30, align:"center" },
            {name: "initiales", label: "Rsp", tree: false, width: 30, align:"center" },
            {name: "copy",label: '',width: 50,template: function (task) {
                var button=''
                if(task.model=='is.doc.moule') {
                    button='<i class="fa fa-copy"  style="cursor: pointer;" title="Dupliquer cette tâche" data-action="copy"></i>';
                }
                return (button);
            }},

            // {name: "edit",label: '',width: 50,template: function (task) {
            //     return (
            //         '<i class="fa fa-pencil" style="cursor: pointer;" title="Modifier"  data-action="edit"></i>' +
            //         '<i class="fa fa-plus"   style="cursor: pointer;" title="Ajouter"   data-action="add"></i>'
            //         );
            // }},


            //{name: "duration"  , label: "Durée", tree: false, width: 50, align:"center" },
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
                return "jour_weekend";
            }
            if (typeof gantt.owl.state.jour_fermeture_ids !== 'undefined') {
                const jour_fermeture_ids = gantt.owl.state.jour_fermeture_ids;
                var formatFunc = gantt.date.date_to_str("%Y-%m-%d");
                var date_str = formatFunc(date); 
                if(jour_fermeture_ids.indexOf(date_str)>=0){
                    return "jour_fermeture";
                }
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
                    "<tr>                           <th style='text-align:right;font-weight: bold;'>J prévue   : </th><td>"+task.j_prevue+ "</td></tr>"+
                    "<tr>                           <th style='text-align:right;font-weight: bold;'>Action     : </th><td>"+task.irv+ "</td></tr>"+
                    "<tr>                           <th style='text-align:right;font-weight: bold;'>Responsable: </th><td>"+task.responsable+ "</td></tr>"+
                    "<tr>                           <th style='text-align:right;font-weight: bold;'>Date début : </th><td>"+gantt.templates.tooltip_date_format(start)+ "</td></tr>"+
                    "<tr>                           <th style='text-align:right;font-weight: bold;'>Date fin   : </th><td>"+gantt.templates.tooltip_date_format(end)+"</td></tr>"+
                    "<tr>                           <th style='text-align:right;font-weight: bold;'>Durée      : </th><td>"+task.duration+"</td></tr>"+
                    "<tr>                           <th style='text-align:right;font-weight: bold;'>Attendus   : </th><td>"+task.attendus+"</td></tr>"+
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
                    gantt.owl.GetFormId(task);
                }
            }
            return true;
        }));

        //Désactiver l'affichage de la boite de dialogue en double cliquant sur une task
        this.gantt.events.push(this.gantt.attachEvent("onBeforeLightbox", function(id) {
            return false;
        }));
        this.gantt.events.push(this.gantt.attachEvent("onTaskClick", function(id, e){
            var button = e.target.closest("[data-action]")
            if(button){
                var action = button.getAttribute("data-action");
                switch (action) {
                    // case "edit":
                    //     console.log('TEST edit',id)
                    //     gantt.showLightbox(id);
                    //     break;
                    // case "add":
                    //     console.log('TEST add',id)
                    //     gantt.createTask(null, id);
                    //     break;
                    case "copy":
                        const task = gantt.getTaskBy("id", [id])[0]; // Recherche de la task avec son id
                        if (task.model=='is.doc.moule'){
                            gantt.owl.CopyTask(id, task);

                        }
                        break;
                    case "delete":
                        gantt.confirm({
                            title: gantt.locale.labels.confirm_deleting_title,
                            text: "Confirmez-vous la suppression (archivage) de cette tâche ?",   //gantt.locale.labels.confirm_deleting,
                            callback: function (res) {
                                if (res) {
                                    const task = gantt.getTaskBy("id", [id])[0]; // Recherche de la task avec son id
                                    if (task.model=='is.doc.moule'){
                                        gantt.owl.ArchiveTask(id, task);
                                    }
                                }
                            }
                        });
                        break;
                }
                return false;
    
            }
            return true;
        }));
    

        this.gantt.events.push(this.gantt.attachEvent("onTaskOpened", function (id) {
            this.owl.OpenCloseTask(id,'open');
            const task = gantt.getTaskBy("id", [id])[0]; // Recherche de la task avec son id
        }));
        this.gantt.events.push(this.gantt.attachEvent("onTaskClosed", function (id) {
            this.owl.OpenCloseTask(id,'close');
        }));


        this.gantt.events.push(this.gantt.attachEvent("onAfterTaskDrag", function(id, mode, e){
            gantt.active_task_id = id;
            var scroll = gantt.getScrollState();
            this.owl.SetScroll(scroll);
            const task = gantt.getTaskBy("id", [id])[0]; // Recherche de la task avec son id
            this.owl.WriteTask(id, task, mode);
        }));
        this.gantt.events.push(this.gantt.attachEvent("onAfterLinkAdd", function(id,item){
            this.owl.LinkAction('link_add', item);
        }));
        this.gantt.events.push(this.gantt.attachEvent("onAfterLinkDelete", function(id,item){
            this.owl.LinkAction('link_delete', item);
        }));
        this.gantt.events.push(this.gantt.attachEvent("onTaskRowClick", function(id,row){
            gantt.active_task_id = id;
            var scroll = gantt.getScrollState();
            this.owl.SetScroll(scroll);
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
                assigned   : item.assigned,
                priority   : item.priority,
                parent     : item.parent,
                color_class: item.color_class,
                section    : item.section,
                responsable: item.responsable,
                initiales  : item.initiales,
                irv        : item.irv,
                attendus   : item.attendus,
                j_prevue   : item.j_prevue,
                open       : item.open,
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
            id        : 'Now',
            start_date:  new Date(),
            css       : "today",
            text      : 'Now',
        });
        this.gantt.markers['Now'] = 'Now';
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
        //*********************************************************************

        //** Positionner le gantt au même endroit après le rafrachissement ****
        //var scroll = this.gantt.scroll;
        //if (scroll!==false){
        //    this.gantt.scrollTo(scroll.x, scroll.y);
        //    //this.gantt.selectTask(this.gantt.active_task_id;);
        //}
        //*********************************************************************
    }


    RafraichirClick(ev) {
        //this.gantt.scroll = this.gantt.getScrollState();
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
    // UndoClick(ev) {
    //     this.gantt.undo();
    // }
    // RedoClick(ev) {
    //     this.gantt.redo();
    // }
    AnneeClick(ev) {
        this.gantt.ext.zoom.setLevel("year");
    }
    MoisClick(ev) {
        this.gantt.ext.zoom.setLevel("month");
    }
    SemaineClick(ev) {
        this.gantt.ext.zoom.setLevel("week");
    }
    GotoNowClick(ev) {
        this.GotoJClick(ev,'Now');
    }
    GotoJ0Click(ev) {
        this.GotoJClick(ev,'J0');
    }
    GotoJ1Click(ev) {
        this.GotoJClick(ev,'J1');
    }
    GotoJ2Click(ev) {
        this.GotoJClick(ev,'J2');
    }
    GotoJ3Click(ev) {
        this.GotoJClick(ev,'J3');
    }
    GotoJ4Click(ev) {
        this.GotoJClick(ev,'J4');
    }
    GotoJ5Click(ev) {
        this.GotoJClick(ev,'J5');
    }
    GotoJClick(ev,j) {
        if (typeof this.gantt.getMarker(this.gantt.markers[j]) !== 'undefined') {
            var marker = this.gantt.getMarker(this.gantt.markers[j]);
            var marker_date = marker.start_date;
            this.gantt.showDate(marker_date)
        }
    }
    LierClick(ev){
        if (ev.target.checked==true){
            this.state.lier=true;
        } else {
            this.state.lier=false;
        }       
    }

    
    PDFClick(ev){
        var dossier_model = gantt.owl.state.dossier_model;
        var dossier_id    = gantt.owl.state.dossier_id;        
        this.GetGanttPdfId(dossier_model,dossier_id);
    }


    async GetGanttPdfId(dossier_model,dossier_id){
        var self=this;
        rpc.query({
            model: 'is.gantt.pdf',
            method: 'get_gantt_pdf_id',
            args: [[0]],
            kwargs: {
                dossier_model: dossier_model,
                dossier_id   : dossier_id,
            }
        }).then(function (result) {
            var gantt_pdf_id = result;
            self.env.bus.trigger('do-action', {
                action: {
                    type: 'ir.actions.act_window',
                    res_model: 'is.gantt.pdf',
                    res_id: parseInt(gantt_pdf_id),
                    view_mode: 'form,list',
                    views: [[false, 'form'],[false, 'list']],
                    //target: 'new',
                },
            });
        });
    }




    async GetFormId(task){
        var self=this;
        rpc.query({
            model: 'is.doc.moule',
            method: 'get_form_view_id',
            args: [[task.res_id]],
        }).then(function (result) {
            const form_id=result;
            self.env.bus.trigger('do-action', {
                action: {
                    type: 'ir.actions.act_window',
                    res_model: task.model,
                    res_id: parseInt(task.res_id),
                    view_mode: 'form,list',
                    views: [[form_id, 'form'],[false, 'list']],
                    target: 'new',
                },
            });
        });
    }


    async GetDocuments(s){
        var self=this;
        rpc.query({
            model: 'is.doc.moule',
            method: 'get_dhtmlx',
            kwargs: {
                domain  : this.props.domain,
            }
        }).then(function (result) {
            self.state.dossier_id         = result.dossier_id;
            self.state.dossier_model      = result.dossier_model;
            self.state.items              = result.items;
            self.state.links              = result.links;
            self.state.markers            = result.markers;
            self.state.jour_fermeture_ids = result.jour_fermeture_ids;
            self.renderDhtmlxGantt();
            self.gantt.scrollTo(result.scroll_x,result.scroll_y);
        });
    }

    async WriteTask(id,item,mode){
        //this.gantt.scroll = this.gantt.getScrollState();
        self.this = this;
        rpc.query({
            model: 'is.doc.moule',
            method: 'write_task',
            args: [[parseInt(item.res_id)], item.start_date, item.duration,this.state.lier,mode]
        }).then(function (result) {
            self.this.GetDocuments();
        }, function () {
                Dialog.alert(this, "Accès non autorisé");
                self.this.GetDocuments();
        });
    }

    async ArchiveTask(id,item){
        self.this = this;
        rpc.query({
            model: 'is.doc.moule',
            method: 'archive_task',
            args: [[parseInt(item.res_id)]]
        }).then(function (result) {
            self.this.GetDocuments();
        }, function () {
                Dialog.alert(this, "Accès non autorisé");
                self.this.GetDocuments();
        });
    }

    async CopyTask(id,item){
        self.this = this;
        rpc.query({
            model: 'is.doc.moule',
            method: 'copy_task',
            args: [[parseInt(item.res_id)]]
        }).then(function (result) {
            self.this.GetDocuments();
        }, function () {
                Dialog.alert(this, "Accès non autorisé");
                self.this.GetDocuments();
        });
    }


    async OpenCloseTask(id,task_state){
        self.this = this;
        const task = gantt.getTaskBy("id", [id])[0]; // Recherche de la task avec son id
        if(task.model=='is.section.gantt'){
            rpc.query({
                model: 'is.doc.moule',
                method: 'open_close_task',
                args: [[parseInt(false)],task.id,task_state]
            }).then(function (result) {
                return true;
            }, function () {
                    Dialog.alert(this, "Accès non autorisé");
                    self.this.GetDocuments();
            });
        }
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



    async SetScroll(scroll){
        self.this = this;
        rpc.query({
            model: 'is.doc.moule',
            method: 'set_scroll',
            args: [[], scroll.x,scroll.y]
        }).then(function (result) {
            console.log('SetScroll')
        });
    }





}
DhtmlxganttProjectRenderer.template = 'is_dynacase2odoo.DhtmlxganttProjectTemplate';
export default DhtmlxganttProjectRenderer;

