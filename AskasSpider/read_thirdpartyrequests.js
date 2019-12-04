var page       = require('webpage').create(),
    system     = require('system');

page.onResourceRequested = function(request) {
	
	var urls = JSON.stringify(request, null, 2);
	
	if(JSON.parse(urls)['url'].substring(0, 4) == "http"){
	console.log('\'' + JSON.parse(urls)['url'] + '\'');
	}
};
page.onResourceReceived = function(response) {
	

	var urls = JSON.stringify(response, null, 2);
	
	if(JSON.parse(urls)['url'].substring(0, 4) == "http"){
	console.log('\'' + JSON.parse(urls)['url'] + '\'');
	}
};

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

	page.open(address, function(status) 
	{
		if(status !== 'success')
		{
			console.log('FAIL to load the address');
		}

		window.setTimeout( function(){
			phantom.exit();

		},7000);

	}


			 )
}