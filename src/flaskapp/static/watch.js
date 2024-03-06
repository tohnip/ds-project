const delay = s => new Promise(res => setTimeout(res, s*1000));
async function load_stream(streamid){
  console.log("FUCK YOU")
  vidframe = document.getElementById("vidframe")
  vidframe.addEventListener("loadedmetadata", () => {
    vidframe.play()
    .then(() => {})
    .catch((error) => {
      console.error('Error playing video:', error);
    });
});
    flag = false
    const ms = new MediaSource()
    ms.addEventListener("sourceopen", sourceOpen)

    async function sourceOpen(){
      const sourceBuffer = ms.addSourceBuffer("video/webm; codecs=vp8")
      while(true){
        console.log("FUKC YOU")
        const response = await fetch("http://127.0.0.1:5000/get_cdn/"+streamid,{method:"GET"})
        const data = await response.json()
        cdn = data.server_id
        const chunk = await fetch(cdn+"/download_chunk/"+streamid,{method:"GET"})
        const resp = await chunk.blob()

        if(flag){
          var fileReader = new FileReader()
          fileReader.onload = function(event) {
              arrayBuffer = event.target.result
              sourceBuffer.appendBuffer(arrayBuffer)
          };
          await fileReader.readAsArrayBuffer(resp);
        }
        flag = true
        await delay(15)

      }
    }
    vidframe.src = URL.createObjectURL(ms)

}
