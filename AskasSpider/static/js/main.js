$(document).ready(function(){
	document.getElementById("defaultOpen").click();

	$(".drop-down-banner .drop-down-heading").click(function(){
    	$(this).parent().parent().find(".drop-down-box:first").slideToggle("slow");
    	
    	if($(this).text() == "[+]"){$(this).html("[-]")}
    	else{$(this).html("[+]")}
    });

    /*
    $('#default_form').submit(function(e) {
        e.preventDefault();
        $('#loader_container').css('visibility', 'visible');
        setTimeout(function(){
          $('#default_form').unbind('submit').submit();
        }, 100);
        
    });

    $('#quickscan_form').submit(function(e) {
        e.preventDefault();
        $('#loader_container').css('visibility', 'visible');
        setTimeout(function(){
          $('#quickscan_form').unbind('submit').submit();
        }, 100);
        
    });

    $(window).bind("pageshow", function(event) {
        $('#loader_container').css('visibility', 'hidden');

        $('#default_form').submit(function(e) {
            e.preventDefault();
            $('#loader_container').css('visibility', 'visible');
            setTimeout(function(){
              $('#default_form').unbind('submit').submit();
            }, 100);
        
        });

        $('#quickscan_form').submit(function(e) {
            e.preventDefault();
            $('#loader_container').css('visibility', 'visible');
            setTimeout(function(){
              $('#quickscan_form').unbind('submit').submit();
            }, 100);
            
        });
    });
    */
});



function switchTab(tabName, element, color) {
    // Hide all elements with class="tabcontent" by default */
    var i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }

    // Remove the background color of all tablinks/buttons
    tablinks = document.getElementsByClassName("tablink");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].style.backgroundColor = "";
    }

    // Show the specific tab content
    document.getElementById(tabName).style.display = "block";

    // Add the specific color to the button used to open the tab content
    element.style.backgroundColor = color;
}




