
/*
 *Resize the graph container
 */
function resizegraph(){
    var windowHeight = $( window ).innerHeight();
    $("#stacked").css('min-height',(windowHeight * 0.35) );
}


//From facebook
window.fbAsyncInit = function(){

FB.init({
    appId: facebook_api_key, status: true, cookie: true, xfbml: true }); 
};
(function(d, debug){var js, id = 'facebook-jssdk', ref = d.getElementsByTagName('script')[0];
    if(d.getElementById(id)) {return;}
    js = d.createElement('script'); js.id = id; 
    js.async = true;js.src = "//connect.facebook.net/fr_CA/all" + (debug ? "/debug" : "") + ".js";
    ref.parentNode.insertBefore(js, ref);}(document, /*debug*/ false));
function postToFeed(title, desc, url, image){
    desc = desc +  url;
    var obj = {method: 'feed',link: url, picture: image,name: title,description: desc};
    function callback(response){}
    FB.ui(obj, callback);
}

/*
 * Sharing functions
 * @param {string} url - An url
 * @param {string} desc - A small description
 * @param {int} winWidth - Width of the popup
 * @param {int} winHeight - height of the popup
 */
function twittershare(url, descr, winWidth, winHeight) {
    var winTop = (screen.height / 2) - (winHeight / 2);
    var winLeft = (screen.width / 2) - (winWidth / 2);
    descr = encodeURIComponent(descr);
    url = encodeURIComponent(url);
    window.open('https://twitter.com/share?url=' + url + '&text='+ descr , 'Partage', 'top=' + winTop + ',left=' + winLeft + ',toolbar=0,status=0,width='+winWidth+',height='+winHeight);
}

function linkedinshare(url, title, descr, winWidth, winHeight) {
    var winTop = (screen.height / 2) - (winHeight / 2);
    var winLeft = (screen.width / 2) - (winWidth / 2);
    title = encodeURIComponent(title);
    descr = encodeURIComponent(descr +  url);
    window.open('http://www.linkedin.com/shareArticle?mini=true&url=' + url + '&title='+ title + '&summary='+ descr , 'Partage', 'top=' + winTop + ',left=' + winLeft + ',toolbar=0,status=0,width='+winWidth+',height='+winHeight);
}

/*
 * Sharing functions
 * @param {string} url - An url
 * Set sharing functions to contracts by ID
 */

function setSocialMedia(contractId){
    var base_url = window.location.protocol + '//' + window.location.hostname + location.pathname;
    var url = base_url + '?q=' + contractId + '&type='+$('[name=type]:checked').val();
    var image_url = base_url + 'img/rosette.jpg';
    var info = $("#contract_"+contractId);
    
    var titlet = "Vue sur les contrats. Consultez les contrats et subventions octroyés par la Ville de Montréal.";
    
    var titlefb = "Vue sur les contrats de la ville de Montréal";
    var descriptionfb = "Vue sur les contrats est un outil de visualisation qui permet de consulter les contrats et les subventions octroyés par la Ville de façon simple et conviviale. ";
    
    var titleli = "Vue sur les contrats de la Ville de Montréal";
    var descriptionli = "Vue sur les contrats est un outil de visualisation qui permet de consulter les contrats et les subventions octroyés par la Ville de façon simple et conviviale. ";

    var formattedBody = encodeURIComponent("Vue sur les contrats est un outil de visualisation qui permet de consulter les contrats et les subventions octroyés par la Ville de façon simple et conviviale. \n \n "+ url);

    var box = $("#modalsocialmedia");
    box.find(".sharetwitter").attr("href",'javascript:twittershare("'+url+'", "'+titlet+'", 520, 350);');
    box.find(".sharefacebook").attr("href",'javascript:postToFeed("'+titlefb+'", "'+descriptionfb+'","'+url+'",  "'+image_url+'");');
    box.find(".sharelinkedin").attr("href",'javascript:linkedinshare("'+url+'", "'+titleli+'", "'+descriptionli+'", 520, 350);');
    box.find(".shareemail").attr('href','mailto:?body='+formattedBody+'&subject=Vue sur les contrats de la Ville de Montréal');
    box.find(".sharelink").val(url);
    box.modal('show');
    
}

