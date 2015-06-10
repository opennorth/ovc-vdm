$.fn.selectpicker.Constructor.prototype.selectAll = function(){
    $(this.$element[0], this.$element.context).addClass('loading');
        this.findLis();
        this.$lis.not('.divider').not('.disabled').not('.selected').filter(':visible').find('a').click();
        $(this.$element[0], this.$element.context).removeClass('loading');
    $(this.$element[0]).trigger('change');
}
$.fn.selectpicker.Constructor.prototype.deselectAll = function(){
    $(this.$element[0], this.$element.context).addClass('loading');
        this.findLis();
        this.$lis.not('.divider').not('.disabled').filter('.selected').filter(':visible').find('a').click();
        $(this.$element[0], this.$element.context).removeClass('loading');
    $(this.$element[0]).trigger('change');
    
}
