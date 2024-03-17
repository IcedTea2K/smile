import asyncio
import json
import logging
import os
import ssl
import uuid

import cv2
from aiohttp import web
from av import VideoFrame

from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaRelay

logger = logging.getLogger("pc")
pcs = set()
relay = MediaRelay()

class VideoTransformTrack(MediaStreamTrack):
  """
  A video stream track that transforms frames from an another track.
  """

  kind = "video"

  def __init__(self, track, transform):
    super().__init__()  # don't forget this!\

  async def recv(self):
    frame = await self.track.recv()

    img = frame.to_ndarray(format="bgr24")
    cv2.imshow('img', img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
      break

async def offer(request):
  params = await request.json()
  offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

  pc = RTCPeerConnection()
  pc_id = "PeerConnection(%s)" % uuid.uuid4()
  pcs.add(pc)

  def log_info(msg, *args):
    logger.info(pc_id + " " + msg, *args)

  log_info("Created for %s", request.remote)

  @pc.on("datachannel")
  def on_datachannel(channel):
    @channel.on("message")
    def on_message(message):
      if isinstance(message, str) and message.startswith("ping"):
          channel.send("pong" + message[4:])

  @pc.on("connectionstatechange")
  async def on_connectionstatechange():
    log_info("Connection state is %s", pc.connectionState)
    if pc.connectionState == "failed":
      await pc.close()
      pcs.discard(pc)

  @pc.on("track")
  def on_track(track):
    log_info("Track %s received", track.kind)

    if track.kind == "video":
      pc.addTrack(
        VideoTransformTrack(
          relay.subscribe(track), transform=params["video_transform"]
        )
      )

    @track.on("ended")
    async def on_ended():
      log_info("Track %s ended", track.kind)

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


app = web.Application()
app.on_shutdown.append(on_shutdown)
app.router.add_post("/offer", offer)
web.run_app(
    app, access_log=None, host="0.0.0.0", port=8001
)