/*
 * @param {string} result - object from the API
 * @return {{ boolean }}
 * Define if data was received
*/
function results_accepted(results) {
    
    if (results && results.meta) {
        if (results.meta.count) {
            $(".graph-container").css('visibility','visible');        
            $(".mainContent").show();
            $(".filters").show();
            $(".noResults").hide();
            return true;
        }else{
            $('html, body').animate({ scrollTop: 0 }, 300);
            $(".mainContent").hide();
            $(".graph-container").css('visibility','hidden');        
            $(".filters").hide();
            $(".noResults").show();
            return false;
        }
    }else{
        $('html, body').animate({ scrollTop: 0 }, 300);
        $(".mainContent").hide();
        $(".graph-container").css('visibility','hidden');        
        $(".filters").hide();
        $(".noResults").show();
        return false;
    }
    
}


/*
 * @param {string} text
 * @param {int} length
 * @return {{ text }}
 * add an ellipsis if needed
 */
function TextAbstract(text, length) {
    if (text == null) {
        return "";
    }
    if (text.length <= length) {
        return text;
    }
    text = text.substring(0, length);
    return text + "...";
}

/*
 *bootstrap-selectpicker init
 */
$.fn.selectpicker.defaults = {
    mobile : false,
    selectAllText: "Tout sélectionner",
    deselectAllText: "Désélectionner",
    noneSelectedText: "Aucune sélection",
    countSelectedText: function (numSelected, numTotal) {
    if (numTotal  == numSelected) {
        return "Tous";
    }else{
        return (numSelected == 1) ? "{0} sélection" : "{0} sélections";  
    }
      
    },
}
 
/*
 * Clear the form
 */ 
function clearForm()
{
    $(':input').not(':button, :submit, :reset, :checkbox, :radio, [name="limit"]').val('');
    $(':checkbox, :radio').prop('checked', false);
    $("#offset").val('0');
}

function renameLabels(){

    if ($( ".switchgraph span" ).hasClass('value')) {
        $( ".switchgraph span" ).html('Voir nombre de '+defTypeName()+'s par mois');
        $(".graphTitle").html('Montant total des '+defTypeName()+'s par mois');
    }else if($( ".switchgraph span" ).hasClass('count')) {
        $( ".switchgraph span" ).html('Voir montant des '+defTypeName()+'s par mois');
        $(".graphTitle").html('Nombre total de '+defTypeName()+'s par mois');
    }

}


/*
 * Add a buyer ID to the request
 */ 
function bybuyer(buyerid, reset) {
    init = true;
    $('.searchboxLabel').html("Octroyé par");
    $("input#offset").val('0');
    $("input#supplier").val('');
    $("input#buyer").val(buyerid);
    $('.searchboxhidden').tagsinput('removeAll');
    $('.searchboxhidden').tagsinput('add', buyerid);
    $(".bootstrap-tagsinput").find('.tag').addClass('buyer');
}
/*
 * Add a supplier ID to the request
 */ 
function bysupplier(supplierid, reset) {
    init = true;
        $('.searchboxLabel').html("Fournisseur");
        $("input#offset").val('0');
        $("input#buyer").val('');
        $("input#supplier").val(supplierid);
        $('.searchboxhidden').tagsinput('removeAll');
        $('.searchboxhidden').tagsinput('add', supplierid);
        $(".bootstrap-tagsinput").find('.tag').addClass('supplier');
        
}

var previousPoint = null, previousLabel = null;
var monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

/*
 * Tooltip
 */ 
$.fn.UseTooltip = function () {
    if($(window).width() > 768){
    $(this).bind("plothover", function (event, pos, item) {
        if (item) {

            if ((previousLabel != item.series.label) || (previousPoint != item.dataIndex)) {
                previousPoint = item.dataIndex;
                previousLabel = item.series.label;

                $("#tooltip").remove();
                var color = item.series.color;
                showTooltip(item.pageX, item.pageY, item.series.color, getTemplateForToolip(item));
            }

        } else {
            $("#tooltip").remove();
            previousPoint = null;
        }
    });
    }
};


