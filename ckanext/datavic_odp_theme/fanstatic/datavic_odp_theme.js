  jQuery(document).ready(function() {
    jQuery('#btn-mobile-menu-close').on('click', function(){
        jQuery('body').css('overflow', '');
        jQuery('#mobile-menu').removeClass('rpl-site-header--open').addClass('hidden');
        jQuery('#main-menu').show();
    });

    jQuery('#btn-mobile-menu-open').on('click', function(){
        jQuery('body').css('overflow', 'hidden');
        jQuery('#mobile-menu').addClass('rpl-site-header--open').removeClass('hidden');
        jQuery('#main-menu').hide();
    });
  });