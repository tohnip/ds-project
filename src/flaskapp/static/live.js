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
    return data.server_id+"/upload_chunk"
}


async function stream(){
  isStreaming = true
  let stream_title = document.getElementById("stream_title").value
  let formData = new FormData()
  formData.append('title',stream_title)
  const response = await fetch("http://127.0.0.1:5000/create_stream",{method:"POST",body:formData})
  const data = await response.json()
  let streamid = data.streamid

  console.log(streamid)

  let captureStream
  try{
  captureStream = await navigator.mediaDevices.getDisplayMedia(displayMediaOptions)
  isStreaming = true
  recorder = new MediaRecorder(captureStream,{ mimeType: "video/webm; codecs=vp8" })
  recorder.ondataavailable = sendToServer
  recorder.onstop = stop_recording

  //idk i'm tired but the logic is not logicing
  recorder.start(5000)
  async function stop_recording(){
    console.log("wtf")
    captureStream.getTracks().forEach((track) => track.stop())
    let formData = new FormData()
    formData.append('streamid',streamid)
    await fetch("http://127.0.0.1:5000/delete_stream",{method:"POST",body:formData})
    isStreaming = false
    return

  }
  async function sendToServer(event){
    console.log("this should eventually stop")
    if(!isStreaming){
      return
    }
    let chunks = []
    chunks.push(event)
    const blob = new Blob(chunks,{type:"video/webm"})
    const blobData = new FormData()
    blobData.append("chunk",event.data,"file")
    console.log(blobData)
    const cdn = await getCDN(streamid)
    let formData = new FormData()
    formData.append('streamid',streamid)

    await fetch(cdn,{method:"POST",body:blobData})
    await fetch("http://127.0.0.1:5000/update_stream",{method:"POST",body:formData})
    chunks = []

  }

}
catch(err){
  console.log(err)

}
  return captureStream
}
async function stop_stream(){
  console.log("we should have stopped")
  isStreaming = false
  recorder.stop()
}
