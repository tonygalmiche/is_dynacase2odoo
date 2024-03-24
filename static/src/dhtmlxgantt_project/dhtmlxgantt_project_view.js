/** @odoo-module **/;
import DhtmlxganttProjectController from '@is_dynacase2odoo/dhtmlxgantt_project/dhtmlxgantt_project_controller';
import DhtmlxganttProjectModel from '@is_dynacase2odoo/dhtmlxgantt_project/dhtmlxgantt_project_model';
import DhtmlxganttProjectRenderer from '@is_dynacase2odoo/dhtmlxgantt_project/dhtmlxgantt_project_renderer';
import BasicView from 'web.BasicView';
import core from 'web.core';
import RendererWrapper from 'web.RendererWrapper';
import view_registry from 'web.view_registry';

const _lt = core._lt;

const DhtmlxganttProjectView = BasicView.extend({
    accesskey: "a",
    display_name: _lt('Gantt des projets'),
    // icon: 'fa fa-clock-o',
    icon: 'fa fa-indent',


    config: _.extend({}, BasicView.prototype.config, {
        Controller: DhtmlxganttProjectController,
        Model: DhtmlxganttProjectModel,
        Renderer: DhtmlxganttProjectRenderer,
    }),
    viewType: 'dhtmlxgantt_project',
    searchMenuTypes: ['filter', 'favorite'],

    /**
     * @override
     */
    init: function (viewInfo, params) {
        this._super.apply(this, arguments);

        const { search_view_id } = params.action || {};
        this.controllerParams.searchViewId = search_view_id ? search_view_id[0] : false;
        this.loadParams.type = 'list';
        // limit makes no sense in this view as we display all records having activities
        this.loadParams.limit = false;

        this.rendererParams.templates = _.findWhere(this.arch.children, { 'tag': 'templates' });
        this.controllerParams.title = this.arch.attrs.string;
    },
    /**
     *
     * @override
     */
    getRenderer(parent, state) {
        state = Object.assign({}, state, this.rendererParams);
        return new RendererWrapper(null, this.config.Renderer, state);
    },
});

view_registry.add('dhtmlxgantt_project', DhtmlxganttProjectView);

export default DhtmlxganttProjectView;














// import BasicView from 'web.BasicView';
// import core from 'web.core';
// import RendererWrapper from 'web.RendererWrapper';
// import view_registry from 'web.view_registry';

// const _lt = core._lt;


// console.log('DhtmlxganttProjectView');



// const DhtmlxganttProjectView = BasicView.extend({
//     accesskey: "a",
//     display_name: _lt('Gantt des projets'),
//     icon: 'fa-list',
//     config: _.extend({}, BasicView.prototype.config, {
//         Controller: DhtmlxganttProjectController,
//         Model: DhtmlxganttProjectModel,
//         Renderer: DhtmlxganttProjectRenderer,
//     }),
//     viewType: 'dhtmlxgantt_project',
//     searchMenuTypes: ['filter', 'favorite'],

//     /**
//      * @override
//      */
//     init: function (viewInfo, params) {
//         this._super.apply(this, arguments);
//         const { search_view_id } = params.action || {};
//         this.controllerParams.searchViewId = search_view_id ? search_view_id[0] : false;
//         this.loadParams.type = 'list';
//         this.loadParams.limit = 2; //false;
//         this.rendererParams.templates = _.findWhere(this.arch.children, { 'tag': 'templates' });
//         this.controllerParams.title = this.arch.attrs.string;
//     },
//     /**
//      *
//      * @override
//      */
//     getRenderer(parent, state) {
//         console.log("DhtmlxganttProjectView : getRenderer",state,this);
//         state = Object.assign({}, state, this.rendererParams);
//         return new RendererWrapper(null, this.config.Renderer, state);
//     },
// });

// view_registry.add('dhtmlxgantt_project', DhtmlxganttProjectView);
// export default DhtmlxganttProjectView;
