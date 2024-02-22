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
    return "http://127.0.0.1:5000" //dummy placeholder. someday this will query the "main" server to get usage data and return the least utilized server
}


async function stream(){
  let captureStream
  try{
  captureStream = await navigator.mediaDevices.getDisplayMedia(displayMediaOptions)
  isStreaming = true
  const recorder = new MediaRecorder(captureStream,{ mimeType: "video/webm; codecs=vp8" })
  console.log("hohohooho")
  recorder.ondataavailable = pushChunk
  recorder.onstop = sendToServer
  while(isStreaming){
    chunks = []
    recorder.start()
    await delay(5)
    cdn = getCDN()
    console.log("bruhhhhhhhhhh")
    recorder.stop()
  }
  function pushChunk(event){
    if(event.data.size > 0){
      chunks.push(event)
    }
  }
  async function sendToServer(){
    const blob = new Blob(chunks,{type:"video/webm"})
    fetch(getCDN(),{method:"POST",body:blob})
  }

}
catch(err){
  console.log(err)

}
  return captureStream
}
async function stop_stream(){
  isStreaming = false
}
