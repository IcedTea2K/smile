// get DOM elements
iceConnectionLog = document.getElementById('ice-connection-state'),
iceGatheringLog = document.getElementById('ice-gathering-state'),
signalingLog = document.getElementById('signaling-state');

// peer connection
let pc = null;

// data channel
let dc = null, dcInterval = null;

function createPeerConnection() {
  let config = {
    sdpSemantics: 'unified-plan'
  };

  if (document.getElementById('use-stun').checked) {
    config.iceServers = [{ urls: ['stun:stun.l.google.com:19302'] }];
  }

  pc = new RTCPeerConnection(config);

  // register some listeners to help debugging
  pc.addEventListener('icegatheringstatechange', function () {
    iceGatheringLog.textContent += ' -> ' + pc.iceGatheringState;
  }, false);
  iceGatheringLog.textContent = pc.iceGatheringState;

  pc.addEventListener('iceconnectionstatechange', function () {
    iceConnectionLog.textContent += ' -> ' + pc.iceConnectionState;
  }, false);
  iceConnectionLog.textContent = pc.iceConnectionState;

  pc.addEventListener('signalingstatechange', function () {
    signalingLog.textContent += ' -> ' + pc.signalingState;
  }, false);
  signalingLog.textContent = pc.signalingState;

  // connect video
  pc.addEventListener('track', function (evt) {
    if (evt.track.kind == 'video')
      document.getElementById('video').srcObject = evt.streams[0];
  });

  pc.addEventListener('datachannel', function (evt) {
    console.log("datas")
    const dataChannel = evt.channel;
    dataChannel.onmessage = function(evt) {
      const message = evt.data;
      console.log(message)
    };
  })

  return pc;
}

function negotiate() {
  return pc.createOffer().then(function (offer) {
    return pc.setLocalDescription(offer);
  }).then(function () {
    // wait for ICE gathering to complete
    return new Promise(function (resolve) {
      if (pc.iceGatheringState === 'complete') {
        resolve();
      } else {
        function checkState() {
          if (pc.iceGatheringState === 'complete') {
            pc.removeEventListener('icegatheringstatechange', checkState);
            resolve();
          }
        }
        pc.addEventListener('icegatheringstatechange', checkState);
      }
    });
  }).then(function () {
    var offer = pc.localDescription;
    
    offer.sdp = sdpFilterCodec('video', "H264/90000", offer.sdp);

    document.getElementById('offer-sdp').textContent = offer.sdp;
    return fetch('http://localhost:8001/offer', {
      body: JSON.stringify({
        sdp: offer.sdp,
        type: offer.type
      }),
      headers: {
        'Content-Type': 'application/json'
      },
      method: 'POST'
    });
  }).then(function (response) {
    return response.json();
  }).then(function (answer) {
    document.getElementById('answer-sdp').textContent = answer.sdp;
    return pc.setRemoteDescription(answer);
  }).catch(function (e) {
    alert(e);
  });
}

function start() {
  document.getElementById('start').style.display = 'none';

  pc = createPeerConnection();

  dc = pc.createDataChannel('emotion');
  dc.onclose = function () {
    console.log("Datachannel closed");
    document.getElementById('emotion-container').style.display = 'none';
  };
  dc.onopen = function () {
    console.log("Datachannel opened");
    document.getElementById('emotion-container').style.display = 'block';
  };
  dc.onmessage = function (evt) {
    const predictions = JSON.parse(evt.data);
    const neutral = predictions.neutral ? `neutral: ${Math.round(predictions.neutral*100)}\n` : '';
    const sad = predictions.sad ? `sad: ${Math.round(predictions.sad * 100)}\n` : '';
    const angry = predictions.angry ? `angry: ${Math.round(predictions.angry * 100)}\n` : '';

    const prediction = predictions?.sad * 100 > 35 ? "sad" : "not sad";
    document.getElementById('emotion').innerText = neutral + sad + angry + prediction;
  };

  var constraints = {
    audio: false,
    video: {
      width: 1280,
      height: 720
    }
  };

  document.getElementById('media').style.display = 'block';
  navigator.mediaDevices.getUserMedia(constraints).then(function (stream) {
    stream.getTracks().forEach(function (track) {
      pc.addTrack(track, stream);
    });
    return negotiate();
  }, function (err) {
    alert('Could not acquire media: ' + err);
  });

  document.getElementById('stop').style.display = 'inline-block';
}

function stop() {
  document.getElementById('stop').style.display = 'none';

  // close data channel
  if (dc) {
    dc.close();
  }

  // close transceivers
  if (pc.getTransceivers) {
    pc.getTransceivers().forEach(function (transceiver) {
      if (transceiver.stop) {
        transceiver.stop();
      }
    });
  }

  // close local audio / video
  pc.getSenders().forEach(function (sender) {
    sender.track.stop();
  });

  // close peer connection
  setTimeout(function () {
    pc.close();
  }, 500);
}

function sdpFilterCodec(kind, codec, realSdp) {
  var allowed = []
  var rtxRegex = new RegExp('a=fmtp:(\\d+) apt=(\\d+)\r$');
  var codecRegex = new RegExp('a=rtpmap:([0-9]+) ' + escapeRegExp(codec))
  var videoRegex = new RegExp('(m=' + kind + ' .*?)( ([0-9]+))*\\s*$')

  var lines = realSdp.split('\n');

  var isKind = false;
  for (var i = 0; i < lines.length; i++) {
    if (lines[i].startsWith('m=' + kind + ' ')) {
      isKind = true;
    } else if (lines[i].startsWith('m=')) {
      isKind = false;
    }

    if (isKind) {
      var match = lines[i].match(codecRegex);
      if (match) {
        allowed.push(parseInt(match[1]));
      }

      match = lines[i].match(rtxRegex);
      if (match && allowed.includes(parseInt(match[2]))) {
        allowed.push(parseInt(match[1]));
      }
    }
  }

  var skipRegex = 'a=(fmtp|rtcp-fb|rtpmap):([0-9]+)';
  var sdp = '';

  isKind = false;
  for (var i = 0; i < lines.length; i++) {
    if (lines[i].startsWith('m=' + kind + ' ')) {
      isKind = true;
    } else if (lines[i].startsWith('m=')) {
      isKind = false;
    }

    if (isKind) {
      var skipMatch = lines[i].match(skipRegex);
      if (skipMatch && !allowed.includes(parseInt(skipMatch[2]))) {
        continue;
      } else if (lines[i].match(videoRegex)) {
        sdp += lines[i].replace(videoRegex, '$1 ' + allowed.join(' ')) + '\n';
      } else {
        sdp += lines[i] + '\n';
      }
    } else {
      sdp += lines[i] + '\n';
    }
  }

  return sdp;
}

function escapeRegExp(string) {
  return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); // $& means the whole matched string
}