document.addEventListener('DOMContentLoaded', function() {
    var startButton = document.getElementById('start');
    var stopButton = document.getElementById('stop');
    var playButton = document.getElementById('play');
    var audioPlayer = document.getElementById('audioPlayer');
    var mediaRecorder;

    startButton.addEventListener('click', function() {
        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(function(stream) {
                mediaRecorder = new MediaRecorder(stream);
                mediaRecorder.start();
            });
    });

    stopButton.addEventListener('click', function() {
        if (mediaRecorder && mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop();
        }
    });

    playButton.addEventListener('click', function() {
        if (audioPlayer.src) {
            audioPlayer.play();
        }
    });

    if (audioPlayer.src) {
        audioPlayer.addEventListener('ended', function() {
            audioPlayer.currentTime = 0;
        });
    }

    if (mediaRecorder) {
        mediaRecorder.addEventListener('dataavailable', function(event) {
            var audioBlob = new Blob([event.data], { type: 'audio/webm' });
            var audioUrl = URL.createObjectURL(audioBlob);
            audioPlayer.src = audioUrl;
        });
    }
});
