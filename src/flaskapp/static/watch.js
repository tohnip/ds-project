const delay = s => new Promise(res => setTimeout(res, s*1000));
async function load_stream(streamid){
  vidframe = document.getElementById("vidframe");
  vidframe.crossOrigin = 'anonymous';
  // vidframe.addEventListener("loadedmetadata", () => {
  //   vidframe.play()
  //   .then(() => {})
  //   .catch((error) => {
  //     console.error('Error playing video:', error);
  //   });
  // });

  flag = false;
  
  const response = await fetch("http://127.0.0.1:5000/get_cdn/"+streamid,{method:"GET"})
  const data = await response.json();
  
  // const chunk = await fetch("http://"+data.server_address+":"+data.server_port+"/download_chunk/"+streamid,{method:"GET"})
  // const resp = await chunk.blob()

  const socket = io("http://"+data.server_address+":"+data.server_port);
  console.log(socket);

  socket.emit("watch_stream", {"streamid": streamid})
  socket.on("stream_request_response", json_arg => {
    console.log(json_arg);
  })

  const mediaSource = new MediaSource();
  vidframe.src = URL.createObjectURL(mediaSource)

  var queue = [];
  var buffer;

  mediaSource.addEventListener('sourceopen', function(e) {
    vidframe.play()
    .then(() => {
      console.log("video should be playing fine")// Audio is playing.
    })
    .catch(error => {
      console.log(error);
    });;
  
    buffer = mediaSource.addSourceBuffer("video/webm; codecs=opus,vp8");
    buffer.addEventListener('update', function() { // Note: Have tried 'updateend'
      if (queue.length > 0 && !buffer.updating) {
        buffer.appendBuffer(queue.shift());
      }
    });
  }, false);
  
  socket.on('streaming_data', data => {
    if (typeof data !== 'string') {
      if (buffer.updating || queue.length > 0) {
        queue.push(data);
      } else {
        buffer.appendBuffer(data);
      }
    }
  }, false);



  // ms.addEventListener("sourceopen", sourceOpen);
  // let sourceBuffer;

  // function sourceOpen() {
  //   sourceBuffer = ms.addSourceBuffer("video/webm; codecs=vp8");
  //   socket.on("streaming_data", data => {
  //     sourceBuffer.appendBuffer(data);
  //   });

    // while(true){

    //   if(flag){
    //     var fileReader = new FileReader()
    //     fileReader.onload = function(event) {
    //         arrayBuffer = event.target.result
    //         sourceBuffer.appendBuffer(arrayBuffer)
    //     };
    //     await fileReader.readAsArrayBuffer(resp);
    //   }
    //   flag = true
    //   await delay(5)

    // }
  // }

}
