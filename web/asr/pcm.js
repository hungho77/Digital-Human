/*
pcm encoder + encoding engine
https://github.com/xiangyuecn/Recorder

Encoding principle: The pcm format data output by this encoder is actually the original data in Recorder's buffers (after resampling), 16-bit is in LE little-endian mode (Little Endian), and has not undergone any encoding processing

The encoding code is not much different from wav.js, adding a 44-byte wav header to pcm creates a wav file; so playing pcm is very simple, just convert it to a wav file to play, the conversion function Recorder.pcm2wav has been provided
*/
(function(){
"use strict";

Recorder.prototype.enc_pcm={
	stable:true
	,testmsg:"pcm is unencapsulated raw audio data, pcm data files cannot be played directly; supports 8-bit and 16-bit (fill in bitrate), sample rate values are unlimited"
};
Recorder.prototype.pcm=function(res,True,False){
		var This=this,set=This.set
			,size=res.length
			,bitRate=set.bitRate==8?8:16;

		var buffer=new ArrayBuffer(size*(bitRate/8));
		var data=new DataView(buffer);
		var offset=0;

		// Write sample data
		if(bitRate==8) {
			for(var i=0;i<size;i++,offset++) {
				//16 to 8 is said to be Lei Xiaohua's https://blog.csdn.net/sevennight1989/article/details/85376149 The details are clearer than blqw's proportional algorithm, although both have obvious noise
				var val=(res[i]>>8)+128;
				data.setInt8(offset,val,true);
			};
		}else{
			for (var i=0;i<size;i++,offset+=2){
				data.setInt16(offset,res[i],true);
			};
		};


		True(new Blob([data.buffer],{type:"audio/pcm"}));
	};





/**pcm directly transcodes to wav, can be used directly for playback; requires wav.js to be imported
data: {
		sampleRate:16000 pcm sample rate
		bitRate:16 pcm bit depth, values: 8 or 16
		blob:blob object
	}
	data if blob is provided directly will default to 16-bit 16khz configuration, for testing only
True(wavBlob,duration)
False(msg)
**/
Recorder.pcm2wav=function(data,True,False){
	if(data.slice && data.type!=null){//Blob for testing
		data={blob:data};
	};
	var sampleRate=data.sampleRate||16000,bitRate=data.bitRate||16;
	if(!data.sampleRate || !data.bitRate){
		console.warn("pcm2wav must provide sampleRate and bitRate");
	};
	if(!Recorder.prototype.wav){
		False("pcm2wav must first load the wav encoder wav.js");
		return;
	};

	var reader=new FileReader();
	reader.onloadend=function(){
		var pcm;
		if(bitRate==8){
			//8-bit to 16-bit
			var u8arr=new Uint8Array(reader.result);
			pcm=new Int16Array(u8arr.length);
			for(var j=0;j<u8arr.length;j++){
				pcm[j]=(u8arr[j]-128)<<8;
			};
		}else{
			pcm=new Int16Array(reader.result);
		};

		Recorder({
			type:"wav"
			,sampleRate:sampleRate
			,bitRate:bitRate
		}).mock(pcm,sampleRate).stop(function(wavBlob,duration){
			True(wavBlob,duration);
		},False);
	};
	reader.readAsArrayBuffer(data.blob);
};



})();
