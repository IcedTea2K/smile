import asyncio
import json
import logging
import uuid
import time

import cv2
from aiohttp import web
import aiohttp_cors
from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription, RTCDataChannel
from aiortc.contrib.media import MediaRelay
import vision

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pc")
pcs: set[RTCPeerConnection] = set()
relay = MediaRelay()

class EmotionRecognitionTrack(MediaStreamTrack):
  """
  A video stream track that consumes frames from an another track.
  """

  kind = "video"

  def __init__(self, track, dc: RTCDataChannel|None):
    super().__init__()  # don't forget this!
    self.track = track
    self.last_time = time.monotonic()
    self.dc = dc
  
  async def recv(self):
    frame = await self.track.recv()

    curr_time = time.monotonic()
    if(curr_time - self.last_time > 0.5):
      self.last_time = curr_time
      await self.predict_emotion(frame)
    
    return frame
  
  async def predict_emotion(self, frame):
    img = frame.to_ndarray(format="bgr24")
    prediction = vision.predict(img)
    if prediction is not None:
      # guess = np.argmax(prediction, axis=-1)[0]
      top = prediction.argsort()[-3:][::-1]
      top_labeled = [f"{vision.labels[guess]} {round(prediction[guess]*100)}%" for guess in top]
      if self.dc and self.dc.readyState == "open":
        self.dc.send(top_labeled.__str__())

async def offer(request):
  params = await request.json()
  offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

  pc = RTCPeerConnection()
  pc_id = "PeerConnection(%s)" % uuid.uuid4()
  pcs.add(pc)

  emotion_track = EmotionRecognitionTrack(None, None)

  # dc = pc.createDataChannel('emotion')

  def log_info(msg, *args):
    logger.info(pc_id + " " + msg, *args)

  log_info("Created for %s", request.remote)

  @pc.on("connectionstatechange")
  async def on_connectionstatechange():
    log_info("Connection state is %s", pc.connectionState)
    if pc.connectionState == "failed":
      await pc.close()
      pcs.discard(pc)

  @pc.on("datachannel")
  def on_datachannel(channel):
    emotion_track.dc = channel

    @channel.on("message")
    def on_message(message):
      print(message)

  @pc.on("track")
  def on_track(track):
    log_info("Track %s received", track.kind)

    if track.kind == "video":
      emotion_track.track = relay.subscribe(track)
      pc.addTrack(emotion_track)

    @track.on("ended")
    async def on_ended():
      log_info("Track %s ended", track.kind)
      # dc.close()

  # handle offer
  await pc.setRemoteDescription(offer)
  
  # send answer
  answer = await pc.createAnswer()
  if answer:
    await pc.setLocalDescription(answer)
  else:
    logger.error("Couldn't create answer")

  return web.Response(
    content_type="application/json",
    text=json.dumps(
      {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
    ),
  )

async def on_shutdown(app):
  # close peer connections
  coros = [pc.close() for pc in pcs]
  await asyncio.gather(*coros)
  pcs.clear()

if __name__ == "__main__":
  app = web.Application()
  app.on_shutdown.append(on_shutdown)
  cors = aiohttp_cors.setup(app)

  offer_resource = cors.add(app.router.add_resource("/offer"))
  cors.add(offer_resource.add_route("POST", offer), {
    "*": aiohttp_cors.ResourceOptions(allow_methods=["POST"], allow_headers=["Content-Type"]),
  })

  web.run_app(
      app, access_log=None, host="0.0.0.0", port=8001
  )