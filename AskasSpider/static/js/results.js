
$(document).ready(function(){

	$('.grade').each(function(index) {
		//var num = $(this).attr('class').match(/\d+$/)[0];
		grade = parseInt($(this).text().replace('%', ''))

		if(grade <= 40)
		{
			$(this).addClass('error');
		}
		else if(grade <= 70)
		{
			$(this).addClass('warning');
		}
		else
		{
			$(this).addClass('success');
		}
	});
});