function showTooltip(x, y, color, contents) {
    var tooltip = $('<div id="tooltip">' + contents + '</div>').css({
        'border-color': color
    });

    tooltip.find('#tooltip-arrow').css('border-top-color', color);
    tooltip.appendTo("body").fadeIn(200);

    tooltip.css({
       top: y - (tooltip[0].offsetHeight + 10),
       left: x - (tooltip[0].offsetWidth - 18)
    });
}

function getTemplateForToolip(item){
    
    if(dataSet == 'amount'){
        var amount = formatedData.value[item.seriesIndex].data[item.dataIndex][1];
        var count = formatedData.value_count[item.seriesIndex].data[item.dataIndex][1];
    }else{
        var count = formatedData.count[item.seriesIndex].data[item.dataIndex][1];
        var amount = formatedData.count_value[item.seriesIndex].data[item.dataIndex][1];   
    }
    
    var x = item.datapoint[0];
    labelContrat = (count == 1) ? " "+defTypeName() : " "+defTypeName()+'s';
    
    var text = "";
    text += "<div style='position: relative;'>";
    text += "   <div style='' class='domaineName'><strong>{month}</strong></div>";
    text += "   <h5 style='margin: 0;'>{label}</h5 style='margin: 0;'>";
    text += "   <div><strong>{money} - {count} "+labelContrat+"</strong></div>";
    text += "   <div id='tooltip-arrow'></div>";
    text += "</div>";
     
    
    var amountFormatted = amount.formatMoney('0', ',', ' ')+ ' $';
    return text
        .replace('{month}', new Date(x).toLongFrenchFormatMonth())
        .replace('{label}', item.series.label)
        .replace('{money}', amountFormatted)
        .replace('{count}', count);
}


/*
 * from http://stackoverflow.com/a/14994860
 * Transform Y labels - money
 */ 
function valueFormatter(num) {
     if (num >= 1000000000) {
        return (num / 1000000000).toFixed(1).replace(/\.0$/, '') + ' G $';
     }
     if (num >= 1000000) {
        return (num / 1000000).toFixed(1).replace(/\.0$/, '') + ' M $';
     }
     if (num >= 1000) {
        return (num / 1000).toFixed(1).replace(/\.0$/, '') + ' K $';
     }
     return num + ' $';
}

/*
 * from http://stackoverflow.com/a/14994860
 * Transform Y labels
 */ 
function countFormatter(num) {
     if (num >= 1000000000) {
        return (num / 1000000000).toFixed(1).replace(/\.0$/, '') + ' G';
     }
     if (num >= 1000000) {
        return (num / 1000000).toFixed(1).replace(/\.0$/, '') + ' M';
     }
     if (num >= 1000) {
        return (num / 1000).toFixed(1).replace(/\.0$/, '') + ' K';
     }
     
     if (num === +num && num !== (num|0)) {
        return num.toFixed(1);
     }
     
     
     return num;
}

/*
 * Init plot
 */ 
function plotWithOptions(formatedData,options) {
    if (formatedData.length > 0) {
        window.plot = $.plot("#stacked", formatedData, options);
        $("#stacked").UseTooltip();
    }
}

/*
 * Refresh the plot with a new width
 */ 
function resizedw(){
    resizegraph();
    plotWithOptions(wg(formatedData), options);
}

/*
 * define which graph is currently displayed
 */ 
function wgcheck() {

    if ($(".switchgraph span").hasClass('value')) {
        return 'value';
    }else{
        return 'count';
    }
}


/*
 * define which graph is currently displayed
 * return the good dataset
 */ 
function wg(data) {
    if (data) {
        if ($(".switchgraph span").hasClass('value')) {
            return data.value;
        }else{
            return data.count;
        }
    }return {};
}

