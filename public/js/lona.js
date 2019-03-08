let button, mic, soundRec, soundFile, time, input;
var isRecording = false;
var btnSize = 500;

function setup() {

  mic = new p5.AudioIn(); // Create an audio input
  mic.start(); // ! Users must manually enable their browser microphone

  soundRec = new p5.SoundRecorder(); // Create a sound recorder
  soundRec.setInput(mic) // Connect the microphone to the recorder

  soundFile = new p5.SoundFile(); // create an empty sound file

  // Create the Recording Button
  button = createButton("<i class=\"fa fa-microphone\" aria-hidden=\"true\">");
  button.position(window.innerWidth / 2 - 80, 2 * window.innerHeight / 3);
  document.querySelector("button").classList.add('button--record', 'button', 'js-record', 'button--disabled');

  // Create the Input field
  input = createInput().attribute('placeholder', 'Dein Name');
  input.position(window.innerWidth / 2 - input.size().width / 2, window.innerHeight / 2);
  document.getElementsByTagName("input").placeholder = "Dein Name";

}

// Enable the Recording button only if the inputfield (name) got filled in
function keyReleased() {
  if (input.value() != '') {
    document.querySelector("button").classList.remove('button--disabled');
  } else {
    document.querySelector("button").classList.add('button--disabled');
  }
}

// Enable the Recording button only if the inputfield (name) got filled in
function mousePressed() {
  console.log("Mouse X: " + mouseX)
  console.log("Button X: " + button.position().x)
  console.log(dist(mouseX, mouseY, button.position().x, button.position().y + btnSize / 2));
  if (((dist(mouseX, mouseY, button.position().x, button.position().y + btnSize / 2)) < btnSize / 2) && (input.value() != '')) {
    isRecording = true;
    document.querySelector("button").classList.add('button--active');

    time = getTime();
    getAudioContext().resume();
    console.log("recording....");
    soundRec.record(soundFile); // set up the soundfile to record and start recording
  }
}

function mouseReleased() {
  if (isRecording) {
    document.querySelector("button").classList.remove('button--active');
    soundRec.stop(); // stop recording
    let soundBlob = soundFile.getBlob(); //get the recorded soundFile's blob & store it in a variable

    let formdata = new FormData(); //create a from to of data to upload to the server
    formdata.append('soundBlob', soundBlob, time + '.wav'); // append the sound blob and the name of the file. third argument will show up on the server as req.file.originalname

    //build a HTTP POST request
    var httpRequestOptions = {
      method: 'POST',
      body: formdata, // with our form data packaged above
      headers: new Headers({
        'enctype': 'multipart/form-data' // the enctype is important to work with multer on the server
      })
    };

    // Now we can send the blob to a server...
    var serverUrl = '/upload'; //we've made a POST endpoint on the server at /upload

    // use p5 to make the POST request at our URL and with our options
    httpDo(
      serverUrl,
      httpRequestOptions,
      (successStatusCode) => { //if we were successful...
        console.log("uploaded recording successfully: " + successStatusCode)
      },
      (error) => {
        console.error(error);
      }
    )

    //let formdataName = new FormData(); //create a from to of data to upload to the server
    //formdataName.append('input', input.value()); // append the sound blob and the name of the file. third argument will show up on the server as req.file.originalname
    var serverUrl = '/name';

    let postData = {
      name: input.value()
    };

/*
    var httpRequestOptionsName = {
      method: 'POST',
      body: formdataName, // with our form data packaged above
      headers: new Headers({
        'enctype': 'multipart/form-data' // the enctype is important to work with multer on the server
      })
    };
    */
    console.log("asds");
    httpPost(serverUrl, 'json', postData, function(result) {
      console.log("Name gesendet");
    });


    isRecording = false;
    console.log('recording stopped');

  }


}

//close setup()


function getTime() {
  var str = "";

  var currentTime = new Date()
  var hours = currentTime.getHours()
  var minutes = currentTime.getMinutes()
  var seconds = currentTime.getSeconds()

  if (minutes < 10) {
    minutes = "0" + minutes
  }
  if (seconds < 10) {
    seconds = "0" + seconds
  }
  str += hours + "-" + minutes + "-" + seconds;
  return str;
}
