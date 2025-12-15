/*
Recording
https://github.com/xiangyuecn/Recorder
*/
(function(factory){
	factory(window);
	//umd returnExports.js
	if(typeof(define)=='function' && define.amd){
		define(function(){
			return Recorder;
		});
	};
	if(typeof(module)=='object' && module.exports){
		module.exports=Recorder;
	};
}(function(window){
"use strict";

var NOOP=function(){};

var Recorder=function(set){
	return new initFn(set);
};
Recorder.LM="2023-02-01 18:05";
var RecTxt="Recorder";
var getUserMediaTxt="getUserMedia";
var srcSampleRateTxt="srcSampleRate";
var sampleRateTxt="sampleRate";
var CatchTxt="catch";


//Whether the global microphone recording has been opened, all work is ready, just waiting to receive audio data
Recorder.IsOpen=function(){
	var stream=Recorder.Stream;
	if(stream){
		var tracks=stream.getTracks&&stream.getTracks()||stream.audioTracks||[];
		var track=tracks[0];
		if(track){
			var state=track.readyState;
			return state=="live"||state==track.LIVE;
		};
	};
	return false;
};
/*H5 recording AudioContext buffer size. Will affect the onProcess call rate during H5 recording, relative to AudioContext.sampleRate=48000, 4096 is close to 12 frames/s, adjusting this parameter can generate smoother callback animations.
	Values 256, 512, 1024, 2048, 4096, 8192, or 16384
	Note, values cannot be too low, starting from 2048 different browsers may have callback rates that can't keep up causing audio quality issues.
	Generally no adjustment needed, after adjustment you need to close the opened recording first, then open again for it to take effect.
*/
Recorder.BufferSize=4096;
//Destroy all held global resources, when completely removing Recorder you need to explicitly call this method
Recorder.Destroy=function(){
	CLog(RecTxt+" Destroy");
	Disconnect();//Disconnect any existing global Stream and resources

	for(var k in DestroyList){
		DestroyList[k]();
	};
};
var DestroyList={};
//Register a method that needs to destroy global resources
Recorder.BindDestroy=function(key,call){
	DestroyList[key]=call;
};
//Determine whether the browser supports recording, can be called anytime. Note: Only detects browser support, does not determine and prompt user authorization, does not determine support for specific format recording.
Recorder.Support=function(){
	var scope=navigator.mediaDevices||{};
	if(!scope[getUserMediaTxt]){
		scope=navigator;
		scope[getUserMediaTxt]||(scope[getUserMediaTxt]=scope.webkitGetUserMedia||scope.mozGetUserMedia||scope.msGetUserMedia);
	};
	if(!scope[getUserMediaTxt]){
		return false;
	};
	Recorder.Scope=scope;

	if(!Recorder.GetContext()){
		return false;
	};
	return true;
};
//Get the global AudioContext object, returns null if browser doesn't support it
Recorder.GetContext=function(){
	var AC=window.AudioContext;
	if(!AC){
		AC=window.webkitAudioContext;
	};
	if(!AC){
		return null;
	};

	if(!Recorder.Ctx||Recorder.Ctx.state=="closed"){
		//Cannot construct repeatedly, low version number of hardware contexts reached maximum (6)
		Recorder.Ctx=new AC();

					Recorder.BindDestroy("Ctx",function(){
			var ctx=Recorder.Ctx;
			if(ctx&&ctx.close){//Close if possible, keep if can't close
				ctx.close();
				Recorder.Ctx=0;
			};
		});
	};
	return Recorder.Ctx;
};


/*Whether to enable MediaRecorder.WebM.PCM for audio collection connection (if browser supports it), enabled by default, disabled or not supported will use AudioWorklet or ScriptProcessor to connect; MediaRecorder collected audio data is better than other methods, almost no frame dropping, so audio quality will be much better, recommend keeping enabled*/
var ConnectEnableWebM="ConnectEnableWebM";
Recorder[ConnectEnableWebM]=true;

/*Whether to enable AudioWorklet feature for audio collection connection (if browser supports it), disabled by default, disabled or not supported will use outdated ScriptProcessor to connect (if method still exists), current AudioWorklet implementation is not as robust as ScriptProcessor on mobile; this parameter will not work if ConnectEnableWebM is enabled and effective*/
var ConnectEnableWorklet="ConnectEnableWorklet";
Recorder[ConnectEnableWorklet]=false;

/*Initialize H5 audio collection connection. If sourceStream is provided, only a simple connection process will be performed. If it's normal microphone recording, the Stream at this time is global, and after disconnection on Safari it cannot be connected again, showing as silence, so use global processing to avoid calling disconnect; global processing also helps shield underlying details, no need to call underlying interfaces at start, improving compatibility and reliability.*/
var Connect=function(streamStore,isUserMedia){
	var bufferSize=streamStore.BufferSize||Recorder.BufferSize;

	var ctx=Recorder.Ctx,stream=streamStore.Stream;
	var mediaConn=function(node){
		var media=stream._m=ctx.createMediaStreamSource(stream);
		var ctxDest=ctx.destination,cmsdTxt="createMediaStreamDestination";
		if(ctx[cmsdTxt]){
			ctxDest=ctx[cmsdTxt]();
		};
		media.connect(node);
		node.connect(ctxDest);
	}
	var isWebM,isWorklet,badInt,webMTips="";
	var calls=stream._call;

	// Process audio data returned by the browser
	var onReceive=function(float32Arr){
		for(var k0 in calls){//has item
			var size=float32Arr.length;

			var pcm=new Int16Array(size);
			var sum=0;
			for(var j=0;j<size;j++){//floatTo16BitPCM
				var s=Math.max(-1,Math.min(1,float32Arr[j]));
				s=s<0?s*0x8000:s*0x7FFF;
				pcm[j]=s;
				sum+=Math.abs(s);
			};

			for(var k in calls){
				calls[k](pcm,sum);
			};

			return;
		};
	};

	var scriptProcessor="ScriptProcessor";// A bunch of string names, helpful for minifying js
	var audioWorklet="audioWorklet";
	var recAudioWorklet=RecTxt+" "+audioWorklet;
	var RecProc="RecProc";
	var MediaRecorderTxt="MediaRecorder";
	var MRWebMPCM=MediaRecorderTxt+".WebM.PCM";


//===================Connection Method 3=========================
	// Legacy ScriptProcessor handling; compatible with all browsers. Though deprecated, it's more robust and has better performance than AudioWorklet on mobile.
	var oldFn=ctx.createScriptProcessor||ctx.createJavaScriptNode;
	var oldIsBest="Because "+audioWorklet+" internally calls back 375 times per second, there may be performance issues on mobile causing callback loss and shorter recordings. No effect on PC, not recommended to enable "+audioWorklet+" for now.";
	var oldScript=function(){
		isWorklet=stream.isWorklet=false;
		_Disconn_n(stream);
		CLog("Connect uses legacy "+scriptProcessor+", "+(Recorder[ConnectEnableWorklet]?"but already":"you can")+" set "+RecTxt+"."+ConnectEnableWorklet+"=true to try enabling "+audioWorklet+webMTips+oldIsBest,3);

		var process=stream._p=oldFn.call(ctx,bufferSize,1,1);// Mono channel, simpler data processing
		mediaConn(process);

		var _DsetTxt="_D220626",_Dset=Recorder[_DsetTxt];if(_Dset)CLog("Use "+RecTxt+"."+_DsetTxt,3);
		process.onaudioprocess=function(e){
			var arr=e.inputBuffer.getChannelData(0);
			if(_Dset){// Temporary debug parameter; will be removed in the future
				arr=new Float32Array(arr);// The block is shared, must copy out
				setTimeout(function(){ onReceive(arr) });// Exit callback immediately to try to reduce impact on recording
			}else{
				onReceive(arr);
			};
		};
	};


//===================Connection Method 2=========================
var connWorklet=function(){
	// Try to enable AudioWorklet
	isWebM=stream.isWebM=false;
	_Disconn_r(stream);

	isWorklet=stream.isWorklet=!oldFn || Recorder[ConnectEnableWorklet];
	var AwNode=window.AudioWorkletNode;
	if(!(isWorklet && ctx[audioWorklet] && AwNode)){
		oldScript();// Disabled or unsupported; fallback to legacy
		return;
	};
	var clazzUrl=function(){
		var xf=function(f){return f.toString().replace(/^function|DEL_/g,"").replace(/\$RA/g,recAudioWorklet)};
		var clazz='class '+RecProc+' extends AudioWorkletProcessor{';
			clazz+="constructor "+xf(function(option){
				DEL_super(option);
				var This=this,bufferSize=option.processorOptions.bufferSize;
				This.bufferSize=bufferSize;
				This.buffer=new Float32Array(bufferSize*2);// Ignore incorrect size to avoid corrupting buffer
				This.pos=0;
				This.port.onmessage=function(e){
					if(e.data.kill){
						This.kill=true;
						console.log("$RA kill call");
					}
				};
				console.log("$RA .ctor call", option);
			});

			// https://developer.mozilla.org/en-US/docs/Web/API/AudioWorkletProcessor/process Callback gets 128 samples each time, 375 times per second; high frequency may cause mobile performance issues leading to lost callbacks.
			clazz+="process "+xf(function(input,b,c){// Need ctx to be active before callbacks occur
				var This=this,bufferSize=This.bufferSize;
				var buffer=This.buffer,pos=This.pos;
				input=(input[0]||[])[0]||[];
				if(input.length){
					buffer.set(input,pos);
					pos+=input.length;

					var len=~~(pos/bufferSize)*bufferSize;
					if(len){
						this.port.postMessage({ val: buffer.slice(0,len) });

						var more=buffer.subarray(len,pos);
						buffer=new Float32Array(bufferSize*2);
						buffer.set(more);
						pos=more.length;
						This.buffer=buffer;
					}
					This.pos=pos;
				}
				return !This.kill;
			});
		clazz+='}'
			+'try{'
				+'registerProcessor("'+RecProc+'", '+RecProc+')'
			+'}catch(e){'
				+'console.error("'+recAudioWorklet+' register failed",e)'
			+'}';
		// Some local browsers report Not allowed to load local resource for URL.createObjectURL; use dataurl instead
		return "data:text/javascript;base64,"+btoa(unescape(encodeURIComponent(clazz)));
	};

	var awNext=function(){// Can continue, not disconnected
		return isWorklet && stream._na;
	};
	var nodeAlive=stream._na=function(){
		// Called on start; if no data received, assume AudioWorklet has an issue and fallback
		if(badInt!==""){// No data callback yet
			clearTimeout(badInt);
			badInt=setTimeout(function(){
				badInt=0;
				if(awNext()){
					CLog(audioWorklet+" returned no audio, fallback to "+scriptProcessor,3);
					oldFn&&oldScript();// legacy may not exist in the future; could be a false positive
				};
			},500);
		};
	};
	var createNode=function(){
		if(!awNext())return;
		var node=stream._n=new AwNode(ctx, RecProc, {
			processorOptions:{bufferSize:bufferSize}
		});
		mediaConn(node);
		node.port.onmessage=function(e){
			if(badInt){
				clearTimeout(badInt);badInt="";
			};
			if(awNext()){
				onReceive(e.data.val);
			}else if(!isWorklet){
				CLog(audioWorklet+" redundant callback",3);
			};
		};
		CLog("Connect uses "+audioWorklet+", set "+RecTxt+"."+ConnectEnableWorklet+"=false to restore legacy "+scriptProcessor+webMTips+oldIsBest,3);
	};

	// If resume at start and node construction happen simultaneously, some browsers may crash. Wrap in resume to avoid the issue
	ctx.resume()[calls&&"finally"](function(){// Comment out to reproduce crash STATUS_ACCESS_VIOLATION
		if(!awNext())return;
		if(ctx[RecProc]){
			createNode();
			return;
		};
		var url=clazzUrl();
		ctx[audioWorklet].addModule(url).then(function(e){
			if(!awNext())return;
			ctx[RecProc]=1;
			createNode();
			if(badInt){// restart timer
				nodeAlive();
			};
		})[CatchTxt](function(e){ // fix keyword to keep catch as string on minify
			CLog(audioWorklet+".addModule failed",1,e);
			awNext()&&oldScript();
		});
	});
};


//===================Connection Method 1=========================
var connWebM=function(){
	// Try MediaRecorder to record webm+pcm
	var MR=window[MediaRecorderTxt];
	var onData="ondataavailable";
	var webmType="audio/webm; codecs=pcm";
	isWebM=stream.isWebM=Recorder[ConnectEnableWebM];

	var supportMR=MR && (onData in MR.prototype) && MR.isTypeSupported(webmType);
	webMTips=supportMR?"":" (browser does not support "+MRWebMPCM+")";
	if(!isUserMedia || !isWebM || !supportMR){
		connWorklet(); // Not microphone recording (MediaRecorder sampleRate uncontrollable) or disabled/unsupported
		return;
	}

	var mrNext=function(){// Can continue, not disconnected
		return isWebM && stream._ra;
	};
	var mrAlive=stream._ra=function(){
		// Called on start; if no data received, degrade handling
		if(badInt!==""){// No data callback yet
			clearTimeout(badInt);
			badInt=setTimeout(function(){
					//badInt=0; keep for nodeAlive to continue checking
				if(mrNext()){
					CLog(MediaRecorderTxt+" returned no audio, degrade to "+audioWorklet,3);
					connWorklet();
				};
			},500);
		};
	};

	var mrSet=Object.assign({mimeType:webmType}, Recorder.ConnectWebMOptions);
	var mr=stream._r=new MR(stream, mrSet);
	var webmData=stream._rd={sampleRate:ctx[sampleRateTxt]};
	mr[onData]=function(e){
		// Extract pcm data from webm; on failure wait for timeout to degrade
		var reader=new FileReader();
		reader.onloadend=function(){
			if(mrNext()){
				var f32arr=WebM_Extract(new Uint8Array(reader.result),webmData);
				if(!f32arr)return;
				if(f32arr==-1){// Extraction failed, degrade immediately
					connWorklet();
					return;
				};

				if(badInt){
					clearTimeout(badInt);badInt="";
				};
				onReceive(f32arr);
			}else if(!isWebM){
				CLog(MediaRecorderTxt+" redundant callback",3);
			};
		};
		reader.readAsArrayBuffer(e.data);
	};
	mr.start(~~(bufferSize/48));// Callback interval based on 48k
	CLog("Connect uses "+MRWebMPCM+", set "+RecTxt+"."+ConnectEnableWebM+"=false to restore "+audioWorklet+" or legacy "+scriptProcessor);
};

	connWebM();
};
var ConnAlive=function(stream){
	if(stream._na) stream._na(); // Check AudioWorklet connection; rollback to ScriptProcessor if invalid
	if(stream._ra) stream._ra(); // Check MediaRecorder connection; degrade if invalid
};
var _Disconn_n=function(stream){
	stream._na=null;
	if(stream._n){
		stream._n.port.postMessage({kill:true});
		stream._n.disconnect();
		stream._n=null;
	};
};
var _Disconn_r=function(stream){
	stream._ra=null;
	if(stream._r){
		stream._r.stop();
		stream._r=null;
	};
};
var Disconnect=function(streamStore){
	streamStore=streamStore||Recorder;
	var isGlobal=streamStore==Recorder;

	var stream=streamStore.Stream;
	if(stream){
		if(stream._m){
			stream._m.disconnect();
			stream._m=null;
		};
		if(stream._p){
			stream._p.disconnect();
			stream._p.onaudioprocess=stream._p=null;
		};
		_Disconn_n(stream);
		_Disconn_r(stream);

		if(isGlobal){// When global, stop the stream (microphone); do not handle provided streams
			var tracks=stream.getTracks&&stream.getTracks()||stream.audioTracks||[];
			for(var i=0;i<tracks.length;i++){
				var track=tracks[i];
				track.stop&&track.stop();
			};
			stream.stop&&stream.stop();
		};
	};
	streamStore.Stream=0;
};

/* Resample PCM data sample rate
pcmDatas: [[Int16,...]] list of PCM chunks
pcmSampleRate:48000 sample rate of PCM input
newSampleRate:16000 target sample rate; if >= input, no processing; if lower, resample
prevChunkInfo:{} optional, previous return to enable continuous resampling from last position; or custom starting point
option:{ optional config
        frameSize:123456 frame size in count of PCM Int16; output length is multiple of frameSize for continuous conversion; for mp3 use 1152
        frameType:"" usually rec.set.type; when provided, frameSize is auto-chosen; currently mp3=1152, others=1
            Only one of the above should be used. For the last segment, omit frame size to output remaining data.
    }

Returns ChunkInfo:{
    index:0 processed index in pcmDatas
    offset:0.0 next offset in pcm at that index
    frameNext:null||[Int16,...] part of next frame when frameSize set
    sampleRate:16000 result sample rate, <= newSampleRate
    data:[Int16,...] resampled PCM; length can be 0 if no new data in continuous conversion
}
*/
Recorder.SampleData=function(pcmDatas,pcmSampleRate,newSampleRate,prevChunkInfo,option){
	prevChunkInfo||(prevChunkInfo={});
	var index=prevChunkInfo.index||0;
	var offset=prevChunkInfo.offset||0;

	var frameNext=prevChunkInfo.frameNext||[];
	option||(option={});
	var frameSize=option.frameSize||1;
	if(option.frameType){
		frameSize=option.frameType=="mp3"?1152:1;
	};

	var nLen=pcmDatas.length;
	if(index>nLen+1){
		CLog("SampleData seems given a non-reset chunk "+index+">"+nLen,3);
	};
	var size=0;
	for(var i=index;i<nLen;i++){
		size+=pcmDatas[i].length;
	};
	size=Math.max(0,size-Math.floor(offset));

	// Sampling https://www.cnblogs.com/blqw/p/3782420.html
	var step=pcmSampleRate/newSampleRate;
	if(step>1){// New sample rate lower than input; downsample
		size=Math.floor(size/step);
	}else{// New sample rate higher; skip processing, no interpolation
		step=1;
		newSampleRate=pcmSampleRate;
	};

	size+=frameNext.length;
	var res=new Int16Array(size);
	var idx=0;
	// Append leftover data from last frame
	for(var i=0;i<frameNext.length;i++){
		res[idx]=frameNext[i];
		idx++;
	};
	// Process data
	for (;index<nLen;index++) {
		var o=pcmDatas[index];
		var i=offset,il=o.length;
		while(i<il){
			//res[idx]=o[Math.round(i)]; direct simple sampling

			//https://www.cnblogs.com/xiaoqi/p/6993912.html
			// Linear interpolation yields better quality than simple sampling
			var before = Math.floor(i);
			var after = Math.ceil(i);
			var atPoint = i - before;

			var beforeVal=o[before];
			var afterVal=after<il ? o[after]
				: (// Next point out of bounds, try next array
					(pcmDatas[index+1]||[beforeVal])[0]||0
				);
			res[idx]=beforeVal+(afterVal-beforeVal)*atPoint;

			idx++;
			i+=step;// sample
		};
		offset=i-il;
	};
	// Frame handling
	frameNext=null;
	var frameNextSize=res.length%frameSize;
	if(frameNextSize>0){
		var u8Pos=(res.length-frameNextSize)*2;
		frameNext=new Int16Array(res.buffer.slice(u8Pos));
		res=new Int16Array(res.buffer.slice(0,u8Pos));
	};

	return {
		index:index
		,offset:offset

		,frameNext:frameNext
		,sampleRate:newSampleRate
		,data:res
	};
};


/* Calculate volume percentage
pcmAbsSum: sum of absolute values of all Int16 samples
pcmLength: pcm length
Return: 0-100, used as percentage (not dB)
*/
Recorder.PowerLevel=function(pcmAbsSum,pcmLength){
	/* Volume calc https://blog.csdn.net/jody1989/article/details/73480259
	Higher sensitivity algorithm:
		Cap max to 10000
			Linear: unfriendly at low volume: power/10000*100
			Log: friendly at low volume, but needs minimum cap: (1+Math.log10(power/10000))*100
	*/
	var power=(pcmAbsSum/pcmLength) || 0;//NaN
	var level;
	if(power<1251){// 10% at 1250; use linear below
		level=Math.round(power/1250*10);
	}else{
		level=Math.round(Math.min(100,Math.max(0,(1+Math.log(power/10000)/Math.log(10))*100)));
	};
	return level;
};

/* Calculate volume in dBFS (Full Scale)
maxSample: max absolute value of 16-bit pcm samples (peak) or average of absolutes
Return: -100~0 (0dB max, -100 for -∞)
*/
Recorder.PowerDBFS=function(maxSample){
	var val=Math.max(0.1, maxSample||0),Pref=0x7FFF;
	val=Math.min(val,Pref);
	//https://www.logiclocmusic.com/can-you-tell-the-decibel/
	//https://blog.csdn.net/qq_17256689/article/details/120442510
	val=20*Math.log(val/Pref)/Math.log(10);
	return Math.max(-100,Math.round(val));
};




// Timestamped logger; set to NOOP to silence logs
// CLog(msg,errOrLogMsg, logMsg...) err numeric: 1=error 2=log 3=warn
Recorder.CLog=function(msg,err){
	var now=new Date();
	var t=("0"+now.getMinutes()).substr(-2)
		+":"+("0"+now.getSeconds()).substr(-2)
		+"."+("00"+now.getMilliseconds()).substr(-3);
	var recID=this&&this.envIn&&this.envCheck&&this.id;
	var arr=["["+t+" "+RecTxt+(recID?":"+recID:"")+"]"+msg];
	var a=arguments,console=window.console||{};
	var i=2,fn=console.log;
	if(typeof(err)=="number"){
		fn=err==1?console.error:err==3?console.warn:fn;
	}else{
		i=1;
	};
	for(;i<a.length;i++){
		arr.push(a[i]);
	};
	if(IsLoser){// Ancient browsers: ensure basic execution only
		fn&&fn("[IsLoser]"+arr[0],arr.length>1?arr:"");
	}else{
		fn.apply(console,arr);
	};
};
var CLog=function(){ Recorder.CLog.apply(this,arguments); };
var IsLoser=true;try{IsLoser=!console.log.apply;}catch(e){};




var ID=0;
function initFn(set){
	this.id=++ID;

	// If traffic collection enabled, send a beacon image
	Traffic();


	var o={
		type:"mp3" // Output type: mp3,wav; wav is huge; mp3 support increases js size
		,bitRate:16 // Bit rate wav:16/8-bit; MP3: 8kbps 1k/s, 8kbps 2k/s small files

		,sampleRate:16000 // Sample rate; wav size = sampleRate*time; mp3 low bitrates affected
					// wav: any; mp3 allowed: 48000,44100,32000,24000,22050,16000,12000,11025,8000
					// Reference: https://www.cnblogs.com/devin87/p/mp3-recorder.html

		,onProcess:NOOP // fn(buffers,powerLevel,bufferDuration,bufferSampleRate,newBufferIdx,asyncEnd) buffers are accumulated PCM chunks since start; powerLevel 0-100; bufferDuration ms; bufferSampleRate sample rate; newBufferIdx start index for this callback; asyncEnd required if returns true (async)

		//******* Advanced Settings ******
		//,sourceStream:MediaStream Object
				// Optionally provide a MediaStream for recording/processing (exclusive to this instance); otherwise use microphone via getUserMedia (global shared)
				// e.g., captureStream of audio/video elements; WebRTC remote stream; custom streams
				// Note: stream must have at least one Audio Track; e.g., wait until audio element can play

		//,audioTrackSet:{ deviceId:"",groupId:"", autoGainControl:true, echoCancellation:true, noiseSuppression:true }
				// getUserMedia audio constraints: deviceId, echoCancellation, noiseSuppression, etc. Not guaranteed to take effect.
				// As microphone is shared globally, close previous before re-open with new config
				// More: https://developer.mozilla.org/en-US/docs/Web/API/MediaTrackConstraints

		//,disableEnvInFix:false internal param to disable input-loss compensation on device stutter

		//,takeoffEncodeChunk:NOOP // fn(chunkBytes) Take over encoder output in real-time encoding env; receives Uint8Array chunks. All chunks concatenated form full audio.
				// When provided, encoder won't store output internally; if real-time not supported, open will fail.
				// stop will return 0-byte blob since encoder holds no audio data.
				// Only mp3 currently supports real-time encoding.
	};

	for(var k in set){
		o[k]=set[k];
	};
	this.set=o;

	this._S=9;// stop sync lock; stop can prevent start during open
	this.Sync={O:9,C:9};// similar to Recorder.Sync but non-global, just to simplify logic
};
// Sync lock controlling competition for Stream; used to interrupt async open during close; prevent close if open changes to a new owner
Recorder.Sync={/*open*/O:9,/*close*/C:9};

Recorder.prototype=initFn.prototype={
	CLog:CLog

	// Where to store stream-related data; if sourceStream provided, store on instance; otherwise global
	,_streamStore:function(){
		if(this.set.sourceStream){
			return this;
		}else{
			return Recorder;
		}
	}

	// Open recording resource True(),False(msg,isUserNotAllow); must call close; async; typically open then close; repeatable
	,open:function(True,False){
		var This=this,streamStore=This._streamStore();
		True=True||NOOP;
		var failCall=function(errMsg,isUserNotAllow){
			isUserNotAllow=!!isUserNotAllow;
			This.CLog("record open failed: "+errMsg+",isUserNotAllow:"+isUserNotAllow,1);
			False&&False(errMsg,isUserNotAllow);
		};

		var ok=function(){
			This.CLog("open ok id:"+This.id);
			True();

				This._SO=0;// release stop's prevention of start during open
		};


		// Sync lock
		var Lock=streamStore.Sync;
		var lockOpen=++Lock.O,lockClose=Lock.C;
		This._O=This._O_=lockOpen;// Remember current open; prevent close if changed
		This._SO=This._S;// Remember stop during open; cannot proceed to start if stopped mid-way
		var lockFail=function(){
			// allow multiple opens but not any close; or self has closed
			if(lockClose!=Lock.C || !This._O){
				var err="open canceled";
				if(lockOpen==Lock.O){
					// no new open; close has been called to cancel; make last close take effect
					This.close();
				}else{
					err="open interrupted";
				};
				failCall(err);
				return true;
			};
		};

		// Environment check
		var checkMsg=This.envCheck({envName:"H5",canProcess:true});
		if(checkMsg){
			failCall("Cannot record: "+checkMsg);
			return;
		};


		//*********** Provided MediaStream directly ************
		if(This.set.sourceStream){
			if(!Recorder.GetContext()){
				failCall("This browser does not support recording from provided stream");
				return;
			};

			Disconnect(streamStore);// If opened before, disconnect first
			This.Stream=This.set.sourceStream;
			This.Stream._call={};

			try{
				Connect(streamStore);
			}catch(e){
				failCall("Open recording from stream failed: "+e.message);
				return;
			}
			ok();
			return;
		};


		//*********** Open microphone to get global audio stream ************
		var codeFail=function(code,msg){
			try{// Check cross-origin first
				window.top.a;
			}catch(e){
				failCall('No permission to record (cross-origin; try adding microphone policy to iframe, e.g., allow="camera;microphone")');
				return;
			};

			if(/Permission|Allow/i.test(code)){
				failCall("User denied microphone permission",true);
			}else if(window.isSecureContext===false){
				failCall("Browser blocks recording on insecure pages; use HTTPS");
			}else if(/Found/i.test(code)){// Possibly no device due to insecure context
				failCall(msg+", no available microphone");
			}else{
				failCall(msg);
			};
		};


		// If already open and valid, do not reopen
		if(Recorder.IsOpen()){
			ok();
			return;
		};
		if(!Recorder.Support()){
			codeFail("","This browser does not support recording");
			return;
		};

		// Request permission; most browsers will prompt if not previously granted
		var f1=function(stream){
			// https://github.com/xiangyuecn/Recorder/issues/14 Sometimes track.readyState!="live" shortly after callback; delay to ensure true async; no impact on normal browsers
			setTimeout(function(){
				stream._call={};
				var oldStream=Recorder.Stream;
				if(oldStream){
				Disconnect(); // Disconnect existing; unfinished Connect will auto-terminate
					stream._call=oldStream._call;
				};
				Recorder.Stream=stream;
				if(lockFail())return;

				if(Recorder.IsOpen()){
					if(oldStream)This.CLog("Detected multiple simultaneous open calls",1);

					Connect(streamStore,1);
					ok();
				}else{
					failCall("Recording invalid: no audio stream");
				};
			},100);
		};
		var f2=function(e){
			var code=e.name||e.message||e.code+":"+e;
			This.CLog("Error requesting microphone permission",1,e);

			codeFail(code,"Cannot record: "+code);
		};

		var trackSet={
			noiseSuppression:false // Default disable NR
			,echoCancellation:false // Echo cancellation
		};
		var trackSet2=This.set.audioTrackSet;
		for(var k in trackSet2)trackSet[k]=trackSet2[k];
		trackSet.sampleRate=Recorder.Ctx.sampleRate;// must specify sampleRate to avoid 16k MediaRecorder on mobile

		try{
			var pro=Recorder.Scope[getUserMediaTxt]({audio:trackSet},f1,f2);
		}catch(e){// if cannot set trackSet, fallback
			This.CLog(getUserMediaTxt,3,e);
			pro=Recorder.Scope[getUserMediaTxt]({audio:true},f1,f2);
		};
		if(pro&&pro.then){
			pro.then(f1)[CatchTxt](f2); // keep catch keyword as string for minification
		};
	}
	// Close and release recording resources
	,close:function(call){
		call=call||NOOP;

		var This=this,streamStore=This._streamStore();
		This._stop();

		var Lock=streamStore.Sync;
		This._O=0;
		if(This._O_!=Lock.O){
			// Stream ownership given to new object; ignore close here
			This.CLog("close ignored (multiple open; only the last truly closes)",3);
			call();
			return;
		};
		Lock.C++;// acquire control

		Disconnect(streamStore);

		This.CLog("close");
		call();
	}





	/* Mock a segment of recording for later encoding; provide pcm data and its sample rate */
	,mock:function(pcmData,pcmSampleRate){
		var This=this;
		This._stop();// clear existing resources

		This.isMock=1;
		This.mockEnvInfo=null;
		This.buffers=[pcmData];
		This.recSize=pcmData.length;
		This[srcSampleRateTxt]=pcmSampleRate;
		return This;
	}
	,envCheck:function(envInfo){// Environment availability check; return errMsg: "" ok or reason
		//envInfo={envName:"H5",canProcess:true}
		var errMsg,This=this,set=This.set;

		// Check CPU endianness; reject rare big-endian since untested
		var tag="CPU_BE";
		if(!errMsg && !Recorder[tag] && window.Int8Array && !new Int8Array(new Int32Array([1]).buffer)[0]){
			Traffic(tag); // send beacon if traffic enabled
			errMsg="Unsupported "+tag+" architecture";
		};

		// Check whether encoder config is usable in environment
		if(!errMsg){
			var type=set.type;
			if(This[type+"_envCheck"]){// encoder implemented env check
				errMsg=This[type+"_envCheck"](envInfo,set);
			}else{// manual check when not implemented
				if(set.takeoffEncodeChunk){
					errMsg=type+" type "+(This[type]?"":"(encoder not loaded)")+" does not support takeoffEncodeChunk";
				};
			};
		};

		return errMsg||"";
	}
	,envStart:function(mockEnvInfo,sampleRate){// Start for platform env
		var This=this,set=This.set;
		This.isMock=mockEnvInfo?1:0;// Non-H5 env needs mock and env info
		This.mockEnvInfo=mockEnvInfo;
		This.buffers=[];// data buffer
		This.recSize=0;// data size

		This.envInLast=0;// last envIn time
		This.envInFirst=0;// first envIn record time
		This.envInFix=0;// total compensation time
		This.envInFixTs=[];// compensation counters

		// engineCtx needs final sample rate predetermined
		var setSr=set[sampleRateTxt];
		if(setSr>sampleRate){
			set[sampleRateTxt]=sampleRate;
		}else{ setSr=0 }
		This[srcSampleRateTxt]=sampleRate;
		This.CLog(srcSampleRateTxt+": "+sampleRate+" set."+sampleRateTxt+": "+set[sampleRateTxt]+(setSr?" ignore "+setSr:""), setSr?3:0);

		This.engineCtx=0;
		// This type may support real-time encode (Worker)
		if(This[set.type+"_start"]){
			var engineCtx=This.engineCtx=This[set.type+"_start"](set);
			if(engineCtx){
				engineCtx.pcmDatas=[];
				engineCtx.pcmSize=0;
			};
		};
	}
	,envResume:function(){// Resume recording (platform-agnostic)
		// Reset counters
		this.envInFixTs=[];
	}
	,envIn:function(pcm,sum){// Platform-agnostic PCM[Int16] input
		var This=this,set=This.set,engineCtx=This.engineCtx;
		var bufferSampleRate=This[srcSampleRateTxt];
		var size=pcm.length;
		var powerLevel=Recorder.PowerLevel(sum,size);

		var buffers=This.buffers;
		var bufferFirstIdx=buffers.length;// Previous buffers processed by onProcess; do not modify
		buffers.push(pcm);

		// Will be overridden with engineCtx; keep a copy
		var buffersThis=buffers;
		var bufferFirstIdxThis=bufferFirstIdx;

		// Compensation for stutter: when device is laggy, H5 may receive less data causing playback speedup; ensure duration doesn't shrink, though audio quality can't be fixed. Uses input timing to detect need to insert silent frames. Requires >=6 inputs or >1s to start. If loss >1/3 within sliding window, compensate.
		var now=Date.now();
		var pcmTime=Math.round(size/bufferSampleRate*1000);
		This.envInLast=now;
		if(This.buffers.length==1){// Record time of first input
			This.envInFirst=now-pcmTime;
		};
		var envInFixTs=This.envInFixTs;
		envInFixTs.splice(0,0,{t:now,d:pcmTime});
		// Keep 3s sliding window; pauses >3s are not compensated
		var tsInStart=now,tsPcm=0;
		for(var i=0;i<envInFixTs.length;i++){
			var o=envInFixTs[i];
			if(now-o.t>3000){
				envInFixTs.length=i;
				break;
			};
			tsInStart=o.t;
			tsPcm+=o.d;
		};
		// Once enough data, detect if compensation is needed
		var tsInPrev=envInFixTs[1];
		var tsIn=now-tsInStart;
		var lost=tsIn-tsPcm;
		if( lost>tsIn/3 && (tsInPrev&&tsIn>1000 || envInFixTs.length>=6) ){
			// Excessive loss; compensate
			var addTime=now-tsInPrev.t-pcmTime;// ms lost since last input
			if(addTime>pcmTime/5){// loss > 1/5 of this frame
				var fixOpen=!set.disableEnvInFix;
				This.CLog("["+now+"]"+(fixOpen?"":"no ")+"compensate "+addTime+"ms",3);
				This.envInFix+=addTime;

				// Compensate with silence
				if(fixOpen){
					var addPcm=new Int16Array(addTime*bufferSampleRate/1000);
					size+=addPcm.length;
					buffers.push(addPcm);
				};
			};
		};


		var sizeOld=This.recSize,addSize=size;
		var bufferSize=sizeOld+addSize;
		This.recSize=bufferSize;// adjust after onProcess; new data may change


		// If supported, enable real-time encoding
		if(engineCtx){
			// Resample to set's sample rate
			var chunkInfo=Recorder.SampleData(buffers,bufferSampleRate,set[sampleRateTxt],engineCtx.chunkInfo);
			engineCtx.chunkInfo=chunkInfo;

			sizeOld=engineCtx.pcmSize;
			addSize=chunkInfo.data.length;
			bufferSize=sizeOld+addSize;
			engineCtx.pcmSize=bufferSize;// Will adjust after onProcess as new data may change

			buffers=engineCtx.pcmDatas;
			bufferFirstIdx=buffers.length;
			buffers.push(chunkInfo.data);
			bufferSampleRate=chunkInfo[sampleRateTxt];
		};

		var duration=Math.round(bufferSize/bufferSampleRate*1000);
		var bufferNextIdx=buffers.length;
		var bufferNextIdxThis=buffersThis.length;

		// Allow async processing of buffer data
		var asyncEnd=function(){
			// Recompute size; async already subtracted; sync needs to subtract then recompute
			var num=asyncBegin?0:-addSize;
			var hasClear=buffers[0]==null;
			for(var i=bufferFirstIdx;i<bufferNextIdx;i++){
				var buffer=buffers[i];
				if(buffer==null){// already freed, e.g., long-time streaming
					hasClear=1;
				}else{
					num+=buffer.length;

					// Push to background real-time encoding
					if(engineCtx&&buffer.length){
						This[set.type+"_encode"](engineCtx,buffer);
					};
				};
			};

			// Sync clean This.buffers; fully clear buffersThis which is unused
			if(hasClear && engineCtx){
				var i=bufferFirstIdxThis;
				if(buffersThis[0]){
					i=0;
				};
				for(;i<bufferNextIdxThis;i++){
					buffersThis[i]=null;
				};
			};

			// Update size; if async clear occurred, add back; sync no-op
			if(hasClear){
				num=asyncBegin?addSize:0;

				buffers[0]=null;// fully cleared
			};
			if(engineCtx){
				engineCtx.pcmSize+=num;
			}else{
				This.recSize+=num;
			};
		};
		// Real-time callback to process data; may modify/replace newly added data since last callback; do not modify earlier segments; can set inner arrays to empty
		var asyncBegin=0,procTxt="rec.set.onProcess";
		try{
			asyncBegin=set.onProcess(buffers,powerLevel,duration,bufferSampleRate,bufferFirstIdx,asyncEnd);
		}catch(e){
				// don't use CLog here to avoid duplicate console logs
			console.error(procTxt+" callback error is not allowed; ensure no exceptions",e);
		};

		var slowT=Date.now()-now;
		if(slowT>10 && This.envInFirst-now>1000){ // start monitoring performance after 1s
			This.CLog(procTxt+" low performance, took "+slowT+"ms",3);
		};

		if(asyncBegin===true){
			// Async mode enabled; onProcess took over new buffers; clear immediately
			var hasClear=0;
			for(var i=bufferFirstIdx;i<bufferNextIdx;i++){
				if(buffers[i]==null){// Already freed, e.g., long streaming; illegal when enabling async now
					hasClear=1;
				}else{
					buffers[i]=new Int16Array(0);
				};
			};

			if(hasClear){
				This.CLog("Cannot clear buffers before entering async",3);
			}else{
					// Restore size; after async ends, only modified sizes are counted; add back if clear occurred
				if(engineCtx){
					engineCtx.pcmSize-=addSize;
				}else{
					This.recSize-=addSize;
				};
			};
		}else{
			asyncEnd();
		};
	}




	// Start recording; must call open first; if not opened and forced to call, internal error will be silent; stop will yield error
	,start:function(){
		var This=this,ctx=Recorder.Ctx;

		var isOpen=1;
		if(This.set.sourceStream){// provided stream; only check if open was called
			if(!This.Stream){
				isOpen=0;
			}
		}else if(!Recorder.IsOpen()){// Check global mic open and valid
			isOpen=0;
		};
		if(!isOpen){
			This.CLog("not opened",1);
			return;
		};
		This.CLog("start recording");

		This._stop();
		This.state=3;// 0=idle 1=recording 2=paused 3=waiting ctx activation
		This.envStart(null, ctx[sampleRateTxt]);

		// check whether stop was called during open
		if(This._SO&&This._SO+1!=This._S){// previously called _stop once
			// stop called before open completed; terminate start; avoid this scenario
			This.CLog("start interrupted",3);
			return;
		};
		This._SO=0;

		var end=function(){
			if(This.state==3){
				This.state=1;
				This.resume();
			}
		};
		if(ctx.state=="suspended"){
			var tag="AudioContext resume: ";
			This.CLog(tag+"wait...");
			ctx.resume().then(function(){
				This.CLog(tag+ctx.state);
				end();
			})[CatchTxt](function(e){ // Rare; might not affect recording
				This.CLog(tag+ctx.state+" possibly unable to record: "+e.message,1,e);
				end();
			});
		}else{
			end();
		};
	}
	/* Pause recording */
	,pause:function(){
		var This=this;
		if(This.state){
			This.state=2;
			This.CLog("pause");
			delete This._streamStore().Stream._call[This.id];
		};
	}
	/* Resume recording */
	,resume:function(){
		var This=this;
		if(This.state){
			This.state=1;
			This.CLog("resume");
			This.envResume();

			var stream=This._streamStore().Stream;
			stream._call[This.id]=function(pcm,sum){
				if(This.state==1){
					This.envIn(pcm,sum);
				};
			};
		ConnAlive(stream);// AudioWorklet runs only after ctx activation
		};
	}




	,_stop:function(keepEngine){
		var This=this,set=This.set;
		if(!This.isMock){
			This._S++;
		};
		if(This.state){
			This.pause();
			This.state=0;
		};
		if(!keepEngine && This[set.type+"_stop"]){
			This[set.type+"_stop"](This.engineCtx);
			This.engineCtx=0;
		};
	}
	/*
    End recording and return blob
        True(blob,duration) blob: audio/mp3|wav
                            duration: ms
        False(msg)
        autoClose:false optional; whether to auto close
	*/
	,stop:function(True,False,autoClose){
		var This=this,set=This.set,t1;
		var envInMS=This.envInLast-This.envInFirst, envInLen=envInMS&&This.buffers.length; // may not have started
		This.CLog("stop delta from start "+(envInMS?envInMS+"ms compensate "+This.envInFix+"ms"+" envIn:"+envInLen+" fps:"+(envInLen/envInMS*1000).toFixed(1):"-"));

		var end=function(){
			This._stop();// fully stop engineCtx
			if(autoClose){
				This.close();
			};
		};
		var err=function(msg){
			This.CLog("stop failed: "+msg,1);
			False&&False(msg);
			end();
		};
		var ok=function(blob,duration){
			This.CLog("stop done encode took "+(Date.now()-t1)+"ms duration "+duration+"ms size "+blob.size+"b");
			if(set.takeoffEncodeChunk){// blob length 0 when taken over
				This.CLog("takeoffEncodeChunk enabled; stop returns 0-length blob",3);
			}else if(blob.size<Math.max(100,duration/2)){// 1s < 0.5k?
				err("generated "+set.type+" invalid");
				return;
			};
			True&&True(blob,duration);
			end();
		};
		if(!This.isMock){
			var isCtxWait=This.state==3;
			if(!This.state || isCtxWait){
				err("not started"+(isCtxWait?", AudioContext not running due to no user interaction before start":""));
				return;
			};
			This._stop(true);
		};
		var size=This.recSize;
		if(!size){
			err("no audio collected");
			return;
		};
		if(!This.buffers[0]){
			err("audio buffers freed");
			return;
		};
		if(!This[set.type]){
			err("encoder not loaded: "+set.type);
			return;
		};

		// Env check for mock, since open already checked
		if(This.isMock){
			var checkMsg=This.envCheck(This.mockEnvInfo||{envName:"mock",canProcess:false});// mock without env info has no onProcess callback
			if(checkMsg){
				err("recording error: "+checkMsg);
				return;
			};
		};

		// If supported, complete real-time encoding
		var engineCtx=This.engineCtx;
		if(This[set.type+"_complete"]&&engineCtx){
			var duration=Math.round(engineCtx.pcmSize/set[sampleRateTxt]*1000);// Slight discrepancy due to continuous resampling precision

			t1=Date.now();
			This[set.type+"_complete"](engineCtx,function(blob){
				ok(blob,duration);
			},err);
			return;
		};

		// UI-thread encoding with resampling
		t1=Date.now();
		var chunk=Recorder.SampleData(This.buffers,This[srcSampleRateTxt],set[sampleRateTxt]);

		set[sampleRateTxt]=chunk[sampleRateTxt];
		var res=chunk.data;
		var duration=Math.round(res.length/set[sampleRateTxt]*1000);

		This.CLog("resample "+size+"->"+res.length+" took:"+(Date.now()-t1)+"ms");

		setTimeout(function(){
			t1=Date.now();
			This[set.type](res,function(blob){
				ok(blob,duration);
			},function(msg){
				err(msg);
			});
		});
	}

};

if(window[RecTxt]){
	CLog("Duplicate include "+RecTxt,3);
	window[RecTxt].Destroy();
};
window[RecTxt]=Recorder;




//======= Extract pcm data from WebM byte stream; return Float32Array on success, null||-1 on failure =====
var WebM_Extract=function(inBytes, scope){
	if(!scope.pos){
		scope.pos=[0]; scope.tracks={}; scope.bytes=[];
	};
	var tracks=scope.tracks, position=[scope.pos[0]];
	var endPos=function(){ scope.pos[0]=position[0] };

	var sBL=scope.bytes.length;
	var bytes=new Uint8Array(sBL+inBytes.length);
	bytes.set(scope.bytes); bytes.set(inBytes,sBL);
	scope.bytes=bytes;

	// First read header and Track info
	if(!scope._ht){
		readMatroskaVInt(bytes, position);//EBML Header
		readMatroskaBlock(bytes, position);// skip EBML Header content
		if(!BytesEq(readMatroskaVInt(bytes, position), [0x18,0x53,0x80,0x67])){
			return;// Segment not recognized
		}
		readMatroskaVInt(bytes, position);// skip Segment length value
		while(position[0]<bytes.length){
			var eid0=readMatroskaVInt(bytes, position);
			var bytes0=readMatroskaBlock(bytes, position);
			var pos0=[0],audioIdx=0;
			if(!bytes0)return;// incomplete data, wait for buffer
			// Track data; iterate TrackEntry
			if(BytesEq(eid0, [0x16,0x54,0xAE,0x6B])){
				while(pos0[0]<bytes0.length){
					var eid1=readMatroskaVInt(bytes0, pos0);
					var bytes1=readMatroskaBlock(bytes0, pos0);
					var pos1=[0],track={channels:0,sampleRate:0};
					if(BytesEq(eid1, [0xAE])){// TrackEntry
						while(pos1[0]<bytes1.length){
							var eid2=readMatroskaVInt(bytes1, pos1);
							var bytes2=readMatroskaBlock(bytes1, pos1);
							var pos2=[0];
							if(BytesEq(eid2, [0xD7])){// Track Number
								var val=BytesInt(bytes2);
								track.number=val;
								tracks[val]=track;
							}else if(BytesEq(eid2, [0x83])){// Track Type
								var val=BytesInt(bytes2);
								if(val==1) track.type="video";
								else if(val==2) {
									track.type="audio";
									if(!audioIdx) scope.track0=track;
									track.idx=audioIdx++;
								}else track.type="Type-"+val;
							}else if(BytesEq(eid2, [0x86])){// Track Codec
								var str="";
								for(var i=0;i<bytes2.length;i++){
									str+=String.fromCharCode(bytes2[i]);
								}
								track.codec=str;
							}else if(BytesEq(eid2, [0xE1])){
								while(pos2[0]<bytes2.length){// iterate Audio attributes
									var eid3=readMatroskaVInt(bytes2, pos2);
									var bytes3=readMatroskaBlock(bytes2, pos2);
									// sample rate, bit depth, channels
									if(BytesEq(eid3, [0xB5])){
										var val=0,arr=new Uint8Array(bytes3.reverse()).buffer;
										if(bytes3.length==4) val=new Float32Array(arr)[0];
										else if(bytes3.length==8) val=new Float64Array(arr)[0];
										else CLog("WebM Track !Float",1,bytes3);
										track[sampleRateTxt]=Math.round(val);
									}else if(BytesEq(eid3, [0x62,0x64])) track.bitDepth=BytesInt(bytes3);
									else if(BytesEq(eid3, [0x9F])) track.channels=BytesInt(bytes3);
								}
							}
						}
					}
				};
				scope._ht=1;
				CLog("WebM Tracks",tracks);
				endPos();
				break;
			}
		}
	}

// Validate audio parameters; if not as expected, refuse to process
	var track0=scope.track0;
	if(!track0)return;
	if(track0.bitDepth==16 && /FLOAT/i.test(track0.codec)){
	track0.bitDepth=32; // chrome v66 actually float
	CLog("WebM change 16->32 bit",3);
	}
	if(track0[sampleRateTxt]!=scope[sampleRateTxt] || track0.bitDepth!=32 || track0.channels<1 || !/(\b|_)PCM\b/i.test(track0.codec)){
	scope.bytes=[];// unexpected format; clear buffer
	if(!scope.bad)CLog("WebM Track unexpected",3,scope);
		scope.bad=1;
		return -1;
	}

// Iterate SimpleBlock in Cluster
	var datas=[],dataLen=0;
	while(position[0]<bytes.length){
		var eid1=readMatroskaVInt(bytes, position);
		var bytes1=readMatroskaBlock(bytes, position);
	if(!bytes1)break;// incomplete data, wait
	if(BytesEq(eid1, [0xA3])){// SimpleBlock complete data
			var trackNo=bytes1[0]&0xf;
			var track=tracks[trackNo];
		if(!track){// should not happen; data error?
				CLog("WebM !Track"+trackNo,1,tracks);
			}else if(track.idx===0){
				var u8arr=new Uint8Array(bytes1.length-4);
				for(var i=4;i<bytes1.length;i++){
					u8arr[i-4]=bytes1[i];
				}
				datas.push(u8arr); dataLen+=u8arr.length;
			}
		}
		endPos();
	}

	if(dataLen){
		var more=new Uint8Array(bytes.length-scope.pos[0]);
		more.set(bytes.subarray(scope.pos[0]));
	scope.bytes=more; // clear already-read buffer
		scope.pos[0]=0;

	var u8arr=new Uint8Array(dataLen); // obtained audio data
		for(var i=0,i2=0;i<datas.length;i++){
			u8arr.set(datas[i],i2);
			i2+=datas[i].length;
		}
		var arr=new Float32Array(u8arr.buffer);

	if(track0.channels>1){// multi-channel; extract single channel
			var arr2=[];
			for(var i=0;i<arr.length;){
				arr2.push(arr[i]);
				i+=track0.channels;
			}
			arr=new Float32Array(arr2);
		};
		return arr;
	}
};
// Whether two byte arrays are equal
var BytesEq=function(bytes1,bytes2){
	if(!bytes1 || bytes1.length!=bytes2.length) return false;
	if(bytes1.length==1) return bytes1[0]==bytes2[0];
	for(var i=0;i<bytes1.length;i++){
		if(bytes1[i]!=bytes2[i]) return false;
	}
	return true;
};
// Convert big-endian byte array to int
var BytesInt=function(bytes){
	var s="";// 0-8 bytes; bit ops only support 4 bytes
	for(var i=0;i<bytes.length;i++){var n=bytes[i];s+=(n<16?"0":"")+n.toString(16)};
	return parseInt(s,16)||0;
};
// Read a variable-length integer byte array
var readMatroskaVInt=function(arr,pos,trim){
	var i=pos[0];
	if(i>=arr.length)return;
	var b0=arr[i],b2=("0000000"+b0.toString(2)).substr(-8);
	var m=/^(0*1)(\d*)$/.exec(b2);
	if(!m)return;
	var len=m[1].length, val=[];
	if(i+len>arr.length)return;
	for(var i2=0;i2<len;i2++){ val[i2]=arr[i]; i++; }
	if(trim) val[0]=parseInt(m[2]||'0',2);
	pos[0]=i;
	return val;
};
// Read a block with embedded length
var readMatroskaBlock=function(arr,pos){
	var lenVal=readMatroskaVInt(arr,pos,1);
	if(!lenVal)return;
	var len=BytesInt(lenVal);
	var i=pos[0], val=[];
	if(len<0x7FFFFFFF){ // very large means no length
		if(i+len>arr.length)return;
		for(var i2=0;i2<len;i2++){ val[i2]=arr[i]; i++; }
	}
	pos[0]=i;
	return val;
};
//===== End WebM read =====




// 1-pixel image url for traffic statistics; set empty to disable
Recorder.TrafficImgUrl="//ia.51.la/go1?id=20469973&pvFlag=1";
var Traffic=Recorder.Traffic=function(report){
	report=report?"/"+RecTxt+"/Report/"+report:"";
	var imgUrl=Recorder.TrafficImgUrl;
	if(imgUrl){
		var data=Recorder.Traffic;
		var m=/^(https?:..[^\/#]*\/?)[^#]*/i.exec(location.href)||[];
		var host=(m[1]||"http://file/");
		var idf=(m[0]||host)+report;

		if(imgUrl.indexOf("//")==0){
			// Prepend http/https for protocol-relative url; file protocol needs prefix
			if(/^https:/i.test(idf)){
				imgUrl="https:"+imgUrl;
			}else{
				imgUrl="http:"+imgUrl;
			};
		};
		if(report){
			imgUrl=imgUrl+"&cu="+encodeURIComponent(host+report);
		};

		if(!data[idf]){
			data[idf]=1;

			var img=new Image();
			img.src=imgUrl;
			CLog("Traffic Analysis Image: "+(report||RecTxt+".TrafficImgUrl="+Recorder.TrafficImgUrl));
		};
	};
};

}));
