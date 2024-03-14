// Documentation for media recorder: https://developer.mozilla.org/en-US/docs/Web/API/MediaStream_Recording_API
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

let isStreaming = false;
let recorder = null;


async function getCDN(streamid)
{
    const response = await fetch("http://127.0.0.1:5000/get_cdn/"+streamid, {method: "GET"});
    const data = await response.json();
    return "http://"+data.server_address+":"+data.server_port;
}


async function stop_stream()
{
    isStreaming = false;
    recorder.stop();
}


async function stream()
{
    isStreaming = true;
    let stream_title = document.getElementById("stream_title").value;

    let formData = new FormData();
    formData.append('title', stream_title);

    const response = await fetch("http://127.0.0.1:5000/create_stream", {method: "POST", body: formData});
    const data = await response.json();
    let streamid = data.streamid;

    vidframe = document.getElementById("live");
    vidframe.crossOrigin = 'anonymous';
    const mediaSource = new MediaSource();
    vidframe.src = URL.createObjectURL(mediaSource);

    var queue = [];
    var buffer;

    mediaSource.addEventListener('sourceopen', () => {
        vidframe.play()
        .then(() => {
            console.log("Video should be playing fine now.");
        })
        .catch(error => {
            console.log(error);
        });

        buffer = mediaSource.addSourceBuffer("video/webm; codecs=opus,vp8");
        buffer.addEventListener('update', () => {
            if (queue.length > 0 && !buffer.updating) buffer.appendBuffer(queue.shift());
        });
    });

    const cdnAddress = await getCDN(streamid);
    const socket = io(cdnAddress);

    socket.emit("register_new_stream", {"streamid": streamid});
    socket.on("stream_registration_response", json_arg => {
        console.log("stream registration response", json_arg);
    });
    
    socket.on("data_broadcast_result", json_arg => {
        console.log("data chunk sending result", json_arg);
    });


    let captureStream;


    async function stop_recording()
    {
        captureStream.getTracks().forEach((track) => track.stop());
        let formData = new FormData();
        formData.append('streamid',streamid);
        await fetch("http://127.0.0.1:5000/delete_stream",{method: "POST", body: formData});
        isStreaming = false;
    }


    async function sendToServer(event)
    {
        if (!isStreaming) return;

        if (typeof event.data !== 'string')
        {
            var buff = await event.data.arrayBuffer();
            if (buffer.updating || queue.length > 0)
            {
                console.log("Pushed a video chunk into the queue.");
                queue.push(buff);
            }
            else
            {
                console.log("Appended the video chunk into the buffer.");
                buffer.appendBuffer(buff);
            }
        }

        socket.emit("broadcast_data", {"data": event.data, "streamid": streamid});
    }

    try
    {
        captureStream = await navigator.mediaDevices.getDisplayMedia(displayMediaOptions);
        recorder = new MediaRecorder(captureStream, {mimeType: "video/webm; codecs=opus,vp8"});
        recorder.ondataavailable = sendToServer;
        recorder.onstop = stop_recording;
        recorder.start(10000);
    }
    catch(err)
    {
        console.log(err);
    }

    return captureStream;
}