/*
 * Plot configuration
*/
var options = {
        series: {
          grow: {
            active: true,
            duration: 400,
            reanimate: false,
            valueIndex: 1
          },
          stack: true,
          lines: {
            show: false,
            fill: true,
            steps: false
          },
          bars: {
            align: "left",
            lineWidth: 0,
            fill: 0.7,
            show: true,
            barWidth: 800 * 60 * 60 * 24 * 30
          }
        },
         yaxis:{
                min: 0,
                tickFormatter: valueFormatter
        },
        xaxis: {
            mode: "time",
            timeformat: "%Y",
            timezone: "browser",
            minTickSize: [1, "year"]
        },
        grid: {
            hoverable: true,
            mouseActiveRadius:1,
        },
        legend: {
            container: "#legend",
            labelFormatter: function (label, series) {
                $('<div class="labelG col-lg-4 col-md-6 col-sm-12"><i class="fa fa-circle-o colorG" style="color:'+series.color+'"></i><span class="innerTextG">'+label+'</span></div>').appendTo("#legend");
                return false;
                }
            //sorted: "ascending",
        }
};


/* 
 * Launch a query with the selected page
 * linked with simplepagination
*/
function page(num) {
    $('html, body').animate({ scrollTop: $(".filters").offset().top  - 150 }, 600);
    var limit = $("#limit").val();
    var offset = (num - 1)*limit;
    $("#offset").val(offset);
    $("#offset").trigger('change');

}

/* 
 * Launch a query with the selected page
 * Linked with simplepagination
*/
function calculHeight() {

    if ($(window).width() > 1200) {
        return {
        padding:150,
        height:150
    }
    }else if($(window).width() <= 1200 && $(window).width() > 992){
        return {
            padding:240,
            height:240
        }
    }else if($(window).width() <= 992) {
        return {
            padding:60,
            height:60
        }
    }else {
        return {
            padding:60,
            height:60
        }
    }
    
}

/* 
 * Return the french translation of the current type
*/
function defTypeName(){
    if ($("input[type='radio'][name=type]:checked").val() == 'contract') {
        return 'contrat';
    }else{
        return 'subvention';
    }
}


/*
 *Global variables
*/
var dataSet = 'amount';
var formatedData;
var ovc;
var init = true;
var navmod;
resizegraph();

