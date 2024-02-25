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

function getCDN(){
    return "http://127.0.0.1:5001/upload_chunk" //dummy placeholder. someday this will query the "main" server to get usage data and return the least utilized server
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


  //outside of loop, get time, activate chunks, recorder, start recorder
  //if 5/15 seconds since t, stop the recording, and after sendtoServer is done calling, refresh chunks and start recorder again (we can also try making new recorder)
  //recorder.start()
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
    fetch(getCDN(),{method:"POST",body:blobData})
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
