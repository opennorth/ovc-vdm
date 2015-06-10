
OvcMtlApi.prototype.flotChartsFormat = function(data, query_contract_no){
    
    var formated_value = [];
    var formated_count = [];
    
    var activityAvailable = {
        value:[],
        count:[],
    };
    
    var activities = this.activityList['activities'];
    var colors = {};
    
    for (var fromlist in activities) {
        var actfrom = activities[fromlist]['name'];
        activityAvailable.count[actfrom] = 0;
        activityAvailable.value[actfrom] = 0;
    }

    //series need to be the same size
    for (var moment in data['releases']) {

        for(var activity in data['releases'][moment]['activities']){
            
                for (var fromlist in activities) {
                    var actfrom = activities[fromlist]['name'];
                    var exists = false;
                        for (var check in data['releases'][moment]['activities']) {
                            if (data['releases'][moment]['activities'][check]['activity'] == actfrom) {
                                exists = true;
                                
                                if (data['releases'][moment]['activities'][check]['count'] > 0) {

                                    activityAvailable.count[actfrom] = activityAvailable.count[actfrom] + data['releases'][moment]['activities'][check]['count'];
                                    activityAvailable.value[actfrom] = activityAvailable.value[actfrom] + data['releases'][moment]['activities'][check]['total_value'];
                                }
                            }    
                        }
                        
                        if (!exists) {
                            data['releases'][moment]['activities'].push({
                                total_value : 0,
                                activity : actfrom,
                                count: 0
                            });
                        }
                }
        }
    }
    

    
    
    for(var activity in  activities){
        
        colors[activities[activity].name] = activities[activity].color_code;

        formated_value[activities[activity].name] = [];
        formated_count[activities[activity].name] = [];

        
        for(var d in data['releases']){
            for(var release in data['releases'][d]){
                for (var activity_by_month in data['releases'][d][release]) {
                    if (data['releases'][d][release][activity_by_month].activity == activities[activity].name ) {
                        
                        var now = data['releases'][d].month+'-01';
                        var value;
                        var count;

                        value = data['releases'][d][release][activity_by_month].total_value;
                        count = data['releases'][d][release][activity_by_month].count;
                        now = now.split('-');

                        formated_value[activities[activity].name].push([new Date(now[0],(now[1]-1),'01').getTime(), value]);
                        formated_count[activities[activity].name].push([new Date(now[0],(now[1]-1),'01').getTime(), count]);
                    }
                }
            }
        }
    }
    
    var postformated = {
        value:[],
        value_count:[],
        count:[],
        count_value:[],
    };
    

    /*
    amount and the count in each dataset with the same order
    */
    
    // AMOUNT
    var tmp = [];
    i = 0;
    for(var act in activityAvailable.value){
        if (activityAvailable.value[act] != 0) {
            tmp[i] = [act, activityAvailable.value[act]];
            i++;
        }
    }
    
    activityAvailable.value = tmp.sort(function(a, b) {return a[1] - b[1]});
    
    for (i=0; i < activityAvailable.value.length; i++){
        activity = activityAvailable.value[i][0];
        if (activityAvailable.value[activity] != 0) {
            postformated.value.push({label: activity, color:colors[activity],data: formated_value[activity], });
        }
    }
    
    postformated.value = postformated.value.reverse();
    
    for (i=0; i < activityAvailable.value.length; i++){
        activity = activityAvailable.value[i][0];
        if (activityAvailable.value[activity] != 0) {
            postformated.value_count.push({label: activity, color:colors[activity],data: formated_count[activity], });
        }
    }
    
    
    postformated.value_count = postformated.value_count.reverse();
    
    
        
    // COUNT
    var tmp = [];
    i = 0;
    for(var act in activityAvailable.count){
        if (activityAvailable.count[act] != 0) {
            tmp[i] = [act, activityAvailable.count[act]];
            i++;
        }
    }
    
    activityAvailable.count = tmp.sort(function(a, b) {return a[1] - b[1]});
    
    for (i=0; i < activityAvailable.count.length; i++){
        activity = activityAvailable.count[i][0];
        if (activityAvailable.count[activity] != 0) {
            postformated.count.push({label: activity, color:colors[activity],data: formated_count[activity], });
        }
    }
    
    postformated.count = postformated.count.reverse();
    
    for (i=0; i < activityAvailable.count.length; i++){
        activity = activityAvailable.count[i][0];
        if (activityAvailable.count[activity] != 0) {
            postformated.count_value.push({label: activity, color:colors[activity],data: formated_value[activity], });
        }
    }
    
    
    postformated.count_value = postformated.count_value.reverse();
    
    
    return postformated;

    
}