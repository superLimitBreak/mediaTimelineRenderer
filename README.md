# mediaTimelineRenderer

Render media files (video or audio) to png timeline strips.

This is used as an optional component of [superLimitBreak/stageViewer](https://github.com/superLimitBreak/stageViewer)

> PLACEHOLDER REPO - No implementation yet

## Description
* `/input/`
    * `video.mp4` (mtime 1234)
    * `audio.mp3` (mtime 5678)
* `/output/`
    * `video.mp4.png` (mtime 1234)
    * `audio.mp3.png` (mtime 5678)

Optimisation: If the `mtimes` of the source and destination file match, there is no need to process the file

Possible output of `x2` and `x4` images for retina displays?

### Configuration

* output image format (jpg or png)
* output image height
* pixels per second
    * from this frame extraction time is derived
* watch daemon time (seconds)
    * If absent just process and exit
    * If present `fast_scan` at duration to reprocess media
        * Hopefully with `mtime` caching this is a trivial operation

## Container considerations

It would be good if the core `python` program was containerised (derived from an `alpine` container) and referenced a pure `ffmpeg` container.

https://forums.docker.com/t/how-can-i-run-docker-command-inside-a-docker-container/337/2

```bash
    docker pull jrottenberg/ffmpeg
    docker run --rm -it jrottenberg/ffmpeg
    docker run -it -v /var/run/docker.sock:/var/run/docker.sock ubuntu:latest sh -c "apt-get update ; apt-get install docker.io -y ; bash"
```

## Python media extraction references

To extract images and audio directly from `ffmpeg` into `python`

* https://stackoverflow.com/questions/13294919/can-you-stream-images-to-ffmpeg-to-construct-a-video-instead-of-saving-them-t
* http://zulko.github.io/blog/2013/09/27/read-and-write-video-frames-in-python-using-ffmpeg/
* http://zulko.github.io/blog/2013/10/04/read-and-write-audio-files-in-python-using-ffmpeg/
