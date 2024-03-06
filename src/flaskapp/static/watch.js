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
    while(true){
      console.log("FUCK YOU")
      const response = await fetch("http://127.0.0.1:5000/get_cdn/"+streamid,{method:"GET"})
      const data = await response.json()
      cdn = data.server_id
      const chunk = await fetch(cdn+"/download_chunk/"+streamid,{method:"GET"})
      const resp = await chunk.blob()

      vidframe.src = window.URL.createObjectURL(resp)
      //if(flag){
      //  await sourceBuffer.appendBuffer(resp.arrayBuffer())

      console.log(resp)
      flag = true
      await delay(15)
    }
}
