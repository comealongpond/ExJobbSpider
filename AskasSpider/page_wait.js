var page       = require('webpage').create(),
    system     = require('system');

if (system.args.length === 1) 
{
    console.log('Usage: page_wait.js <some URL>');
    phantom.exit(1);
} 


else 
{ try{
	address = system.args[1];
	//if(system.args[2] != null && system.args[3] != null){
	page.settings.userName = system.args[2];
	page.settings.password = system.args[3];

	cookies = system.args[4];
	cookies = cookies.split("---ENDCOOKIE---");
	phantom.clearCookies();
	for (var i = 0; i < cookies.length; i++) 
	{
		builtCookie = {'domain' : system.args[5]}
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

	page.open(address, function(status) {
		if(status !== 'success')
		{
			console.log('FAIL to load the address');
		}

		window.setTimeout(function() {
			console.log(page.content);
			phantom.exit();
		}, 200);
	})
}
catch(ex){
	phantom.exit()
}
}