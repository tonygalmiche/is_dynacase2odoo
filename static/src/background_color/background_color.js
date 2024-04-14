/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { IntegerField } from "@web/views/fields/integer/integer_field";
import { CharField } from "@web/views/fields/char/char_field";
import { SelectionField } from "@web/views/fields/selection/selection_field";
//import { formatInteger } from "@web/views/fields/formatters";
//import { formatSelection } from "@web/views/fields/formatters";
//import { formatChar } from "@web/views/fields/formatters";
import {onMounted, onPatched} from "@odoo/owl";
import core from 'web.core';


patch(SelectionField.prototype, 'SelectionFieldWidget', {
	setup() {
        this._super(...arguments);
		onMounted(this.changeColor);
        onPatched(this.changeColor);
	},
	changeColor() {
		if (this.props.type) {
	        var activeFields = this.props.record.activeFields;
	        var field = activeFields[this.props.name];
			var options = field.options;
			if (field.rawAttrs){
				if (field.rawAttrs.is_widget=='background_color'){
					var bdom = this.__owl__.bdom;
					if(bdom){
						if (bdom.parentEl){
							if (options && Array.isArray(options)) {
								$(bdom.parentEl).css('background-color', 'transparent');
								options.forEach((option, index) => {
									if (option['color'] && option['value']) {
										if (option['value']==this.props.value) {
											$(bdom.parentEl).css('background-color', option['color']);
										} 
									}
								});
							} else {
								$(bdom.parentEl).css('background-color', 'transparent');
								if (this.props.value=='I'){
									$(bdom.parentEl).css('background-color', 'yellow');
								}
								if (this.props.value=='R'){
									$(bdom.parentEl).css('background-color', 'orange');
								}
								if (this.props.value=='V'){
									$(bdom.parentEl).css('background-color', 'red');
								}
							}
						}
					}
				}
				if (field.rawAttrs.is_widget=='is_revue_risque'){
					var bdom = this.__owl__.bdom;
					if(bdom){
						if (bdom.parentEl){
							$(bdom.parentEl).css('background-color', 'transparent');
							if (this.props.value==='0')  $(bdom.parentEl).css('background-color', 'GreenYellow');
							if (this.props.value==='1')  $(bdom.parentEl).css('background-color', 'orange');
							if (this.props.value==='2')  $(bdom.parentEl).css('background-color', 'red');
							if (this.props.value==='na') $(bdom.parentEl).css('background-color', 'Gainsboro');
						}
					}
				}


			}
		}
	},
});


// patch(CharField.prototype, 'CharFieldWidget', {
// 	get formattedValue() {
// 		const bdom = this.__owl__.bdom;
// 		if(bdom){
// 			if (bdom.parentEl){
// 				$(bdom.parentEl).css('background-color', 'orange');

// 			}
// 		}
// 		return formatChar(this.props.value, { isPassword: this.props.isPassword });
// 	}
// });
			
					
// patch(IntegerField.prototype, 'IntegerFieldIntegerWidget', {
// 	get formattedValue() {
//         if (this.props.type) {
// 	        var activeFields = this.props.record.activeFields
// 			if (parseInt(this.props.value)>=100){
// 		    	$(this.__owl__.refs.numpadDecimal).css('background-color', 'green');
// 			}
// 			if (parseInt(this.props.value)<100){
// 		    	$(this.__owl__.refs.numpadDecimal).css('background-color', 'orange');
// 			}
// 			if (parseInt(this.props.value)==10){
// 		    	$(this.__owl__.refs.numpadDecimal).css('background-color', 'blue');
// 			}
//         }
//         if (!this.props.readonly && this.props.inputType === "number") {
//             return this.props.value;
//         }
//         return formatInteger(this.props.value);
//     }
// });
