/** @odoo-module **/
import BasicModel from 'web.BasicModel';
import session from 'web.session';

console.log('DhtmlxganttProjectModel');


const DhtmlxganttProjectModel = BasicModel.extend({

    /**
     * @override
     * @param {Array[]} params.domain
     */
    __load: function (params) {
        console.log("DhtmlxganttProjectModel : __load : params=",params); 
        this.originalDomain = _.extend([], params.domain);
        //params.domain.push(['id', '=', false]);
        this.domain = params.domain;
        this.modelName = params.modelName;
        params.groupedBy = [];
        var def = this._super.apply(this, arguments);
        return Promise.all([def, this._fetchData()]).then(function (result) {
            return result[0];
        });
    },
    /**
     * @override
     * @param {Array[]} [params.domain]
     */
    __reload: function (handle, params) {
        console.log("DhtmlxganttProjectModel : __reload : params=",params); 
        if (params && 'domain' in params) {
            this.originalDomain = _.extend([], params.domain);
            //params.domain.push(['id', '=', false]);
            this.domain = params.domain;
        }
        if (params && 'groupBy' in params) {
            params.groupBy = [];
        }
        var def = this._super.apply(this, arguments);
        return Promise.all([def, this._fetchData()]).then(function (result) {
            return result[0];
        });
    },


    /**
     * Fetch activity data.
     *
     * @private
     * @returns {Promise}
     */
    _fetchData: function () {
        console.log("DhtmlxganttProjectModel : this.domain=",this.domain); 
    },
});

export default DhtmlxganttProjectModel;
