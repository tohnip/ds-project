async function load_stream(streamid)
{
    vidframe = document.getElementById("vidframe");
    vidframe.crossOrigin = 'anonymous';

    const response = await fetch("http://127.0.0.1:5000/get_cdn/"+streamid, {method: "GET"});
    const data = await response.json();

    const socket = io("http://"+data.server_address+":"+data.server_port);
    socket.emit("watch_stream", {"streamid": streamid});
    socket.on("stream_request_response", json_arg => {
        console.log("stream request response", json_arg);
    })

    const mediaSource = new MediaSource();
    vidframe.src = URL.createObjectURL(mediaSource)

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

    socket.on('streaming_data', data => {
        if (typeof data !== 'string')
        {
            if (buffer.updating || queue.length > 0) queue.push(data);
            else buffer.appendBuffer(data);
        }
    });
}