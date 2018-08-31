window.fusionJavaScriptHandler = 
{
	handle: function(action, data)
	{
		var unit;
		var f;
		var numdec;
		var val;
		
		try 
		{

			if ( document.getElementById("radioGB").checked == true)
			{	
				unit = " GB";
				power = 30;	
				numdec = 2;
			}
			else if ( document.getElementById("radioMB").checked == true)
			{
				unit = " MB";
				power = 20;
				numdec = 0;
			}
			else
			{
				unit = " KB";
				power = 10;
				numdec = 0;
			}
		
			f = Math.pow(2,power);
		
			obj = JSON.parse(data)
			
			val = parseInt(obj.min)/f;
			document.getElementById('mem_min').innerHTML = val.toFixed(numdec);
			val = parseInt(obj.uss)/f;
			document.getElementById('mem_cur').innerHTML = val.toFixed(numdec);
			val = parseInt(obj.max)/f;
			document.getElementById('mem_max').innerHTML = val.toFixed(numdec);
			
		} 
		catch (e)
		{
			console.log(e);
			console.log('exception caught with command: ' + action + ', data: ' + data);
		}
		return 'OK';
	}
};