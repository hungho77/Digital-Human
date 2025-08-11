var pc = null;

function negotiate() {
    console.log('Starting negotiation...');
    pc.addTransceiver('video', { direction: 'recvonly' });
    pc.addTransceiver('audio', { direction: 'recvonly' });
    console.log('Added transceivers');
    
    return pc.createOffer().then((offer) => {
        console.log('Created offer:', offer);
        return pc.setLocalDescription(offer);
    }).then(() => {
        // wait for ICE gathering to complete
        return new Promise((resolve) => {
            if (pc.iceGatheringState === 'complete') {
                resolve();
            } else {
                const checkState = () => {
                    if (pc.iceGatheringState === 'complete') {
                        pc.removeEventListener('icegatheringstatechange', checkState);
                        resolve();
                    }
                };
                pc.addEventListener('icegatheringstatechange', checkState);
            }
        });
    }).then(() => {
        var offer = pc.localDescription;
        console.log('Sending offer to server:', offer);
        return fetch('/offer', {
            body: JSON.stringify({
                sdp: offer.sdp,
                type: offer.type,
            }),
            headers: {
                'Content-Type': 'application/json'
            },
            method: 'POST'
        });
    }).then((response) => {
        console.log('Received response from server:', response);
        if (!response.ok) {
            throw new Error(`Server responded with ${response.status}: ${response.statusText}`);
        }
        return response.json();
    }).then((answer) => {
        console.log('Received answer from server:', answer);
        document.getElementById('sessionid').value = answer.sessionid;
        console.log('Setting remote description...');
        return pc.setRemoteDescription(answer);
    }).catch((e) => {
        console.error('WebRTC negotiation failed:', e);
        alert('Connection failed: ' + e.message);
    });
}

function start() {
    console.log('Starting WebRTC connection...');
    
    var config = {
        sdpSemantics: 'unified-plan'
    };

    if (document.getElementById('use-stun').checked) {
        config.iceServers = [{ urls: ['stun:stun.l.google.com:19302'] }];
        console.log('Using STUN server:', config.iceServers);
    } else {
        console.log('STUN server disabled');
    }

    pc = new RTCPeerConnection(config);
    console.log('RTCPeerConnection created with config:', config);
    
    // Add comprehensive connection monitoring
    pc.addEventListener('connectionstatechange', () => {
        console.log('Connection state changed to:', pc.connectionState);
        if (pc.connectionState === 'failed') {
            console.error('WebRTC connection failed!');
        }
    });
    
    pc.addEventListener('iceconnectionstatechange', () => {
        console.log('ICE connection state changed to:', pc.iceConnectionState);
        if (pc.iceConnectionState === 'failed') {
            console.error('ICE connection failed!');
        }
    });
    
    pc.addEventListener('icegatheringstatechange', () => {
        console.log('ICE gathering state:', pc.iceGatheringState);
    });

    // connect audio / video
    pc.addEventListener('track', (evt) => {
        console.log('Received track:', evt.track.kind, evt.track);
        if (evt.track.kind == 'video') {
            const video = document.getElementById('video');
            video.srcObject = evt.streams[0];
            console.log('Set video stream:', evt.streams[0]);
            
            // Handle autoplay issues
            video.play().catch(e => {
                console.log('Video autoplay failed, user interaction required:', e);
                // Add play button or click handler if needed
            });
        } else {
            const audio = document.getElementById('audio');
            if (audio) {
                audio.srcObject = evt.streams[0];
                console.log('Set audio stream:', evt.streams[0]);
            } else {
                console.error('Audio element not found!');
            }
        }
    });

    document.getElementById('start').style.display = 'none';
    console.log('Hidden start button, starting negotiation...');
    negotiate().then(() => {
        console.log('Negotiation completed successfully');
    }).catch((e) => {
        console.error('Negotiation failed:', e);
        // Show start button again if negotiation fails
        document.getElementById('start').style.display = 'inline-block';
        document.getElementById('stop').style.display = 'none';
    });
    document.getElementById('stop').style.display = 'inline-block';
    console.log('Start function completed');
}

function stop() {
    document.getElementById('stop').style.display = 'none';

    // close peer connection
    setTimeout(() => {
        pc.close();
    }, 500);
}

window.onunload = function(event) {
    // Execute the operations you want here
    setTimeout(() => {
        pc.close();
    }, 500);
};

window.onbeforeunload = function (e) {
        setTimeout(() => {
                pc.close();
            }, 500);
        e = e || window.event
        // Compatible with IE8 and Firefox versions before 4
        if (e) {
          e.returnValue = 'Close prompt'
        }
        // Chrome, Safari, Firefox 4+, Opera 12+ , IE 9+
        return 'Close prompt'
      }