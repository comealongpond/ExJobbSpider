$(document).ready(function(){
	$(".drop-down-banner .drop-down-heading").click(function(){
    	$(this).parent().parent().find(".drop-down-box:first").slideToggle("slow");
    	
    	if($(this).text() == "[+]"){$(this).html("[-]")}
    	else{$(this).html("[+]")}
    });

});
