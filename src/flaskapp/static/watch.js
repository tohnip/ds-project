const delay = s => new Promise(res => setTimeout(res, s*1000));

async function load_stream(streamid){
  vidframe = document.getElementById("vidframe")

  while(true){
    const response = await fetch("http://127.0.0.1:5000/get_cdn/"+streamid,{method:"GET"})
    const data = await response.json()
    cdn = data.server_id

    const chunk = await fetch(cdn+"/download_chunk/"+streamid,{method:"GET"})
    const newObjectUrl = await URL.createObjectURL(chunk.response())
    const oldObjectUrl = vidframe.currentSrc
    if( oldObjectUrl && oldObjectUrl.startsWith('blob:') ) {
        vidframe.src = ''
        URL.revokeObjectURL( oldObjectUrl )
    }
    vidframe.src = await newObjectUrl;
    await vidframe.load();

    await delay(5)
  }

}
