


var page       = require('webpage').create(),
    system     = require('system');

page.viewportSize = { width: 1920, height: 1080 };

if (system.args.length === 1) 
	{
    console.log('Usage: read_thirdpartyrequests.js <some URL>');
    phantom.exit(1);
	} 

else 
{
	address = system.args[1];
	page.settings.userName = system.args[2];
	page.settings.password = system.args[3];
	cookies = system.args[4];
	cookies = cookies.split("---ENDCOOKIE---");
	phantom.clearCookies();
	for (var i = 0; i < cookies.length; i++) 
	{
		builtCookie = {'domain' : 'api3.cdsuperstore.se'}
		cookievalues = cookies[i].split(";");
		for(var j = 0; j < cookievalues.length; j++)
		{
			cookieAttributes = cookievalues[j].split("=");
			if(j == 0)
			{
				builtCookie['name'] = cookieAttributes[0];
				builtCookie['value'] = cookieAttributes[1];
			}
			if(j == 1)
			{
				builtCookie['expires'] = cookieAttributes[1];
			}
			if(j == 2)
			{
				builtCookie['path'] = cookieAttributes[1];
			}
		}
		phantom.addCookie(builtCookie);
	}
	
	page.open(address, function(status) 
	{
		if(status !== 'success')
		{
			console.log('FAIL to load the address');
		}
		console.log('TAR BILD');
		page.render('helllooooo.png');
		window.setTimeout( function(){
			phantom.exit();

		},4000);

	}


			 )
}