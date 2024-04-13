/** @odoo-module **/
import { _lt } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
//import { standardFieldProps } from "../standard_field_props";

import { standardFieldProps } from "@web/views/fields/standard_field_props";



import { Component } from "@odoo/owl";
const formatters = registry.category("formatters");


console.log("## TEST 1");


export class SelectBackgroundColor extends Component {
    get formattedValue() {

        console.log("## TEST 2");


        const formatter = formatters.get(this.props.type);
        return formatter(this.props.value, {
            selection: this.props.record.fields[this.props.name].selection,
        });
    }

    get classFromDecoration() {

        console.log("## TEST 3");


        for (const decorationName in this.props.decorations) {
            if (this.props.decorations[decorationName]) {
                return `text-bg-${decorationName}`;
            }
        }
        return "";
    }
}

SelectBackgroundColor.template = "is_dynacase2odoo.SelectBackgroundColor";
SelectBackgroundColor.props = {
   ...standardFieldProps,
};

//BadgeField.displayName = _lt("Badge");
//SelectBackgroundColor.supportedTypes = ["selection", "many2one", "char"];
SelectBackgroundColor.supportedTypes = ["selection"];


registry.category("fields").add("select_background_color", SelectBackgroundColor);









// import fieldRegistry from 'web.field_registry';
// import { FieldChar } from 'web.basic_fields';


// console.log("## TEST 1");

// export const SelectBackgroundColor = FieldChar.extend({
//     /**
//      * @override
//      */
//     init() {

//         console.log("## TEST 2");


//         this._super(...arguments);
//         if (this.viewType === 'kanban') {
//             // remove click event handler
//             this.events = { ...this.events };
//             delete this.events.click;
//         }
//     },

//     // _renderReadonly: function() {
//     _render: function () {

//             console.log("## TEST 3");


//             console.log(this.record)
//             console.log(this.$el)
//             this._super();
//             var color = this.record.data.color;
//             var $div = $('<div/>', {
//                 class: 'o_field_many2manytags o_field_widget' 
//             });
//             var $div2 = $('<div/>', {
//                 class: 'badge badge-pill  o_tag_color_'+color
//             });
//             $div2.append(this.$el);
//             $div.append($div2);
//             this.setElement($div);
//         },
// });



//     // _render: function () {
//     //     let result = this._super.apply(this, arguments);
//     //     if (this.recordData.allow_subtasks && this.recordData.child_text) {
//     //         this.$el.append($('<span>')
//     //                 .addClass("text-muted ms-2")
//     //                 .text(this.recordData.child_text)
//     //                 .css('font-weight', 'normal'));
//     //     }
//     //     return result;
//     // }
// //});

// fieldRegistry.add('select_background_color', SelectBackgroundColor);





// odoo.define('my_module.ColoredField', function(require) {
//     "use strict";

//     var FieldChar = require('web.basic_fields').FieldChar;
//     var fieldRegistry = require('web.field_registry');
//     var ColoredField = FieldChar.extend({
//         _renderReadonly: function() {
//             console.log(this.record)
//             console.log(this.$el)
//             this._super();
//             var color = this.record.data.color;
//             var $div = $('<div/>', {
//                 class: 'o_field_many2manytags o_field_widget' 
//             });
//             var $div2 = $('<div/>', {
//                 class: 'badge badge-pill  o_tag_color_'+color
//             });
//             $div2.append(this.$el);
//             $div.append($div2);
//             this.setElement($div);
//         },
//     });
//     fieldRegistry.add('colored_field', ColoredField);
//     return ColoredField;
// });













// import { standardFieldProps } from "@web/views/fields/standard_field_props";
// import { registry } from "@web/core/registry";
// const {Component} = owl;


// export class IsProgressbar extends Component {
//     setup() {
//         super.setup();
//     }
// }
// IsProgressbar.template = "is_plastigray16.IsProgressbar";
// IsProgressbar.props = standardFieldProps;
// registry.category("fields").add("is_progressbar", IsProgressbar);


