import logo from './logo.svg';
import './App.css';
import { useEffect, useState } from 'react';

function App() {
  const stream = useCaptureVideo()

  useEffect(() => {
    const peerConnection = new RTCPeerConnection 
  }, [])

  return (
    <div className="App">
      <video autoPlay 
      ref={video => {
        if (video)
          video.srcObject = stream
      }}/>
      <h1> Happy </h1>
    </div>
  );
}

function useCaptureVideo() {
  const [stream, setStream] = useState(null)

  const captureVideo = async () => {
    if (stream)
      return
    try {
      setStream(await navigator.mediaDevices.getUserMedia({video: true})) 
    } catch (error) {
      console.log(error) 
    }
  }

  captureVideo() // capture video without a way to stop

  return stream
}

export default App;
