/**
 * Copyright FunASR (https://github.com/alibaba-damo-academy/FunASR). All Rights
 * Reserved. MIT License  (https://opensource.org/licenses/MIT)
 */
/* 2021-2023 by zhaoming,mali aihealthx.com */

function WebSocketConnectMethod( config ) { //Define socket connection method class


	var speechSokt;
	var connKeeperID;

	var msgHandle = config.msgHandle;
	var stateHandle = config.stateHandle;

	this.wsStart = function () {
		var Uri = document.getElementById('wssip').value; //"wss://111.205.137.58:5821/wss/" //Set wss asr online interface address like wss://X.X.X.X:port/wss/
		if(Uri.match(/wss:\S*|ws:\S*/))
		{
			console.log("Uri"+Uri);
		}
		else
		{
			alert("Please check the correctness of the wss address");
			return 0;
		}

		if ( 'WebSocket' in window ) {
			speechSokt = new WebSocket( Uri ); // Define socket connection object
			speechSokt.onopen = function(e){onOpen(e);}; // Define response function
			speechSokt.onclose = function(e){
			    console.log("onclose ws!");
			    //speechSokt.close();
				onClose(e);
				};
			speechSokt.onmessage = function(e){onMessage(e);};
			speechSokt.onerror = function(e){onError(e);};
			return 1;
		}
		else {
			alert('Current browser does not support WebSocket');
			return 0;
		}
	};

	// Define stop and send functions
	this.wsStop = function () {
		if(speechSokt != undefined) {
			console.log("stop ws!");
			speechSokt.close();
		}
	};

	this.wsSend = function ( oneData ) {

		if(speechSokt == undefined) return;
		if ( speechSokt.readyState === 1 ) { // 0:CONNECTING, 1:OPEN, 2:CLOSING, 3:CLOSED

			speechSokt.send( oneData );


		}
	};

	// Message and state response in SOCKET connection
	function onOpen( e ) {
		// Send json
		var chunk_size = new Array( 5, 10, 5 );
		var request = {
			"chunk_size": chunk_size,
			"wav_name":  "h5",
			"is_speaking":  true,
			"chunk_interval":10,
			"itn":getUseITN(),
			"mode":getAsrMode(),

		};
		if(isfilemode)
		{
			request.wav_format=file_ext;
			if(file_ext=="wav")
			{
				request.wav_format="PCM";
				request.audio_fs=file_sample_rate;
			}
		}

		var hotwords=getHotwords();

		if(hotwords!=null  )
		{
			request.hotwords=hotwords;
		}
		console.log(JSON.stringify(request));
		speechSokt.send(JSON.stringify(request));
		console.log("Connection successful");
		stateHandle(0);

	}

	function onClose( e ) {
		stateHandle(1);
	}

	function onMessage( e ) {

		msgHandle( e );
	}

	function onError( e ) {

		info_div.innerHTML="Connection"+e;
		console.log(e);
		stateHandle(2);

	}


}
