console.log('[');

var page       = require('webpage').create(),
    system     = require('system');

page.onResourceRequested = function(request) {
	console.log(JSON.stringify(request, null, 2) + ',');
};
page.onResourceReceived = function(response) {
	console.log(JSON.stringify(response, null, 2) + ',');
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
			console.log('{"failsafe" : "hah"}]');
			phantom.exit();
		}, 15000);

	}


			 )
}