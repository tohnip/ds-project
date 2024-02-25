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

const delay = s => new Promise(res => setTimeout(res, s*1000)); //https://stackoverflow.com/questions/14226803/wait-5-seconds-before-executing-next-line

async function getCDN(){
    const response = await fetch("http://127.0.0.1:5000/get_cdn",{method:"GET"})
    const data = await response.json()
    return [data.server_ip+"/upload_chunk",data.server_n] //dummy placeholder. someday this will query the "main" server to get usage data and return the least utilized server
}


async function stream(){
  let captureStream
  try{
  captureStream = await navigator.mediaDevices.getDisplayMedia(displayMediaOptions)
  isStreaming = true
  const recorder = new MediaRecorder(captureStream,{ mimeType: "video/webm; codecs=vp8" })
  console.log("hohohooho")
  recorder.ondataavailable = sendToServer
  recorder.onstop = blah


  let t = Date.now()
  recorder.start(5000)
  console.log(t)
  async function blah(){
      console.log("yooo")
  }
  async function sendToServer(event){
    let chunks = []
    chunks.push(event)
    const blob = new Blob(chunks,{type:"video/webm"})
    const blobData = new FormData()
    blobData.append("chunk",event.data,"file")
    console.log(blobData)
    const [cdn, server_n] = await getCDN()
    fetch("http://127.0.0.1:5000/update_cdn/"+server_n+"/1",{method:"PUT"})
    await fetch(cdn,{method:"POST",body:blobData})
    fetch("http://127.0.0.1:5000/update_cdn/"+server_n+"/0",{method:"PUT"})
    chunks = []
  }

}
catch(err){
  console.log(err)

}
  return captureStream
}
async function stop_stream(){
  recorder.stop()
}
