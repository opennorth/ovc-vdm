"use strict";
/**
* DEPENDANCIES:
* jquery.js
*/
$.ajaxSetup({
async: false
});
jQuery.support.cors = true;

function OvcMtlApi() {
    
    this.base_url = "api/"
    this.form =  "#ovcForm";
    this.activityList = {};
    this.procuringEntity = {};
    //pagination
    this.paginationSelector = "ul.pagination.pages";
    this.items = 0;
    this.itemsOnPage = 20;
    this.currOffsetFieldSelector = "input#offset";
    this.countSelector = "#labelitems";
    
    //queries
    this.params_stats = null;
    this.params_list = null;
    
    this.stats = {}
    this.list = {}
    //error handling
    this.redirectOnError = 'error.html';
    
    
    

    /* *
     * @return {{ void }}
     * Initialize the form and bind elements to actions
     */    
    
    this.init = function (){
            //Fetch and populate activities
            this.populateActivities(this.getActivitiesList());
            this.populateEntities(this.getProcuringEntities());
            this.historyState(true);
            this.loadPage();
    }

    
    this.refresh = function(){
            //Fetch and populate activities
            this.populateActivities(this.getActivitiesList());
            this.populateEntities(this.getProcuringEntities());
            this.loadPage();
            return true;
    }
    /**
     * @return {{ boolean }}
     * Load the page from the current url and set the form values
     */    
    this.loadPage = function(){
        var data = {};

            var field;
            var qd = this.paramsExtract();
         
            if (!qd.offset) {
                $(this.currOffsetFieldSelector).val(0);
            }
            //set current values from url
            for(field in qd){
                $("[NAME='"+field+"']").not("[type=radio]").not("#activity").not("#procuring_entity").val(decodeURIComponent(qd[field]).replace(/\?%/g,'').replace(/\?/g,'').replace(/\+/g, ' '));
            }

            
            if (qd.activity) {
                var splitActivity = qd.activity[0].replace(/\+/g, ' ');
                $.each(splitActivity.split(";"), function(i,e){
                    $('#activity option[value="' + e + '"]').prop("selected", true);
                });
            }else{
                $('#activity option').prop("selected",true);
            }
            
            if (qd.procuring_entity) {
                var splitEntities = qd.procuring_entity[0].replace(/\+/g, ' ');
                $.each(splitEntities.split(";"), function(i,e){
                    $('#procuring_entity option[value="' + e + '"]').prop("selected", true);
                });
            }else{
                 $('#procuring_entity option').prop("selected", true);
            }

            
            if (qd.type) {
                $("[name='type']").parent().removeClass('active');
                $("#"+qd.type).prop("checked", true);
                $("#"+qd.type).parent().addClass("active");
            }else{
                $("[name='type']").parent().removeClass('active');
                $("#contract").prop("checked", true);
                $("#contract").parent().addClass("active");
            }
            if (!qd.supplier) {
                $('#supplier').val('');
            }
            
            if (!qd.buyer) {
                $('#supplier').val('');
            }
            
            
            if (qd.date_lt) {
                var date_lt = qd.date_lt.toString().split('-');
                $("#date_lt_view").val(new Date(date_lt[0],(date_lt[1]-1),'01').yyyymm());
            }else{
                $("#date_lt_view").val(new Date(new Date().setYear(new Date().getFullYear())).yyyymm());
                $("#date_lt").val(new Date(new Date().setYear(new Date().getFullYear())).yyyymmlastdd());
            }
            
            if (qd.date_gt) {
                var date_gt = qd.date_gt.toString().split('-');
                $("#date_gt_view").val(new Date(date_gt[0],(date_gt[1]-1),date_gt[2]).yyyymm());
            }else{
                $("#date_gt_view").val('2012-01');
                $("#date_gt").val('2012-01-01');
            }
            
            if (qd.order_by) {
                $(".orderby").removeClass('active');
                $(".orderby[id='ob_"+qd.order_by+"']").addClass('active');
            }
            return true;
    }
    
    
    
    
    /**
     * @param {object} data
     * @return {{ boolean }}
     * Populate the activities selectbox
     * Field [name='activity'] required
     */    
    this.populateActivities = function (data){
        
        if (data) {
            var cb = '';
                
            $.each(data['activities'], function(i,d){
                d.name = (d.name);
                if (d.name) {
                    if ($("[name='activity']").val() == d.name) {
                        cb+='<option value="'+d.name+'" selected="selected">'+d.name+'</option>';
                    }else{
                        cb+='<option value="'+d.name+'">'+d.name+'</option>';
                    }
                }
            });
            
            $("[name='activity']").html(cb);
            return true;
        }else{
            return false;
        }
        
    }
    
    /**
     * @param {object} data
     * @return {{ boolean }}
     * Populate the selectbox
     * Field [name='procuring_entity'] required
     */    
    this.populateEntities = function (data){
        
        if (data) {
            var cb = '';
            
            $.each(data['releases'], function(i,d){

                
                if (d.procuring_entity_slug) {
                    d.procuring_entity = (d.procuring_entity);
                    if ($("[name='procuring_entity']").val() == d.procuring_entity_slug) {
                        cb+='<option value="'+d.procuring_entity_slug+'" selected="selected">'+d.procuring_entity+'</option>';
                    }else{
                        cb+='<option value="'+d.procuring_entity_slug+'">'+d.procuring_entity+'</option>';
                    }
                }
            });
            
            $("[name='procuring_entity']").html(cb);
            return true;
        }else{
            return false;
        }
        
    }


    /**
     * @param {string} templateSelector - A jQuery selector
     * @param {object} data
     * @param {string} outputSelector - A jQuery selector 
     * @return {{ boolean }}
     * Populate the list
     */    
    this.createListFromTemplate = function (templateSelector, data, outputSelector ){

        if (data) {

            var output = $(outputSelector);
            output.empty();
            $.each(data['releases'], function(i,d){
                var template = $(templateSelector).clone();
                template.removeClass("template");
                template.attr('id', 'contract_'+ $("<p>"+d.awards[0].id+"<p>").text());
                template.find('.share').attr('href', "javascript:setSocialMedia('"+$("<p>"+d.awards[0].id+"<p>").text()+"');");
                
                
                template.find('.supplier').html(d.awards[0].suppliers[0].name);
                template.find('.supplier').attr('data', d.awards[0].suppliers[0].identifier.id);
                
                template.find('.supplier').parent().attr('href', "javascript:bysupplier('"+d.awards[0].suppliers[0].identifier.id+"');");
                
                template.find('.buyer').html(d.buyer.name);
                template.find('.buyer').attr('data', d.buyer.identifier.id);
                
                template.find('.buyer').parent().attr('href', "javascript:bybuyer('"+d.buyer.identifier.id+"');");
                
                template.find('.value').html((d.awards[0].value.amount).formatMoney(2, ',', ' ')+' $');
                
                template.find('.description').html(d.awards[0].items[0].description);
                
                
                var vardetails = {
                   date: {
                            label: "Date",
                            data: new Date(d.date).toLongFrenchFormat(),
                   },
                   record: {
                            label: "N<sup>o</sup> de dossier",
                            data: d.awards[0].id,
                   },
                   dispatch: {
                            label: "Répartition",
                            data: d.awards[0].repartition,
                   },
                   decision: {
                            label: "N<sup>o</sup> de décision",
                            data: d.awards[0].items[0].id,
                   },
                }
                
                var k = 1;
                for (var detail in vardetails) {
                    if (vardetails[detail].data) {
                
                        template.find('#details_'+detail).addClass('detail'+k);
                        k++;
                        template.find('#details_'+detail).find('.data').html(vardetails[detail].data);
                        template.find('#details_'+detail).find('.label').html(vardetails[detail].label);
                    }else{
                        template.find('#details_'+detail).hide();
                    }
                }
                
                
                
                output.append(template);

                
            });
            
            return true;
        }else{
            return false;
        }
        
    }

    /**
     * @return {{ object }}
     * Extract params from url
     */    
    this.paramsExtract = function(){
        var qd = {};
        if (this.detectIE() > 9 || !this.detectIE()) {
            var qstring = window.location.search;
        }else{
            var qstring = window.location.hash;
        }
        
        if (qstring) {
         var qsplit = qstring.substr(1).split('&');
            
            for (var params in qsplit) {
                var pair = qsplit[params].split('=');
                qd[pair [0]]= [decodeURIComponent(pair[1]),];
            }
        }
        
        
        
        if (typeof(qd.buyer) != "undefined" ) {
            if (qd.buyer.indexOf(qd.q) !== -1) {
                delete qd.q;
            }
        }
        if (typeof(qd.supplier) != "undefined" ) {
            if (qd.supplier.indexOf(qd.q) !== -1) {
                delete qd.q;
            }
        }
        
        return  qd; 
    }
    
    /**
     * @param {string} endpoint - API endpoint
     * @param {string} params - url encoded
     * @return {{ object }}
     * Make a call to API
     */    
    this.call = function(endpoint, params){
        var response ={};
            var redirect = this.redirectOnError;
            $.getJSON(this.base_url+endpoint+'?'+params, function(jsonData){
                response = jsonData;
            }).error(function(jqXHR, textStatus, errorThrown) {
                console.log("error " + textStatus);
                console.log("incoming Text " + jqXHR.responseText);
                console.log("errorThrown "+ errorThrown);
                console.log("on : "+ endpoint);
                console.log("with : "+ params);
                console.log("redirect to:" +redirect);
                if (redirect) {
                    window.location.href=redirect;
                }
                
                
            });

        return response;        
    }

    /**
     * detect IE
     * returns version of IE or false, if browser is not Internet Explorer
     * http://stackoverflow.com/questions/19999388/jquery-check-if-user-is-using-ie
     */
    
    this.detectIE = function() {
        var ua = window.navigator.userAgent;
    
        var msie = ua.indexOf('MSIE ');
        if (msie > 0) {
            // IE 10 or older => return version number
            return parseInt(ua.substring(msie + 5, ua.indexOf('.', msie)), 10);
        }
    
        var trident = ua.indexOf('Trident/');
        if (trident > 0) {
            // IE 11 => return version number
            var rv = ua.indexOf('rv:');
            return parseInt(ua.substring(rv + 3, ua.indexOf('.', rv)), 10);
        }
    
        var edge = ua.indexOf('Edge/');
        if (edge > 0) {
           // IE 12 => return version number
           return parseInt(ua.substring(edge + 5, ua.indexOf('.', edge)), 10);
        }
    
        // other browser
        return false;
    }

    /**
     * @return {{ boolean }}
     * update url
     */        
    this.historyState = function(init){
        if (!init) {

            if ($("[name=buyer]").val() || $("[name=supplier]").val() ) {
                $('[name=q]').val('');
            }
            if ($("[name=buyer]").val()) {
                $("[name=supplier]").val('')
                $('[name=q]').val('');
            }
            if ($("[name=supplier]").val()) {
                $("[name=buyer]").val('')
                $('[name=q]').val('');
            }

            var query = $(this.form).find(':not(.void)').not('[multiple]').serialize();
            
            var multipleSelect = {}
            $(this.form).find('[multiple] option').each(function(i, selected){
                if (multipleSelect[$(selected).parent().attr('name')]  === undefined) {
                        multipleSelect[$(selected).parent().attr('name')] = '';
                }
                if($(selected).is(':selected')){
                    if ($(selected).val()) {
                        multipleSelect[$(selected).parent().attr('name')] += ($(selected).val()) + ';';
                    }
                }
            });
            
            
            if (multipleSelect) {
                for(var selectelm in multipleSelect){
                    multipleSelect[selectelm] = multipleSelect[selectelm].slice(0, - 1);
                }
            }
            
            var multipleCSV = $.param( multipleSelect );
            query = query.replace(/[^&]+=&/g, '').replace(/&[^&]+=$/g, '');
            if(multipleCSV){
                query += '&' + multipleCSV;
            }
        
            

            if (this.detectIE() > 9 || !this.detectIE()) {
                history.pushState({}, "Ville de Montréal - Vue sur les contrats",
                window.location.protocol +
                '//' +
                window.location.hostname +
                window.location.pathname +
                "?" +
                query);    
            }else{
                window.location.hash = query;
            }
            
        }
        return true;
    }
    
    
    this.countLabel = function (items,type){
       if(type == 'contract'){
        type = 'contrat';
       }
       var s = (items == 1) ? " "+type : " "+type+'s';
       $(this.countSelector).html('<span id="countReleases">'+items+'</span> ' + s );
       } 
    
    /**
     * @return {{ int }}
     * find the current page by the query string (first) or the offset field 
     */          
    this.currentPageByOffset = function(){
        if (location.search) {
            var qd = this.paramsExtract();
            if (qd.offset) {
                return (qd.offset / this.itemsOnPage) + 1;    
            }
            return 1;
        }else{
            return ($(this.currOffsetFieldSelector).val() / this.itemsOnPage) + 1;    
        }
        
    }

    
    /**
     * @return {{ object }}
     * A list of the activities
     */    
    this.getActivitiesList = function(){
        var params = $.param( {'order_by':'value' ,'order_dir':'desc' });
        var activityList = {};
        
        activityList = this.call('helpers/activity_list', params);
        
        if (activityList) {
            
            this.activityList = activityList;
            
        }
        return activityList;
    }
    
    /**
     * @return {{ object }}
     * A list of the procuring entities
     */    
    this.getProcuringEntities = function(){
        var params = $.param( {'order_by':'procuring_entity' ,'order_dir':'asc' });
        return this.call('releases/by_procuring_entity', params);
    }
    
    this.getFormatList = function(){
        return this.call('helpers/format_list', '');
    }
    /**
     * @param {object} endpoint - API endpoint
     * @return {{ object }}
     * Decode values of an object
     */    
    this.decode = function(qd){
        
        for (var d in qd) {
            qd[d] = decodeURIComponent(qd[d]).replace(/\+/g, ' ');
        }
        
        return qd;
    }
    
    /**
     * @return {{ object }}
     * Decode values of an object
     */        
        
    this.byMonthActivity = function(aggregate){
        aggregate = aggregate == undefined ? "value" : aggregate;

        var results = {
            stats : {},
            list : {},
        };
        
        
        
        var qd = this.paramsExtract();
        var params_list = $.param(this.decode(qd));
        
        
        
        //delete all prop who are needed only for the listing, we want to have all data for the graph.
        delete qd.order_by;
        delete qd.order_dir;
        delete qd.offset;
        delete qd.limit;
        
        
        
        var params_stats = $.param(qd);
        
        if(this.params_stats != params_stats){
            var param_aggregate = '&aggregate='+aggregate;
            if(qd.buyer || qd.supplier){
                param_aggregate = '';
            }
            results.stats = this.call('releases/by_month_activity', params_stats.replace(/%5B%5D/gi,'') + param_aggregate);
            if (results.stats && results.stats.meta) {
                this.params_stats = params_stats;
                this.stats = results.stats;
            }else{
                console.log("error on call");
            }
        }else{
            results.stats = this.stats; 
        }
        
        
        
        if(this.params_list != params_list){

            results.list = this.call('releases', params_list.replace(/%5B%5D/gi,'') + '&highlight=True');
            if (results.list && results.list.meta) {
                this.params_list = params_list;
                this.items = results.list.meta.count;
                this.list = results.list;
                this.createListFromTemplate(".template.listing", this.list, '#listdisplay');
                this.countLabel(results.list.meta.count, qd.type);
            }else{
                console.log("error on call");
            }
        }else{
            results.list = this.list; 
        }
        
        return results;

    }
    /**
     * @return {{ object }}
     * A list of links by format
     */     
    this.export = function(){
        var links = {
            csv : {
                label: 'CSV',
                ext: '.csv',
                link_to: '',
                enabled: false,
                limit: 0,
                },
            json : {
                label: 'JSON (OCDS)',
                ext: '.json',
                link_to: '',
                enabled: false,
                limit: 0,
                },
            pdf : {
                label: 'PDF',
                ext: '.pdf',
                link_to: '',
                enabled: false,
                limit: 0,
                },
            xlsx : {
                label: 'Excel',
                ext: '.xlsx',
                link_to: '',
                enabled: false,
                limit: 0,
                },
            };
            
        var qd = this.paramsExtract();
        qd.offset = 0;

        var params_export = $.param(this.decode(qd));
        var limit = this.getFormatList();
        var limitByFormat = limit['formats'];
        
        
                
        if(params_export){
            for (var link in links) {
                var thisLimit = '';
                if (limitByFormat) {
                    for(var format in limitByFormat){;
                        if(limitByFormat[format].format == link){
                            thisLimit = '&limit='+ limitByFormat[format].record_limit + '&offset=0';
                            if(this.items <= limitByFormat[format].record_limit){
                                links[link].enabled = true;
                            }
                            links[link].limit = limitByFormat[format].record_limit;
                        }
                        
                    }
                }
                
                links[link].link_to = this.base_url+'releases'+ links[link].ext + '?'+ params_export.replace(/%5B%5D/gi,'') + '&format=' + link + thisLimit;
            }
            return links;
        }else return links;
    }
    
    
}