$(function() {
    
$(".noResults").hide();


    $(".searchbar").sticky({
      responsiveWidth: true,
      topSpacing: 0,
      })
    
    /*
    //Uncomment if you want to have the "filters bar" sticky
    $(".filters").sticky({
      responsiveWidth: true,
      topSpacing: 0,
    })
    .on('sticky-start', function() {
        $(".toolbars.filters").css('padding-top', calculHeight().padding);
        $(".toolbars.filters").parent().css('height',calculHeight().height);
        })
    .on('sticky-end', function() {
        $(".toolbars.filters").css('padding-top', '60px');
        $(".toolbars.filters").parent().css('height','auto');
        });
    $(".toolbars.filters").css('padding-top', '60px');
    $(".toolbars.filters").parent().css('height','auto');
    */


    // Init API client
    ovc = new OvcMtlApi();
    if (ovc_api_url) {
    ovc.base_url = ovc_api_url;
    }
    ovc.init();
    
    
    // Init pagination
    var pages = $(ovc.paginationSelector).pagination({
            displayedPages : 3,
            edges: 1,
            prevText: '<',
            nextText: '>',
            hrefTextPrefix : "javascript:page('",
            hrefTextSuffix : "')",
        });
        
    
    // the default request 
    if(ovc.historyState()){
        var apiData = ovc.byMonthActivity();
        if (results_accepted(apiData.stats)) {

            formatedData = ovc.flotChartsFormat(apiData.stats);
            
            var links = ovc.export();
                     for (var l in links) {
                        if(links[l].enabled){
                           $(".export."+l).attr('href',links[l].link_to);
                           $(".export."+l).css('cursor','pointer');
                           $(".export."+l).attr('title','Exportation limitée à '+links[l].limit +' fiches');
                        }else{
                           $(".export."+l).css('cursor','not-allowed');
                           $(".export."+l).attr('title','Exportation limitée à '+links[l].limit +' fiches');
                        }
                    }
            
            
            
            pages.pagination('updateItemsOnPage', ovc.itemsOnPage);
            pages.pagination('updateItems', ovc.items);
            pages.pagination('selectPage', ovc.currentPageByOffset());
            renameLabels();
        }
    }


    //Needed - Growraf is not enough fast to calculate on each screen resize, Y axis bug
    var doit;
    $( window ).resize(function() {
        if (window.plot) {
            window.plot.shutdown();
            clearTimeout(doit);
            doit = setTimeout(resizedw, 1000);
        }    
    });

    $('#procuring_entity').selectpicker('render');
    $('#activity').selectpicker('render');
    if( /Android|webOS|iPhone|iPad|iPod|BlackBerry/i.test(navigator.userAgent) ) {
                    $('#procuring_entity').selectpicker('mobile');
                    $('#activity').selectpicker('mobile');    
    }        
    
    
    /*
    * On each request
    */
    if (ovc.detectIE() > 9 || !ovc.detectIE()) {
        $(window).bind('popstate', function(event){
            init = false
            navmod = 'popstate';
            if(ovc.refresh()){
            var apiData = ovc.byMonthActivity();
                if (results_accepted(apiData.stats)) {
                    
                    formatedData = ovc.flotChartsFormat(apiData.stats);
                    
                    var links = ovc.export();
                    for (var l in links) {
                        if(links[l].enabled){
                           $(".export."+l).attr('href',links[l].link_to);
                           $(".export."+l).css('cursor','pointer');
                           $(".export."+l).attr('title','Exportation limitée à '+links[l].limit +' fiches');
                        }else{
                           $(".export."+l).css('cursor','not-allowed');
                           $(".export."+l).attr('title','Exportation limitée à '+links[l].limit +' fiches');
                        }
                    }
            
                    
                    pages.pagination('updateItemsOnPage', ovc.itemsOnPage);
                    pages.pagination('updateItems', ovc.items);
                    pages.pagination('selectPage', ovc.currentPageByOffset());
                    plotWithOptions(wg(formatedData), options);
                }    
                    var qd = ovc.paramsExtract();
                 
                    $('.searchboxhidden').tagsinput('removeAll');
                    if (qd.supplier) {
                        $('.searchboxLabel').html("Fournisseur");
                        $(".bootstrap-tagsinput").find('.searchbox').hide();
                        $(".bootstrap-tagsinput").find('.searchbutton').hide();
                        $('.searchboxhidden').tagsinput('removeAll');
                        $('.searchboxhidden').tagsinput('add', ovc.decode(qd).supplier);
                        $(".bootstrap-tagsinput").find('.tag').addClass('supplier');
                        
                    }else if(qd.buyer) {
                        $('.searchboxLabel').html("Octroyé par");
                        $(".bootstrap-tagsinput").find('.searchbox').hide();
                        $(".bootstrap-tagsinput").find('.searchbutton').hide();
                        $('.searchboxhidden').tagsinput('add', ovc.decode(qd).buyer);
                        $(".bootstrap-tagsinput").find('.tag').addClass('buyer');
                    }else if(qd.q){
                        $('.searchboxLabel').html("Mots clés");
                        $(".bootstrap-tagsinput").find('.searchbox').hide();
                        $(".bootstrap-tagsinput").find('.searchbutton').hide();
                        $('.searchboxhidden').tagsinput('add',ovc.decode(qd).q);
                    }else{
                        $('.searchboxLabel').html("Mots clés");
                        $("#theMainTag").css('display','none');
                        $(".bootstrap-tagsinput").find('.searchbox').show();
                        $(".bootstrap-tagsinput").find('.searchbutton').show();
                    }
                    $('#procuring_entity').selectpicker('refresh');
                    $('#activity').selectpicker('refresh');
                    renameLabels();
                
            
            }
        });
    }else{
        $(window).bind('hashchange', function() {
            init = false
            navmod = 'hashchange';
            if(ovc.refresh()){
            var apiData = ovc.byMonthActivity();
                if (results_accepted(apiData.stats)) {
                    
                    formatedData = ovc.flotChartsFormat(apiData.stats);
                    
                    var links = ovc.export();
                    for (var l in links) {
                        if(links[l].enabled){
                           $(".export."+l).attr('href',links[l].link_to);
                           $(".export."+l).css('cursor','pointer');
                           $(".export."+l).attr('title','Exportation limitée à '+links[l].limit +' fiches');
                        }else{
                           $(".export."+l).css('cursor','not-allowed');
                           $(".export."+l).attr('title','Exportation limitée à '+links[l].limit +' fiches');
                        }
                    }
            

                    
                    pages.pagination('updateItemsOnPage', ovc.itemsOnPage);
                    pages.pagination('updateItems', ovc.items);
                    pages.pagination('selectPage', ovc.currentPageByOffset());
                    plotWithOptions(wg(formatedData), options);
                }    
                    var qd = ovc.paramsExtract();

                    $('.searchboxhidden').tagsinput('removeAll');
                    if (qd.supplier) {
                        $('.searchboxLabel').html("Fournisseur");
                        $(".bootstrap-tagsinput").find('.searchbox').hide();
                        $(".bootstrap-tagsinput").find('.searchbutton').hide();
                        $('.searchboxhidden').tagsinput('removeAll');
                        $('.searchboxhidden').tagsinput('add', ovc.decode(qd).supplier);
                        $(".bootstrap-tagsinput").find('.tag').addClass('supplier');
                    }else if(qd.buyer) {
                        $('.searchboxLabel').html("Octroyé par");
                        $(".bootstrap-tagsinput").find('.searchbox').hide();
                        $(".bootstrap-tagsinput").find('.searchbutton').hide();
                        
                        $('.searchboxhidden').tagsinput('add', ovc.decode(qd).buyer);
                        $(".bootstrap-tagsinput").find('.tag').addClass('buyer');
                    }else if(qd.q){
                        $('.searchboxLabel').html("Mots clés");
                        $(".bootstrap-tagsinput").find('.searchbox').hide();
                        $(".bootstrap-tagsinput").find('.searchbutton').hide();
                        $('.searchboxhidden').tagsinput('add',ovc.decode(qd).q);
                    }else{
                        $('.searchboxLabel').html("Mots clés");
                        $("#theMainTag").css('display','none');
                        $(".bootstrap-tagsinput").find('.searchbox').show();
                        $(".bootstrap-tagsinput").find('.searchbutton').show();
                    }
                    $('#procuring_entity').selectpicker('refresh');
                    $('#activity').selectpicker('refresh');
                    renameLabels();
                
            
            }
        });
    }   



    $("input, select, textarea").not('[name=q]').not("[type=hidden]").not('.loading').change(function(event){
        //offset to zero, it is a new search
        if (!$(event.currentTarget).hasClass('loading')) {
        
            $(ovc.currOffsetFieldSelector).val(0);
            //remove buyer and supplier input values

            if(ovc.historyState()){
                var apiData = ovc.byMonthActivity();
                if (results_accepted(apiData.stats)) {
                    formatedData = ovc.flotChartsFormat(apiData.stats);
                    var links = ovc.export();
                    for (var l in links) {
                        if(links[l].enabled){
                           $(".export."+l).attr('href',links[l].link_to);
                           $(".export."+l).css('cursor','pointer');
                           $(".export."+l).attr('title','Exportation limitée à '+links[l].limit +' fiches');
                        }else{
                           $(".export."+l).css('cursor','not-allowed');
                           $(".export."+l).attr('title','Exportation limitée à '+links[l].limit +' fiches');
                        }
                    }
                }
            }
            
            pages.pagination('updateItems', ovc.items);
            pages.pagination('selectPage', ovc.currentPageByOffset());
            plotWithOptions(wg(formatedData), options);
            $('html, body').animate({ scrollTop: 0 }, 300);
                
        }
        
    }).keyup(function(event){
            if(event.keyCode == 13){
                
                $("[name=q]").trigger("change");
            }
    });

    
    $("input[type='hidden']").not(".buyer").not(".supplier").change(function(event){
        
        
        if(event.currentTarget.name == 'date_lt' || event.currentTarget.name == 'date_gt' || event.currentTarget.name == 'order_by'){
            $(ovc.currOffsetFieldSelector).val(0);
            pages.pagination('selectPage', '1');            
        }
        console.log('keyword');
        $("[name=q]").val($("[name=q]").val().replace(/\?/g,'').replace(/&/g,'').replace(/%/g,''));
        
        
        
        if(ovc.historyState()){
             var apiData = ovc.byMonthActivity();
             if (results_accepted(apiData.stats)) {
                formatedData = ovc.flotChartsFormat(apiData.stats);
                    var links = ovc.export();
                    for (var l in links) {
                        if(links[l].enabled){
                           $(".export."+l).attr('href',links[l].link_to);
                           $(".export."+l).css('cursor','pointer');
                           $(".export."+l).attr('title','Exportation limitée à '+links[l].limit +' fiches');
                        }else{
                           $(".export."+l).css('cursor','not-allowed');
                           $(".export."+l).attr('title','Exportation limitée à '+links[l].limit +' fiches');
                        }
                    }
            

             }
        }
        
        pages.pagination('updateItems', ovc.items);
        plotWithOptions(wg(formatedData), options);
        
    });
    

    plotWithOptions(wg(formatedData), options);

    $("#date_gt_view").datepicker( {
        format: "yyyy-mm",
        viewMode: "months",
        minViewMode: "months",
        minDate: '2012/01/01',
    }).on('changeDate', function(ev){
        var unix_timestamp = ev.date.valueOf();
        formatedDate = new Date(unix_timestamp ).yyyymmdd();
        $("#date_gt").val(formatedDate);
        $("#date_gt").trigger('change');
        $(this).datepicker('hide');
    });


    $("#date_lt_view").datepicker( {
        format: "yyyy-mm",
        viewMode: "months",
        minViewMode: "months",
        minDate: '2012/01/01',
    }).on('changeDate', function(ev){
        var unix_timestamp = ev.date.valueOf();
        formatedDate = new Date(unix_timestamp ).yyyymmlastdd();
        $("#date_lt").val(formatedDate);
        $("#date_lt").trigger('change');
        $(this).datepicker('hide');

    });

    $("#ob_value").on('click', function(){
            $("#order_by").val('value');
            $("#order_dir").val('desc');

            $("#order_by").trigger('change');

            $(".orderby").removeClass("active");
            $(this).addClass("active");
    });

    $("#ob_date").on('click', function(){
            $("#order_by").val('date');
            $("#order_dir").val('desc');

            $("#order_by").trigger('change');

            $(".orderby").removeClass("active");
            $(this).addClass("active");
    });

    $("#od_supplier").on('click', function(){
            $("#order_by").val('supplier');
            $("#order_dir").val('asc');

            $("#order_by").trigger('change');

            $(".orderby").removeClass("active");
            $(this).addClass("active");
    });



    $( ".upbtn-container" ).click(function() {
        $(".graph-container").toggle(function(e){
                if ($(this).is(":visible") ) {
                    $(".filters").css("padding-top","0px");
                    $("#toggleGraph").find('i').removeClass('fa-angle-double-down');
                    $("#toggleGraph").find('i').addClass('fa-angle-double-up');
                    $('html, body').animate({ scrollTop: 0 }, 300);
                }else{
                    $(".filters").css("padding-top","70px");
                    $("#toggleGraph").find('i').removeClass('fa-angle-double-up');
                    $("#toggleGraph").find('i').addClass('fa-angle-double-down');
                }
                $(".filters").sticky('update');
        });
    });


$(".btnmenu").on('click', function(){

    if (!$(".searchbar").is(':visible')) {
            $(".searchbar").show();
            $(".btnmenu i").removeClass('fa-bars');
            $(".btnmenu i").addClass('fa-close');
             
        }else {
            $(".searchbar").hide();
            $(".btnmenu i").removeClass('fa-close');
            $(".btnmenu i").addClass('fa-bars');
   }     
        
      return false;
}); 

    $('.money').mask('00000000000000', {reverse: true});
    
    $( ".switchgraph span" ).click(function() {
        var optionsx = options;
        if ($(this).hasClass('count')) {
        var apiData = ovc.byMonthActivity('count');
            $(this).removeClass('count');
            $(this).addClass('value');
            $(this).html('Voir nombre de '+defTypeName()+'s par mois');
            $(".graphTitle").html('Montant total des '+defTypeName()+'s par mois');
            dataSet = 'amount';
            optionsx.yaxis.tickFormatter = valueFormatter;
        }else if($(this).hasClass('value')) {
        var apiData = ovc.byMonthActivity('value');
            $(this).removeClass('value');
            $(this).addClass('count');
            $(this).html('Voir montant des '+defTypeName()+'s par mois');
            $(".graphTitle").html('Nombre total de '+defTypeName()+'s par mois');
            dataSet = 'count';
            optionsx.yaxis.tickFormatter = countFormatter;
        }
        
        formatedData = ovc.flotChartsFormat(apiData.stats);
        plotWithOptions(wg(formatedData), options);

    });
    $('.searchboxhidden').tagsinput({
        maxTags: 1,
        trimValue: true,
        addOnBlur: false,
      });
    
    if ($(".searchboxhidden").val()) {
    $(".bootstrap-tagsinput").find('.searchbox').hide();
    $(".bootstrap-tagsinput").find('.searchbutton').hide();
    //$('.searchboxhidden').tagsinput('refresh');
    }
    
    $('.searchboxhidden').on('beforeItemAdd', function(event) {
        $(".bootstrap-tagsinput").find('.searchbox').hide();
        $(".bootstrap-tagsinput").find('.searchbutton').hide();
        $("input#offset").val('0');
        pages.pagination('selectPage', '1');
     })
    
    $('.searchboxhidden').on('itemAdded', function(event) {
        
          
        if (init || (ovc.decode(ovc.paramsExtract()).q != event.item && navmod == 'hashchange') || /Android|webOS|iPhone|iPad|iPod|BlackBerry/i.test(navigator.userAgent) ) {
            $("#supplier").trigger('change');
        }
        init = true;
     })
    
     
    $('.searchboxhidden').on('itemRemoved', function(event) {
        $('.searchboxLabel').html("Mots clés");
        $(".bootstrap-tagsinput").find('.searchbox').show();
        $(".bootstrap-tagsinput").find('.searchbutton').show();
        $("#buyer").val('');
        $("#supplier").val('');
        if (init) {
        $("#supplier").trigger('change');
        }
        init = true;
      });
    
    if ($('#supplier').val()) {
        bysupplier($('#supplier').val());    
    }
    if ($('#buyer').val()) {
        bybuyer($('#buyer').val());
    }
    
    $(".scrolltop").on('click', function(){
        $('html, body').animate({ scrollTop: 0 }, 300);
    });
    
    $(".scrolldown").on('click', function(){
        $('html, body').animate({ scrollTop: $(".filters").offset().top  - 140 }, 600);
    });
    
    $(".searchbutton i.fa").on('click', function(){
       $('.searchbox').trigger($.Event( "keypress", { which: 13 } ));
    });
    
    $("[name=type]").on('change', function(){renameLabels()});
    
     $(".export").hover(
        function() // on mouseover
        {
            $(".exportInfo").html($(this).attr('title'));
        }, 

        function() // on mouseout
        {
            $(".exportInfo").html('');

        });
    
});

$(window).load(function() {
    $(".loading").fadeOut(500);
})