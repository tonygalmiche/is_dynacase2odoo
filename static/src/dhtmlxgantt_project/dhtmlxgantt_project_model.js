/** @odoo-module **/
import BasicModel from 'web.BasicModel';
import session from 'web.session';


const DhtmlxganttProjectModel = BasicModel.extend({
    /**
     * @override
     * @param {Array[]} params.domain
     */
    __load: function (params) {
        this.originalDomain = _.extend([], params.domain);
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
        //console.log("DhtmlxganttProjectModel : _fetchData : this.domain=",this.domain,this.modelName); 
    },
});
export default DhtmlxganttProjectModel;
