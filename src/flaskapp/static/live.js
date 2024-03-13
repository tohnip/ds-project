//https://developer.mozilla.org/en-US/docs/Web/API/MediaStream_Recording_API
const displayMediaOptions = {
  video: {
    displaySurface: "browser",
  },
  audio: {
    suppressLocalAudioPlayback: false,
  },
  preferCurrentTab: false,
  selfBrowserSurface: "exclude",
  systemAudio: "include",
  surfaceSwitching: "include",
  monitorTypeSurfaces: "include",
};
let isStreaming = false
let recorder = null

async function getCDN(streamid){
    const response = await fetch("http://127.0.0.1:5000/get_cdn/"+streamid,{method:"GET"})
    const data = await response.json()
    return "http://"+data.server_address+":"+data.server_port
}


async function stream(){


  isStreaming = true
  let stream_title = document.getElementById("stream_title").value
  let formData = new FormData()
  formData.append('title',stream_title)
  const response = await fetch("http://127.0.0.1:5000/create_stream",{method:"POST",body:formData})
  const data = await response.json()
  let streamid = data.streamid
  let header
  let establishStreamData = new FormData()
  establishStreamData.append('streamid',streamid)
  establishStreamData.append('msg','Awaiting Data')
  const initcdn = await getCDN(streamid)
  //const establishStream = await fetch(initcdn,{method:"POST",body:establishStreamData})
  //const response2 = await fetch(initcdn,{method:"GET"});

  vidframe = document.getElementById("live");
  vidframe.crossOrigin = 'anonymous';
  const mediaSource = new MediaSource();
  vidframe.src = URL.createObjectURL(mediaSource)

  var queue = [];
  var buffer;

  mediaSource.addEventListener('sourceopen', function(e) {
    vidframe.play()
    .then(() => {
      console.log("video should be playing fine");
    })
    .catch(error => {
      console.log(error);
    });
  
    buffer = mediaSource.addSourceBuffer("video/webm; codecs=opus,vp8");
    buffer.addEventListener('update', function() {
      if (queue.length > 0 && !buffer.updating) {
        buffer.appendBuffer(queue.shift());
      }
    });
  }, false);
  
  const socket = io(initcdn);
  console.log(socket);

  socket.emit("register_new_stream", {"streamid": streamid});
  socket.on("stream_registration_response", json_arg => {
    console.log(json_arg);
  });
  
  let captureStream
  try{
  captureStream = await navigator.mediaDevices.getDisplayMedia(displayMediaOptions)
  isStreaming = true
  recorder = new MediaRecorder(captureStream,{ mimeType: "video/webm; codecs=opus,vp8" })
  recorder.ondataavailable = sendToServer
  recorder.onstop = stop_recording
  chunks = []

  recorder.start(15000)
  async function stop_recording(){
    captureStream.getTracks().forEach((track) => track.stop())
    let formData = new FormData()
    formData.append('streamid',streamid)
    await fetch("http://127.0.0.1:5000/delete_stream",{method:"POST",body:formData})
    isStreaming = false
    return

  }

  socket.on("data_broadcast_result", json_arg => {
    console.log(json_arg);
  });

  async function sendToServer(event){
    if(!isStreaming){
      return
    }

    var buff = await event.data.arrayBuffer();

    if (typeof event.data !== 'string') {
      if (buffer.updating || queue.length > 0) {
        console.log("pushed to queue");
        queue.push(buff);
      } else {
        console.log("appended to buffer");
        buffer.appendBuffer(buff);
      }
    }
    
    socket.emit("broadcast_data", {"data": event.data, "streamid": streamid});

    //chunks.push(event.data)

    //const blobData = new FormData()
    //blobData.append("chunk",new Blob(chunks, { type: 'video/webm' }),"file")
    //let formData = new FormData()
    //formData.append('streamid',streamid)
    //blobData.append('streamid',streamid)

    //await fetch("http://127.0.0.1:5000/update_stream",{method:"POST",body:formData})

    //const cdn = await getCDN(streamid)

    //await fetch(cdn,{method:"POST",body:blobData})
  }

}
catch(err){
  console.log(err)

}
  return captureStream
}
async function stop_stream(){
  isStreaming = false
  recorder.stop()
}
